# Status and plan: sunflower group (Hadi Nasooti, Jia)

Last update: Monday 19 October 2026. CNH Data Collection module, KU Leuven MAIBI.

## 1. Where we are

| Task | Status |
|---|---|
| 1. Plan the data collection | Jia's plan reviewed; pilot done; procedure written: [`PROCEDURE.md`](PROCEDURE.md); main collection done (8 piles, 19 Oct) |
| 2. Feature + number of samples (code) | Code done (`learning_curve`, `bootstrap_ci`); main data in; full analysis run still to do |
| 3. Bounds + error propagation (code) | Code done (`low_g`/`high_g`, `propagate`); main data in; full analysis run still to do |
| 4. Team-mate repeats the procedure | Jia, after Monday, with her own 150 g of unused seeds |
| 5. Report / presentation | To start after the main data (send before 26 Oct) |
| 6. Demo with CNH | App runs on Hadi's laptop; procedure for CNH in `PROCEDURE.md` |

All 72 tests pass, including the course self-check `tests/test_student_tasks.py` (6 of 6).

## 2. What changed compared to Jia's Task 1 plan

Jia's plan is the basis (15 piles, 5 small / 5 medium / 5 large, focus on seed spacing, same balance, same
device, unique IDs, collector recorded). Four gaps were closed, mainly because task 3 needs a measured error
for every stage:

1. **Seed weight variation was in the error list but not measured.** Now measured: 3 batches of exactly
   200 hand-counted seeds were weighed (all 11 g, so any difference between batches is smaller than the 1 g
   scale step).
2. **Detector error could not be isolated without a manual count of the true number of seeds.** The same 3 hand-counted batches give
   the detector error directly (true count = 200).
3. **Scale calibration was not concrete.** Now: a steel ruler in every photo and the camera at 40 cm, checked
   with the ruler standing upright.
4. **Task 6 (CNH takes the photos with their own phone) was not covered.** The procedure is now written so an
   outsider can follow it.

## 3. Results so far (17 October, pilot)

Full record with times: [`lab_log.md`](lab_log.md).

**Scale**
- 2 x 2-euro coins (17.0 g) read 18 g, 4 x 1-euro coins (30.0 g) read 31 g, without TARE just before.
  After TARE, all 6 coins (47.0 g) read 47 g. Conclusion: zero drift of +1 g; rule "TARE before every
  weighing".
- Same 25 g pile weighed 5 times (lift off, put back): 25, 25, 25, 25, 25 g.

All counts below are on the photos as they are stored in `data/` (cropped to the table, upright).

**Pilot pile, 25 g, detector at its standard settings (tile 1500, score 0.38)**

| Photo | All boxes | Sunflower boxes |
|---|---|---|
| Seeds apart | 460 | 452 |
| Same layout, photo taken again | 472 | 466 |
| Seeds pushed together (touching) | 310 | 308 |

Touching seeds: about one third of the seeds are missed (308 vs 452 sunflower boxes, 32 % fewer).
Rule: no seed may touch another.

**3 batches of 200 hand-counted seeds** (all weighed 11 g), photographed at 40 cm and at 25 cm

| Photo | All boxes | Error | Sunflower boxes only | Error |
|---|---|---|---|---|
| B1, 40 cm | 210 | +5.0 % | 205 | +2.5 % |
| B2, 40 cm | 212 | +6.0 % | 199 | -0.5 % |
| B3, 40 cm | 217 | +8.5 % | 206 | +3.0 % |
| B1, 25 cm | 229 | +14.5 % | 206 | +3.0 % |
| B2, 25 cm | 234 | +17.0 % | 199 | -0.5 % |
| B3, 25 cm | 257 | +28.5 % | 205 | +2.5 % |

- The extra boxes sit on the ruler digits and the handwriting, labelled as other crops (mostly popcorn
  corn, pumpkin and wheat). Counting only the `sunflower` boxes removes them. New weight models were added
  for this: `crop_count_x_constant` and `crop_area_x_constant`.
- Before cropping, the detector also put 6 `sunflower` boxes on the trousers at the edge of photo B2-40 cm
  (206 boxes instead of 199 after cropping). Rule added: only the table may be in the photo.
- The same photo gives a slightly different count when it is stored differently (cropped, turned upright):
  for example B1-40 cm gave 202 before and 205 after. This is because the photo is cut into different tiles.
  This variation of a few seeds is part of the detector error.
- Over 84 combinations (4 tile sizes x 7 score thresholds x 3 counting modes, `analysis/tune_detector.py`),
  the sunflower-only count is always much better than counting all boxes. Between tile sizes and thresholds
  the differences are small (sd of the error 0.8 to 1.8 %), and the best combination changed between the
  original and the cropped photos. With only 3 independent batches we cannot really tell them apart, so we
  keep the standard setting (tile 1500, score 0.38, the course default and the app default): bias +1.7 %,
  sd 1.7 % over the 6 photos. The bias is absorbed when the grams-per-seed constant is calibrated.
- Chosen camera height: **40 cm** (about as accurate as 25 cm: mean error +1.7 % at both heights, and the
  photo covers about 2.5 times the area: (40/25)^2 = 2.56, from geometry, not measured).

**Grams per seed, two independent ways**
- Batches: 11 g / 200 seeds = 0.055 g per seed.
- Pilot: 25 g / 452 sunflower boxes = 0.0553 g per seed.
- Note: the batches were whole seeds only, while the piles keep the broken hull pieces (procedure rule 7),
  so the two numbers measure slightly different material.

## 3b. Main collection (19 October, Hadi)

Piles P01 to P08 (10 to 24 g, 2 g steps), 2 photos each, plus re-spread (R) and touching (T) photos for P03
and P08: 24 photos in `data/photos/2026-10-19_main/`. Daylight, marker sheet in every photo. Each pile weighed
its target weight. P09 to P15 (26 to 38 g) were **not** collected; see the decision below.

**Scale from the markers** (`tools/measure_scale.py`, result in `data/photos/2026-10-19_main/scale.csv`):
0.106 to 0.136 mm per pixel, so the camera height was not constant (roughly 36 to 46 cm; estimate from the
marker, not measured). The two markers in one photo differ by up to 3.6 %, so the phone was sometimes tilted.

**Effect of the camera height**: on the photos as taken, grams per seed varies 5.9 % (relative sd, 16 main
photos) and is correlated with mm per pixel (r = +0.63): photos taken from higher up miss seeds. Example: P01
photo A 185 seeds at 0.108 mm/px, photo B 164 seeds at 0.134 mm/px.

**Standardised scale** (every photo resized to the same mm per pixel before detection, section 6). Counts per
photo: `analysis/results/2026-10-19_standardisation_counts.csv`.

| Detector input | Grams per seed (mean) | Relative sd (16 photos) | Correlation with mm/px | Mean difference photo A vs B |
|---|---|---|---|---|
| Photos as taken | 0.0542 | 5.9 % | +0.63 | 3.0 % |
| Resized to 0.110 mm/px | 0.0530 | 4.2 % | +0.12 | 1.6 % |
| Resized to 0.135 mm/px | 0.0566 | 4.8 % | +0.12 | 2.5 % |

Resizing to 0.110 mm/px removes the height effect and halves the A vs B difference. 0.135 mm/px also removes
the correlation, but the seeds are smaller in pixels and the detector misses more of them. Chosen standard:
**0.110 mm/px**; photos taken from higher up (or with a phone with fewer pixels) are enlarged to it.

After standardising (pile level, mean of photos A and B, 8 piles), computed in Python:
- Grams per seed: relative sd between piles 4.3 %, no trend with pile weight (r = -0.10).
- Constant (grams per seed): relative standard error 1.5 % with 8 piles; with 15 piles and the same spread
  it would be about 1.1 %.
- 95 % prediction interval for one new pile: about +-10.7 % (t with 7 degrees of freedom).
- The spread that is left comes from the detector (example: P06, 0.0574 g per seed, about 7 seeds lying close
  together not found, and 2 `sunflower` boxes on the handwritten note) and from the scale rounding (0.29 g,
  which is 2.9 % of 10 g and 1.2 % of 24 g).
- Re-spread photos now agree with the main photos (P03: 273/276 vs 278/274; P08: 459/460 vs 462/467).
- Touching seeds: P03 218/231 and P08 377/383 instead of about 276 and 465, so about 18 to 19 % fewer.

**Decision (19 Oct): 8 piles are enough for tasks 2 and 3.** More piles taken the same way would mainly shrink
the error of the constant from 1.5 % to about 1.1 %, while the error for one new sample (about +-10.7 %) is
set by the pile-to-pile spread, which more piles do not reduce. The validity range of the result is 10 to
24 g; if the CNH demo sample is larger, it is split over several photos (question 1 for CNH).

## 4. Plan and who does what (updated 19 Oct)

**Done:** pilot, scale checks, hand-counted batches, main collection (8 piles), standardised scale (section 3b),
code for tasks 2 and 3.

**Hadi**
| When | What |
|---|---|
| Mon 19 Oct (done) | 12 MP / 8 MP test: with the fixed scale, counts stay within about 2 % (section 6) |
| Tue 20 to Wed 21 Oct | Full task 2 and 3 analysis on the standardised photos: best feature, learning curve, bootstrap confidence interval, bounds, error budget |
| Tue 20 to Wed 21 Oct | Standardising built into the app, so the demo photo is resized automatically; new constant and bounds saved in the app |
| Wed 21 Oct | `PROCEDURE.md` version 2: marker sheet instead of ruler, no handwritten note near the seeds, height check from the marker |
| Optional | If a 0.01 g scale can be borrowed: weigh about 30 single seeds (seed weight spread for task 3) |

**Jia**
| When | What |
|---|---|
| Before Mon 19 Oct evening | Read `PROCEDURE.md`; write down every step that is unclear (part of task 4) |
| Tue 20 to Thu 22 Oct | Task 4: with the jar of unused seeds, a printed marker sheet (print at 100 %, check the 100 mm line) and a kitchen scale, collect 4 piles of 10, 14, 18 and 22 g, 2 photos each, following only `PROCEDURE.md`. Write down phone model, light, any problem. Upload to `data/photos/<date>_task4/` plus lines in `data/samples.csv` |
| Thu 22 Oct | Business case slide (why CNH needs seed weight) and first draft of the presentation |

**Together**
| When | What |
|---|---|
| Mon 19 Oct, CNH session | Mini Gauge R&R (section 5, row 1) and the questions in section 7 |
| Thu 22 Oct | Draft presentation complete; Hadi adds tasks 2, 3 and 6 results, Jia tasks 1, 4 and the business case |
| Sat 24 Oct | Final version; send to CNH before the 26 Oct session |
| Sun 25 Oct | Demo rehearsal: one of us acts as CNH and follows the procedure with a phone that was not used before |
| Mon 26 Oct | Presentation and live demo |

**Mini Gauge R&R** (lecture: repeatability = same person, same tool, again; reproducibility = other person or
other tool). One pile of about 16 g on white paper, marker sheet next to it, no seed touching.
1. Hadi weighs the pile (TARE first), Jia weighs it again. Write both readings.
2. Hadi takes 2 photos with his phone, then 2 with Jia's phone (move away and come back between photos).
3. Jia does the same: 2 with her phone, 2 with Hadi's phone. Do not touch the seeds in between.
4. Result: 8 photos of the same seeds. Differences between photos of the same person and phone show
   repeatability; between persons and between phones show reproducibility. Same seeds, so the true count is
   the same in all 8.

## 5. Weak spots we found ourselves, and how we close them

| # | Weak spot | Why it matters for the grade | What we do | Who, when |
|---|---|---|---|---|
| 1 | Task 4 mixes person, phone and seeds: if Jia's results differ we cannot say why | Lecture "Gauge R and R": repeatability (same person, again) vs reproducibility (other person, same thing) | Mini Gauge R&R on Monday: one small pile, the ruler and the scale; both of us photograph the SAME pile, each with our own phone and with the other's phone (4 photos), and both weigh it | Both, Mon 19 Oct, about 15 min |
| 2 | The demo phone of CNH may have another resolution (12 MP instead of 24 MP), so seeds have fewer pixels and the count can change | Task 6 is done with their phone; the result must not depend on the phone | (a) Test: shrink our photos to 12 MP and 8 MP and count again; (b) standardise every photo to the same millimetres per pixel before detection (see section 6). Done: height effect (section 3b) and 12 MP / 8 MP test (section 6) | Hadi |
| 3 | Seed weight spread is only an upper limit: all 3 batches weighed 11 g on a scale with 1 g steps | "Measure the errors": the kernel weight stage in task 3 needs a number, not only a limit | If a 0.01 g scale can be borrowed: weigh about 30 single seeds. If not: say so, and use the pile-to-pile spread (top-down) instead | Hadi or Jia |
| 4 | No business case on the first slide yet | Lecture starts with "identify the business case": why CNH needs kernel weight (harvest losses, seed planning) | One slide at the start of the presentation | Jia |
| 5 | No datasheet for our dataset | Lecture "Datasheets for datasets" | One page in `data/`: who collected, how, when, conditions, limits | Hadi |
| 6 | Possible bias: one bucket of seeds, one table, one light, one person | Lecture "Bias while data collection" | Slide on where the method may not hold (other varieties, piles, other light, other background) | Both |
| 7 | Scattered seeds only; real samples can be piles | Assignment asks for scattered kernels; still a limit of the method | State the validity range; touching photos (pilot, P03-T, P08-T, P13-T) show how fast it breaks down; piles would need another feature or a retrained detector | Both (report) |

## 6. Making the result independent of the phone (standardised scale)

The detector cuts each photo into tiles and shrinks every tile to the same size before looking at it, so
what matters is how many pixels one seed covers. That depends on the phone resolution and on the camera
height. Plan: measure millimetres per pixel in every photo from a reference of known size (ruler, or a
printed marker that a program can find automatically), then resize every photo to the same millimetres per
pixel before detection. Then 12 MP, 24 MP and small changes of camera height all give the detector seeds of
the same pixel size. Tested on the main collection (section 3b): standard 0.110 mm/px. Because the detector finds
more seeds when they are bigger in pixels, photos are also enlarged to this standard when needed (enlarging
adds no detail). Code: `tools/measure_scale.py --images DIR --standardise OUT --target 0.110`. Still to do:
the same test on our photos shrunk to 12 MP and 8 MP.

**Phone resolution test (19 Oct).** The 24 main photos were shrunk to 12 MP and to 8 MP (as a phone with
fewer pixels would take them) and counted, once as they are and once after resizing to 0.110 mm/px. Counts
compared with the full-resolution photos resized to 0.110 mm/px (16 main photos;
`analysis/results/2026-10-19_megapixel_test_counts.csv`):

| Detector input | Mean count difference | Range | Grams per seed relative sd |
|---|---|---|---|
| 12 MP, as it is | -17.8 % | -33.0 to -7.5 % | 9.6 % |
| 12 MP, resized to 0.110 mm/px | +0.1 % | -1.9 to +2.2 % | 3.6 % |
| 8 MP, as it is | -42.6 % | -68.1 to -26.1 % | 25.4 % |
| 8 MP, resized to 0.110 mm/px | +0.2 % | -1.7 to +1.7 % | 3.7 % |

Without the fixed scale, a phone with fewer pixels misses many seeds. With it, the count stays within about
2 % of the full-resolution count. The markers were still found at 8 MP (in 19 of 24 photos both markers, in
5 one marker). This is the main reason the demo with CNH's phone must use the fixed scale.

## 7. Questions for CNH on Monday 19 October

1. Demo (task 6): how big is the sample you bring, roughly in grams? Our method is tested for 10 to 24 g per
   photo. May a bigger sample be split over several photos?
2. Which phone will you use (model or megapixels)? Is it fine that you put our printed marker sheet next to
   the seeds, on white paper, so the program can measure the scale in your photo?
3. Is it allowed to resize the photo to a fixed scale before detection (we do not retrain the detector)?
4. Number of samples (task 2): is it fine that we decide it from our own learning curve and stopped at 8
   piles, or do you expect a minimum?
5. Task 4: is a small repeat by the team mate plus a mini Gauge R&R on one pile what you expect?
6. Presentation: how long, and is a slide deck enough or do you also want a report or notebook?
7. GitHub: the slide says "Github repo with your code (6/10/2026)". Which date is meant, and should we add
   you as collaborators (user names) or make the repository public?
8. Is it fine that we added two weight models (count and area of the photo's own crop only) and changed two
   course tests that listed the models?

## 8. Using this repository

This is the course repository (`niru-5/manama_data_collection_course`) with our changes on top:
- `detkit/weight/stats.py`, `detkit/weight/models.py`: tasks 2 and 3
- `detkit/weight/features.py`, `models.py`: crop-only count and area (`count_<crop>`, `area_px_<crop>`)
- `analysis/sunflower_analysis.py`: all task 2 and 3 tables and plots in one run
- `analysis/tune_detector.py`: detector settings against hand-counted photos
- `docs/group/`: this file, the procedure and the lab log
- `data/`: all photos, the sample table and the lab measurements

On a Mac: install as in the main `README.md` (Quick start, Linux/macOS), but clone this repository
(https://github.com/HadiNasooti/cnh-sunflower-weight, private: Hadi adds you as a collaborator) instead of the
course one. All photos and measurements are in `data/` (see `data/README.md`). The detector model weights are not in the
repository (they are downloaded by the quick start, step 2).

Working together: you can read and edit every file directly on the GitHub website (pencil icon), and upload
your task 4 photos with *Add file* > *Upload files* into a new folder `data/photos/<date>_task4/`, plus one
line per photo in `data/samples.csv`.
