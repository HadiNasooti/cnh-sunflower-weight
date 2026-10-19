"""Fixed scale for the detector: millimetres per pixel from the printed marker sheet.

The marker sheet (``tools/make_marker_sheet.py``) holds two ArUco markers (dictionary DICT_4X4_50, ids 0 and
1), each 50 mm wide. OpenCV finds their corners; the side length in pixels gives mm per pixel.

Why: the detector cuts a photo into tiles of a fixed pixel size, so the number of pixels per seed matters.
That changes with the camera height and the phone resolution. Resizing every photo to the same mm per pixel
before detection removes both effects (tested on the main collection of 19 Oct 2026: see
``docs/group/STATUS_AND_PLAN.md``). Boxes are always mapped back to the pixels of the original photo.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

MARKER_MM = 50.0
MARKER_IDS = (0, 1)                     # the two markers on our sheet; any other id is ignored
TILT_WARN_PCT = 5.0                     # the two markers differ by more than this: phone probably tilted
DEFAULT_TARGET_MM_PER_PX = 0.110        # chosen on the main collection (19 Oct 2026)


def marker_sides(image: Image.Image) -> dict[int, float]:
    """Mean side length in pixels of every marker found, by marker id (empty dict if none)."""
    import cv2

    gray = np.asarray(image.convert("L"))
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50),
                                  cv2.aruco.DetectorParameters())
    corners, ids, _ = det.detectMarkers(gray)
    out: dict[int, float] = {}
    if ids is None:
        return out
    for c, i in zip(corners, ids.ravel()):
        if int(i) not in MARKER_IDS:
            continue
        p = c.reshape(4, 2)
        out[int(i)] = float(np.mean([np.linalg.norm(p[k] - p[(k + 1) % 4]) for k in range(4)]))
    return out


def measure_scale(image: Image.Image, marker_mm: float = MARKER_MM) -> dict:
    """``{"scale_mm_per_px", "n_markers", "marker_diff_pct", "scale_source"}``; scale is None when no marker
    is found. marker_diff_pct = difference between the two markers (a sign of a tilted phone); above
    TILT_WARN_PCT a ``warning`` is added."""
    sides = marker_sides(image)
    vals = [marker_mm / s for s in sides.values() if s > 0]
    info = {"scale_mm_per_px": float(np.mean(vals)) if vals else None, "n_markers": len(vals),
            "marker_diff_pct": (100 * (max(vals) - min(vals)) / float(np.mean(vals))) if len(vals) > 1 else None,
            "scale_source": "markers" if vals else None}
    if info["marker_diff_pct"] is not None and info["marker_diff_pct"] > TILT_WARN_PCT:
        info["warning"] = (f"the two markers differ by {info['marker_diff_pct']:.1f} %: phone probably tilted, "
                           f"take the photo again with the phone level")
    return info


def standardise(image: Image.Image, target_mm_per_px: float = DEFAULT_TARGET_MM_PER_PX,
                known_scale: float | None = None) -> tuple[Image.Image, float, dict]:
    """Resize *image* so one pixel is *target_mm_per_px*. Returns ``(image, factor, info)``; factor is
    new size / old size (1.0 and the original image when no marker is found, with ``info["note"]``).
    ``known_scale`` (mm per pixel measured another way, e.g. from a ruler) is used only when no marker is
    found."""
    info = measure_scale(image)
    if not info["scale_mm_per_px"] and known_scale:
        info.update(scale_mm_per_px=float(known_scale), scale_source="given (no marker in the photo)")
    s = info["scale_mm_per_px"]
    if not s:
        info["note"] = "no marker found: photo used as it is (scale not fixed)"
        return image, 1.0, info
    f = s / target_mm_per_px
    info["std_factor"] = f
    if abs(f - 1.0) < 1e-3:
        return image, 1.0, info
    size = (max(1, round(image.width * f)), max(1, round(image.height * f)))
    return image.resize(size, Image.LANCZOS), f, info


def boxes_to_original(dets: list[dict], factor: float, key: str = "bbox") -> list[dict]:
    """Divide box coordinates by *factor* (boxes of the resized photo -> original photo pixels)."""
    if factor == 1.0:
        return dets
    for d in dets:
        d[key] = [round(v / factor, 1) for v in d[key]]
    return dets
