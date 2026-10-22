"""Business case for the data: time and cost per pile and per photo, the bound as a function of the number of
piles, and the stop rule. All inputs are written out below or read from results_2026_10_22.py's results.json.

Labour rate: Eurostat, hourly labour cost 2024, Belgium, whole economy (enterprises with 10 or more
employees): 48.2 euro per hour (Eurostat news, 28 March 2025). Used as an EXAMPLE rate only.

Output: analysis/results/2026-10-22_analysis/business_case.json and business_case.md
Usage: python analysis/business_case.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/results/2026-10-22_analysis"
R = json.loads((OUT / "results.json").read_text())

RATE_EUR_PER_H = 48.2                                   # example rate (Eurostat, Belgium, 2024)
S_REL = R["pooled_17"]["rel_sd_pct"] / 100              # pile-to-pile spread of grams per seed, 17 piles
N_NOW = 17
MIN_PER_PILE = {                                         # measured from photo timestamps (results.json)
    "Hadi P01-P08, 10-24 g": R["minutes_per_pile"]["2026-10-19_main"]["min_between_piles_mean"],
    "Jia task 4, 11-23 g": R["minutes_per_pile"]["2026-10-20_task4"]["min_between_piles_mean"],
    "Jia P09-P13, 27-34 g": R["minutes_per_pile"]["2026-10-21_extra_piles"]["min_between_piles_mean"],
}


def rr_same_setup_gaps() -> list[int]:
    """One more photo of a pile that is already spread: in the Gauge R&R session (17 photos of one pile),
    the seconds between two consecutive photos by the same person, phone and height (EXIF times).
    Gaps over 5 minutes are breaks and left out."""
    import csv
    import datetime as dt

    from PIL import Image
    rows = [r for r in csv.DictReader(open(ROOT / "data/samples.csv", encoding="utf-8-sig"))
            if r["folder"] == "2026-10-19_gauge_rr"]
    seq = []
    for r in rows:
        ex = Image.open(ROOT / "data/photos" / r["folder"] / r["file"]).getexif()
        v = ex.get_ifd(0x8769).get(36867) or ex.get(306)
        key = (r["collector"], r["phone"], "high" if "height high" in r["notes"] else "normal")
        seq.append((dt.datetime.strptime(v, "%Y:%m:%d %H:%M:%S"), key))
    seq.sort()
    return [int((b[0] - a[0]).total_seconds()) for a, b in zip(seq, seq[1:])
            if a[1] == b[1] and (b[0] - a[0]).total_seconds() <= 300]


SAME_SETUP_GAPS_S = rr_same_setup_gaps()
REPEAT_SD_PCT = R["gauge_rr_marker_ok"]["repeatability_rel_pct"]   # one photo again, same pile
BAL_RMS_PCT = R["floor_note"]["balance_rms_rel_pct"]


def bound(n: int, s: float = S_REL) -> float:
    """95 % prediction bound (half-width, relative) for one new pile with n calibration piles."""
    return stats.t.ppf(0.975, n - 1) * s * math.sqrt(1 + 1 / n)


out = {"inputs": {"rate_eur_per_h": RATE_EUR_PER_H, "rate_source": "Eurostat 2024, Belgium (example rate)",
                  "s_rel_pct": round(100 * S_REL, 2), "n_piles_now": N_NOW,
                  "minutes_per_pile": MIN_PER_PILE, "same_setup_photo_gaps_s": SAME_SETUP_GAPS_S}}



def session_photo_hours() -> dict:
    """Photo time per data-collection session: first to last photo (EXIF), so the last pile's own time,
    travel and preparation are not included."""
    import csv
    import datetime as dt

    from PIL import Image
    spans = {}
    for r in csv.DictReader(open(ROOT / "data/samples.csv", encoding="utf-8-sig")):
        ex = Image.open(ROOT / "data/photos" / r["folder"] / r["file"]).getexif()
        v = ex.get_ifd(0x8769).get(36867) or ex.get(306)
        if v:
            spans.setdefault(r["folder"], []).append(dt.datetime.strptime(v, "%Y:%m:%d %H:%M:%S"))
    mins = {k: round((max(v) - min(v)).total_seconds() / 60, 1) for k, v in spans.items()}
    return {"minutes_per_session": mins, "total_hours": round(sum(mins.values()) / 60, 2)}


out["photo_time_all_sessions"] = session_photo_hours()
out["cost_per_pile_eur"] = {k: round(v / 60 * RATE_EUR_PER_H, 2) for k, v in MIN_PER_PILE.items()}
med_gap = sorted(SAME_SETUP_GAPS_S)[len(SAME_SETUP_GAPS_S) // 2]
out["extra_photo"] = {"median_s": med_gap, "cost_eur": round(med_gap / 3600 * RATE_EUR_PER_H, 2),
                      "note": "an extra photo of the same pile costs seconds, but only lowers the photo error "
                              f"({REPEAT_SD_PCT} % for one photo), not the pile-to-pile spread"}

# bound versus number of piles, cost of each step (Hadi's 12.7 min per pile)
m = MIN_PER_PILE["Hadi P01-P08, 10-24 g"]
curve = []
for n in (3, 4, 5, 6, 8, 10, 12, 15, 17, 20, 25, 30, 50, 100):
    curve.append({"n_piles": n, "bound_pct": round(100 * bound(n), 2),
                  "gain_of_next_pile_pct_points": round(100 * (bound(n) - bound(n + 1)), 3),
                  "hours": round(n * m / 60, 1), "cost_eur": round(n * m / 60 * RATE_EUR_PER_H)})
out["bound_vs_piles"] = curve
out["floor_pct"] = round(100 * stats.norm.ppf(0.975) * S_REL, 2)

# piles needed for a target bound
targets = {}
for tgt in (12, 10, 9, 8.75, 8.5, 8.25, 8):
    n = next((n for n in range(3, 2000) if 100 * bound(n) <= tgt), None)
    targets[str(tgt)] = None if n is None else {"piles": n, "hours": round(n * m / 60, 1),
                                                "cost_eur": round(n * m / 60 * RATE_EUR_PER_H)}
out["piles_for_target_bound"] = targets

# stop rule: stop when the next pile improves the bound by less than 0.2 percentage points
STOP_GAIN = 0.2
n_stop = next(n for n in range(3, 500) if 100 * (bound(n) - bound(n + 1)) < STOP_GAIN)
out["stop_rule"] = {"rule": f"stop when one more pile improves the bound by less than {STOP_GAIN} percentage points",
                    "n_stop": n_stop, "bound_at_stop_pct": round(100 * bound(n_stop), 2),
                    "cost_of_next_pile_eur": round(m / 60 * RATE_EUR_PER_H, 2),
                    "eur_per_0p1_pct_point_at_stop": round(m / 60 * RATE_EUR_PER_H /
                                                           (1000 * (bound(n_stop) - bound(n_stop + 1))), 2)}
# what the uncertainty of s does to the stop point (s itself is known only to 0.74-1.52 x with 17 piles)
lo = math.sqrt((N_NOW - 1) / stats.chi2.ppf(0.975, N_NOW - 1))
hi = math.sqrt((N_NOW - 1) / stats.chi2.ppf(0.025, N_NOW - 1))
out["s_uncertainty"] = {"factor_95ci": [round(lo, 2), round(hi, 2)],
                        "bound_at_17_piles_pct_range": [round(100 * bound(N_NOW, S_REL * lo), 1),
                                                        round(100 * bound(N_NOW, S_REL * hi), 1)]}
# where the rest of the error sits (relative sd, %): spending money on more piles cannot remove these
rest = math.sqrt(max(100 ** 2 * S_REL ** 2 - BAL_RMS_PCT ** 2 - (REPEAT_SD_PCT / math.sqrt(2)) ** 2, 0))
out["error_budget_pct"] = {"total_between_piles": round(100 * S_REL, 2), "balance_1g_step": BAL_RMS_PCT,
                           "photo_mean_of_2": round(REPEAT_SD_PCT / math.sqrt(2), 2),
                           "seed_weight_and_rest": round(rest, 2)}

(OUT / "business_case.json").write_text(json.dumps(out, indent=1))

md = ["# Business case numbers (generated by analysis/business_case.py)", "",
      f"Example labour rate {RATE_EUR_PER_H} euro per hour (Eurostat, Belgium, 2024). Spread between piles "
      f"s = {100 * S_REL:.2f} % (17 piles).", "",
      "| Piles | Bound (+-%) | Gain of the next pile (points) | Hours | Cost (euro, example) |", "|---|---|---|---|---|"]
md += [f"| {c['n_piles']} | {c['bound_pct']} | {c['gain_of_next_pile_pct_points']} | {c['hours']} | {c['cost_eur']} |"
       for c in curve]
md += ["", f"Floor (infinitely many piles): +-{out['floor_pct']} %.",
       f"Stop rule: {out['stop_rule']['rule']}: n = {n_stop} piles (bound +-{out['stop_rule']['bound_at_stop_pct']} %)."]
(OUT / "business_case.md").write_text("\n".join(md) + "\n")
print(json.dumps(out, indent=1))
