"""Summary of the seed-scale test (analysis/seed_scale_test.py): the four points agreed on 22 Oct.

1. count error against the marker count, all photos;
2. effect on the bound (17 piles, same formula as with the markers);
3. does it still remove phone, person and height (Gauge R&R, now with all 17 photos);
4. what can break it.
Output: analysis/results/2026-10-22_seed_scale/summary.json
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "analysis/results/2026-10-22_seed_scale"
rows = list(csv.DictReader(open(D / "seed_scale.csv", encoding="utf-8")))
ref = json.loads((D / "reference.json").read_text())
f = lambda v: float(v) if v not in ("", None) else None  # noqa: E731
for r in rows:
    for k in ("scale_marker", "scale_seed_pass1", "scale_seed_pass2", "scale_diff_pct", "count_marker",
              "count_seed_pass1", "count_seed", "count_diff_pct", "weight_after_g", "seed_length_mm_marker"):
        r[k] = f(r[k])
out = {"typical_seed_length_mm": ref}


def desc(v):
    v = np.array(v, float)
    return {"n": len(v), "mean": round(float(v.mean()), 2), "sd": round(float(v.std(ddof=1)), 2),
            "mean_abs": round(float(np.abs(v).mean()), 2), "min": round(float(v.min()), 2), "max": round(float(v.max()), 2)}


# 1. count error against the marker count
cm = [r for r in rows if r["count_marker"]]
out["1_count_diff_pct_vs_marker"] = {"all": desc([r["count_diff_pct"] for r in cm])}
for fo in sorted({r["folder"] for r in cm}):
    out["1_count_diff_pct_vs_marker"][fo] = desc([r["count_diff_pct"] for r in cm if r["folder"] == fo])
out["1_pass1_only_count_diff_pct"] = desc([100 * (r["count_seed_pass1"] / r["count_marker"] - 1) for r in cm])
out["1_scale_diff_pct_vs_marker"] = desc([r["scale_diff_pct"] for r in cm])
out["1_worst_photos"] = sorted(({"file": r["file"], "count_diff_pct": r["count_diff_pct"],
                                  "scale_diff_pct": r["scale_diff_pct"]} for r in cm),
                                key=lambda x: -abs(x["count_diff_pct"]))[:5]

# 2. effect on the bound: piles = mean of the main/Task4 photos, grams per seed spread, 17 piles
piles = {}
for r in rows:
    if r["condition"] in ("main", "Task4") and r["weight_after_g"]:
        piles.setdefault((r["folder"], r["pile_id"]), {"w": r["weight_after_g"], "seed": [], "marker": [],
                                                       "who": r["collector"]})
        piles[(r["folder"], r["pile_id"])]["seed"].append(r["count_seed"])
        piles[(r["folder"], r["pile_id"])]["marker"].append(r["count_marker"])
n = len(piles)
t = stats.t.ppf(0.975, n - 1)
for key in ("seed", "marker"):
    g = np.array([p["w"] / np.mean(p[key]) for p in piles.values()])
    s = g.std(ddof=1) / g.mean()
    out[f"2_bound_{key}"] = {"n_piles": n, "g_per_seed": round(float(g.mean()), 5), "rel_sd_pct": round(100 * s, 2),
                             "bound_pct": round(100 * t * s * math.sqrt(1 + 1 / n), 2)}
# task 4 style test with the seed scale: constant from Hadi's 8 piles, applied to Jia's 9
for key in ("seed", "marker"):
    gh = np.array([p["w"] / np.mean(p[key]) for p in piles.values() if p["who"] == "Hadi"])
    k, s = gh.mean(), gh.std(ddof=1) / gh.mean()
    h = stats.t.ppf(0.975, len(gh) - 1) * s * math.sqrt(1 + 1 / len(gh))
    errs = [100 * (np.mean(p[key]) * k - p["w"]) / p["w"] for p in piles.values() if p["who"] == "Jia"]
    out[f"2_jia_test_{key}"] = {"hadi_bound_pct": round(100 * h, 2), "bias_pct": round(float(np.mean(errs)), 2),
                                "mean_abs_err_pct": round(float(np.mean(np.abs(errs))), 2),
                                "inside": f"{sum(abs(e) <= 100 * h for e in errs)} of {len(errs)}"}

# 3. Gauge R&R with the seed scale (all 17 photos, IMG_2261 included: it needs no marker now)
rr = [r for r in rows if r["condition"] == "gauge_rr"]
v = np.array([r["count_seed"] for r in rr], float)
g3 = {"n": len(v), "min": int(v.min()), "max": int(v.max()), "mean": round(float(v.mean()), 1),
      "rel_sd_pct": round(float(100 * v.std(ddof=1) / v.mean()), 2)}
rr16 = [r for r in rr if r["count_marker"]]           # the 16 photos where the markers were found
for key in ("count_seed", "count_marker"):
    x16 = np.array([r[key] for r in rr16], float)
    g3[f"same_16_photos_rel_sd_pct_{key}"] = round(float(100 * x16.std(ddof=1) / x16.mean()), 2)
for key, sel in (("seed", rr), ("marker", rr16)):
    col = "count_seed" if key == "seed" else "count_marker"
    m = np.mean([r[col] for r in sel])
    for fac, (a, b) in (("collector", ("Jia", "Hadi")), ("phone", ("iPhone 14 1x", "iPhone 15 Pro 1x")),
                        ("height_class", ("high", "normal"))):
        x = np.array([r[col] for r in sel if r[fac] == a], float)
        y = np.array([r[col] for r in sel if r[fac] == b], float)
        va, vb = x.var(ddof=1) / len(x), y.var(ddof=1) / len(y)
        dfw = (va + vb) ** 2 / (va ** 2 / (len(x) - 1) + vb ** 2 / (len(y) - 1))
        hw = stats.t.ppf(0.975, dfw) * math.sqrt(va + vb)
        d = x.mean() - y.mean()
        g3[f"{key}: {a}_minus_{b}_pct_95ci"] = [round(100 * (d - hw) / m, 1), round(100 * d / m, 1),
                                                round(100 * (d + hw) / m, 1)]
g3["IMG_2261_no_marker"] = next(r["count_seed"] for r in rr if r["file"] == "IMG_2261.jpg")
out["3_gauge_rr_seed_scale"] = g3

# 4. what can break it: the typical seed length must be right for the seeds in the photo
lens = {}
for r in rows:
    if r["seed_length_mm_marker"]:
        lens.setdefault(r["folder"], []).append(r["seed_length_mm_marker"])
out["4_seed_length_mm_by_folder"] = {k: desc(x) for k, x in lens.items()}
sc = [(r["scale_diff_pct"], r["count_diff_pct"]) for r in cm]
lr = stats.linregress([a for a, _ in sc], [b for _, b in sc])
out["4_count_change_per_1pct_scale_error"] = {"slope": round(float(lr.slope), 3), "r": round(float(lr.rvalue), 2),
                                              "note": "regression across photos, weak (r 0.39); see sensitivity.json "
                                                      "for the controlled test with the scale set 5 % off"}
out["4_note"] = ("seed lengths differ by session (main 11.25, Gauge R&R 11.48, Jia 11.75-11.88 mm); in the Gauge "
                 "R&R both persons and both phones measure the same length, so it is a session effect (sheet, "
                 "pile or seeds), not person or phone. Jia's grams per seed is only 1.5 % above Hadi's, so her "
                 "seeds are probably not 5 % longer. A marker card printed short would fit the length, but it "
                 "would push her count UP, not explain her -1.3 % bias. Direct test: measure her card. "
                 "Medians include boxes on the sticky note (about 2 per photo, negligible).")

(D / "summary.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
