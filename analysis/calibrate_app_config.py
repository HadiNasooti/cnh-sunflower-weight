"""Build the app's weight_config.json from all 17 piles (decision of 22 Oct 2026).

Same method as detkit's own calibration (FeatureTimesConstant.fit): constant = mean over piles of
(pile weight / mean count of its 2 photos); bound h = t(0.975, n_piles - 1) x s x sqrt(1 + 1/n_piles), with s
the relative spread of the per-photo ratios (a prediction is made from one photo).
  - crop_count_constants: counts with the marker scale (analysis/results/2026-10-22_analysis/per_photo.csv)
  - seed_scale_constants: counts with the seeds as the ruler (analysis/results/2026-10-22_seed_scale/seed_scale.csv)
  - seed_length_mm: typical seed length from Hadi's 24 main photos (marker scale)
  - quality: limits of the photo checks (detkit/quality.py)
The previous config (Hadi's 8 piles, 19 Oct) is kept as weight_config_19oct_8piles.json.
Usage: python analysis/calibrate_app_config.py
"""
import csv
import json
import math
import shutil
import statistics
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "analysis/results/main_std/weight_config.json"
OLD = CFG.with_name("weight_config_19oct_8piles.json")
if not OLD.exists():
    shutil.copy(CFG, OLD)
cfg = json.loads(OLD.read_text())

pp = [r for r in csv.DictReader(open(ROOT / "analysis/results/2026-10-22_analysis/per_photo.csv", encoding="utf-8"))
      if r["condition"] in ("main", "Task4") and r["weight_after_g"] and r["predicted_g"]]
ss = {r["file"]: r for r in csv.DictReader(open(ROOT / "analysis/results/2026-10-22_seed_scale/seed_scale.csv",
                                                encoding="utf-8"))}
ref = json.loads((ROOT / "analysis/results/2026-10-22_seed_scale/reference.json").read_text())


def fit(count_of):
    photos, piles = [], {}
    for r in pp:
        w, c = float(r["weight_after_g"]), float(count_of(r))
        photos.append(w / c)
        piles.setdefault((r["folder"], r["pile_id"]), []).append((w, c))
    ratios = [statistics.fmean(w for w, _ in v) / statistics.fmean(c for _, c in v) for v in piles.values()]
    k, n, m = statistics.fmean(ratios), len(ratios), len(photos)
    s = math.sqrt(sum((x - k) ** 2 for x in photos) / (m - 1)) / k
    t = float(stats.t.ppf(0.975, n - 1))
    return k, {"rel_halfwidth": t * s * math.sqrt(1 + 1 / n), "rel_sd": s, "n_piles": n, "n_photos": m,
               "t": t, "level": 0.95}


k_m, b_m = fit(lambda r: r["count_sunflower"])
k_s, b_s = fit(lambda r: ss[r["file"]]["count_seed"])
cfg["crop_count_constants"] = {"sunflower": k_m, "default": k_m}
cfg["crop_count_constants_bounds"] = {"sunflower": b_m, "default": b_m}
cfg["seed_scale_constants"] = {"sunflower": k_s}
cfg["seed_scale_constants_bounds"] = {"sunflower": b_s}
cfg["seed_length_mm"] = {"sunflower": round(ref["typical_seed_length_mm_hadi_main"], 3)}
cfg["quality"] = {"max_marker_diff_pct": 5.0, "max_overlap_share": 0.25, "overlap_min": 0.20,
                  "max_count": 651, "min_count": 20}
cfg["calibration_note"] = ("22 Oct 2026: 17 piles (Hadi P01-P08, Jia T4-01 to T4-04 and P09-P13), 34 photos; "
                           "built by analysis/calibrate_app_config.py")
CFG.write_text(json.dumps(cfg, indent=2))
print(json.dumps({k: cfg[k] for k in ("crop_count_constants", "seed_scale_constants", "seed_length_mm")}, indent=1))
print("bounds marker", round(100 * b_m["rel_halfwidth"], 2), "seeds", round(100 * b_s["rel_halfwidth"], 2))
