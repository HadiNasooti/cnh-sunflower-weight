"""Test: can the seeds themselves replace the marker sheet as the scale?

Idea: the detector needs each seed to be about the same size in pixels. The marker sheet gives mm per pixel.
Without a marker, use the seeds as the ruler: typical seed length (mm, known per grain type) divided by the
median length of the seed boxes in this photo (pixels) gives mm per pixel.

Steps per photo (all photos of 19-21 Oct; the marker result is the reference):
  1. first pass: the detector on the photo as taken (existing "raw" predictions); median long side of the
     sunflower boxes in pixels;
  2. seed scale = typical seed length / that median; resize the photo to 0.110 mm per pixel with it;
  3. count again (same settings as the app), drop boxes on the sticky note, compare with the marker count;
  4. second pass: median box length from step 3 gives a refined scale; if it differs by more than 1 %,
     count once more.
Typical seed length: from Hadi's 24 main photos of 19 Oct (marker scale), so Jia's photos and the Gauge R&R
are a test. A second variant uses all marker photos (in-sample, for comparison only).

Output: analysis/results/2026-10-22_seed_scale/seed_scale.csv and summary.json
Usage: PYTHONPATH=. python analysis/seed_scale_test.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "analysis"))
from detkit.predict import load_model, predict_image  # noqa: E402

RES = ROOT / "analysis/results"
OUT = RES / "2026-10-22_seed_scale"
TARGET = 0.110
CROP = "sunflower"
RUNS = {"2026-10-19_main": ["2026-10-22_detect_main"],
        "2026-10-20_task4": ["2026-10-22_detect"],
        "2026-10-21_extra_piles": ["2026-10-22_detect"],
        "2026-10-19_gauge_rr": ["2026-10-22_detect", "2026-10-22_detect_rr5"]}


def load(folder, mode):
    out = {}
    for r in RUNS[folder]:
        p = RES / r / mode / folder / "predictions.json"
        if p.exists():
            out.update(json.loads(p.read_text()))
    return out


def zones(folder):
    p = ROOT / "data/photos" / folder / "note_zones.json"
    if not p.exists():
        return {}
    return {k: np.array(v, float) for k, v in json.loads(p.read_text()).items() if not k.startswith("_")}


def inside(poly, x, y):
    n, ins = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def long_sides(dets):
    return [max(d["bbox"][2] - d["bbox"][0], d["bbox"][3] - d["bbox"][1]) for d in dets if d["label"] == CROP]


def count(dets, poly):
    return sum(1 for d in dets if d["label"] == CROP and not
               (poly is not None and inside(poly, (d["bbox"][0] + d["bbox"][2]) / 2, (d["bbox"][1] + d["bbox"][3]) / 2)))


def run(img, scale, model, proc, device):
    f = scale / TARGET
    work = img.resize((max(1, round(img.width * f)), max(1, round(img.height * f))), Image.LANCZOS)
    dets = predict_image(work, model, proc, device, tile=1500, overlap=0.2, score=0.38)
    for d in dets:                                   # back to upright photo pixels
        d["bbox"] = [v / f for v in d["bbox"]]
    return dets


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "data/samples.csv", encoding="utf-8-sig")) if r["folder"] in RUNS]
    std = {fo: load(fo, "std") for fo in RUNS}
    raw = {fo: load(fo, "raw") for fo in RUNS}
    # typical seed length (mm) from Hadi's main photos with the marker scale
    lens = {}
    for fo in RUNS:
        for f, d in std[fo].items():
            if d.get("scale_mm_per_px"):
                lens[(fo, f)] = float(np.median(long_sides(d["detections"]))) * d["scale_mm_per_px"]
    L_hadi = float(np.mean([v for (fo, _), v in lens.items() if fo == "2026-10-19_main"]))
    L_all = float(np.mean(list(lens.values())))
    model, proc, _, device = load_model(ROOT / "weights/grain_rfdetr_small_v1/final")
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for r in rows:
        fo, f = r["folder"], r["file"]
        if f not in std[fo] or f not in raw[fo]:
            continue
        img = ImageOps.exif_transpose(Image.open(ROOT / "data/photos" / fo / f)).convert("RGB")
        poly = zones(fo).get(f)
        med_raw = float(np.median(long_sides(raw[fo][f]["detections"])))
        s1 = L_hadi / med_raw
        d1 = run(img, s1, model, proc, device)
        n1 = count(d1, poly)
        s2 = L_hadi / float(np.median(long_sides(d1)))
        if abs(s2 / s1 - 1) > 0.01:
            d2 = run(img, s2, model, proc, device)
            n2 = count(d2, poly)
        else:
            s2, n2 = s1, n1
        sm = std[fo][f].get("scale_mm_per_px")
        nm = count(std[fo][f]["detections"], poly) if sm else None
        row = {"file": f, "folder": fo, "pile_id": r["pile_id"], "condition": r["condition"],
               "collector": r["collector"], "phone": r["phone"],
               "height_class": "high" if "height high" in r["notes"] else ("normal" if fo == "2026-10-19_gauge_rr" else ""),
               "weight_after_g": r["total_weight_g"],
               "scale_marker": sm, "scale_seed_pass1": round(s1, 5), "scale_seed_pass2": round(s2, 5),
               "scale_diff_pct": round(100 * (s2 / sm - 1), 2) if sm else None,
               "count_marker": nm, "count_seed_pass1": n1, "count_seed": n2,
               "count_diff_pct": round(100 * (n2 / nm - 1), 2) if nm else None,
               "seed_length_mm_marker": round(lens[(fo, f)], 3) if (fo, f) in lens else None}
        out.append(row)
        print(f, row["scale_diff_pct"], nm, n1, n2, row["count_diff_pct"], flush=True)
        with open(OUT / "seed_scale.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(out)
    (OUT / "reference.json").write_text(json.dumps({"typical_seed_length_mm_hadi_main": round(L_hadi, 4),
                                                    "typical_seed_length_mm_all_marker_photos": round(L_all, 4),
                                                    "used": "hadi_main"}, indent=1))


if __name__ == "__main__":
    main()
