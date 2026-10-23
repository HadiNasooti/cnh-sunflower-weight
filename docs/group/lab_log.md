# Lab log (collector: Hadi, 17 Oct 2026)
Balance: kitchen scale, Max 3000 g, Div 1 g.
13:28 2x 2-euro coins (nominal 17.0 g): read 18 g. 4x 1-euro (nominal 30.0 g): read 31 g. Scale NOT re-tared just before.
13:30 After TARE on empty scale, all 6 coins (nominal 47.0 g): read 47 g.
Conclusion: +1 g came from zero drift (no tare); after tare reading matches nominal within 1 g. Rule: TARE before every weighing.
13:36 Jia's task-4 seeds: glass jar tared, seeds added to 150 g, scooped from bucket. Jar removed: display -223 g (= jar mass, tare stays active).
13:51 PILOT-1: bowl tared, seeds 20 g (IMG_4129), topped up to 25 g (IMG_4130, 13:52).
14:02 IMG_4131 photo 1, seeds apart, ruler + PILOT-1 note (24 MP, 5712x4284).
14:02 IMG_4132 photo 2, same layout, phone lowered and lifted (height visibly different).
14:04 IMG_4133 photo 3, seeds pushed together (touching, some may overlap).
After: seeds back in bowl, weighed 5 times (lift off / put back): 25, 25, 25, 25, 25 g.
Observation: sample contains broken hull pieces / chaff (brown fragments) besides whole seeds.
14:20 Detector (tile 1500, score 0.38) on pilot: photo1 482 (sunflower 457, wheat 25), photo2 476 (468/6/2), photo3 touching 324 (sunflower 306, popcorn_corn 10, wheat 6, peanuts 1, pumpkin 1).
Seed box median ~80x82 px (training sunflower median 110x120 px): seeds look smaller than in training.
Tile 1000 -> 558 (sunflower 488, popcorn_corn 64); tile 750 -> 620 (sunflower 490, popcorn_corn 115). Ground truth unknown -> batches of 200 needed.
14:56-15:17 Seed batches, 200 hand-counted whole seeds each (10 groups of 20), bowl tared: B1 = 11 g, B2 = 11 g, B3 = 11 g.
Photos: IMG_4138 B1-40cm, IMG_4139 B1-25cm, IMG_4140 B2-40, IMG_4141 B2-25, IMG_4142 B3-40, IMG_4143 B3-25 (labels read from the notes in the photos).
15:40 Detector tuning on batches (true 200 each). Counting only boxes labelled 'sunflower' is accurate; counting all classes over-counts 5.5-26.5 % because of false boxes on ruler digits and handwritten note.
40 cm, tile 1500, score 0.38, sunflower only: 202, 206, 203 (+1.8 % mean). 25 cm same settings: 203, 203, 202.
Decision: camera height 40 cm (fits more seeds), default detector settings, count = sunflower boxes only.
Cross-check: pilot 25 g / 457 sunflower boxes = 0.0547 g/seed vs batches 11 g / 200 = 0.055 g/seed.
16:20 Photos cropped to the table area (trousers, floor, hand, other objects removed), turned upright, location data removed; not resized. Crop boxes: data/photos/crop_log_2026-10-17.json. The cropped files replace the originals.
Detector on cropped photos (tile 1500, score 0.38): pilot apart 460 (sunflower 452), retake 472 (466), touching 310 (308).
Batches, sunflower boxes: B1-40 205, B2-40 199, B3-40 206, B1-25 206, B2-25 199, B3-25 205 (bias +1.7 %, sd 1.7 %). All boxes: 210, 212, 217, 229, 234, 257.
Before cropping, B2-40 had 6 sunflower boxes on the trousers at the photo edge, and B3-40 had 1 on the phone at the top. Rule: only the table in the photo.
Counts also change by a few seeds when the same photo is stored differently (other tile layout), e.g. B1-40: 202 before, 205 after.

# Main collection (collector: Hadi, Mon 19 Oct 2026, 13:23 to 15:00, daylight, at home)
Piles P01 to P08 done (10 to 24 g in 2 g steps); P09 to P15 not done. Hadi reported that every pile weighed its target weight.
Photos (labels read from the notes): P01 4147/4148, P02 4149/4150, P03 4152/4153, P03-R 4155/4156, P03-T 4157/4158, P04 4159/4160, P05 4163/4164, P06 4165/4166, P07 4167/4168, P08 4169/4170, P08-T 4171/4172, P08-R 4173/4174 (two photos each for R and T).
Most photos were cropped on the phone before upload; 4165/4166 (P06) showed knees at the bottom and were cropped to 86 % of the height. All photos turned upright, location data removed.
Printed ArUco marker (50 mm) found automatically in all 24 photos. Scale ranged from 0.106 to 0.134 mm per pixel per photo, so the camera height varied by about 26 % between the lowest and highest photo (estimate from the scale; the height was not measured). The two markers in one photo differ by up to 3.6 %, a sign of a slightly tilted phone.
Detector (tile 1500, score 0.38), sunflower boxes, main photos: grams per seed 0.0500 to 0.0610, mean 0.0542, relative sd 5.9 % (16 photos). The count falls about 4 % for every +0.01 mm/px (correlation -0.63): photos taken from higher up miss seeds. Example: P01 photo A 185 seeds at 0.108 mm/px, photo B 164 at 0.134 mm/px.
Touching: P03 226/220 vs 278/274 apart; P08 363/364 vs 437/424 apart. Re-spread: P03 272/259, P08 466/446.

Standardised scale test (same day): every photo resized to 0.110 mm per pixel (`tools/measure_scale.py`), then counted again.
Grams per seed relative sd 5.9 % -> 4.2 %, correlation with mm/px +0.63 -> +0.12, mean photo A vs B difference 3.0 % -> 1.6 %.
Resized to 0.135 mm/px instead: 4.8 %, +0.12, 2.5 % (seeds smaller in pixels, more missed). Standard chosen: 0.110 mm/px.
P01 after standardising: 182 / 185 (was 185 / 164). P08: 462 / 467. Counts per photo in analysis/results/2026-10-19_standardisation_counts.csv.
P06 is the largest outlier (0.0574 g per seed): about 7 seeds lying close together visibly not found and 2 sunflower boxes on the handwritten note; this explains only a small part (see the analysis section below).
Decision: stop at 8 piles for now (numbers from the test copies: constant rel. standard error 1.5 % with 8 piles, about 1.1 % with 15; prediction interval about +-10.7 %). Superseded by the analysis section below, where the decision is also reworded.
Hadi confirmed the order for P08: normal photos, then touching, then re-spread.

Phone resolution test (same day): main photos shrunk to 12 MP and 8 MP, counted as they are and after resizing to 0.110 mm/px.
As they are: 12 MP -17.8 % seeds on average (range -33.0 to -7.5 %), 8 MP -42.6 % (-68.1 to -26.1 %), compared with full resolution at 0.110 mm/px.
After resizing to 0.110 mm/px: 12 MP +0.1 % (-1.9 to +2.2 %), 8 MP +0.2 % (-1.7 to +1.7 %). Counts in analysis/results/2026-10-19_megapixel_test_counts.csv.

# Analysis with the fixed scale built in (Mon 19 Oct, evening)
Fixed scale (0.110 mm/px from the markers) built into `detkit predict` and the app. All 33 seed photos counted this way (analysis/results/main_std).
Pilot and batch photos (17 Oct) have no markers: scale ESTIMATED from seed size (median long side of the sunflower boxes 11.25 mm on average, sd 0.17 mm over the 24 main photos): batches at 40 cm 0.095 to 0.101 mm/px, at 25 cm 0.062 to 0.073 mm/px.
Batches at the fixed scale, sunflower boxes: 197, 196, 198, 198, 202, 199 (true 200): mean -0.8 %, sd 1.0 %.
Main photos at the fixed scale: grams per seed 0.0529, rel sd 4.0 %, photo A vs B 1.2 %. Constant crop_count_x_constant 0.05294 g per seed, 95 % bounds +-10.0 % (8 piles, 16 photos), saved with detkit weight calibrate --main-only.
Leave one pile out: mean absolute error 3.3 %, 14 of 16 photos inside their bounds = 7 of 8 piles (both P06 photos outside); with 8 piles this test is weak.
Review of the same day: the +-10.0 % rests on 8 piles; with 15 piles it would be about +-8.8 % and firmer. Whether to add P09 to P15 is open (STATUS_AND_PLAN section 3b).
The analysis was re-run with the exact commands at the top of analysis/build_project.py: identical counts.

# Decision (Mon 19 Oct, evening)
Option (b) chosen: 7 more piles P09 to P15 (26 to 38 g). Jia collects them with Hadi's scale and ruler and her own iPhone 14, after her task 4. Plan and analysis rules in STATUS_AND_PLAN section 4b.

# Jia's weighing (reported Thu 22 Oct, 23:57)
Task 4 and P09 to P11 were weighed in a container (tared). From P12 on Jia weighed the seeds directly on the scale; since then the before and after readings are the same (P12, P13). She thinks the container and its TARE may explain the 2 g difference of T4-02 (14 g before, 12 g after), but cannot confirm it.

# Checks by Jia (Fri 23 Oct)
- Coin test after TARE: one 20 cent coin (5.74 g nominal) reads 6 g; one 50 cent coin (7.80 g nominal) reads 8 g. The scale rounds to the nearest gram; it does not cut off.
- Her printed marker squares measured with a ruler: all 50 mm.
- Original photos of task 4 uploaded to Drive. IMG_2305 was cropped again from its original (no seed cut). The "original" files of P09 to P13 are the same pixels as the cropped ones (no uncropped version exists). In IMG_2302 the cut seed is cut by the edge of the original photo itself.
- P14: two photos taken, but the seeds touch; spread out they would not fit in the photo. Not used for calibration; the app result is in analysis/results/2026-10-23_p14_app_test.
