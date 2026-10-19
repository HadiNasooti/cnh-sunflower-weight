"""Build a detkit project from the photos in data/ (all folders) with their metadata, ready for the analysis.

Steps it does:
1. create the project (the 6 detector classes) with the extra photo properties condition, collector,
   scale_mm_per_px;
2. import every photo listed in data/samples.csv, with crop, pile_id, total_weight_g, manual_count,
   collector, condition, and scale_mm_per_px from the folder's scale.csv when there is one.

Then, from the repository folder:
    python -m detkit predict --model weights/grain_rfdetr_small_v1/final --images runs/analysis/photos \
        --tile 1500 --overlap 0.2 --score 0.38 --std-mm-per-px 0.110 --out runs/analysis/predictions
    python analysis/sunflower_analysis.py --workdir runs/analysis --lab data/lab_measurements.json \
        --use predictions --out analysis/results/main_std

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
    p = Project(workdir=Path(a.workdir), classes=CLASSES, tile=1500, overlap=0.2, extra_image_fields=EXTRA)
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
