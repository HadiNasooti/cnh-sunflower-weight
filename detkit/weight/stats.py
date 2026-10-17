"""Statistics for judging weight models (numpy; scipy used for the BCa bootstrap when installed)."""

from __future__ import annotations

import numpy as np

from .features import SampleTable


def evaluate_model(model, samples: SampleTable) -> dict:
    """Score ``model.predict`` against the true weights: n, mae_g, mape, bias_g (mean pred - true), r2,
    per-crop breakdown (same metrics) and ``rows`` (file, crop, true_g, pred_g, error_g)."""
    rows = []
    for s in samples.with_weight():
        est = model.predict(s.features, s.crop)
        rows.append({"file": s.file, "crop": s.crop, "true_g": s.weight_g, "pred_g": est.weight_g,
                     "error_g": est.weight_g - s.weight_g})
    res = _metrics(rows)
    res["per_crop"] = {c: _metrics([r for r in rows if r["crop"] == c])
                       for c in sorted({r["crop"] or "?" for r in rows})}
    res["rows"] = rows
    return res


def _metrics(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"n": 0, "mae_g": None, "mape": None, "bias_g": None, "r2": None}
    err = np.array([r["error_g"] for r in rows])
    true = np.array([r["true_g"] for r in rows])
    nz = true != 0
    ss_tot = float(np.sum((true - true.mean()) ** 2))
    return {"n": n, "mae_g": float(np.abs(err).mean()), "bias_g": float(err.mean()),
            "mape": float(np.mean(np.abs(err[nz]) / true[nz])) if nz.any() else None,
            "r2": 1 - float(np.sum(err ** 2)) / ss_tot if n > 1 and ss_tot > 0 else None}



# ---- task 2: pile-level data, bootstrap, learning curve ----------------------------------------------
#
# Photos of the same physical pile (same ``pile_id``) share one balance reading and one set of seeds, so
# they are NOT independent samples. Everything below first averages the photos of a pile into ONE point
# (mean feature, the pile's weight) and then resamples piles, never single photos ("cluster" resampling).
# A photo without a ``pile_id`` counts as its own pile.

def pile_key(s) -> str:
    """Identity of the physical pile of a photo: ``<crop>|<pile_id>`` (stripped). A photo without a usable
    pile_id (missing, empty, NaN) is its own pile."""
    pid = s.meta.get("pile_id")
    if pid is None or (isinstance(pid, float) and pid != pid) or str(pid).strip() == "":
        return f"__photo__{s.file}"
    return f"{s.crop}|{str(pid).strip()}"


def pile_points(samples: SampleTable, x_key: str, y_key: str = "weight_g",
                crop: str | None = None) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """One (x, y) point per pile: x = mean of ``x_key`` over the pile's photos, y = mean of ``y_key``.
    Photos with a missing x or y are skipped. Returns ``(x, y, pile_ids)``."""
    groups: dict[str, list[tuple[float, float]]] = {}
    for s in samples.for_crop(crop):
        x, y = s.get(x_key), s.get(y_key)
        if x is None or y is None:
            continue
        groups.setdefault(pile_key(s), []).append((float(x), float(y)))
    ids = sorted(groups)
    x = np.array([np.mean([p[0] for p in groups[i]]) for i in ids], dtype=float)
    y = np.array([np.mean([p[1] for p in groups[i]]) for i in ids], dtype=float)
    return x, y, ids


def _n_photos(samples: SampleTable, x_key: str, y_key: str, crop: str | None) -> int:
    return sum(1 for s in samples.for_crop(crop) if s.get(x_key) is not None and s.get(y_key) is not None)


def _stat(x: np.ndarray, y: np.ndarray, stat: str) -> float:
    """r = Pearson correlation; slope = least-squares slope with intercept (y = a + b x);
    ratio = mean of y / x per pile (the constant of the feature x constant models)."""
    if stat == "ratio":
        ok = x != 0
        return float(np.mean(y[ok] / x[ok])) if ok.any() else float("nan")
    if len(x) < 2 or np.ptp(x) == 0:
        return float("nan")
    if stat == "slope":
        return float(np.polyfit(x, y, 1)[0])
    if stat == "r":
        if np.ptp(y) == 0:
            return float("nan")
        return float(np.corrcoef(x, y)[0, 1])
    raise ValueError(f"stat must be 'r', 'slope' or 'ratio', got {stat!r}")


def learning_curve(samples: SampleTable, x_key: str, sizes: list[int], y_key: str = "weight_g",
                   crop: str | None = None, repeats: int = 200, seed: int = 0):
    """Task 2. How does the relation between ``x_key`` and ``y_key`` settle as the number of samples grows?

    ``n`` in ``sizes`` = number of independent PILES. For each n we draw ``repeats`` random sets of n piles
    WITH replacement from the piles we collected (a bootstrap of size n: each draw mimics "collect n new
    piles from the same population") and measure, over those sets, the spread of
    * ``r``     the correlation between feature and weight,
    * ``ratio`` the fitted constant (mean weight / feature per pile, e.g. grams per seed),
    * ``slope`` the least-squares slope.
    (Without replacement the spread would shrink artificially and reach 0 at n = all piles.)
    Each entry: ``n``, ``n_piles`` (piles available), ``r_mean``, ``r_sd``, ``r_lo``/``r_hi`` (2.5 / 97.5
    percentiles), ``ratio_mean``, ``ratio_sd``, ``ratio_rel_sd`` (sd / mean), ``ratio_lo``/``ratio_hi``,
    ``slope_mean``, ``slope_sd``, ``extrapolated`` (n > piles collected) and ``note``. n < 3: statistics
    are ``None``. Read it as: "with n piles, the constant we would fit varies by about ratio_rel_sd from
    one collection to the next". Pick the n where that spread is small enough for your use.
    Returns ``None`` with fewer than 3 weighed photos.
    """
    if _n_photos(samples, x_key, y_key, crop) < 3:
        return None
    x, y, _ = pile_points(samples, x_key, y_key, crop)
    n_piles = len(x)
    rng = np.random.default_rng(seed)
    out = []
    for n in sizes:
        n = int(n)
        entry: dict = {"n": n, "n_piles": n_piles}
        keys = ("r_mean", "r_sd", "r_lo", "r_hi", "ratio_mean", "ratio_sd", "ratio_rel_sd", "ratio_lo",
                "ratio_hi", "slope_mean", "slope_sd")
        entry["extrapolated"] = n > n_piles
        if n < 3 or n_piles < 3:
            entry.update({k: None for k in keys})
            entry["note"] = "need at least 3 piles"
            out.append(entry)
            continue
        rs, ratios, slopes = [], [], []
        for _ in range(repeats):
            idx = rng.integers(0, n_piles, size=n)
            rs.append(_stat(x[idx], y[idx], "r"))
            ratios.append(_stat(x[idx], y[idx], "ratio"))
            slopes.append(_stat(x[idx], y[idx], "slope"))
        rs, ratios, slopes = (np.array(v, dtype=float) for v in (rs, ratios, slopes))
        rs, ratios, slopes = rs[~np.isnan(rs)], ratios[~np.isnan(ratios)], slopes[~np.isnan(slopes)]

        def _q(a, q):
            return float(np.percentile(a, q)) if len(a) else None

        def _m(a):
            return float(a.mean()) if len(a) else None

        def _s(a):
            return float(a.std(ddof=1)) if len(a) > 1 else None

        entry.update({"r_mean": _m(rs), "r_sd": _s(rs), "r_lo": _q(rs, 2.5), "r_hi": _q(rs, 97.5),
                      "ratio_mean": _m(ratios), "ratio_sd": _s(ratios), "ratio_lo": _q(ratios, 2.5),
                      "ratio_hi": _q(ratios, 97.5), "slope_mean": _m(slopes), "slope_sd": _s(slopes)})
        entry["ratio_rel_sd"] = (entry["ratio_sd"] / entry["ratio_mean"]
                                 if entry["ratio_sd"] is not None and entry["ratio_mean"] else None)
        entry["note"] = (f"resampled with replacement from {n_piles} piles"
                         + ("; n > piles collected: extrapolation" if n > n_piles else ""))
        out.append(entry)
    return out


def bootstrap_ci(samples: SampleTable, x_key: str, y_key: str = "weight_g", crop: str | None = None,
                 stat: str = "r", n_boot: int = 1000, alpha: float = 0.05, seed: int = 0):
    """Task 2. ``(lo, hi)``: the (1 - alpha) bootstrap confidence interval (BCa; percentile if scipy is
    missing) of ``stat`` of
    ``y_key`` against ``x_key``. ``stat``: ``"r"`` (correlation), ``"slope"`` (least-squares slope) or
    ``"ratio"`` (the model constant, mean y / x per pile).

    Cluster bootstrap: piles are resampled with replacement and each pile brings its photos as one
    averaged point, because photos of one pile are not independent. Resamples where the statistic is
    undefined (e.g. all x equal) are dropped. Returns ``None`` with fewer than 3 weighed photos or
    fewer than 3 piles."""
    if _n_photos(samples, x_key, y_key, crop) < 3:
        return None
    x, y, _ = pile_points(samples, x_key, y_key, crop)
    if len(x) < 3:
        return None
    def _percentile():
        rng = np.random.default_rng(seed)
        vals = []
        for _ in range(n_boot):
            idx = rng.integers(0, len(x), size=len(x))
            v = _stat(x[idx], y[idx], stat)
            if not np.isnan(v):
                vals.append(v)
        if not vals:
            return None
        lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        return float(lo), float(hi)

    # BCa (bias-corrected and accelerated) bootstrap over pile indices: with 10-25 piles the plain
    # percentile interval was measured (simulation) to cover only about 89-92 % instead of 95 %.
    try:
        from scipy.stats import bootstrap
    except ImportError:
        return _percentile()
    idx_all = np.arange(len(x))

    def _s(i):
        i = np.asarray(i).astype(int)
        return _stat(x[i], y[i], stat)

    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = bootstrap((idx_all,), _s, n_resamples=n_boot, method="BCa", confidence_level=1 - alpha,
                            random_state=seed, vectorized=False)
        lo, hi = float(res.confidence_interval.low), float(res.confidence_interval.high)
        if np.isnan(lo) or np.isnan(hi):
            return _percentile()
        return lo, hi
    except (ValueError, FloatingPointError, ZeroDivisionError):   # degenerate data: fall back
        return _percentile()


# ---- task 3: error propagation ---------------------------------------------------------------------------

def propagate(rel_errors: dict[str, float], weight_g: float, method: str = "rss") -> dict:
    """Task 3. Combine the relative error of each stage into the relative error of the weight.

    ``rel_errors`` = {stage: relative standard error of that stage}, e.g.
    {"scale": 0.02, "detector": 0.05, "kernel_weight": 0.03}, as measured in task 1.

    The estimate is a product of factors (weight = count x grams per seed, or area x grams per area), so
    for INDEPENDENT stages the relative errors add in quadrature ("root sum of squares", ``method="rss"``):
        rel_total = sqrt(sum_i e_i^2),   share_i = e_i^2 / sum_j e_j^2   (share of the total variance).
    ``method="linear"`` adds them up (rel_total = sum_i |e_i|): the worst case, when all stages push the
    same way (fully correlated); the shares are then e_i / sum_j e_j.
    Only list a stage once: e.g. the spread of grams per seed already contains the balance error of
    the batches it was measured with.

    Returns ``rel_total``, ``weight_u_g`` (= weight_g x rel_total), ``dominant`` (stage with the largest
    share), ``budget`` ({stage: share}, sums to 1) and ``method``."""
    errs = {k: abs(float(v)) for k, v in rel_errors.items()}
    if not errs:
        raise ValueError("rel_errors is empty")
    if method == "rss":
        parts = {k: e * e for k, e in errs.items()}
        rel_total = float(np.sqrt(sum(parts.values())))
    elif method == "linear":
        parts = dict(errs)
        rel_total = float(sum(parts.values()))
    else:
        raise ValueError(f"method must be 'rss' or 'linear', got {method!r}")
    tot = sum(parts.values())
    budget = {k: (p / tot if tot else 1.0 / len(parts)) for k, p in parts.items()}
    return {"rel_total": rel_total, "weight_u_g": float(weight_g) * rel_total,
            "dominant": max(budget, key=budget.get), "budget": budget, "method": method}
