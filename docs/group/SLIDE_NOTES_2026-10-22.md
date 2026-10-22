# Notes on the draft slides (ppt_slide_topics/Sunflower_Weight_Estimation_Report_Draft-2.pptx), 22 Oct evening

The draft was made from the repo as it was before the 22 Oct analysis. Since then the detector was run on all
new photos and the Gauge R&R is complete. New numbers: `docs/group/PLAN_2026-10-22.md` (sections 2 and 5),
`docs/group/VARIABLES.md`, and `analysis/results/2026-10-22_analysis/` (per_photo.csv, per_pile.csv,
results.json, business_case.md).

## What CNH asked for on 19 Oct (not yet in the slides)

1. All variables that can make the weight wrong, how we measured each one and how we handle it: a slide with
   the top 8 to 10 rows of `VARIABLES.md` (camera height, phone, person, tilt, marker, touching seeds, sample
   size, other objects, shadows, scale step).
2. How it works for the end user (very easy): the 5 steps and the traffic light (PLAN section 4).
3. A business case: cost per pile, bound against number of piles, stop rule (PLAN section 5).

## Slide by slide

| Slide | What to change |
|---|---|
| 2 | Add the new key findings: Jia's 9 piles all inside the bounds; Gauge R&R: same pile, 2 persons x 2 phones x 2 heights, spread 1.2 %, no person/phone/height effect; all 17 piles together give +-8.7 % |
| 5 | Task 4 was on 20 Oct (photo dates), not 21 Oct. Jia's task 4 piles are now called T4-01 to T4-04 (P01 to P04 were already used). Gauge R&R: 17 photos. P09 to P13 are no longer exploratory: they were analysed (5 of 5 inside the bounds) |
| 6 | "Detector bias on batches ~0.8 %": the 17 Oct result is that the spread of the error was 0.8 to 1.8 % for every detector setting. "Balance error at 17 g 1.7 %": now 1.73 % over all 17 piles (2.9 % at 10 g, 0.8 % at 34 g) |
| 7 | Can add: for Jia's photos the count still correlates best (r 0.994, box area 0.988) |
| 9 | The "15-pile projection" can now be replaced by the real result: 17 piles, +-8.7 % |
| 10 | New error budget (17 piles): total 3.97 %, scale step 1.73 %, photo 0.93 % (measured in the Gauge R&R), remainder 3.45 % |
| 11 | Title: the repeat is now clean enough: 9 of 9 inside, Jia's grams per seed +1.5 % (95 % CI -2.7 to +5.7 %). Pile names T4-01 to T4-04. T4-03 before and after are both 18 g (written as "consistent with before"). T4-02: rounding cannot explain 2 g, still to explain |
| 12 | P09 to P13 were analysed: 5 of 5 inside the bounds, mean absolute error 3.0 %, no trend with weight from 10 to 34 g. P14/P15: dropped on purpose; a bigger sample is split into two photos (the program counts up to 651 seeds, our largest tested photo) |
| 13 | Item 4 "fix the camera height": our Gauge R&R shows height does not matter with the fixed scale (high minus normal 0.0 %), so the user needs no stand. Items 5 and 6 are done now. Items 1 and 3 are good ideas |
| 14 | "Ask Hadi whether task 4 must be repeated": no, it holds. The R&R results are in. samples.csv now has 63 photo rows |
| New | Business case slide (PLAN section 5) and end-user / traffic light slide (PLAN section 4) |
