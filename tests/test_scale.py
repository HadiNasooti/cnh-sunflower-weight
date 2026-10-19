"""Fixed scale from the printed marker sheet (detkit/scale.py) and its use in the app."""

import numpy as np
import pytest
from PIL import Image

cv2 = pytest.importorskip("cv2")

from detkit import scale as S                       # noqa: E402
from detkit.project import Project                  # noqa: E402


@pytest.fixture
def wd(tmp_path):
    p = Project(workdir=tmp_path / "w", classes=["wheat", "sunflower"])
    p.save()
    p.photos_dir.mkdir()
    return p


def marker_photo(px_per_marker: int = 400, size=(3000, 2000)) -> Image.Image:
    """White photo with markers 0 and 1 drawn so each 50 mm marker is ``px_per_marker`` px wide
    (a white quiet zone around each marker, as on the printed sheet)."""
    canvas = np.full((size[1], size[0]), 255, np.uint8)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    for i, x in ((0, 200), (1, size[0] - 200 - px_per_marker)):
        canvas[300:300 + px_per_marker, x:x + px_per_marker] = cv2.aruco.generateImageMarker(d, i, px_per_marker)
    return Image.fromarray(canvas).convert("RGB")


def test_measure_scale_two_markers():
    info = S.measure_scale(marker_photo(400))
    assert info["n_markers"] == 2
    assert info["scale_mm_per_px"] == pytest.approx(50 / 400, rel=0.01)
    assert info["marker_diff_pct"] < 1


def test_standardise_resizes_to_target_and_maps_boxes_back():
    im = marker_photo(400)                              # 0.125 mm/px
    out, f, info = S.standardise(im, 0.110)
    assert f == pytest.approx(0.125 / 0.110, rel=0.01) and out.width == round(im.width * f)
    assert S.measure_scale(out)["scale_mm_per_px"] == pytest.approx(0.110, rel=0.01)
    dets = S.boxes_to_original([{"bbox": [f * 100, f * 50, f * 200, f * 150]}], f)
    assert dets[0]["bbox"] == pytest.approx([100, 50, 200, 150], abs=0.2)


def test_no_marker_keeps_photo_and_says_so():
    im = Image.new("RGB", (800, 600), (255, 255, 255))
    out, f, info = S.standardise(im, 0.110)
    assert out is im and f == 1.0 and info["scale_mm_per_px"] is None and "no marker" in info["note"]


def test_app_fixed_scale(wd, tmp_path, monkeypatch):
    """run_inference with the fixed scale: the detector sees the resized photo, boxes come back in original
    pixels, the measured scale is kept as photo metadata, and the note says what was done."""
    from detkit.app import inference as I
    from detkit.app import proposals as P

    seen = {}
    monkeypatch.setattr(P, "load_bundle", lambda ckpt, device="auto": ("bundle", ckpt, device))

    def fake(image, bundle, classes, crop, **kw):
        seen["size"] = image.size
        return ([{"bbox": [100, 100, 200, 200], "class": crop or classes[0], "origin": "rfdetr", "score": 0.9}], {})

    monkeypatch.setattr(P, "propose_rfdetr", fake)
    src = tmp_path / "up"
    src.mkdir()
    marker_photo(400).save(src / "m.png")
    Image.new("RGB", (800, 600), (255, 255, 255)).save(src / "plain.png")
    rows, items, _ = I.run_inference(
        [src / "m.png", src / "plain.png"], {}, wd, ckpt="ck", device="cpu", score=0.3, tile=800, overlap=0.2,
        max_side=0, roi_text="", model_name="count_x_constant", cache=tmp_path / "c", std_mm_per_px=0.110)
    f = 0.125 / 0.110
    assert items[0]["dets"][0]["bbox"] == pytest.approx([100 / f, 100 / f, 200 / f, 200 / f], abs=0.5)
    assert items[0]["meta"]["scale_mm_per_px"] == pytest.approx(0.125, rel=0.01)
    assert "mm/px" in rows[0]["note"] and "no marker" in rows[1]["note"]
    assert seen["size"] == (800, 600)                   # the plain photo was used as it is
