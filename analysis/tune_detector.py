"""Choose the detector settings (tile size, score threshold, how to count) on photos with a KNOWN seed count.

The provided detector is used as it is (no retraining). What we can choose is how a photo is cut into
tiles before it goes into the model (a smaller tile = the model "zooms in"), the score threshold, and
whether we count all detected boxes or only those labelled sunflower. Each setting is scored by the
count error against the hand count (manual_count).

Usage:
    python analysis/tune_detector.py --images DIR --truth truth.csv --out analysis/tuning \
        [--tiles 1500,1250,1000,800] [--model weights/grain_rfdetr_small_v1/final]
truth.csv: columns file,manual_count
Output: tuning.csv (one row per photo x tile x threshold x mode) and a summary table on screen.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detkit.merge import nms_per_class          # noqa: E402

THRESHOLDS = [0.2, 0.25, 0.3, 0.38, 0.45, 0.5, 0.6]


def agnostic(dets: list[dict], iou_thr=0.4, ioma_thr=0.7) -> list[dict]:
    """Class-agnostic NMS: one box per seed whatever class it was given (the photo holds one crop)."""
    if not dets:
        return []
    keep = nms_per_class([d["bbox"] for d in dets], [0] * len(dets), [d["score"] for d in dets],
                         iou_thr=iou_thr, ioma_thr=ioma_thr)
    return [dets[k] for k in keep]


def counts(dets: list[dict], thr: float) -> dict:
    d = [x for x in dets if x["score"] >= thr]
    return {"all": len(d), "sunflower": sum(x["label"] == "sunflower" for x in d), "agnostic": len(agnostic(d))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--truth", required=True)
    ap.add_argument("--out", default="analysis/tuning")
    ap.add_argument("--tiles", default="1500,1250,1000,800")
    ap.add_argument("--model", default=str(ROOT / "weights/grain_rfdetr_small_v1/final"))
    a = ap.parse_args()
    from PIL import Image
    from detkit.predict import load_model, predict_image

    truth = {r["file"]: int(r["manual_count"]) for r in csv.DictReader(open(a.truth, encoding="utf-8-sig"))}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    model, proc, _, device = load_model(a.model, "cpu")
    cache = out / "raw_detections.json"
    raw = json.loads(cache.read_text()) if cache.exists() else {}
    rows = []
    for f, n_true in truth.items():
        with Image.open(Path(a.images) / f) as im:
            im = im.convert("RGB")
            for tile in map(int, a.tiles.split(",")):
                key = f"{f}|{tile}"
                if key not in raw:
                    raw[key] = predict_image(im, model, proc, device, tile=tile, overlap=0.2, score=0.15)
                    cache.write_text(json.dumps(raw))
                for thr in THRESHOLDS:
                    for mode, c in counts(raw[key], thr).items():
                        rows.append({"file": f, "true": n_true, "tile": tile, "score": thr, "mode": mode,
                                     "count": c, "rel_err": (c - n_true) / n_true})
                print(f, tile, counts(raw[key], 0.38), "true", n_true, flush=True)
    with open(out / "tuning.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # summary: mean |rel err| and sd of rel err per setting
    keys = sorted({(r["tile"], r["score"], r["mode"]) for r in rows})
    summ = []
    for k in keys:
        e = np.array([r["rel_err"] for r in rows if (r["tile"], r["score"], r["mode"]) == k])
        summ.append((float(np.abs(e).mean()), float(e.mean()), float(e.std(ddof=1)) if len(e) > 1 else 0.0, *k))
    summ.sort()
    print("\nbest settings (mean |error|, bias, sd, tile, score, mode):")
    for s in summ[:15]:
        print(f"  {100 * s[0]:5.1f} %  bias {100 * s[1]:+5.1f} %  sd {100 * s[2]:4.1f} %  tile {s[3]}  score {s[4]}  {s[5]}")
    (out / "summary.json").write_text(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
