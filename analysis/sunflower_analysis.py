"""Tasks 2 and 3 for the sunflower group: feature choice, sample size, bounds and error budget.

Usage (environment active, from the repository folder):
    python analysis/sunflower_analysis.py --workdir runs/sunflower --lab analysis/lab_measurements.json \
        --out analysis/results

Input
* the project (reviewed photos with crop, pile_id, total_weight_g, optional manual_count,
  scale_mm_per_px, condition, collector)
* ``lab_measurements.json``: side experiments of task 1 that are not photos (balance repeats, seed
  batches); see ``load_lab`` for the format.

Output (in --out): results.md (all numbers), results.json, and PNG plots.
Only photos marked ``condition == "main"`` (or without a condition) are used to fit the models; the
other conditions (touching, re-spread, ...) are experiments that are compared against the main ones.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detkit.project import Project                                   # noqa: E402
from detkit.weight import (AreaTimesConstant, CountTimesConstant, SampleTable, bootstrap_ci,  # noqa: E402
                           evaluate_model, learning_curve, propagate)
from detkit.weight.stats import pile_key, pile_points                # noqa: E402

FEATURES = ["count", "total_area_px", "mean_area_px", "median_area_px", "mean_diag_px",
            "total_area_mm2", "mean_area_mm2"]
CROP = "sunflower"


# ---- inputs ---------------------------------------------------------------------------------------
def load_lab(path: str | Path | None) -> dict:
    """lab_measurements.json, e.g.
    {
      "balance_resolution_g": 1,
      "balance_repeats": {"pile_A": [52, 52, 53, 52, 52]},       # same pile weighed several times
      "reference_check": {"items": "4 x 2-euro coins", "nominal_g": 34.0, "reading_g": 34},
      "seed_batches": [{"n_seeds": 100, "weight_g": 7}, ...]       # hand-counted batches
    }"""
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def subset(t: SampleTable, **conds) -> SampleTable:
    """Rows whose meta matches every condition; value None means 'missing or empty'."""
    out = []
    for s in t:
        ok = True
        for k, v in conds.items():
            got = s.meta.get(k)
            if v is None:
                ok &= got in (None, "")
            elif isinstance(v, (list, tuple, set)):
                ok &= got in v
            else:
                ok &= got == v
        if ok:
            out.append(s)
    return SampleTable(out)


MAIN = (None, "", "main")
REPEATS = (None, "", "main", "same_layout", "re_spread")   # photos used for photo-to-photo spread


def main_rows(t: SampleTable) -> SampleTable:
    return SampleTable([s for s in t if s.meta.get("condition") in MAIN])


def with_condition(t: SampleTable, conds) -> SampleTable:
    return SampleTable([s for s in t if s.meta.get("condition") in conds])


# ---- task 2 ---------------------------------------------------------------------------------------
def feature_table(t: SampleTable) -> list[dict]:
    """Per feature: pile-level Pearson r with weight, its 95 % cluster-bootstrap CI, and the relative spread
    of weight/feature over piles (a feature x constant model works best when this is small)."""
    rows = []
    for f in FEATURES:
        x, y, ids = pile_points(t, f, crop=CROP)
        ok = x != 0
        x, y = x[ok], y[ok]
        if len(x) < 3:
            continue
        r = float(np.corrcoef(x, y)[0, 1]) if np.ptp(x) and np.ptp(y) else float("nan")
        ci = bootstrap_ci(t, f, crop=CROP, stat="r", n_boot=2000)
        ratio = y / x
        rows.append({"feature": f, "n_piles": len(x), "r": r, "r_lo": ci and ci[0], "r_hi": ci and ci[1],
                     "ci_note": "fewer than 5 piles: CI not reliable" if len(x) < 5 else "",
                     "ratio_mean": float(ratio.mean()), "ratio_rel_sd": float(ratio.std(ddof=1) / ratio.mean())})
    return sorted(rows, key=lambda r: r["ratio_rel_sd"])


def within_between(t: SampleTable, feature: str) -> dict:
    """How many photos per pile? Compare the spread of the feature between photos of ONE pile (photo /
    detector noise) with the spread of weight/feature between piles. Relative standard deviations."""
    by_pile: dict[str, list[float]] = {}
    for s in t.for_crop(CROP):
        v = s.get(feature)
        k = pile_key(s)
        if v is not None and not k.startswith("__photo__"):
            by_pile.setdefault(k, []).append(float(v))
    within = [statistics.stdev(v) / statistics.fmean(v) for v in by_pile.values() if len(v) > 1 and statistics.fmean(v)]
    x, y, _ = pile_points(t, feature, crop=CROP)
    ratio = y / x if len(x) else np.array([])
    return {"feature": feature, "piles_with_repeats": len(within),
            "within_pile_rel_sd": float(np.sqrt(np.mean(np.square(within)))) if within else None,
            "between_pile_ratio_rel_sd": float(ratio.std(ddof=1) / ratio.mean()) if len(ratio) > 2 else None}


def leave_one_pile_out(t: SampleTable, model_cls) -> dict:
    """Honest error: fit on all piles but one, predict that pile's photos; repeat for every pile. Also
    the share of held-out photos that fall inside their bounds (should be close to 95 %)."""
    piles = sorted({pile_key(s) for s in t if s.weight_g is not None})
    rows = []
    for p in piles:
        train = SampleTable([s for s in t if pile_key(s) != p])
        test = [s for s in t if pile_key(s) == p and s.weight_g is not None]
        m = model_cls().fit(train)
        for s in test:
            e = m.predict(s.features, s.crop)
            rows.append({"pile": p, "file": s.file, "true_g": s.weight_g, "pred_g": e.weight_g,
                         "low_g": e.low_g, "high_g": e.high_g,
                         "inside": (e.low_g is not None and e.low_g <= s.weight_g <= e.high_g)})
    if not rows:
        return {"n": 0}
    err = np.array([r["pred_g"] - r["true_g"] for r in rows])
    rel = err / np.array([r["true_g"] for r in rows])
    with_b = [r for r in rows if r["low_g"] is not None]
    return {"n": len(rows), "mae_g": float(np.abs(err).mean()), "bias_g": float(err.mean()),
            "mape": float(np.abs(rel).mean()), "rel_sd": float(rel.std(ddof=1)) if len(rel) > 1 else None,
            "coverage": (sum(r["inside"] for r in with_b) / len(with_b)) if with_b else None, "rows": rows}


# ---- task 3 ---------------------------------------------------------------------------------------
def stage_errors(t: SampleTable, lab: dict, model_feature: str, top_rel_sd: float | None = None) -> dict:
    """Relative standard error of each stage, measured in task 1. Returns {stage: (value, how)}.
    Each physical error source is counted ONCE:

    * balance: max(rounding resolution/sqrt(12), sd of repeated readings) / mean main weight. (Repeated
      readings are already rounded, so the two are not added.)
    * kernel_weight (count model): seed-to-seed mass variation for a sample of N seeds, cv_seed/sqrt(N);
      cv_seed from hand-counted batches, with the balance rounding part removed.
    * detector (count model): sd of (detected count - hand count)/hand count on photos with manual_count.
      This already contains photo-to-photo counting noise, so "photo" is only used when there are no hand
      counts. A constant bias is absorbed by the calibrated constant and not counted.
    * photo (area model, or count model without hand counts): photo-to-photo spread of the feature for the
      same pile (repeat photos).
    * scale (area model in px): 2 x relative sd of scale_mm_per_px over the photos: the camera distance
      changes the pixel area as scale^2. For mm2 features the measured scale corrects this, and only the
      error of reading the ruler remains (``lab["scale_read_rel"]``, if measured).
    * unexplained: what the top-down spread (``top_rel_sd``) has that the stages above do not explain,
      sqrt(top^2 - bottom^2) (e.g. seed shape / density variation for the area model).
    """
    out: dict[str, tuple[float, str]] = {}
    main = main_rows(t).with_weight()
    w_mean = statistics.fmean([s.weight_g for s in main]) if len(main) else None
    res = lab.get("balance_resolution_g")
    reps = [v for v in (lab.get("balance_repeats") or {}).values() if len(v) > 1]
    if w_mean and (res or reps):
        u_round = (res or 0) / math.sqrt(12)
        u_rep = math.sqrt(statistics.fmean([statistics.variance(v) for v in reps])) if reps else 0.0
        u = max(u_round, u_rep)
        out["balance"] = (u / w_mean, f"max(rounding {u_round:.3f} g, repeat sd {u_rep:.3f} g) "
                                      f"/ mean main weight {w_mean:.1f} g")
    is_count = model_feature == "count"
    batches = lab.get("seed_batches") or []
    if is_count and len(batches) > 1:
        per_seed = [b["weight_g"] / b["n_seeds"] for b in batches]
        n_b = statistics.fmean([b["n_seeds"] for b in batches])
        w_b = statistics.fmean([b["weight_g"] for b in batches])
        var_batch = (statistics.stdev(per_seed) / statistics.fmean(per_seed)) ** 2
        var_round = ((res or 0) / math.sqrt(12) / w_b) ** 2
        cv_seed = math.sqrt(max(var_batch - var_round, 0.0) * n_b)
        n_main = statistics.fmean([s.features["count"] for s in main]) if len(main) else None
        if n_main:
            note = "" if var_batch > var_round else "; batch spread not above rounding"
            out["kernel_weight"] = (cv_seed / math.sqrt(n_main),
                                    f"cv per seed {cv_seed:.3f} from {len(batches)} batches of ~{n_b:.0f} seeds "
                                    f"weighed at {res} g (rounding removed; few batches: rough) "
                                    f"/ sqrt(mean count {n_main:.0f}){note}")
    counted = [s for s in t if s.meta.get("manual_count") not in (None, "")]
    if is_count and len(counted) > 1:
        rel = [(s.features["count"] - float(s.meta["manual_count"])) / float(s.meta["manual_count"]) for s in counted]
        out["detector"] = (statistics.stdev(rel),
                           f"sd of (count - hand count) / hand count on {len(rel)} photos "
                           f"(mean bias {100 * statistics.fmean(rel):+.1f} %, absorbed by the calibration)")
    if not is_count or "detector" not in out:
        wb = within_between(with_condition(t, REPEATS), model_feature)
        if wb["within_pile_rel_sd"] is not None:
            out["photo"] = (wb["within_pile_rel_sd"], f"photo-to-photo spread of {model_feature} within a pile "
                                                      f"({wb['piles_with_repeats']} piles)")
    if model_feature.endswith("_px") and not is_count:
        sc = [float(s.meta["scale_mm_per_px"]) for s in t if s.meta.get("scale_mm_per_px")]
        if len(sc) > 1:
            out["scale"] = (2 * statistics.stdev(sc) / statistics.fmean(sc),
                            f"2 x relative sd of scale_mm_per_px over {len(sc)} photos (camera distance)")
    elif model_feature.endswith("mm2") and lab.get("scale_read_rel"):
        out["scale"] = (2 * float(lab["scale_read_rel"]), "2 x relative error of reading the ruler")
    if top_rel_sd is not None and out:
        bottom = math.sqrt(sum(v[0] ** 2 for v in out.values()))
        if top_rel_sd > bottom:
            out["unexplained"] = (math.sqrt(top_rel_sd ** 2 - bottom ** 2),
                                  "sqrt(top-down^2 - sum of the stages above^2): not measured separately")
    return out


# ---- report -----------------------------------------------------------------------------------------
def _f(v, nd=3, pct=False):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{100 * v:.{max(nd - 2, 1)}f} %" if pct else f"{v:.{nd}f}"


def run(workdir: str, lab_path: str | None, out_dir: str, use: str = "reviewed") -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # use="reviewed": boxes as saved in the Review tab (we save the detector's boxes WITHOUT correcting them,
    # so they equal the raw detections the app uses in deployment); use="predictions": predictions.json.
    t_all = SampleTable.from_project(Project.load(workdir), reviewed_only=(use == "reviewed"),
                                     use=use).for_crop(CROP)
    lab = load_lab(lab_path)
    t = main_rows(t_all).with_weight()
    res: dict = {"n_photos_all": len(t_all), "n_photos_main": len(t)}
    lines = ["# Sunflower: tasks 2 and 3 results", "",
             f"Boxes from: {use}. Sunflower photos: {len(t_all)}; main-collection photos with a weight: {len(t)}.", ""]

    # task 2a: features
    ft = feature_table(t)
    res["features"] = ft
    lines += ["## Task 2: which feature tells the weight", "",
              "Pile level (photos of one pile averaged). r = Pearson correlation with the weight, CI = 95 % "
              "cluster bootstrap over piles. ratio spread = relative sd of weight / feature over piles: the "
              "error a feature x constant model would make.", "",
              "| feature | piles | r | r 95 % CI | weight/feature | ratio spread |", "|---|---|---|---|---|---|"]
    for r in ft:
        lines.append(f"| {r['feature']} | {r['n_piles']} | {_f(r['r'])} | {_f(r['r_lo'])} .. {_f(r['r_hi'])}"
                     f"{' (!)' if r['ci_note'] else ''} | "
                     f"{r['ratio_mean']:.4g} | {_f(r['ratio_rel_sd'], pct=True)} |")
    # task 2b: learning curve on count and total area
    lines += ["", "### How many piles do we need", ""]
    for f in ("count", "total_area_mm2" if any(r["feature"] == "total_area_mm2" for r in ft) else "total_area_px"):
        x, _, _ = pile_points(t, f, crop=CROP)
        sizes = list(range(3, len(x) + 1))
        lc = learning_curve(t, f, sizes=sizes, crop=CROP, repeats=500) or []
        res[f"learning_curve_{f}"] = lc
        lines += [f"**{f}**: spread of the fitted constant (weight / {f}) over random subsets of n piles.", "",
                  "| n piles | constant mean | constant rel. sd | r mean | r 2.5 % |", "|---|---|---|---|---|"]
        for e in lc:
            if e["ratio_mean"] is not None:
                lines.append(f"| {e['n']} | {e['ratio_mean']:.4g} | {_f(e['ratio_rel_sd'], pct=True)} | "
                             f"{_f(e['r_mean'])} | {_f(e['r_lo'])} |")
        lines.append("")
        _plot_lc(lc, f, out / f"learning_curve_{f}.png")
    # task 2c: photos per pile
    wb = [within_between(with_condition(t_all, REPEATS), f)
          for f in ("count", "total_area_px")]
    res["within_between"] = wb
    lines += ["### How many photos of the same pile", "",
              "| feature | piles with repeats | photo-to-photo spread (same pile) | pile-to-pile spread of weight/feature |",
              "|---|---|---|---|"]
    for w in wb:
        lines.append(f"| {w['feature']} | {w['piles_with_repeats']} | {_f(w['within_pile_rel_sd'], pct=True)} | "
                     f"{_f(w['between_pile_ratio_rel_sd'], pct=True)} |")

    # calibrate both models + honest errors
    lines += ["", "## Calibrated models", ""]
    for cls in (CountTimesConstant, AreaTimesConstant):
        m = cls().fit(t)
        ev = evaluate_model(m, t)
        lo = leave_one_pile_out(t, cls)
        b = m.bounds.get(CROP, {})
        res[cls.name] = {"constant": m.constants.get(CROP), "bounds": b, "fit_eval": {k: v for k, v in ev.items() if k != "rows"},
                         "lopo": {k: v for k, v in lo.items() if k != "rows"}}
        lines += [f"**{cls.name}**: constant {m.constants.get(CROP, float('nan')):.6g} {cls.unit}; 95 % bounds "
                  f"+/- {_f(b.get('rel_halfwidth'), pct=True)} ({b.get('n_piles', '-')} piles).",
                  f"* on the photos it was fitted on: MAPE {_f(ev['mape'], pct=True)}, bias {_f(ev['bias_g'])} g (optimistic)",
                  f"* leave-one-pile-out: MAPE {_f(lo.get('mape'), pct=True)}, bias {_f(lo.get('bias_g'))} g, "
                  f"held-out photos inside their bounds {_f(lo.get('coverage'), pct=True)}", ""]
        _plot_pred(lo.get("rows", []), cls.name, out / f"lopo_{cls.name}.png")

    # task 3: bottom-up vs top-down
    lines += ["## Task 3: error budget", ""]
    for cls, feat in ((CountTimesConstant, "count"), (AreaTimesConstant, "total_area_px")):
        top = res[cls.name]["bounds"].get("rel_sd")
        st = stage_errors(t_all, lab, feat, top_rel_sd=top)
        if not st:
            continue
        w_mean = statistics.fmean([s.weight_g for s in t]) if len(t) else 0.0
        pr = propagate({k: v[0] for k, v in st.items()}, weight_g=w_mean)
        res[f"budget_{cls.name}"] = {"stages": {k: v[0] for k, v in st.items()}, "how": {k: v[1] for k, v in st.items()},
                                     "propagate": pr, "top_down_rel_sd": top}
        lines += [f"**{cls.name}** (at the mean pile weight {w_mean:.1f} g)", "",
                  "| stage | relative error | share of variance | how measured |", "|---|---|---|---|"]
        for k, (v, how) in st.items():
            lines.append(f"| {k} | {_f(v, pct=True)} | {_f(pr['budget'][k], pct=True)} | {how} |")
        lines += ["", f"Total (root sum of squares, incl. 'unexplained' if present): {_f(pr['rel_total'], pct=True)} "
                      f"(+/- {pr['weight_u_g']:.2f} g, 1 sd). Dominant stage: {pr['dominant']}.",
                  f"Top-down (spread of weight/feature over the main photos): {_f(top, pct=True)}.", ""]
    (out / "results.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "results.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    return res


def _plot_lc(lc, feature, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pts = [e for e in lc if e["ratio_rel_sd"] is not None]
    if not pts:
        return
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.plot([e["n"] for e in pts], [100 * e["ratio_rel_sd"] for e in pts], marker="o")
    ax.set_xlabel("number of piles")
    ax.set_ylabel("rel. sd of fitted constant (%)")
    ax.set_title(f"Learning curve: {feature}")
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_pred(rows, name, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    tr = [r["true_g"] for r in rows]
    pr = [r["pred_g"] for r in rows]
    err = [[r["pred_g"] - (r["low_g"] if r["low_g"] is not None else r["pred_g"]) for r in rows],
           [(r["high_g"] if r["high_g"] is not None else r["pred_g"]) - r["pred_g"] for r in rows]]
    ax.errorbar(tr, pr, yerr=err, fmt="o", ms=4, capsize=2)
    lim = [0, max(tr + pr) * 1.1]
    ax.plot(lim, lim, "k--", lw=1)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("balance (g)")
    ax.set_ylabel("predicted (g), held-out pile")
    ax.set_title(name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--lab")
    ap.add_argument("--out", default="analysis/results")
    ap.add_argument("--use", choices=["reviewed", "predictions"], default="reviewed")
    a = ap.parse_args()
    r = run(a.workdir, a.lab, a.out, a.use)
    print((Path(a.out) / "results.md").read_text(encoding="utf-8"))
