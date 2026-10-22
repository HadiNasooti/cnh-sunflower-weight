"""Photo checks for the end user: one light (green, orange or red) with one sentence that says what to do.

Every check is one variable from docs/group/VARIABLES.md; the limits come from our own photos (22 Oct 2026,
`analysis/validate_light.py` checks them on all 59 photos). The light is about the PHOTO: a photo without a
marker still gets a weight (the seeds are used as the ruler), with a wider range, and an orange light.

Also here: the seeds as their own ruler (`seed_scale`): typical seed length (mm, per crop, measured on photos
with the marker sheet) divided by the median length of the seed boxes in this photo (pixels).
"""

from __future__ import annotations

import statistics

# limits, from our photos (see QUALITY_DEFAULTS in the config to change them)
QUALITY_DEFAULTS = {
    "max_marker_diff_pct": 5.0,   # 47 of the 48 photos with both markers found: 3.7 % or less
    "max_overlap_share": 0.25,    # share of seed boxes overlapping another one by > 20 %: normal <= 17 %, touching 42-51 %
    "overlap_min": 0.20,          # overlap of two boxes, as a share of the smaller box
    "max_count": 651,             # largest count we tested in one photo (P13, 34 g)
    "min_count": 20,              # fewer seeds: orange, and the seeds are not used as a ruler (we tested 182 to 651)
}

GREEN, ORANGE, RED = "green", "orange", "red"
DOT = {GREEN: "\U0001F7E2", ORANGE: "\U0001F7E0", RED: "\U0001F534"}

INSTRUCTIONS = """**How to take the photo**
1. Spread the seeds on white paper or a white table so that **no seed touches another**.
2. Put the **printed marker sheet** next to the seeds (both squares fully visible, 3 cm from the seeds).
   No marker sheet? The app still works: it then uses the seeds as the ruler, and the range is a little wider.
3. Hold the phone **flat, straight above** the seeds, at any height, with the normal 1x camera.
   All seeds and the markers must be in the photo; nothing else (no hands, notes or pens).
4. More seeds than fit in one photo? Split the sample and add the weights.
5. Upload the photo. The light next to the result tells you if the photo was good, and what to change if not.
"""


def long_side(d: dict) -> float:
    x1, y1, x2, y2 = d["bbox"]
    return max(x2 - x1, y2 - y1)


def seed_scale(dets: list[dict], crop: str, seed_length_mm: float) -> float | None:
    """mm per pixel from the seeds: typical seed length / median box long side (pixels) of the crop's boxes."""
    sides = [long_side(d) for d in dets if d.get("label") == crop]
    if len(sides) < QUALITY_DEFAULTS["min_count"] or not seed_length_mm:
        return None
    return seed_length_mm / statistics.median(sides)


def overlap_share(dets: list[dict], crop: str, min_overlap: float = QUALITY_DEFAULTS["overlap_min"]) -> float:
    """Share of the crop's boxes that overlap another box of the crop by more than ``min_overlap`` of the
    smaller box (seeds touching or lying close together)."""
    b = [d["bbox"] for d in dets if d.get("label") == crop]
    if len(b) < 2:
        return 0.0
    import numpy as np
    a = np.array(b, float)
    x1, y1, x2, y2 = a.T
    area = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
    iw = np.maximum(0, np.minimum(x2[:, None], x2[None]) - np.maximum(x1[:, None], x1[None]))
    ih = np.maximum(0, np.minimum(y2[:, None], y2[None]) - np.maximum(y1[:, None], y1[None]))
    inter = iw * ih
    np.fill_diagonal(inter, 0)
    small = np.minimum(area[:, None], area[None])
    ratio = np.divide(inter, small, out=np.zeros_like(inter), where=small > 0)
    return float((ratio.max(1) > min_overlap).mean())


def check_photo(dets: list[dict], crop: str | None, scale_from: str, marker_diff_pct: float | None = None,
                limits: dict | None = None) -> dict:
    """Light and sentences for one photo.

    ``scale_from``: "markers", "seeds" (no marker; seeds used as the ruler) or "none" (no scale at all).
    Returns {"light", "message" (the most important sentence), "messages" (all), "overlap_share", "count"}.
    """
    lim = {**QUALITY_DEFAULTS, **(limits or {})}
    n = sum(1 for d in dets if d.get("label") == crop) if crop else 0
    share = overlap_share(dets, crop, lim["overlap_min"]) if crop else 0.0
    red, orange = [], []
    if not crop or n == 0:
        red.append("No seeds found: check that the seeds are in the photo and the crop is right.")
    if scale_from == "none" and not red:
        red.append("No marker found and the seed size of this crop is not known: "
                   "put the marker sheet fully in the photo.")
    if not red:
        if n < lim["min_count"]:
            orange.append(f"Only {n} seeds found: use a bigger sample (at least {lim['min_count']} seeds).")
        if share > lim["max_overlap_share"]:
            orange.append("Seeds too close together: spread them so that no seed touches another, "
                          "and take the photo again.")
        if n > lim["max_count"]:
            orange.append(f"More seeds than we tested ({n}, tested up to {lim['max_count']}): "
                          "split the sample into two photos and add the weights.")
        if marker_diff_pct is not None and marker_diff_pct > lim["max_marker_diff_pct"]:
            orange.append("Phone tilted: hold it flat, straight above the seeds, and take the photo again.")
        if scale_from == "seeds":
            orange.append("No marker found: the size was estimated from the seeds, so the range is wider. "
                          "Put the marker sheet fully in the photo for a more precise result.")
    light = RED if red else (ORANGE if orange else GREEN)
    msgs = red or orange or ["Good photo."]
    return {"light": light, "message": msgs[0], "messages": msgs, "overlap_share": round(share, 3), "count": n}
