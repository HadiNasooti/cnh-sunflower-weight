"""Controlled check: how much does the count change if the assumed seed length is 5 % wrong?
Four photos (two of Hadi, two of Jia) are counted with the scale from the markers, then with that scale
made 5 % smaller and 5 % larger (same as a seed length that is 5 % off). Same settings as the app.
Output: analysis/results/2026-10-22_seed_scale/sensitivity.json
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "analysis"))
from seed_scale_test import run, count, zones, load  # noqa: E402
from detkit.predict import load_model  # noqa: E402
PHOTOS = [("2026-10-19_main", "IMG_4149.JPG"), ("2026-10-19_main", "IMG_4167.JPG"),
          ("2026-10-20_task4", "IMG_2303.jpg"), ("2026-10-21_extra_piles", "IMG_2322.jpg")]
model, proc, _, device = load_model(ROOT / "weights/grain_rfdetr_small_v1/final")
out = []
for fo, f in PHOTOS:
    sm = load(fo, "std")[f]["scale_mm_per_px"]
    img = ImageOps.exif_transpose(Image.open(ROOT / "data/photos" / fo / f)).convert("RGB")
    poly = zones(fo).get(f)
    c = {k: count(run(img, sm * k, model, proc, device), poly) for k in (0.95, 1.0, 1.05)}
    row = {"file": f, "count_scale_x0.95": c[0.95], "count_marker_scale": c[1.0], "count_scale_x1.05": c[1.05],
           "pct_per_1pct_scale": round(100 * (c[1.05] - c[0.95]) / c[1.0] / 10, 3)}
    out.append(row); print(row, flush=True)
res = {"photos": out, "mean_pct_count_per_1pct_scale": round(float(np.mean([r["pct_per_1pct_scale"] for r in out])), 3)}
(ROOT / "analysis/results/2026-10-22_seed_scale/sensitivity.json").write_text(json.dumps(res, indent=1))
print(res["mean_pct_count_per_1pct_scale"])
