"""Check the sticky-note outlines of a photo folder: no seed may lie inside an outline.

Seeds are found with a simple dark-blob finder that does not depend on the detector (dark spots on white
paper, compared with the local background). For every photo in <folder>/note_zones.json it lists the dark
blobs that touch the outline (grown by --margin pixels) and writes an overlay: outline in magenta, touching
blobs in red. A red box INSIDE the outline is handwriting or the note's shadow; look at every overlay.

Usage: python tools/check_note_zones.py data/photos/2026-10-20_task4 --out runs/note_check --margin 45
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


def load(path):
    return np.array(ImageOps.exif_transpose(Image.open(path)).convert("RGB"))


def blobs(rgb):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    bg = cv2.GaussianBlur(g, (0, 0), 25)
    m = (((bg.astype(int) - g.astype(int)) > 45) & (g < 140)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    return lab, st[1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="runs/note_check")
    ap.add_argument("--margin", type=int, default=45)
    a = ap.parse_args()
    folder, out = Path(a.folder), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    zones = {k: v for k, v in json.loads((folder / "note_zones.json").read_text()).items() if not k.startswith("_")}
    for name, poly in zones.items():
        rgb = load(folder / name)
        h, w = rgb.shape[:2]
        pts = np.array(poly, np.int32)
        zm = np.zeros((h, w), np.uint8)
        cv2.fillPoly(zm, [pts], 1)
        k = 2 * a.margin + 1
        zg = cv2.dilate(zm, np.ones((k, k), np.uint8))
        lab, st = blobs(rgb)
        area = st[:, 4]
        med = np.median(area[area > 50])
        hits = []
        for i in range(len(st)):
            if not 0.15 * med <= area[i] <= 4 * med:
                continue
            x, y, bw, bh = st[i, :4]
            comp = lab[y:y + bh, x:x + bw] == i + 1
            if (comp & (zg[y:y + bh, x:x + bw] > 0)).any():
                hits.append((int(x), int(y), int(bw), int(bh),
                             int((comp & (zm[y:y + bh, x:x + bw] > 0)).sum())))
        vis = rgb.copy()
        cv2.polylines(vis, [pts], True, (255, 0, 255), max(3, w // 500))
        for x, y, bw, bh, _ in hits:
            cv2.rectangle(vis, (x - 10, y - 10), (x + bw + 10, y + bh + 10), (255, 0, 0), max(3, w // 400))
        im = Image.fromarray(vis)
        im.thumbnail((1200, 1200))
        im.save(out / f"{Path(name).stem}_zone.jpg", quality=85)
        print(f"{name}: {len(hits)} dark blob(s) near the outline "
              f"(pixels inside the outline: {[hh[4] for hh in hits]})")


if __name__ == "__main__":
    main()
