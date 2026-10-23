"""Check the photo light (detkit/quality.py) on all 59 photos of 19-21 Oct, from the saved detector boxes.
Rule: the 53 normal photos must be green; IMG_2261 (no marker) orange; IMG_4183 (tilted) orange; the 4
touching photos orange. Output: analysis/results/2026-10-22_light/light.csv
Usage: PYTHONPATH=. python analysis/validate_light.py
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from detkit import quality as Q  # noqa: E402
from detkit.scale import measure_scale  # noqa: E402
from PIL import Image, ImageOps  # noqa: E402

RUNS = {"2026-10-19_main": ["2026-10-22_detect_main"], "2026-10-20_task4": ["2026-10-22_detect", "2026-10-23_detect_2305"],
        "2026-10-21_extra_piles": ["2026-10-22_detect"],
        "2026-10-19_gauge_rr": ["2026-10-22_detect", "2026-10-22_detect_rr5"]}
cfg = json.loads((ROOT / "analysis/results/main_std/weight_config.json").read_text())
EXPECT_ORANGE = {"IMG_2261.jpg", "IMG_4183.JPG", "IMG_4157.JPG", "IMG_4158.JPG", "IMG_4171.JPG", "IMG_4172.JPG"}
rows = [r for r in csv.DictReader(open(ROOT / "data/samples.csv", encoding="utf-8-sig")) if r["folder"] in RUNS]
out, bad = [], []
for fo, runs in RUNS.items():
    P = {}
    for run in runs:
        P.update(json.loads((ROOT / "analysis/results" / run / "std" / fo / "predictions.json").read_text()))
    for r in (r for r in rows if r["folder"] == fo):
        d = P[r["file"]]
        info = measure_scale(ImageOps.exif_transpose(Image.open(ROOT / "data/photos" / fo / r["file"])))
        scale_from = "markers" if d.get("scale_mm_per_px") else "seeds"
        q = Q.check_photo(d["detections"], "sunflower", scale_from, info.get("marker_diff_pct"), cfg["quality"])
        want = "orange" if r["file"] in EXPECT_ORANGE else "green"
        ok = q["light"] == want
        out.append({"file": r["file"], "folder": fo, "condition": r["condition"], "light": q["light"],
                    "expected": want, "ok": ok, "overlap_share": q["overlap_share"], "count": q["count"],
                    "marker_diff_pct": round(info["marker_diff_pct"], 2) if info.get("marker_diff_pct") else None,
                    "message": q["message"]})
        if not ok:
            bad.append(out[-1])
o = ROOT / "analysis/results/2026-10-22_light"
o.mkdir(parents=True, exist_ok=True)
with open(o / "light.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(out)
from collections import Counter  # noqa: E402
print(Counter((x["light"], x["expected"]) for x in out))
for x in out:
    if x["light"] != "green":
        print(x["file"], x["light"], x["message"])
print("NOT AS EXPECTED:", bad if bad else "none")
