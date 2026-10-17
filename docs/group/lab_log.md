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
14:20 Detector (tile 1500, score 0.38) on pilot: photo1 482 (sunflower 457, wheat 25), photo2 476 (468/6/2), photo3 touching 324 (306 ...).
Seed box median ~80x82 px (training sunflower median 110x120 px): seeds look smaller than in training.
Tile 1000 -> 558 (sunflower 488, popcorn_corn 64); tile 750 -> 620 (sunflower 490, popcorn_corn 115). Ground truth unknown -> batches of 200 needed.
14:56-15:17 Seed batches, 200 hand-counted whole seeds each (10 groups of 20), bowl tared: B1 = 11 g, B2 = 11 g, B3 = 11 g.
Photos: IMG_4138 B1-40cm, IMG_4139 B1-25cm, IMG_4140 B2-40, IMG_4141 B2-25, IMG_4142 B3-40, IMG_4143 B3-25 (labels read from the notes in the photos).
15:40 Detector tuning on batches (true 200 each). Counting only boxes labelled 'sunflower' is accurate; counting all classes over-counts 5.5-26.5 % because of false boxes on ruler digits and handwritten note.
40 cm, tile 1500, score 0.38, sunflower only: 202, 206, 203 (+1.8 % mean). 25 cm same settings: 203, 203, 202.
Decision: camera height 40 cm (fits more seeds), default detector settings, count = sunflower boxes only.
Cross-check: pilot 25 g / 457 sunflower boxes = 0.0547 g/seed vs batches 11 g / 200 = 0.055 g/seed.
