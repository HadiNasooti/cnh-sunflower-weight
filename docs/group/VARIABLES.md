# Everything that can make the weight wrong, and how we handle it (22 October 2026)

Group: Hadi Nasooti, Jia. Crop: sunflower seeds with hulls. Method: weight = number of seeds the detector
finds x grams per seed. Since 22 Oct the app uses all 17 piles: 0.05336 g per seed and a 95 % bound of +-8.7 %
with the marker sheet; without a marker the seeds are the ruler: 0.05385 g per seed and +-9.4 % (before: Hadi's
8 piles, 0.05294 g and +-10.0 %).

All numbers come from our own photos and weighings, computed by `analysis/results_2026_10_22.py` and
`analysis/business_case.py` (tables in `analysis/results/2026-10-22_analysis/`). Older numbers (17 and 19 Oct)
are in `STATUS_AND_PLAN.md` sections 3 to 3c. "Not tested" means we have no measurement.

Words used:
- **Fixed scale**: the program finds the two printed markers (50 mm squares), measures how many mm one pixel
  is, and resizes every photo to 0.110 mm per pixel before counting. So every photo looks the same to the
  detector, whatever the phone or the height.
- **Gauge R&R** (repeatability and reproducibility): one pile that is not touched, photographed 17 times by
  2 persons, with 2 phones, at 2 heights (16 photos have both markers; IMG_2261 has none). It shows how much
  the photo alone changes the count. It does not test how a person spreads the seeds; task 4 does that.
- **95 % CI** (confidence interval): the range in which the true value lies with 95 % certainty, given our data.
  A CI that includes 0 means "no difference found", but a difference up to the edge of the CI is still possible.
- **p** (p-value): a high p (above 0.05) means the difference could easily be chance.
- **Root mean square**: a kind of average size of an error.
- **Bound**: the 95 % range around the predicted weight; about 19 of 20 true weights should fall inside it.
- **TARE**: the scale button that sets the display to 0.
- **P** = handled in the procedure (what the user does), **PRE** = by the program before counting,
  **POST** = by the program after counting.
- Percentages are relative: 1 % of a 20 g pile is 0.2 g.

## The table

| # | Variable | Effect (what goes wrong) | How we measured it | Our number | How we handle it | What the user sees |
|---|---|---|---|---|---|---|
| 1 | Camera height | Higher photo = smaller seeds in pixels = the detector misses seeds | Gauge R&R: same pile, "normal" and "high" photos, counted with and without the fixed scale | Without fixed scale: 112 to 292 seeds for the same pile (spread 18.6 %). With it: 283 to 298 (spread 1.2 %); high minus normal 0.0 % (95 % CI -1.3 to +1.3 %) | PRE: fixed scale | Nothing: any height works as long as all seeds and both markers are in the photo |
| 2 | Phone resolution (megapixels) | Fewer pixels per seed = missed seeds | 19 Oct: Hadi's photos saved again at 12 MP and 8 MP; 22 Oct: Jia's 12 MP photos | Without fixed scale: 12 MP -17.8 %, 8 MP -42.6 % (19 Oct); Jia's iPhone 14 photos -10 to -14 % on average; the same pile in the Gauge R&R down to -61 % (IMG_2268, iPhone 14, high). With fixed scale: within about 2 % | PRE: fixed scale | Nothing |
| 3 | Phone model and its colours | Different camera processing | Gauge R&R: iPhone 14 versus iPhone 15 Pro on the same pile | +0.3 % (95 % CI -1.1 to +1.7 %): no effect found | Nothing needed | Nothing |
| 4 | Person who spreads, photographs and weighs | Different habits | (a) Gauge R&R, same pile; (b) task 4: Jia repeated the procedure on 4 new piles, plus 5 bigger piles | (a) Jia minus Hadi 0.0 % (95 % CI -1.4 to +1.5 %); (b) Jia's grams per seed +1.5 % (95 % CI -2.7 to +5.7 %); all 9 of Jia's piles inside Hadi's +-10 % bounds | P: written procedure (PROCEDURE.md) | The 5 steps on the screen |
| 5 | Phone tilted (not straight down) | One side of the photo looks smaller | The two markers should be the same size; we compare them in every photo where both are found (48 of 59) | 47 of those 48 photos: markers differ 3.7 % or less. IMG_4183 (Gauge R&R): 9.5 %, count 283 against 289.5 average (-2.2 %) | P: phone level; POST: warning above 5 % | Orange: "Phone tilted: hold it flat" |
| 6 | Marker cut by the photo edge | No scale: back to row 1 and 2 | IMG_2261 (Gauge R&R): both markers touch the edge | No marker found: -12.6 %. With the seeds as the ruler (since 22 Oct): +1.5 % | POST: no marker, so the app uses the seeds as the ruler (range +-9.4 % instead of +-8.7 %) | Orange: "No marker found: the size was estimated from the seeds, so the range is wider. Put the marker sheet fully in the photo for a more precise result." |
| 6b | Only one of the two markers found | Scale from one marker only; tilt cannot be checked | Counted in all 59 photos | One marker found in 10 good photos (for example IMG_4147, IMG_2304): the 9 with a weight are all inside the bounds, the 10th (IMG_2263, Gauge R&R) is +0.9 % from the average: no effect shown | PRE: one marker is enough for the scale | Nothing |
| 7 | Seeds touching | Two touching seeds look like one; seeds hidden | 19 Oct: same piles pushed together (T photos); 17 Oct pilot | 16 to 19 % fewer seeds (19 Oct), 32 % (pilot). Boxes that overlap another box: 42 to 51 % in touching photos, 17 % or less in all normal photos | P: no seed touches another; POST: overlap check (proposed) | Orange: "Seeds too close: spread them out" |
| 8 | Seeds close but not touching | Some missed | P06 (19 Oct), the pile with the densest spread | About 2 % missed; P06 error -7.5 % (inside the bound in the fit, but outside it when P06 is left out of the fit, 19 Oct) | Part of the spread in the bound | Nothing (covered by the bound) |
| 9 | Size of the sample | Pile does not fit in one photo, or seeds start to touch | Piles from 10 to 34 g (17 piles), up to 651 seeds in one photo | No trend: grams per seed changes +0.2 % per 10 g (p = 0.87). Jia reported that P14 (36 g) did not fit at the height she used (not recorded in the data) | P: if the app says "too many seeds", split the sample in two photos and add the weights; POST: count check (proposed) | Orange above 651 seeds: "More seeds than we tested: split the sample" |
| 10 | Other objects in the photo (notes, ruler, pen, hands) | False seed boxes | 22 Oct: sticky notes in task 4 and Gauge R&R photos; 17 Oct: ruler and writing | Notes: 0 to 6 seed boxes on the note per photo (up to 2 % of the count), now removed. Ruler and writing: +5.0 to +28.5 % when all box classes are counted, -0.5 to +3.0 % when only sunflower boxes are counted (17 Oct) | PRE/POST: count sunflower boxes only, drop boxes on a known note; P: nothing else in the photo; POST: object check (proposed) | Orange: "Something else is in the photo: remove it" |
| 11 | Shadows | Darker background, less contrast | Shadows on P10, P11, P13 (Jia) and a strong shadow of the photographer on IMG_4179 (Gauge R&R) | P10, P11, P13 errors -2.3, +2.0, +0.7 %; IMG_4179: 294 seeds against 289.5 average (+1.6 %): within the normal spread, no effect shown | P: do not stand between the lamp and the seeds; POST: shadow check (proposed) | Orange: "Shadow on the seeds: change position" |
| 12 | Light colour (warm or cold) | Colours change | Gauge R&R: Hadi's phone gives warmer colours | Included in row 3: +0.3 % | Nothing needed (one test) | Nothing |
| 13 | User crops the photo | Seeds at the cut edge are halved or lost | Jia's own crops of task 4 and P09 to P13, checked one by one | 8 seeds cut in 4 photos (1 % or less per photo) | P: never crop, the program ignores the rest | Nothing to do |
| 14 | Photo turned (portrait or landscape) | None expected | P10 (landscape) and IMG_4179 (phone turned 90 degrees) | P10 -2.3 %; IMG_4179 +1.6 %: no effect shown | Nothing needed | Nothing |
| 15 | Saved or shared at lower size (for example sent by chat) | Fewer pixels, as row 2 | IMG_2285 is a smaller copy (1782 pixels wide) | Count 238 against 235 for its pair: fixed scale handles it | PRE: fixed scale | Nothing |
| 16 | Background colour | Less contrast | Not tested (white only) | None | P: white paper or white table | "Use white paper" in the steps |
| 17 | Blur (moved phone, out of focus) | Edges unclear, seeds missed | Not tested (no blurred photo in our data) | None yet; to measure by blurring our own photos on purpose (proposed) | POST: sharpness check (proposed) | Orange: "Photo not sharp: hold still and take it again" |
| 18 | Photo format (iPhone HEIC) | The program cannot read it | Found on 17 Oct | Not a number: the file is refused | P: iPhone setting "Most Compatible" (JPEG) | Error message on upload |
| 19 | Lens or zoom (0.5x, 2x) | Other distortion | Not tested | None | P: main camera 1x | "Use the normal 1x camera" |
| 20 | Kitchen scale with 1 g steps | Reading up to 0.5 g off | Calculated: 1/sqrt(12) g per reading, on our 17 piles | 1.7 % (root mean square); 2.9 % at 10 g, 0.8 % at 34 g | P: piles of 10 g or more; press TARE | Not for the user (only for calibration) |
| 21 | TARE missed, seed lost or added between weighings | Wrong reference weight | Jia wrote a weight before and after the photos | Before and after differ in 5 of 9 of Jia's piles. 4 differ by 1 g, which the 1 g scale step can explain. T4-02 went from 14 to 12 g: rounding cannot explain 2 g, so something really changed (cause asked to Jia); the photo (12.5 g) fits the 12 g after weight | P: TARE every time, weigh before and after, write a gap above 1 g | Not for the user |
| 22 | Seed-to-seed weight, broken hulls | One seed is not always 0.053 g | NOT measured directly: it is what is left after the scale and the photo are taken out of the total | 3.45 % remainder (of the total 3.97 % spread between piles); it also holds detector and weighing errors we cannot separate | Bound covers it; calibrate again for a new seed lot | Not for the user |
| 23 | Seed lot or variety, moisture | Different grams per seed | Not tested (one bag) | None | Calibrate again for each new lot (about 10 piles, see the business case) | Not for the user |
| 24 | Photo-to-photo noise (same pile, photo again) | Count changes a little | Gauge R&R, two photos in the same setup | 1.3 % for one photo (3.8 seeds; 95 % CI 2.6 to 7.3 seeds) | Use 2 photos per pile for calibration | Nothing |
| 25 | Detector settings | Different count | 17 Oct: several tile and score settings | Spread of the error 0.8 to 1.8 % for every setting; with 3 batches the settings cannot be told apart | Fixed and saved with the model | Nothing |
| 26 | Recording errors (pile names, files) | Wrong weight linked to a photo | Found on 22 Oct | Pile names P01 to P04 used twice (renamed T4-01 to T4-04) | Unique names, label photo, one line per photo in samples.csv | Not for the user |
| 27 | Marker sheet printed at the wrong size ("fit to page") or curled | The scale is wrong by the same %, so the count changes | Not tested | None | P: print at 100 %, check that the 100 mm line on the sheet measures 100 mm, keep it flat | "Print at 100 %" in the steps |
| 28 | Seeds on or against a marker | Marker not found, or a seed not counted | Not tested (we kept 3 cm free) | None | P: keep 3 cm between seeds and markers; POST: the "no marker" and "one marker" checks catch a hidden marker | Red or orange marker message |
| 29 | Outdoor light, sun, glare on the markers | Marker not found, strong shadows | Not tested (indoor only) | None | P: indoor light | Red "No marker found" if it fails |
| 30 | Lens distortion at the photo edges | Seeds at the edge look a little smaller | Not tested separately; part of the Gauge R&R (seeds at different places in the photo) | Included in the 1.2 % Gauge R&R spread | Nothing needed so far | Nothing |
| 31 | Dust, empty hull pieces, other material counted as seeds | Count too high | Not tested separately; broken hull pieces stay in our samples on purpose (PROCEDURE rule 7) | Part of the 3.45 % remainder | P: sample as it comes; calibration includes the same kind of material | Nothing |

## What is left of the error (error budget)

Spread of grams per seed between our 17 piles: 3.97 %. Of this, the scale step is 1.73 % (calculated) and the
photo (mean of 2 photos) 0.93 % (measured in the Gauge R&R). What is left, 3.45 %, is a remainder found by
subtraction, not a measurement: the seed weight itself plus detector and weighing errors we cannot separate.
Parts add as squares: 3.97^2 = 1.73^2 + 0.93^2 + 3.45^2. To check the remainder independently we would need to
weigh single seeds or count piles by hand (on 17 Oct, 3 hand-counted batches of 200 seeds all weighed 11 g,
which a 1 g scale cannot split further).

The bound is checked against a kitchen scale, not against the true weight. Part of it (the 1 g scale step) is
error in our reference, not in the photo method. Without the scale step the bound would be about +-7.8 %
instead of +-8.7 % with 17 piles (estimate: 3.97 % with the 1.73 % taken out).

So the photo is no longer the main error. To make the bound smaller, the money should go to a better scale
and to knowing the seed lot, not to more photos.

## Limits

One seed lot, one white table, indoor light, two iPhones, two persons, 10 to 34 g per photo. Android phones,
other varieties, other backgrounds and blurred photos are not tested. The heights in the Gauge R&R are
"normal" or "high" as written on the sticky note, not measured with a ruler.
