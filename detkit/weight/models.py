"""Weight models: features -> Estimate. weight = feature x constant per crop, for kernel count
(``CountTimesConstant``, the baseline) or box area (``AreaTimesConstant``). Bounds: student task 3."""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT_CONFIG
from .features import SampleTable
from .stats import pile_key


@dataclass
class Estimate:
    weight_g: float
    low_g: float | None = None       # lower/upper bound of an interval, if the model can give one
    high_g: float | None = None
    note: str = ""


class WeightModel:
    """Interface. Subclass, set ``name``/``description``, implement ``fit`` and ``predict``.

    ``params()``/``set_params()`` hold everything needed to save and restore a fitted model as JSON.
    """
    name = "base"
    description = ""
    implemented = False

    def fit(self, samples: SampleTable) -> "WeightModel":
        raise NotImplementedError

    def predict(self, features: dict, crop: str | None = None) -> Estimate:
        raise NotImplementedError

    def params(self) -> dict:
        return {}

    def set_params(self, params: dict) -> None:
        pass

    def to_dict(self) -> dict:
        return {"name": self.name, "params": self.params()}

    @staticmethod
    def from_dict(d: dict) -> "WeightModel":
        m = get_model(d["name"])
        m.set_params(d.get("params", {}))
        return m

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def load(path: str | Path) -> "WeightModel":
        return WeightModel.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


_T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
         10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101,
         19: 2.093, 20: 2.086, 25: 2.060, 30: 2.042}        # Student t, 97.5 % quantile


def _t_quantile(p: float, df: int) -> float:
    """Student-t quantile. scipy when installed (it is, with the cpu/gpu extras); else the 97.5 % table
    above, else a Cornish-Fisher expansion (good for df >= 5)."""
    try:
        from scipy.stats import t
        return float(t.ppf(p, df))
    except ImportError:
        if abs(p - 0.975) < 1e-9 and df in _T975:
            return _T975[df]
        z = statistics.NormalDist().inv_cdf(p)
        v = float(df)
        return (z + (z ** 3 + z) / (4 * v) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * v ** 2)
                + (3 * z ** 7 + 19 * z ** 5 + 17 * z ** 3 - 15 * z) / (384 * v ** 3))


class FeatureTimesConstant(WeightModel):
    """weight = feature x constant, one constant per crop (``feature`` is a key of ``image_features``).

    ``constants`` = {"default": c, "<crop>": c}. Subclasses pick the feature; ``config_key`` is where the
    constants live in weight_config.json.

    Bounds (task 3): ``bounds`` = {"<crop>": {"rel_halfwidth": h, "rel_sd": s, "n_piles": n, "n_photos": m,
    "level": 0.95}} and the prediction interval is weight x (1 - h) .. weight x (1 + h). They are stored in
    weight_config.json under ``<config_key>_bounds`` so the app and the CLI use them too.
    """
    name = "feature_x_constant"
    feature = "count"
    unit = "g per unit"
    config_key = "constants"
    implemented = True
    level = 0.95                     # coverage of the prediction interval
    min_piles = 3                    # fewer piles: no bounds (t with 1 degree of freedom is useless)

    def __init__(self, constants: dict[str, float] | None = None, bounds: dict | None = None):
        self.constants = dict(DEFAULT_CONFIG[self.config_key] if constants is None else constants)
        self.bounds: dict = {k: dict(v) for k, v in (bounds or {}).items()}

    def feature_value(self, features: dict, crop: str | None):
        """The feature this model multiplies by its constant (subclasses may make it crop-specific)."""
        return features.get(self.feature)

    @classmethod
    def bounds_key(cls) -> str:
        return f"{cls.config_key}_bounds"

    def fit(self, samples: SampleTable) -> "FeatureTimesConstant":
        """Calibrate per crop. Photos of one pile are first averaged into one point per pile (they are not
        independent); constant = mean over piles of (pile weight / mean feature of its photos). Crops without data keep their
        current constant. ``default`` = pooled over all crops.

        Bounds: the scatter of the per-PHOTO ratios around the constant (relative sd ``s``; per photo
        because a prediction is made from one photo, so photo-to-photo noise belongs in it) and the number
        of independent piles ``n`` give a 95 % prediction interval for a new photo:
            h = t(0.975, n - 1) x s x sqrt(1 + 1/n)
        (t from Student's t because s is estimated from few piles; 1/n for the uncertainty of the
        constant itself). Needs at least 3 piles per crop. Assumes the relative error does not depend on
        the size of the sample: check that on your data (errors vs weight) and say so in the report."""
        photo_r: dict[str, list[float]] = {}
        pile_r: dict[str, dict[str, list[tuple[float, float]]]] = {}
        for s in samples.with_weight():
            f = self.feature_value(s.features, s.crop)
            if not f:
                continue
            crop = s.crop or "default"
            r = s.weight_g / f
            pid = pile_key(s)
            photo_r.setdefault(crop, []).append(r)
            pile_r.setdefault(crop, {}).setdefault(pid, []).append((s.weight_g, f))

        def _fit(photos: list[float], piles: list[tuple[float, float]]) -> tuple[float, dict | None]:
            # piles: (weight, mean feature over the pile's photos); pile ratio = weight / mean feature
            # (the same definition as stats.pile_points / bootstrap_ci "ratio")
            pile_ratios = [w / f for w, f in piles if f]
            c = statistics.fmean(pile_ratios) if pile_ratios else 0.0
            n = len(pile_ratios)
            m = len(photos)
            if n < self.min_piles or m < 2 or c == 0:
                return c, None
            rel_sd = math.sqrt(sum((r - c) ** 2 for r in photos) / (m - 1)) / abs(c)
            k = _t_quantile(0.5 + self.level / 2, n - 1)
            h = k * rel_sd * (1 + 1 / n) ** 0.5
            return c, {"rel_halfwidth": h, "rel_sd": rel_sd, "n_piles": n, "n_photos": m,
                       "t": k, "level": self.level}

        def _piles(d: dict[str, list[tuple[float, float]]]) -> list[tuple[float, float]]:
            return [(statistics.fmean(w for w, _ in v), statistics.fmean(f for _, f in v)) for v in d.values()]

        for crop in photo_r:
            c, b = _fit(photo_r[crop], _piles(pile_r[crop]))
            self.constants[crop] = c
            if b:
                self.bounds[crop] = b
            else:
                self.bounds.pop(crop, None)
        if photo_r:
            allp = [r for v in photo_r.values() for r in v]
            allpiles = [p for d in pile_r.values() for p in _piles(d)]
            c, b = _fit(allp, allpiles)
            self.constants["default"] = c
            if b:
                self.bounds["default"] = b
            else:
                self.bounds.pop("default", None)
        return self

    def predict(self, features: dict, crop: str | None = None) -> Estimate:
        known = crop in self.constants
        if not known and "default" not in self.constants:
            raise ValueError(f"no {self.unit} constant for crop {crop!r}: "
                             f"run `detkit weight calibrate --model {self.name}`")
        c = self.constants[crop] if known else self.constants["default"]
        note = "" if known or crop is None else f"no constant for crop {crop!r}, used default"
        f = self.feature_value(features, crop)
        w = (f or 0) * c
        if not f:
            return Estimate(0.0, note=(note + "; " if note else "") + "no detections: no bounds")
        # an unknown crop uses the default constant, which is a guess for that crop: no bounds then
        b = self.bounds.get(crop) if known else None
        if b is None:
            why = "crop not calibrated" if not known else "calibrate on >= 3 piles"
            return Estimate(w, note=(note + "; " if note else "") + f"no bounds: {why}")
        h = b["rel_halfwidth"]
        return Estimate(w, low_g=max(0.0, w * (1 - h)), high_g=w * (1 + h), note=note)

    def params(self) -> dict:
        return {"constants": self.constants, "bounds": self.bounds}

    def set_params(self, params: dict) -> None:
        self.constants = dict(params["constants"])
        self.bounds = {k: dict(v) for k, v in params.get("bounds", {}).items()}


class CountTimesConstant(FeatureTimesConstant):
    """Baseline: weight = number of detected kernels x grams per kernel of the crop."""
    name = "count_x_constant"
    description = "weight = kernel count x g/kernel per crop (baseline)"
    feature = "count"
    unit = "g/kernel"
    config_key = "constants"


class AreaTimesConstant(FeatureTimesConstant):
    """weight = total box area (px^2) x grams per px^2 of the crop. The constant depends on the camera
    distance (pixels per mm), so it is only valid for photos taken the same way as the calibration photos."""
    name = "area_x_constant"
    description = "weight = total box area (px^2) x g/px^2 per crop"
    feature = "total_area_px"
    unit = "g/px^2"
    config_key = "area_constants"


class CropCountTimesConstant(FeatureTimesConstant):
    """weight = number of boxes labelled as the photo's OWN crop x grams per kernel.

    Why: on our sunflower photos the detector also draws boxes on the ruler digits and on handwriting,
    labelled as other crops. Counting all boxes over-counted by 6-26 %; counting only the sunflower
    boxes was within 1-3 % of the hand count (3 batches of 200 seeds). Needs the crop of the photo."""
    name = "crop_count_x_constant"
    description = "weight = boxes of the photo's own crop x g/kernel (other classes ignored)"
    feature = "count_<crop>"
    unit = "g/kernel"
    config_key = "crop_count_constants"

    def feature_value(self, features, crop):
        return features.get(f"count_{crop}") if crop else None


class CropAreaTimesConstant(FeatureTimesConstant):
    """weight = box area of the photo's own crop (px^2) x grams per px^2 (other classes ignored).
    Same camera-distance caveat as area_x_constant."""
    name = "crop_area_x_constant"
    description = "weight = box area of the photo's own crop (px^2) x g/px^2"
    feature = "area_px_<crop>"
    unit = "g/px^2"
    config_key = "crop_area_constants"

    def feature_value(self, features, crop):
        return features.get(f"area_px_{crop}") if crop else None


MODELS: dict[str, type[WeightModel]] = {
    m.name: m for m in (CountTimesConstant, AreaTimesConstant, CropCountTimesConstant, CropAreaTimesConstant)
}


def get_model(name: str, **kw) -> WeightModel:
    if name not in MODELS:
        raise KeyError(f"unknown weight model {name!r}; available: {sorted(MODELS)}")
    return MODELS[name](**kw)
