# Sunflower seeds: data collection procedure (version 1, 17 October 2026)

This is the written procedure of our group (Hadi Nasooti, Jia). It must be complete enough that someone who
was not there can follow it from this text alone: Jia for task 4, and CNH for the demo in task 6.
Based on Jia's Task 1 plan (`Task_1_Sunflower_Data_Collection_Plan`), with the changes found in the pilot of
17 October (see `STATUS_AND_PLAN.md` and `lab_log.md`).

A **sample** (= one pile, `pile_id`) is one portion of seeds that is weighed and photographed.

## Equipment

| Item | What we use | Why it matters |
|---|---|---|
| Scale | Kitchen scale, max 3000 g, steps of 1 g | 1 g steps: piles below 10 g get a large rounding error |
| Bowl | Any bowl or jar | Seeds are weighed in it (after TARE) |
| Background | Plain white matte table or white paper | Dark seeds on white give the best contrast |
| Ruler | Steel ruler (50 cm) | Gives the scale (mm per pixel) in every photo and is used to check the camera height |
| Notes | Small sticky notes + pen | The pile name is written in every photo, so photo and weight can never be mixed up |
| Phone | iPhone, main camera **1x** (not 0.5x or 2x), no flash. Android: main lens 1x, JPEG, no flash, grid or level on if available | Different lenses or zoom change the size of the seeds in pixels |

Phone settings, once: Settings > Camera > Formats > **Most Compatible** (gives JPEG photos; the course
program cannot read Apple's HEIC format). Settings > Camera > **Level** ON (on older iOS: Grid ON). When the
phone points straight down, a white and a yellow crosshair appear; they merge into one yellow crosshair when
the phone is level.

## Rules (each one comes from a measured problem)

1. **Press TARE right before every weighing.** Without it, the scale read 1 g too high (zero drift, coin test).
2. **No seed may touch another seed.** With seeds touching, the detector found one third fewer seeds
   (457 vs 306 sunflower boxes, same 25 g).
3. **Camera straight down at 40 cm**, crosshair yellow. At 40 cm the detector counted 200 hand-counted seeds
   as 202, 206 and 203 (sunflower boxes only).
4. **Ruler and note in the photo, but at least 3 cm away from the seeds.** The detector puts false boxes on
   ruler digits and handwriting; they are labelled as other crops and are not counted (rule 6), but keeping
   them away from the seeds avoids mixing.
5. **All seeds, the ruler and the note inside the photo.**
6. **Only boxes labelled `sunflower` are counted** (model `crop_count_x_constant`). This is done by the
   software, nothing to do by hand.
7. **Keep the seeds as they come**: whole seeds and the small broken hull pieces stay in the sample (a real
   sample from a harvest contains them too). Do not clean the sample.
8. Same light during one session (daylight or room light). If the light changes, write it down.

## Steps for one pile

1. Stir the seed container with your hand.
2. Empty scale: **TARE**. Put the empty bowl on: **TARE** again.
3. Scoop seeds into the bowl until the target weight (main collection: 10 to 38 g in 2 g steps, P01 = 10 g,
   P02 = 12 g, ...; task 4: for example 10, 15, 20, 25, 30 g). Write down: `P01 before = ___ g`.
4. Pour the seeds on the white table and spread them so **no seed touches another**. Keep a compact area.
5. Put the ruler along the bottom edge of the photo area and the note with the pile name (`P01`) at the side, both at least 3 cm
   from the seeds.
6. Check the height once: stand the ruler upright next to the seeds and hold the phone so its back camera
   lens is at the 40 cm mark, measured from the table top.
   Lay the ruler flat again in the same place.
7. **Photo A**: phone straight down at 40 cm, crosshair yellow, everything in the picture.
8. **Photo B**: move the phone away, come back to 40 cm, take the same photo again.
9. Put the empty bowl on the scale, press TARE, then put **all** seeds back into the bowl. Write down:
   `P01 after = ___ g`.
   The `after` weight is the weight we use (the course defines a sample as photographed, then weighed).
   If before and after differ by more than 1 g, a seed was lost or added: write it down.
10. Pour the seeds back into the container.

Extra for piles P03, P08 and P13 (one small, one medium, one large), to measure the effect of how seeds
are spread, and of touching:
- **R photo** (re-spread): after photo B, sweep the seeds together, spread them again in a new way (still
  none touching), change the note to `P03-R`, take one photo.
- **T photo** (touching): push the seeds together so they touch (none on top of another), change the note to
  `P03-T`, take one photo. Then continue with step 9.

## Recording sheet

One line per pile:

| pile_id | target_g | before_g | after_g | photos (file names) | collector | phone | light | remarks |
|---|---|---|---|---|---|---|---|---|

Photo conditions: photos A and B = `main`, R = `re_spread`, T = `touching`.

## From photos to data

1. Create the project once, as in the README quick start (`python -m detkit init --workdir runs/sunflower ...`).
2. In the app (Review tab, *Add an extra property*) add three properties: `condition` (text), `collector`
   (text) and `scale_mm_per_px` (number). Without them, the import silently drops these columns, and the
   touching photos would be treated as normal ones.
3. Import the photos with the weights:
   `python -m detkit import-photos --workdir runs/sunflower --images <folder> --meta weights.csv`
   (`weights.csv`: columns `file, crop, pile_id, total_weight_g, collector, condition, scale_mm_per_px`).
4. `scale_mm_per_px` is measured afterwards by Hadi from the ruler in each photo: a known length on the
   ruler (for example 100 mm) divided by its length in pixels.
5. Open every photo in the app and **save** it. Only saved photos count.

## Limits of this procedure (version 1)

- Largest pile that fits in one photo at 40 cm with all seeds apart: to be confirmed in the main collection
  (the 25 g pilot pile fitted easily, but that photo was taken from somewhat higher than 40 cm; the largest
  planned pile, 38 g, is about 690 seeds at 0.055 g per seed).
- The scale has 1 g steps: a 10 g reading can be up to 0.5 g off (5 %); as a standard uncertainty this is
  1/sqrt(12) = 0.29 g, or 2.9 % of 10 g.
- The camera height is set by hand with the ruler; the real distance can be checked afterwards from the
  ruler length in pixels.
