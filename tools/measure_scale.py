"""Measure millimetres per pixel from the printed markers, and optionally standardise the photos.

The marker sheet (tools/make_marker_sheet.py) holds two ArUco markers (dictionary DICT_4X4_50, ids 0 and 1),
each 50 mm wide. OpenCV finds their corners; the side length in pixels gives mm per pixel.

Usage:
    python tools/measure_scale.py --images DIR [--out scale.csv]
    python tools/measure_scale.py --images DIR --standardise OUT_DIR [--target 0.110]

--standardise writes a resized copy of every photo so that one pixel is --target mm (default 0.110 mm/px).
A photo finer than the target is made smaller; a photo coarser than the target is enlarged (enlarging adds no
detail, it only gives the detector seeds of the same pixel size). Choose a target close to the coarsest photo
you expect to avoid enlarging. Run the detector on OUT_DIR afterwards.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

MARKER_MM = 50.0
EXTS = {".jpg", ".jpeg", ".png"}


def marker_sides(gray: np.ndarray) -> dict[int, float]:
    """Mean side length in pixels of every marker found, by marker id."""
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50),
                                  cv2.aruco.DetectorParameters())
    corners, ids, _ = det.detectMarkers(gray)
    out = {}
    if ids is None:
        return out
    for c, i in zip(corners, ids.ravel()):
        p = c.reshape(4, 2)
        out[int(i)] = float(np.mean([np.linalg.norm(p[k] - p[(k + 1) % 4]) for k in range(4)]))
    return out


def measure(path: Path) -> dict:
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("L")
        gray = np.asarray(im)
    sides = marker_sides(gray)
    row = {"file": path.name, "width_px": gray.shape[1], "height_px": gray.shape[0], "n_markers": len(sides)}
    for i in (0, 1):
        row[f"mm_per_px_id{i}"] = round(MARKER_MM / sides[i], 5) if i in sides else ""
    vals = [MARKER_MM / s for s in sides.values()]
    row["scale_mm_per_px"] = round(float(np.mean(vals)), 5) if vals else ""
    row["marker_diff_pct"] = round(100 * (max(vals) - min(vals)) / np.mean(vals), 2) if len(vals) > 1 else ""
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--out", default=None, help="CSV file (default: <images>/scale.csv)")
    ap.add_argument("--standardise", default=None, help="folder for the resized copies")
    ap.add_argument("--target", type=float, default=0.110, help="target mm per pixel")
    a = ap.parse_args()
    src = Path(a.images)
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in EXTS)
    rows = []
    for p in files:
        r = measure(p)
        if a.standardise and r["scale_mm_per_px"] != "":
            dst = Path(a.standardise)
            dst.mkdir(parents=True, exist_ok=True)
            f = r["scale_mm_per_px"] / a.target          # < 1 means shrink
            with Image.open(p) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
                r["std_factor"] = round(f, 4)
                im.save(dst / p.name, quality=95)
        rows.append(r)
        print(r, flush=True)
    out = Path(a.out) if a.out else src / "scale.csv"
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("written", out)


if __name__ == "__main__":
    main()
