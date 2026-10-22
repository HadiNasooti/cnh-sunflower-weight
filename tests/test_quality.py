"""Photo light and the seeds as ruler (detkit/quality.py) and their use in the app's Inference tab."""

import json

import pytest
from PIL import Image

from detkit import quality as Q
from detkit.project import Project


def boxes(n, size=100, gap=150, label="sunflower"):
    return [{"bbox": [i * gap, 0, i * gap + size, size / 2], "label": label, "score": 0.9} for i in range(n)]


def test_overlap_share_separate_and_touching():
    assert Q.overlap_share(boxes(30), "sunflower") == 0.0
    touching = boxes(30, size=100, gap=60)                    # each box overlaps its neighbours by 40 %
    assert Q.overlap_share(touching, "sunflower") == 1.0
    assert Q.overlap_share(boxes(30, label="wheat"), "sunflower") == 0.0


def test_seed_scale_from_median_box_length():
    assert Q.seed_scale(boxes(30, size=100), "sunflower", 11.0) == pytest.approx(0.11)
    assert Q.seed_scale(boxes(5), "sunflower", 11.0) is None                 # too few seeds
    assert Q.seed_scale(boxes(30), "sunflower", None) is None                # seed size of the crop unknown


def test_check_photo_lights():
    good = Q.check_photo(boxes(300), "sunflower", "markers", 1.0)
    assert good["light"] == Q.GREEN and good["message"] == "Good photo."
    tilt = Q.check_photo(boxes(300), "sunflower", "markers", 9.5)
    assert tilt["light"] == Q.ORANGE and "tilted" in tilt["message"]
    many = Q.check_photo(boxes(700), "sunflower", "markers", 1.0)
    assert many["light"] == Q.ORANGE and "split" in many["message"]
    close = Q.check_photo(boxes(300, gap=60), "sunflower", "markers", 1.0)
    assert close["light"] == Q.ORANGE and "too close" in close["message"]
    seeds = Q.check_photo(boxes(300), "sunflower", "seeds")
    assert seeds["light"] == Q.ORANGE and "No marker" in seeds["message"]
    both = Q.check_photo(boxes(300), "sunflower", "seeds", None)
    assert len(both["messages"]) == 1
    assert Q.check_photo([], "sunflower", "markers")["light"] == Q.RED
    assert Q.check_photo(boxes(300), "sunflower", "none")["light"] == Q.RED
    few = Q.check_photo(boxes(10), "sunflower", "markers")
    assert few["light"] == Q.ORANGE and "bigger sample" in few["message"]


@pytest.fixture
def wd(tmp_path):
    p = Project(workdir=tmp_path / "w", classes=["wheat", "sunflower"])
    p.save()
    p.photos_dir.mkdir()
    cfg = {"model": "crop_count_x_constant",
           "crop_count_constants": {"sunflower": 0.05},
           "crop_count_constants_bounds": {"sunflower": {"rel_halfwidth": 0.087}},
           "seed_scale_constants": {"sunflower": 0.06},
           "seed_scale_constants_bounds": {"sunflower": {"rel_halfwidth": 0.094}},
           "seed_length_mm": {"sunflower": 11.0}}
    (p.workdir / "weight_config.json").write_text(json.dumps(cfg))
    return p


def test_app_uses_the_seeds_when_no_marker(wd, tmp_path, monkeypatch):
    """No marker in the photo: first pass on the photo as it is, scale from the seed boxes, count again at
    that scale with the seed constants and their wider range, orange light with the 'No marker' sentence."""
    from detkit.app import inference as I
    from detkit.app import proposals as P

    sizes = []
    monkeypatch.setattr(P, "load_bundle", lambda ckpt, device="auto": ("bundle", ckpt, device))

    def fake(image, bundle, classes, crop, **kw):
        sizes.append(image.size)
        side = 100 * image.size[0] / 3000                      # seeds are 100 px long in the original photo
        return ([{"bbox": [i * 2 * side, 0, i * 2 * side + side, side / 2], "class": "sunflower",
                  "origin": "rfdetr", "score": 0.9} for i in range(30)], {})

    monkeypatch.setattr(P, "propose_rfdetr", fake)
    src = tmp_path / "up"
    src.mkdir()
    Image.new("RGB", (3000, 2000), (255, 255, 255)).save(src / "plain.png")
    rows, items, _ = I.run_inference([src / "plain.png"], {"plain.png": {"crop": "sunflower"}}, wd, ckpt="ck",
                                     device="cpu", score=0.3, tile=800, overlap=0.2, max_side=0, roi_text="",
                                     model_name="crop_count_x_constant", cache=tmp_path / "c", std_mm_per_px=0.110)
    r = rows[0]
    assert sizes[0] == (3000, 2000) and sizes[1] == (3000, 2000)    # 11 mm / 100 px = 0.110 mm/px: no resize
    assert r["scale_from"] == "seeds" and r["light"].endswith("orange") and "No marker" in r["message"]
    assert r["weight_g"] == pytest.approx(30 * 0.06) and r["range_pct"] == pytest.approx(9.4)
    assert "estimated from the seeds" in r["note"]


def _app(monkeypatch, n=30, side_fn=None):
    from detkit.app import proposals as P
    calls = []
    monkeypatch.setattr(P, "load_bundle", lambda ckpt, device="auto": ("bundle", ckpt, device))

    def fake(image, bundle, classes, crop, **kw):
        calls.append(image.size)
        side = side_fn(image, len(calls)) if side_fn else 100 * image.size[0] / 3000
        return ([{"bbox": [i * 2 * side, 0, i * 2 * side + side, side / 2], "class": "sunflower",
                  "origin": "rfdetr", "score": 0.9} for i in range(n)], {})

    monkeypatch.setattr(P, "propose_rfdetr", fake)
    return calls


def _run(wd, src, tmp_path, std=0.110, name="plain.png"):
    from detkit.app import inference as I
    return I.run_inference([src / name], {name: {"crop": "sunflower", "total_weight_g": 2.0}}, wd, ckpt="ck",
                           device="cpu", score=0.3, tile=800, overlap=0.2, max_side=0, roi_text="",
                           model_name="crop_count_x_constant", cache=tmp_path / "c", std_mm_per_px=std)[0][0]


def _plain(tmp_path, name="plain.png"):
    src = tmp_path / "up"
    src.mkdir(exist_ok=True)
    Image.new("RGB", (3000, 2000), (255, 255, 255)).save(src / name)
    return src


def test_few_seeds_without_marker_is_red_with_the_right_reason(wd, tmp_path, monkeypatch):
    _app(monkeypatch, n=10)
    r = _run(wd, _plain(tmp_path), tmp_path)
    assert r["scale_from"] == "few" and r["light"].endswith("red") and "too few seeds (10)" in r["message"]
    assert r["weight_g"] is None and "too few seeds" in r["note"]


def test_fixed_scale_off_is_orange(wd, tmp_path, monkeypatch):
    _app(monkeypatch, n=30)
    r = _run(wd, _plain(tmp_path), tmp_path, std=None)
    assert r["scale_from"] == "off" and r["light"].endswith("orange") and "switched off" in r["message"]


def test_seed_scale_refines_once_when_it_moves(wd, tmp_path, monkeypatch):
    # first pass on the photo as it is: seeds 100 px -> 0.110 mm/px; at that size the detector returns
    # boxes 5 % longer, so the scale moves by about 5 % and one more pass is made
    calls = _app(monkeypatch, n=30, side_fn=lambda im, k: 100 * im.size[0] / 3000 * (1.0 if k == 1 else 1.05))
    r = _run(wd, _plain(tmp_path), tmp_path)
    assert len(calls) == 3 and r["scale_from"] == "seeds"


def test_upright_copy_keeps_the_user_file_name(wd, tmp_path, monkeypatch):
    _app(monkeypatch, n=30)
    src = tmp_path / "up"
    src.mkdir()
    im = Image.new("RGB", (3000, 2000), (255, 255, 255))
    ex = im.getexif()
    ex[0x0112] = 6                                           # "rotate 90 degrees" in EXIF
    im.save(src / "rot.jpg", exif=ex)
    r = _run(wd, src, tmp_path, name="rot.jpg")
    assert r["file"] == "rot.jpg" and r["measured_g"] == 2.0


def test_quality_limits_from_the_config_are_used():
    q = Q.check_photo(boxes(300), "sunflower", "markers", 1.0, {"max_count": 100})
    assert q["light"] == Q.ORANGE and "split" in q["message"]
