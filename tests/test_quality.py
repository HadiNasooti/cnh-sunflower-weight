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
