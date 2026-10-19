# Status and plan: sunflower group (Hadi Nasooti, Jia)

Last update: Monday 19 October 2026. CNH Data Collection module, KU Leuven MAIBI.

## 1. Where we are

| Task | Status |
|---|---|
| 1. Plan the data collection | Jia's plan reviewed; pilot done; procedure written: [`PROCEDURE.md`](PROCEDURE.md); main collection done (8 piles, 19 Oct) |
| 2. Feature + number of samples (code) | Done: count of sunflower boxes, 8 piles enough (section 3c) |
| 3. Bounds + error propagation (code) | Done: +-10.0 % bounds, error budget (section 3c) |
| 4. Team-mate repeats the procedure | Jia, after Monday, with her own 150 g of unused seeds |
| 5. Report / presentation | To start after the main data (send before 26 Oct) |
| 6. Demo with CNH | App with fixed scale and calibrated constant ready; Hadi's laptop to be updated (`3_UPDATE_double_click.bat`); procedure version 2 in `PROCEDURE.md` |

All 83 tests pass, including the course self-check `tests/test_student_tasks.py` (6 of 6).

## 2. What changed compared to Jia's Task 1 plan

Jia's plan is the basis (15 piles, 5 small / 5 medium / 5 large, focus on seed spacing, same balance, same
device, unique IDs, collector recorded). Four gaps were closed, mainly because task 3 needs a measured error
for every stage:

1. **Seed weight variation was in the error list but not measured.** Now measured: 3 batches of exactly
   200 hand-counted seeds were weighed (all 11 g, so any difference between batches is smaller than the 1 g
   scale step).
2. **Detector error could not be isolated without a manual count of the true number of seeds.** The same 3 hand-counted batches give
   the detector error directly (true count = 200).
3. **Scale calibration was not concrete.** Pilot (17 Oct): a steel ruler in every photo and the camera at
   40 cm, checked with the ruler standing upright. From the main collection on (19 Oct): a printed marker
   sheet in every photo, from which the program measures the scale itself (section 6).
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
  keep the standard setting (tile 1500, score 0.38, the best-F1 score of the course model; since 19 Oct it is
  saved with the calibrated constant and used as the app default): bias +1.7 %,
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
its target weight, as reported by Hadi (the filled-in checklist with the before and after readings is still
to be photographed and added). P09 to P15 (26 to 38 g) were **not** collected; see the decision below.

**Scale from the markers** (`tools/measure_scale.py`, result in `data/photos/2026-10-19_main/scale.csv`):
0.106 to 0.134 mm per pixel per photo. The scale grows in proportion to the camera height, so the height
varied by about 26 % between the lowest and the highest photo (the height itself was not measured). The two
markers in one photo differ by up to 3.6 %, so the phone was sometimes a little tilted.

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
| Fixed scale 0.110 mm/px inside the program (final) | 0.0529 | 4.0 % | +0.04 | 1.2 % |

Resizing to 0.110 mm/px removes the height effect and halves the A vs B difference. 0.135 mm/px also removes
the correlation, but the seeds are smaller in pixels and the detector misses more of them. Chosen standard:
**0.110 mm/px**; photos taken from higher up (or with a phone with fewer pixels) are enlarged to it.

The fixed scale is now built into the program (`detkit predict --std-mm-per-px 0.110` and the app, section 6):
the photo is resized in memory and the boxes are mapped back to the original pixels. Counted this way (the
way the app counts, `analysis/results/main_std/`), the main photos give: grams per seed 0.0529 on average,
relative sd 4.0 %, correlation with mm/px +0.04, mean difference photo A vs B 1.2 %. These counts differ by a
few seeds from the test copies above (other resizing and no extra JPEG step); the numbers below use them.

Pile level (mean of photos A and B, 8 piles), computed in Python:
- Grams per seed per pile: 0.0506 to 0.0572; relative sd between piles 4.0 %; no trend with pile weight
  (r = -0.08).
- Constant (grams per seed): relative standard error 1.4 % with 8 piles; with 15 piles and the same spread
  it would be about 1.0 %.
- 95 % prediction interval for one new photo: +-10.0 % (the bounds the app shows). A prediction interval is
  the range in which the true weight of a NEW sample should fall 19 times out of 20. It uses the t
  distribution with 7 degrees of freedom (8 piles minus 1), which widens the range because the spread is
  estimated from few piles.
- P06 is the clearest outlier: 0.0572 g per seed. With the fitted constant, 20 g should be about 378 seeds;
  the detector found 352 and 347, so about 7.5 % fewer. About 7 seeds lying close together are visibly not
  found (about 2 %), while 2 `sunflower` boxes on the handwritten note work the other way (net about 1.3 %). The rest is not
  explained; a weighing error is possible (the readings are reported, not yet written down, see above).
- Re-spread photos agree with the main photos (P03: 275/276 vs 277/273; P08: 458/464 vs 464/468).
- Touching seeds: P03 223/232 and P08 389/389 instead of 275 and 466 (mean of A and B), so 17 % fewer.

**Decision on the number of piles (19 Oct, reworded after review).** 8 piles give a usable first constant
(0.05294 g per seed, standard error 1.4 %). But the +-10.0 % is itself uncertain: it rests on a spread
estimated from only 8 piles, and with 8 piles the true spread could be about 0.66 to 2.0 times the estimate,
so the true half-width could be roughly 7 to 20 % (95 % confidence, chi-square, computed in Python). More
piles DO help: with 15 piles and the same spread the interval would be about +-8.8 % and its own
uncertainty much smaller (0.73 to 1.58 times). Two limits stay: the range is 10 to 24 g, not the planned 10 to
38 g, and the bound covers one seed lot, one person and one phone. Options: (a) keep 8 piles and state these
limits clearly; (b) add P09 to P15 (26 to 38 g, about 1 to 1.5 hours, estimate from the 19 Oct session) to firm up the bound and cover larger
samples. To be decided by Hadi.

## 3c. Tasks 2 and 3: results (19 October)

Full output: [`analysis/results/main_std/results.md`](../../analysis/results/main_std/results.md) (tables)
and the plots in the same folder. The exact commands, in order, are at the top of `analysis/build_project.py`;
running them again gives the same counts. The pilot and batch photos of 17 Oct have no markers; their scale
was **estimated** from the size of the seed boxes (`analysis/estimate_scale_from_seeds.py`: median long side
of the sunflower boxes, 11.25 mm on average, sd 0.17 mm, over the 24 main photos).

Words used below: **r** = correlation (1 = a perfect straight line). **Cluster bootstrap** = we draw whole
piles at random many times and recompute, so photos of one pile always stay together. **Top-down** = the
total spread we see in the data; **bottom-up** = the separate stages added up. **Root sum of squares** = how
independent errors add up: sqrt(a^2 + b^2 + ...).

**Task 2, which feature** (pile level, 8 piles; 95 % cluster bootstrap):

| Feature | r | r 95 % CI | Spread of weight / feature |
|---|---|---|---|
| count of all boxes | 0.990 | 0.950 .. 0.999 | 3.7 % |
| count of sunflower boxes | 0.989 | 0.945 .. 0.999 | 4.0 % |
| box area of sunflower boxes, mm^2 | 0.985 | 0.930 .. 0.999 | 5.4 % |
| box area of sunflower boxes, px^2 | 0.900 | 0.635 .. 0.990 | 11.6 % |
| mean box area, px^2 | -0.271 | -0.984 .. 0.753 | 35.7 % |

Chosen: **count of sunflower boxes** (`crop_count_x_constant`, 0.05294 g per seed, +-10.0 %). Counting all
boxes is as good here (the confidence intervals overlap almost fully), but at the fixed scale it still gave 1
to 6 extra boxes of other classes per batch photo (0.5 to 3 %); counting only sunflower boxes is safer when
the demo photo has other objects in it. Area in px^2 is poor because it changes with the camera height; in
mm^2 (scale from the markers) it is good but still behind the count. The high r values partly come from the
wide weight range (10 to 24 g); the spread column is the better guide.

**Task 2, how many samples**: in the learning curve (bootstrap draws of n piles) the relative sd of the
constant falls from 2.2 % (3 piles) to 1.3 % (8 piles); this follows about 1/sqrt(n), as expected. See the
decision in section 3b. **Photos per pile**: two photos of the same pile differ by 1.0 % (count), while piles
differ by 4.0 %, so one photo per sample is enough for the demo and a second photo adds little.

**Honest error** (leave one pile out: fit on 7 piles, predict the 8th, for every pile): mean absolute error
3.3 %. 7 of the 8 piles fall inside their 95 % bounds (both photos of P06 fall outside). With only 8 piles
this test is weak: even if the bounds were exactly right, 7 or fewer of 8 would happen about 1 time in 3.

**Task 3, error budget** (count model, at the mean pile weight of 17 g; relative standard errors):

| Stage | Relative error | Share of variance | How measured |
|---|---|---|---|
| Balance | 1.7 % | 18 % | 1 g steps: 0.29 g / 17 g (2.9 % at 10 g, 1.2 % at 24 g); 5 repeated weighings gave no spread |
| Seed weight (200 seeds) | not measurable | - | 3 batches of 200 seeds all 11 g: the 1 g scale cannot show their difference |
| Detector | 1.0 % | 7 % | 3 hand-counted batches of 200 seeds, 2 photos each (scale estimated from seed size): 196 to 202, mean -0.8 % |
| Not explained by the stages above | 3.4 % | 75 % | sqrt(4.0^2 - 1.7^2 - 1.0^2) |
| **Total (top-down)** | **4.0 %** | | spread of weight / count over the main photos |

The biggest part is not explained by the measured stages. Possible causes, not measured: seed-to-seed
weight differences (the 1 g scale cannot show them), seeds lying close together missed by the detector (P06),
and piles differing in the share of broken hull pieces (procedure rule 7 keeps them). A scale with 0.01 g
steps would show the first one. Note that the balance error is not a fixed percentage (larger for small
piles), while the prediction interval treats the spread as one percentage for all weights.

## 4. Plan and who does what (updated 19 Oct)

**Done:** pilot, scale checks, hand-counted batches, main collection (8 piles), standardised scale (section 3b),
code for tasks 2 and 3.

**Hadi**
| When | What |
|---|---|
| Mon 19 Oct (done) | 12 MP / 8 MP test: with the fixed scale, counts stay within about 2 % (section 6) |
| Mon 19 Oct (done) | Full task 2 and 3 analysis on the standardised photos (section 3c) |
| Mon 19 Oct (done) | Fixed scale built into the app and `detkit predict`; constant and bounds calibrated (`analysis/results/main_std/weight_config.json`; both count models are calibrated, the area models are not) |
| Before Wed 21 Oct | Hadi: double-click `03_Assignment/setup/3_UPDATE_double_click.bat` on the laptop, then test the app with one photo |
| Mon 19 Oct (done) | `PROCEDURE.md` version 2 and `data/DATASHEET.md` |
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

**Mini Gauge R&R** (Jia: iPhone 14, main camera 12 MP; Hadi: iPhone 15 Pro, 24 MP photos. The phone is one of
the factors we want to measure, and every person uses both phones, so the phone effect and the person effect can
be separated. The 12 MP test in section 6 shows the fixed scale keeps the count within about 2 %.) (lecture: repeatability = same person, same tool, again; reproducibility = other person or
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
| 1 | Task 4 mixes person, phone and seeds: if Jia's results differ we cannot say why | Lecture "Gauge R and R": repeatability (same person, again) vs reproducibility (other person, same thing) | Mini Gauge R&R on Monday (steps in section 4): one pile of about 16 g with the marker sheet; each of us takes 2 photos with each phone (8 photos of the SAME seeds), and both weigh it | Both, Mon 19 Oct, about 15 min |
| 2 | The demo phone of CNH may have another resolution (12 MP instead of 24 MP), so seeds have fewer pixels and the count can change | Task 6 is done with their phone; the result must not depend on the phone | (a) Test: shrink our photos to 12 MP and 8 MP and count again; (b) standardise every photo to the same millimetres per pixel before detection (see section 6). Done: height effect (section 3b) and 12 MP / 8 MP test (section 6) | Hadi |
| 3 | Seed weight spread is not measured: all 3 batches weighed 11 g on a scale with 1 g steps | "Measure the errors": the kernel weight stage in task 3 needs a number; now it is listed as "not measurable" and may be part of the unexplained 3.4 % | If a 0.01 g scale can be borrowed: weigh about 30 single seeds. If not: say so, and use the pile-to-pile spread (top-down) instead | Hadi or Jia |
| 4 | No business case on the first slide yet | Lecture starts with "identify the business case": why CNH needs kernel weight (harvest losses, seed planning) | One slide at the start of the presentation | Jia |
| 5 | No datasheet for our dataset | Lecture "Datasheets for datasets" | Done: `data/DATASHEET.md` | Hadi |
| 6 | Possible bias: one bucket of seeds, one table, one light, one person | Lecture "Bias while data collection" | Slide on where the method may not hold (other varieties, piles, other light, other background) | Both |
| 7 | Scattered seeds only; real samples can be piles | Assignment asks for scattered kernels; still a limit of the method | State the validity range; touching photos (pilot, P03-T, P08-T) show how fast it breaks down; piles would need another feature or a retrained detector | Both (report) |

## 6. Making the result independent of the phone (standardised scale)

The detector cuts each photo into tiles and shrinks every tile to the same size before looking at it, so
what matters is how many pixels one seed covers. That depends on the phone resolution and on the camera
height. Plan: measure millimetres per pixel in every photo from a reference of known size (ruler, or a
printed marker that a program can find automatically), then resize every photo to the same millimetres per
pixel before detection. Then 12 MP, 24 MP and small changes of camera height all give the detector seeds of
the same pixel size. Tested on the main collection (section 3b): standard 0.110 mm/px. Because the detector finds
more seeds when they are bigger in pixels, photos are also enlarged to this standard when needed (enlarging
adds no detail). Code: `detkit/scale.py`, used by `detkit predict --std-mm-per-px 0.110` and by the app
(Inference tab, "Fixed scale from the marker sheet", on by default; the row note shows the measured scale or
"no marker found"). Photos without markers can get a scale measured another way (`--scale-csv`). The
stand-alone tool `tools/measure_scale.py` writes the scale of a folder of photos to a CSV.

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
5. Task 4 (Jia): should the team mate repeat the full data collection with new piles, or is a smaller
   independent replication enough? And what does "independent" mean for you: another person only, or also
   another phone and other seeds?
6. Task 4 (Jia): we plan to compare measured weight, predicted weight and prediction error between our
   collection and the replication, check how many of the replication's true weights fall inside our 95 %
   bounds, compare the grams per seed of both, and add a mini Gauge R&R (2 persons x 2 phones x 2 photos of one
   pile). Is that enough, or do you expect more statistical analysis?
7. Presentation: how long, and is a slide deck enough or do you also want a report or notebook?
8. GitHub: the slide says "Github repo with your code (6/10/2026)". Which date is meant, and should we add
   you as collaborators (user names) or make the repository public?
9. Is it fine that we added two weight models (count and area of the photo's own crop only) and changed two
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
