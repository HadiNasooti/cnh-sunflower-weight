"""Run the detector on every photo listed in data/samples.csv for the given folders, in two ways:
  std: with the fixed scale from the marker sheet (0.110 mm per pixel), the way the app counts;
  raw: on the photo as it is (no fixed scale), to show what the phone and camera height do without it.
Writes analysis/results/<out>/<std|raw>/<folder>/predictions.json (+ overlays for std).
Used by .github/workflows/detect.yml (the cloud runner downloads the model); runs the same on a PC:
    python analysis/detect_new.py --folders 2026-10-20_task4,2026-10-21_extra_piles --out 2026-10-22_detect
"""
import argparse, csv, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--folders", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--model", default=str(ROOT / "weights/grain_rfdetr_small_v1/final"))
ap.add_argument("--modes", default="std,raw")
a = ap.parse_args()
rows = list(csv.DictReader(open(ROOT / "data/samples.csv", encoding="utf-8-sig")))
for folder in a.folders.split(","):
    files = [str(ROOT / "data/photos" / folder / r["file"]) for r in rows if r["folder"] == folder]
    files = [f for f in files if Path(f).exists()]
    for mode in a.modes.split(","):
        out = ROOT / "analysis/results" / a.out / mode / folder
        cmd = [sys.executable, "-m", "detkit", "predict", "--model", a.model, "--images", *files,
               "--tile", "1500", "--overlap", "0.2", "--score", "0.38", "--out", str(out)]
        cmd += ["--std-mm-per-px", "0.110"] if mode == "std" else ["--no-overlay"]
        print(">>", folder, mode, len(files), "photos", flush=True)
        subprocess.run(cmd, check=True, cwd=ROOT)
