"""Analysis of 22 Oct 2026: Jia's task 4 and extra piles, the Gauge R&R, and the business case numbers.

Input: detector output of .github/workflows/detect.yml (analysis/results/2026-10-22_detect*/{std,raw}/<folder>/
predictions.json), data/samples.csv, the note outlines (data/photos/<folder>/note_zones.json) and the constant of
19 Oct (analysis/results/main_std/weight_config.json).

Counting rule (same as the app): sunflower boxes only, photo resized to 0.110 mm per pixel from the markers.
Boxes whose centre lies inside a sticky-note outline are dropped (the photos are not changed).

Output (analysis/results/2026-10-22_analysis/): per_photo.csv, per_pile.csv, results.json, results.md.
Usage: python analysis/results_2026_10_22.py
"""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "analysis/results"
OUT = RES / "2026-10-22_analysis"
CROP = "sunflower"

cfg = json.loads((RES / "main_std/weight_config.json").read_text())
G_PER_SEED = cfg["crop_count_constants"][CROP]                 # 0.05294 g per seed (Hadi P01-P08, 19 Oct)
HALF = cfg["crop_count_constants_bounds"][CROP]["rel_halfwidth"]  # 0.0998 -> +-10.0 %

RUNS = {"2026-10-19_main": "2026-10-22_detect_main"}
for f in ("2026-10-20_task4", "2026-10-21_extra_piles", "2026-10-19_gauge_rr"):
    RUNS[f] = "2026-10-22_detect"


def load_pred(folder: str, mode: str) -> dict:
    p = RES / RUNS[folder] / mode / folder / "predictions.json"
    return json.loads(p.read_text()) if p.exists() else {}


def zones(folder: str) -> dict:
    p = ROOT / "data/photos" / folder / "note_zones.json"
    if not p.exists():
        return {}
    return {k: np.array(v, float) for k, v in json.loads(p.read_text()).items() if not k.startswith("_")}


def inside(poly: np.ndarray, x: float, y: float) -> bool:
    """Ray casting point-in-polygon."""
    n, ins = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def count(pred: dict, poly: np.ndarray | None) -> tuple[int, int, int]:
    """(sunflower boxes kept, sunflower boxes dropped in the note, boxes of all classes kept)."""
    keep = drop = allc = 0
    for d in pred.get("detections", []):
        x1, y1, x2, y2 = d["bbox"]
        in_note = poly is not None and inside(poly, (x1 + x2) / 2, (y1 + y2) / 2)
        if not in_note:
            allc += 1
        if d["label"] == CROP:
            if in_note:
                drop += 1
            else:
                keep += 1
    return keep, drop, allc


def before_weight(notes: str, after: float | None) -> float | None:
    m = re.search(r"weight before (\d+(?:\.\d+)?)\s*g", notes or "")
    if m:
        return float(m.group(1))
    if "consistent with before" in (notes or ""):
        return after
    return None


rows = list(csv.DictReader(open(ROOT / "data/samples.csv", encoding="utf-8-sig")))
photos = []
for folder in RUNS:
    std, raw, zn = load_pred(folder, "std"), load_pred(folder, "raw"), zones(folder)
    for r in (r for r in rows if r["folder"] == folder):
        f = r["file"]
        if f not in std:
            continue
        poly = zn.get(f)
        n, dropped, n_all = count(std[f], poly)
        n_raw = count(raw[f], poly)[0] if f in raw else None
        w = float(r["total_weight_g"]) if r["total_weight_g"] else None
        pred = n * G_PER_SEED
        low, high = pred * (1 - HALF), pred * (1 + HALF)
        hm = re.search(r"camera height (\w+)", r["notes"])
        photos.append({
            "file": f, "folder": folder, "pile_id": r["pile_id"], "condition": r["condition"],
            "collector": r["collector"], "phone": r["phone"], "height_cm": r["height_cm"],
            "height_class": hm.group(1) if hm else "",
            "scale_mm_per_px": std[f].get("scale_mm_per_px"), "scale_note": std[f].get("scale_note", ""),
            "count_sunflower": n, "boxes_in_note_dropped": dropped, "count_all_classes": n_all,
            "count_sunflower_no_fixed_scale": n_raw,
            "weight_before_g": before_weight(r["notes"], w), "weight_after_g": w,
            "predicted_g": round(pred, 2), "low_g": round(low, 2), "high_g": round(high, 2),
            "error_g": round(pred - w, 2) if w else None,
            "error_pct": round(100 * (pred - w) / w, 1) if w else None,
            "inside_bounds": (low <= w <= high) if w else None,
            "g_per_seed": round(w / n, 5) if (w and n) else None,
        })

OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / "per_photo.csv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(photos[0]), lineterminator="\n")
    wr.writeheader()
    wr.writerows(photos)

# ---------------------------------------------------------------- pile level (mean of the photos of a pile)
piles: dict = {}
for p in photos:
    if p["condition"] not in ("main", "Task4") or not p["weight_after_g"]:
        continue
    k = (p["folder"], p["pile_id"])
    piles.setdefault(k, {"folder": p["folder"], "pile_id": p["pile_id"], "collector": p["collector"],
                         "weight_after_g": p["weight_after_g"], "weight_before_g": p["weight_before_g"],
                         "counts": []})["counts"].append(p["count_sunflower"])
pile_rows = []
for v in piles.values():
    c = float(np.mean(v["counts"]))
    pred = c * G_PER_SEED
    w, wb = v["weight_after_g"], v["weight_before_g"]
    pile_rows.append({**{k: v[k] for k in ("folder", "pile_id", "collector", "weight_before_g", "weight_after_g")},
                      "n_photos": len(v["counts"]), "mean_count": round(c, 1),
                      "photo_diff_pct": round(100 * (max(v["counts"]) - min(v["counts"])) / c, 1),
                      "predicted_g": round(pred, 2), "error_pct_vs_after": round(100 * (pred - w) / w, 1),
                      "error_pct_vs_before": round(100 * (pred - wb) / wb, 1) if wb else None,
                      "inside_bounds": pred * (1 - HALF) <= w <= pred * (1 + HALF),
                      "g_per_seed": round(w / c, 5)})
with open(OUT / "per_pile.csv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(pile_rows[0]), lineterminator="\n")
    wr.writeheader()
    wr.writerows(pile_rows)


def group(sel):
    return [p for p in pile_rows if sel(p)]


def summary(ps, label):
    if not ps:
        return {"group": label, "n_piles": 0}
    gps = np.array([p["g_per_seed"] for p in ps])
    err = np.array([p["error_pct_vs_after"] for p in ps])
    n = len(gps)
    out = {"group": label, "n_piles": n, "g_per_seed_mean": round(float(gps.mean()), 5),
           "g_per_seed_rel_sd_pct": round(float(100 * gps.std(ddof=1) / gps.mean()), 2) if n > 1 else None,
           "bias_pct": round(float(err.mean()), 2), "mape_pct": round(float(np.abs(err).mean()), 2),
           "inside_bounds": f"{sum(p['inside_bounds'] for p in ps)} of {n}"}
    if n > 1:
        se = gps.std(ddof=1) / math.sqrt(n)
        t = stats.t.ppf(0.975, n - 1)
        out["g_per_seed_95ci"] = [round(float(gps.mean() - t * se), 5), round(float(gps.mean() + t * se), 5)]
    return out


main = group(lambda p: p["folder"] == "2026-10-19_main")
t4 = group(lambda p: p["folder"] == "2026-10-20_task4")
extra = group(lambda p: p["folder"] == "2026-10-21_extra_piles")
results = {"constant_used_g_per_seed": G_PER_SEED, "bound_rel_halfwidth": HALF,
           "groups": [summary(main, "Hadi P01-P08 (10-24 g)"), summary(t4, "Jia task 4 (11-23 g)"),
                      summary(extra, "Jia P09-P13 (26-34 g)"), summary(main + t4 + extra, "all 17 piles")]}

# Welch t-test: is Jia's grams per seed different from Hadi's?
for lab, g in (("task4", t4), ("extra", extra), ("jia_all", t4 + extra)):
    if len(g) > 1:
        a = [p["g_per_seed"] for p in main]
        b = [p["g_per_seed"] for p in g]
        tt = stats.ttest_ind(a, b, equal_var=False)
        results[f"welch_hadi_vs_{lab}"] = {"diff_pct": round(100 * (np.mean(b) - np.mean(a)) / np.mean(a), 2),
                                            "p_value": round(float(tt.pvalue), 3)}

# trend of grams per seed with pile weight over all piles (does the constant hold for bigger piles?)
allp = main + t4 + extra
w = np.array([p["weight_after_g"] for p in allp])
g = np.array([p["g_per_seed"] for p in allp])
lr = stats.linregress(w, g)
results["trend_g_per_seed_vs_weight"] = {"slope_pct_per_10g": round(float(100 * lr.slope * 10 / g.mean()), 2),
                                         "r": round(float(lr.rvalue), 3), "p_value": round(float(lr.pvalue), 3)}

# ---------------------------------------------------------------- Gauge R&R (one untouched pile)
rr = [p for p in photos if p["condition"] == "gauge_rr"]
if rr:
    def cell(sel):
        v = [p["count_sunflower"] for p in rr if sel(p)]
        return {"n": len(v), "mean": round(float(np.mean(v)), 1) if v else None, "counts": v}
    gr = {"all": cell(lambda p: True)}
    for ph in sorted({p["phone"] for p in rr}):
        for who in ("Hadi", "Jia"):
            for h in ("normal", "high"):
                gr[f"{ph} | {who} | {h}"] = cell(lambda p, ph=ph, who=who, h=h: p["phone"] == ph and
                                                  p["collector"] == who and p["height_class"] == h)
    allc = np.array([p["count_sunflower"] for p in rr], float)
    gr["rel_sd_all_pct"] = round(float(100 * allc.std(ddof=1) / allc.mean()), 2)
    gr["range_pct"] = round(float(100 * (allc.max() - allc.min()) / allc.mean()), 2)
    # one-factor comparisons (fixed scale); and the same without the fixed scale
    for fac in ("phone", "collector", "height_class"):
        lv = {}
        for p in rr:
            lv.setdefault(p[fac], []).append(p["count_sunflower"])
        gr[f"by_{fac}"] = {k: round(float(np.mean(v)), 1) for k, v in lv.items()}
    rawc = [p["count_sunflower_no_fixed_scale"] for p in rr if p["count_sunflower_no_fixed_scale"] is not None]
    if rawc:
        rawc = np.array(rawc, float)
        gr["no_fixed_scale_rel_sd_pct"] = round(float(100 * rawc.std(ddof=1) / rawc.mean()), 2)
        gr["no_fixed_scale_range_pct"] = round(float(100 * (rawc.max() - rawc.min()) / rawc.mean()), 2)
    sc = [p["scale_mm_per_px"] for p in rr if p["scale_mm_per_px"]]
    gr["scale_mm_per_px_range"] = [round(min(sc), 4), round(max(sc), 4)] if sc else None
    results["gauge_rr"] = gr

# ---------------------------------------------------------------- effect of the note filter and of the fixed scale
results["note_boxes_dropped"] = {p["file"]: p["boxes_in_note_dropped"] for p in photos if p["boxes_in_note_dropped"]}
fs = [(p["count_sunflower"], p["count_sunflower_no_fixed_scale"]) for p in photos
      if p["count_sunflower_no_fixed_scale"] and p["folder"] != "2026-10-19_gauge_rr"]
if fs:
    d = np.array([100 * (b - a) / a for a, b in fs])
    results["no_fixed_scale_vs_fixed_pct"] = {"mean": round(float(d.mean()), 1), "min": round(float(d.min()), 1),
                                              "max": round(float(d.max()), 1), "n_photos": len(d)}

(OUT / "results.json").write_text(json.dumps(results, indent=1))
print(json.dumps(results, indent=1))

# ---------------------------------------------------------------- pooled model over all 17 piles, honest error, stop rule
ALL = main + t4 + extra
g = np.array([p["g_per_seed"] for p in ALL])
c = np.array([p["mean_count"] for p in ALL])
wt = np.array([p["weight_after_g"] for p in ALL])
k_all = float(wt.sum() / c.sum())        # pooled grams per seed: total weight / total count (ratio estimator)
s_rel = float(g.std(ddof=1) / g.mean())  # pile-to-pile relative spread
n = len(g)
lopo = []
for i in range(n):
    m = np.ones(n, bool); m[i] = False
    k = wt[m].sum() / c[m].sum()
    s = (g[m]).std(ddof=1) / g[m].mean()
    h = stats.t.ppf(0.975, n - 2) * s * math.sqrt(1 + 1 / (n - 1))
    pred = c[i] * k
    lopo.append({"pile": ALL[i]["pile_id"], "err_pct": 100 * (pred - wt[i]) / wt[i],
                 "inside": pred * (1 - h) <= wt[i] <= pred * (1 + h)})
results["pooled_17"] = {
    "g_per_seed": round(k_all, 5), "rel_sd_pct": round(100 * s_rel, 2),
    "bound_halfwidth_pct": round(100 * stats.t.ppf(0.975, n - 1) * s_rel * math.sqrt(1 + 1 / n), 2),
    "lopo_mape_pct": round(float(np.mean([abs(x["err_pct"]) for x in lopo])), 2),
    "lopo_inside": f"{sum(x['inside'] for x in lopo)} of {n}",
    "lopo": [{"pile": x["pile"], "err_pct": round(x["err_pct"], 1), "inside": bool(x["inside"])} for x in lopo]}

# bound versus number of piles, with the pooled spread; and how much one more pile buys
curve = []
for k in (3, 4, 5, 6, 8, 10, 12, 15, 17, 20, 25, 30, 50):
    curve.append({"n_piles": k, "bound_pct": round(100 * stats.t.ppf(0.975, k - 1) * s_rel * math.sqrt(1 + 1 / k), 2)})
for a_, b_ in zip(curve, curve[1:]):
    b_["gain_per_extra_pile_pct_points"] = round((a_["bound_pct"] - b_["bound_pct"]) / (b_["n_piles"] - a_["n_piles"]), 3)
results["bound_vs_piles"] = curve
results["bound_floor_pct"] = round(100 * 1.959964 * s_rel, 2)

# Gauge R&R without the photo where no marker was found (the app would refuse it)
ok = [p for p in rr if p["scale_mm_per_px"]]
if ok:
    v = np.array([p["count_sunflower"] for p in ok], float)
    results["gauge_rr_marker_ok"] = {"n": len(v), "mean": round(float(v.mean()), 1),
                                     "rel_sd_pct": round(float(100 * v.std(ddof=1) / v.mean()), 2),
                                     "range_pct": round(float(100 * (v.max() - v.min()) / v.mean()), 2),
                                     "excluded": [p["file"] for p in rr if not p["scale_mm_per_px"]]}
    for fac in ("phone", "collector", "height_class"):
        lv = {}
        for p in ok:
            lv.setdefault(p[fac], []).append(p["count_sunflower"])
        results["gauge_rr_marker_ok"][f"by_{fac}"] = {k: [round(float(np.mean(x)), 1), len(x)] for k, x in lv.items()}
    raw_ok = np.array([p["count_sunflower_no_fixed_scale"] for p in ok], float)
    results["gauge_rr_marker_ok"]["no_fixed_scale"] = {
        "rel_sd_pct": round(float(100 * raw_ok.std(ddof=1) / raw_ok.mean()), 2),
        "min": int(raw_ok.min()), "max": int(raw_ok.max())}
    # repeatability: two photos of the same person, phone and height; reproducibility: the rest
    cells = {}
    for p in ok:
        cells.setdefault((p["phone"], p["collector"], p["height_class"]), []).append(p["count_sunflower"])
    within = [np.var(x, ddof=1) for x in cells.values() if len(x) > 1]
    rep_sd = math.sqrt(np.mean(within)) if within else None
    tot_sd = float(v.std(ddof=1))
    results["gauge_rr_marker_ok"]["repeatability_sd_seeds"] = round(rep_sd, 2) if rep_sd else None
    results["gauge_rr_marker_ok"]["total_sd_seeds"] = round(tot_sd, 2)
    results["gauge_rr_marker_ok"]["reproducibility_sd_seeds"] = (
        round(math.sqrt(max(tot_sd ** 2 - rep_sd ** 2, 0.0)), 2) if rep_sd else None)

# before or after weight: which one does the photo agree with? (piles with two different readings)
ba = [p for p in pile_rows if p["weight_before_g"] and p["weight_before_g"] != p["weight_after_g"]]
results["before_vs_after"] = [{"pile": p["pile_id"], "before": p["weight_before_g"], "after": p["weight_after_g"],
                               "predicted": p["predicted_g"],
                               "closer_to": "after" if abs(p["error_pct_vs_after"]) < abs(p["error_pct_vs_before"]) else "before"}
                              for p in ba]

# time per pile, from the photo timestamps (first photo of one pile to the first photo of the next)
from PIL import Image
import datetime as dt


def stamp(folder, f):
    return dt.datetime.strptime(Image.open(ROOT / "data/photos" / folder / f).getexif().get(306), "%Y:%m:%d %H:%M:%S")


times = {}
for folder in ("2026-10-19_main", "2026-10-20_task4", "2026-10-21_extra_piles"):
    first = {}
    for r in (r for r in rows if r["folder"] == folder and r["condition"] in ("main", "Task4")):
        t = stamp(folder, r["file"])
        first[r["pile_id"]] = min(first.get(r["pile_id"], t), t)
    ts = sorted(first.values())
    gaps = [(b - a).total_seconds() / 60 for a, b in zip(ts, ts[1:])]
    times[folder] = {"n_piles": len(ts), "min_per_pile_mean": round(float(np.mean(gaps)), 1),
                     "min_per_pile_range": [round(min(gaps), 1), round(max(gaps), 1)]}
results["minutes_per_pile"] = times

(OUT / "results.json").write_text(json.dumps(results, indent=1))
for k in ("pooled_17", "bound_vs_piles", "bound_floor_pct", "gauge_rr_marker_ok", "before_vs_after", "minutes_per_pile"):
    print(k, json.dumps(results[k]))
