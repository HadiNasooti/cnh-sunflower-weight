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
    assert "mm/px" in rows[0]["note"] and "no marker" in rows[1]["note"].lower()
    assert rows[1]["low_g"] is None and rows[1]["high_g"] is None        # bounds not valid without the scale
    assert seen["size"] == (800, 600)                   # the plain photo was used as it is


def marker_photo_ids(ids, px=400, size=(3000, 2000)) -> Image.Image:
    canvas = np.full((size[1], size[0]), 255, np.uint8)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    for k, (i, p) in enumerate(zip(ids, px if isinstance(px, (list, tuple)) else [px] * len(ids))):
        x = 200 + k * 1000
        canvas[300:300 + p, x:x + p] = cv2.aruco.generateImageMarker(d, i, p)
    return Image.fromarray(canvas).convert("RGB")


def test_only_our_marker_ids_and_tilt_warning():
    info = S.measure_scale(marker_photo_ids([0, 7], px=[400, 200]))      # id 7 is not on our sheet
    assert info["n_markers"] == 1 and info["scale_mm_per_px"] == pytest.approx(0.125, rel=0.01)
    tilted = S.measure_scale(marker_photo_ids([0, 1], px=[400, 440]))
    assert tilted["marker_diff_pct"] > 5 and "tilted" in tilted["warning"]


def test_known_scale_only_without_marker():
    plain = Image.new("RGB", (1000, 800), (255, 255, 255))
    out, f, info = S.standardise(plain, 0.110, known_scale=0.055)
    assert f == pytest.approx(0.5) and out.size == (500, 400) and info["scale_source"].startswith("given")
    _, _, info2 = S.standardise(marker_photo(400), 0.110, known_scale=0.055)
    assert info2["scale_source"] == "markers" and info2["scale_mm_per_px"] == pytest.approx(0.125, rel=0.01)


def test_app_fixed_scale_roi_is_scaled(wd, tmp_path, monkeypatch):
    from detkit.app import inference as I
    from detkit.app import proposals as P

    seen = {}
    monkeypatch.setattr(P, "load_bundle", lambda ckpt, device="auto": ("bundle", ckpt, device))

    def fake(image, bundle, classes, crop, **kw):
        seen.update(kw)
        return ([], {})

    monkeypatch.setattr(P, "propose_rfdetr", fake)
    src = tmp_path / "up"
    src.mkdir()
    marker_photo(400).save(src / "m.png")
    I.run_inference([src / "m.png"], {}, wd, ckpt="ck", device="cpu", score=0.3, tile=800, overlap=0.2,
                    max_side=1000, roi_text="100,100,1100,900", model_name="count_x_constant",
                    cache=tmp_path / "c", std_mm_per_px=0.110)
    f = S.measure_scale(marker_photo(400))["scale_mm_per_px"] / 0.110
    assert seen["roi"] == pytest.approx((100 * f, 100 * f, 1100 * f, 900 * f), abs=1)
    assert seen["max_side"] == 0                       # scale fixed: no extra downscaling


def test_scale_csv_several_files(tmp_path):
    from detkit.cli import _scale_csv

    (tmp_path / "a.csv").write_text("file,scale_mm_per_px\na.jpg,0.1\nb.jpg,\n")
    (tmp_path / "b.csv").write_text("file,scale_mm_per_px,scale_source\nc.jpg,0.07,estimate\n")
    assert _scale_csv([str(tmp_path / "a.csv"), str(tmp_path / "b.csv")]) == {"a.jpg": 0.1, "c.jpg": 0.07}
    assert _scale_csv(None) is None


def test_upright_copy_follows_exif_orientation(tmp_path):
    from detkit.app.inference import upright_copy

    im = Image.new("RGB", (300, 200), (255, 255, 255))
    ex = im.getexif()
    ex[0x0112] = 6                                     # "rotate 90 degrees" as phones store it
    im.save(tmp_path / "r.jpg", exif=ex)
    im.save(tmp_path / "plain.jpg")
    out = upright_copy(tmp_path / "r.jpg", tmp_path / "up")
    assert out != tmp_path / "r.jpg" and Image.open(out).size == (200, 300)
    assert upright_copy(tmp_path / "plain.jpg", tmp_path / "up") == tmp_path / "plain.jpg"
