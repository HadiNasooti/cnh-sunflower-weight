# Sunflower: tasks 2 and 3 results

Boxes from: predictions. Sunflower photos: 33; main-collection photos with a weight: 16.

## Task 2: which feature tells the weight

Pile level (photos of one pile averaged). r = Pearson correlation with the weight, CI = 95 % cluster bootstrap over piles. ratio spread = relative sd of weight / feature over piles: the error a feature x constant model would make.

| feature | piles | r | r 95 % CI | weight/feature | ratio spread |
|---|---|---|---|---|---|
| count | 8 | 0.990 | 0.950 .. 0.999 | 0.05226 | 3.7 % |
| count_sunflower | 8 | 0.989 | 0.945 .. 0.999 | 0.05294 | 4.0 % |
| total_area_mm2 | 8 | 0.985 | 0.937 .. 0.999 | 0.0007025 | 5.1 % |
| area_mm2_sunflower | 8 | 0.985 | 0.930 .. 0.999 | 0.0007144 | 5.4 % |
| total_area_px | 8 | 0.902 | 0.629 .. 0.989 | 9.743e-06 | 11.5 % |
| area_px_sunflower | 8 | 0.900 | 0.635 .. 0.990 | 9.908e-06 | 11.6 % |
| mean_area_mm2 | 8 | 0.463 | -0.366 .. 0.932 | 0.2278 | 27.8 % |
| mean_diag_px | 8 | -0.212 | -0.976 .. 0.781 | 0.1529 | 31.6 % |
| mean_area_px | 8 | -0.271 | -0.984 .. 0.753 | 0.003193 | 35.7 % |
| median_area_px | 8 | -0.330 | -0.969 .. 0.745 | 0.003213 | 35.8 % |

### How many piles do we need

**count_sunflower**: spread of the fitted constant (weight / count_sunflower) over bootstrap draws of n piles (with replacement).

| n piles | constant mean | constant rel. sd | r mean | r 2.5 % |
|---|---|---|---|---|
| 3 | 0.05291 | 2.2 % | 0.951 | 0.809 |
| 4 | 0.05286 | 1.9 % | 0.980 | 0.908 |
| 5 | 0.05295 | 1.6 % | 0.987 | 0.937 |
| 6 | 0.05297 | 1.5 % | 0.986 | 0.939 |
| 7 | 0.05294 | 1.4 % | 0.986 | 0.950 |
| 8 | 0.053 | 1.3 % | 0.987 | 0.948 |

**area_mm2_sunflower**: spread of the fitted constant (weight / area_mm2_sunflower) over bootstrap draws of n piles (with replacement).

| n piles | constant mean | constant rel. sd | r mean | r 2.5 % |
|---|---|---|---|---|
| 3 | 0.0007136 | 2.9 % | 0.950 | 0.836 |
| 4 | 0.0007132 | 2.5 % | 0.979 | 0.912 |
| 5 | 0.000715 | 2.1 % | 0.984 | 0.925 |
| 6 | 0.0007151 | 2.0 % | 0.983 | 0.936 |
| 7 | 0.0007146 | 1.9 % | 0.982 | 0.934 |
| 8 | 0.0007154 | 1.8 % | 0.982 | 0.939 |

### How many photos of the same pile

| feature | piles with repeats | photo-to-photo spread (same pile) | pile-to-pile spread of weight/feature |
|---|---|---|---|
| count_sunflower | 8 | 1.0 % | 4.0 % |
| area_mm2_sunflower | 8 | 2.1 % | 5.1 % |

(These two columns use the main AND the re-spread photos, so the pile-to-pile spread can differ a little from the feature table above, which uses the main photos only.)

## Calibrated models

**crop_count_x_constant**: constant 0.0529394 g/kernel; 95 % bounds +/- 10.0 % (8 piles).
* on the photos it was fitted on: MAPE 2.9 %, bias 0.040 g (optimistic)
* leave-one-pile-out: MAPE 3.3 %, bias 0.046 g, held-out photos inside their bounds 87.5 %

**crop_area_mm2_x_constant**: constant 0.000714438 g/mm^2; 95 % bounds +/- 13.6 % (8 piles).
* on the photos it was fitted on: MAPE 4.2 %, bias 0.121 g (optimistic)
* leave-one-pile-out: MAPE 4.8 %, bias 0.138 g, held-out photos inside their bounds 93.8 %

**count_x_constant**: constant 0.0522585 g/kernel; 95 % bounds +/- 9.4 % (8 piles).
* on the photos it was fitted on: MAPE 2.9 %, bias 0.023 g (optimistic)
* leave-one-pile-out: MAPE 3.2 %, bias 0.027 g, held-out photos inside their bounds 87.5 %

**area_x_constant**: constant 9.74297e-06 g/px^2; 95 % bounds +/- 42.6 % (8 piles).
* on the photos it was fitted on: MAPE 13.5 %, bias 0.080 g (optimistic)
* leave-one-pile-out: MAPE 14.6 %, bias 0.091 g, held-out photos inside their bounds 93.8 %

## Task 3: error budget

**crop_count_x_constant** (at the mean pile weight 17.0 g)

| stage | relative error | share of variance | how measured |
|---|---|---|---|
| balance | 1.7 % | 18.2 % | max(rounding 0.289 g, repeat sd 0.000 g) / mean main weight 17.0 g |
| detector | 1.0 % | 6.7 % | sd of (count - hand count) / hand count on 6 photos (mean bias -0.8 %, absorbed by the calibration) |
| unexplained | 3.4 % | 75.1 % | sqrt(top-down^2 - sum of the stages above^2). Possible causes, NOT measured: seed-to-seed weight variation (kernel_weight: not measurable), seeds lying close together missed by the detector, differences in seed mix between piles |
| kernel_weight | not measurable | - | 3 batches of ~200 seeds all read 11, 11, 11 g on a 1 g scale: their spread is below what the scale can show |

Total (root sum of squares, incl. 'unexplained' if present): 4.0 % (+/- 0.68 g, 1 sd). Dominant stage: unexplained.
Top-down (spread of weight/feature over the main photos): 4.0 %.

**crop_area_mm2_x_constant** (at the mean pile weight 17.0 g)

| stage | relative error | share of variance | how measured |
|---|---|---|---|
| balance | 1.7 % | 9.7 % | max(rounding 0.289 g, repeat sd 0.000 g) / mean main weight 17.0 g |
| photo | 2.1 % | 15.5 % | photo-to-photo spread of area_mm2_sunflower within a pile (8 piles) |
| scale | 2.3 % | 17.6 % | 2 x relative error of the scale from the markers (lab: scale_read_rel) |
| unexplained | 4.1 % | 57.2 % | sqrt(top-down^2 - sum of the stages above^2). Possible causes, NOT measured: seed-to-seed weight variation (kernel_weight: not measurable), seeds lying close together missed by the detector, differences in seed mix between piles |

Total (root sum of squares, incl. 'unexplained' if present): 5.4 % (+/- 0.92 g, 1 sd). Dominant stage: unexplained.
Top-down (spread of weight/feature over the main photos): 5.4 %.
