"""Build a detkit project from the photos in data/ (all folders) with their metadata, ready for the analysis.

What it does:
1. create the project (the 6 detector classes) with the extra photo properties condition, collector,
   scale_mm_per_px;
2. import every photo listed in data/samples.csv, with crop, pile_id, total_weight_g, manual_count,
   collector, condition, and scale_mm_per_px from the folder's scale.csv when there is one.
It refuses to run on a work folder that already has photos (importing twice would duplicate them).

The full analysis of 19 Oct 2026 (analysis/results/main_std), in this order, from the repository folder:
    python analysis/build_project.py --workdir runs/analysis
    # pass 1: count with the fixed scale; the 17 Oct photos have no markers and are counted as they are
    python -m detkit predict --model weights/grain_rfdetr_small_v1/final --images runs/analysis/photos \
        --tile 1500 --overlap 0.2 --score 0.38 --std-mm-per-px 0.110 --out runs/analysis/predictions_pass1
    # ESTIMATE the scale of the 17 Oct photos from the seed size (writes their scale.csv files)
    python analysis/estimate_scale_from_seeds.py --predictions runs/analysis/predictions_pass1/predictions.json \
        --data data --folders 2026-10-17_pilot,2026-10-17_batches
    # pass 2: all photos at the fixed scale (17 Oct photos with the estimated scale)
    python -m detkit predict --model weights/grain_rfdetr_small_v1/final --images runs/analysis/photos \
        --tile 1500 --overlap 0.2 --score 0.38 --std-mm-per-px 0.110 --out runs/analysis/predictions \
        --scale-csv data/photos/2026-10-17_pilot/scale.csv data/photos/2026-10-17_batches/scale.csv
    python analysis/sunflower_analysis.py --workdir runs/analysis --lab data/lab_measurements.json \
        --use predictions --out analysis/results/main_std
    # constants for the app (main photos only), with the detector settings they belong to
    python -m detkit weight calibrate --workdir runs/analysis --use predictions --main-only \
        --model crop_count_x_constant --detector-score 0.38 --detector-tile 1500 --detector-overlap 0.2 \
        --detector-std-mm-per-px 0.110
Pass 1 and the estimate step only recreate the scale.csv files of the 17 Oct folders. These files are in the
repository, so a re-run can go straight from build_project to pass 2 (build_project then also stores the
estimated scales as photo metadata).

Usage:
    python analysis/build_project.py [--workdir runs/analysis] [--folders 2026-10-17_batches,2026-10-19_main]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detkit.app import logic as L                   # noqa: E402
from detkit.project import Project                  # noqa: E402

CLASSES = ["corn", "peanuts", "popcorn_corn", "pumpkin", "sunflower", "wheat"]
EXTRA = [{"key": "condition", "kind": "str"}, {"key": "collector", "kind": "str"},
         {"key": "scale_mm_per_px", "kind": "float", "unit": "mm/px"}]


def num(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default="runs/analysis")
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--folders", help="comma-separated photo folders (default: all in samples.csv)")
    a = ap.parse_args()
    data = Path(a.data)
    wd = Path(a.workdir)
    if (wd / "photos").exists() and any((wd / "photos").iterdir()):
        sys.exit(f"{wd} already has photos: use a new --workdir (importing twice duplicates the photos)")
    p = Project(workdir=wd, classes=CLASSES, tile=1500, overlap=0.2, extra_image_fields=EXTRA)
    p.save()
    p.photos_dir.mkdir(parents=True, exist_ok=True)
    store = p.store()
    folders = set(a.folders.split(",")) if a.folders else None
    rows = [r for r in csv.DictReader(open(data / "samples.csv", encoding="utf-8-sig"))
            if folders is None or r["folder"] in folders]
    scales: dict[str, dict] = {}
    for f in {r["folder"] for r in rows}:
        sc = data / "photos" / f / "scale.csv"
        if sc.exists():
            scales[f] = {s["file"]: num(s.get("scale_mm_per_px")) for s in csv.DictReader(open(sc, encoding="utf-8"))}
    from PIL import Image
    n = 0
    for r in rows:
        src = data / "photos" / r["folder"] / r["file"]
        if not src.exists():
            print("missing", src)
            continue
        name = L.import_photos([src], p.photos_dir)[0]
        with Image.open(p.photos_dir / name) as im:
            size = im.size
        meta = {"crop": r["crop"], "pile_id": r["pile_id"], "total_weight_g": num(r["total_weight_g"]),
                "manual_count": int(float(r["manual_count"])) if r.get("manual_count") else None,
                "collector": r.get("collector"), "condition": r.get("condition"),
                "scale_mm_per_px": scales.get(r["folder"], {}).get(r["file"])}
        store.upsert_image(name, size[0], size[1], [], {k: v for k, v in meta.items() if v not in (None, "")},
                           reviewed=False, proposer="none")
        n += 1
    print(f"project {p.workdir}: {n} photos imported")


if __name__ == "__main__":
    main()
