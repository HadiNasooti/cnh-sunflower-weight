"""ESTIMATE mm per pixel for photos without the marker sheet (pilot and batches of 17 Oct), from the seed size.

In photos WITH markers, the median length of the sunflower boxes (long side) is converted to mm with the
measured scale; its mean over those photos is the typical seed length. For a photo without markers,
scale = typical seed length / median box length in pixels. This is an estimate (it assumes the seeds of all
photos come from the same lot), written as such into the scale.csv of the folder.

Usage:
    python analysis/estimate_scale_from_seeds.py --predictions runs/analysis/predictions/predictions.json \
        --data data --folders 2026-10-17_pilot,2026-10-17_batches
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def median_long_side(dets: list[dict], label: str = "sunflower") -> float | None:
    sides = [max(d["bbox"][2] - d["bbox"][0], d["bbox"][3] - d["bbox"][1]) for d in dets if d["label"] == label]
    return float(np.median(sides)) if sides else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--data", default="data")
    ap.add_argument("--folders", required=True)
    a = ap.parse_args()
    preds = {Path(k).name: v for k, v in json.loads(Path(a.predictions).read_text(encoding="utf-8")).items()}
    data = Path(a.data)
    samples = list(csv.DictReader(open(data / "samples.csv", encoding="utf-8-sig")))
    seed_mm = []
    for r in samples:
        sc = data / "photos" / r["folder"] / "scale.csv"
        if not sc.exists() or r["file"] not in preds:
            continue
        known = {s["file"]: s for s in csv.DictReader(open(sc, encoding="utf-8"))}
        k = known.get(r["file"]) or {}
        if k.get("scale_mm_per_px") and not k.get("scale_source"):      # measured from markers only
            m = median_long_side(preds[r["file"]]["detections"])
            if m:
                seed_mm.append(m * float(k["scale_mm_per_px"]))
    seed_mm = np.array(seed_mm)
    typical = float(seed_mm.mean())
    print(f"typical seed length {typical:.2f} mm (sd {seed_mm.std(ddof=1):.2f} mm over {len(seed_mm)} photos with markers)")
    for folder in a.folders.split(","):
        rows = []
        for r in samples:
            if r["folder"] != folder or r["file"] not in preds:
                continue
            m = median_long_side(preds[r["file"]]["detections"])
            if m:
                rows.append({"file": r["file"], "scale_mm_per_px": round(typical / m, 5),
                             "scale_source": f"ESTIMATE from seed size: {typical:.2f} mm typical seed length / "
                                             f"{m:.1f} px median box length"})
        out = data / "photos" / folder / "scale.csv"
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["file", "scale_mm_per_px", "scale_source"])
            w.writeheader()
            w.writerows(rows)
        print("written", out, [(r["file"], r["scale_mm_per_px"]) for r in rows])


if __name__ == "__main__":
    main()
