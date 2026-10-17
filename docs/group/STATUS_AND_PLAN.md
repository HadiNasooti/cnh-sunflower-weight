# Status and plan: sunflower group (Hadi Nasooti, Jia)

Last update: Saturday 17 October 2026. CNH Data Collection module, KU Leuven MAIBI.

## 1. Where we are

| Task | Status |
|---|---|
| 1. Plan the data collection | Jia's plan reviewed; pilot done; procedure written: [`PROCEDURE.md`](PROCEDURE.md) |
| 2. Feature + number of samples (code) | Code done (`learning_curve`, `bootstrap_ci`); waiting for the main data |
| 3. Bounds + error propagation (code) | Code done (`low_g`/`high_g`, `propagate`); waiting for the main data |
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

## 4. Plan and who does what

| When | Who | What |
|---|---|---|
| Sun 18 Oct | Hadi | Main collection: 15 piles from 10 to 38 g (2 g steps), 2 photos each at 40 cm; extra re-spread (R) and touching (T) photos for P03, P08, P13. Then run the task 2 and 3 analysis. |
| Sun 18 Oct | Jia | Read `PROCEDURE.md` and note every step that is unclear or that you would do differently (that is part of task 4). Clone this repository on your Mac (see below). |
| Mon 19 Oct, 15:00-15:30 | Both | Online meeting: go through the first results and the questions for CNH. |
| Mon 19 Oct, evening | Both | CNH session: questions (below). Hadi brings Jia's jar with 150 g of unused seeds. |
| After Monday | Jia | Task 4: collect a small new sample with your own seeds, following only `PROCEDURE.md` (for example 5 piles of 10, 15, 20, 25 and 30 g, 2 photos each). Write down the phone model. |
| After Monday | Both | Task 4 analysis, report and presentation. Draft by Thu 22 Oct, final Sat 24 Oct, send before the 26 Oct session. |
| Mon 26 Oct | Both | Presentation and live demo (app on Hadi's laptop over a phone hotspot). |

## 5. Questions for CNH on Monday 19 October

1. How big is the sample you bring for the demo (task 6), roughly in grams? If it is more than fits in one
   photo with all seeds apart, may it be split over several photos?
2. Will you photograph with your own phone, at the height our procedure says, with our ruler in the photo?
3. The deliverables slide says "Github repo with your code (6/10/2026)". Which date is meant, and should
   the repository be shared with you (user names), or made public?
4. Is it fine that we added two weight models (count and area of the photo's own crop only) and changed two
   course tests that listed the models?

## 6. Using this repository

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
