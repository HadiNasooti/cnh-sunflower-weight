"""Remove the GPS block from the EXIF of JPEG photos, in place, without touching the image pixels.

The image data is not re-encoded (piexif rewrites only the EXIF segment); a check compares the decoded
pixels before and after. Usage: python tools/strip_gps.py data/photos/<folder>/*.jpg
"""
import sys

import numpy as np
import piexif
from PIL import Image

for path in sys.argv[1:]:
    exif = piexif.load(path)
    if not exif.get("GPS"):
        print(f"{path}: no GPS")
        continue
    before = np.asarray(Image.open(path))
    exif["GPS"] = {}
    piexif.insert(piexif.dump(exif), path)
    after = np.asarray(Image.open(path))
    assert before.shape == after.shape and (before == after).all(), f"pixels changed in {path}"
    print(f"{path}: GPS removed, pixels identical")
