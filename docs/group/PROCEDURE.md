# Sunflower seeds: data collection procedure (version 3, 22 October 2026)

This is the written procedure of our group (Hadi Nasooti, Jia). It must be complete enough that someone who
was not there can follow it from this text alone: Jia for task 4, and CNH for the demo in task 6.
Based on Jia's Task 1 plan (`Task_1_Sunflower_Data_Collection_Plan`), with the changes found in the pilot of
17 October and the main collection of 19 October (see `STATUS_AND_PLAN.md` and `lab_log.md`).

**Changes from version 1 (17 Oct):** the printed marker sheet replaces the ruler as the scale reference, and
the program measures the scale itself; the pile name note is photographed separately and is not in the seed
photos; the tested range is 10 to 24 g per photo; a bigger sample is split into portions.

**Changes in version 3 (22 Oct):** never crop a photo (Jia's crops cut seeds at the edge); both markers must be
fully in the photo (IMG_2261 had both cut by the edge); tested range now 10 to 34 g per photo (up to 651 seeds);
the app gives every photo a light with a sentence, uses the seeds as the ruler when no marker is found, and
uses the constants of all 17 piles.

A **sample** (= one pile, `pile_id`) is one portion of seeds that is weighed and photographed.

## Equipment

| Item | What we use | Why it matters |
|---|---|---|
| Scale | Kitchen scale, max 3000 g, steps of 1 g | 1 g steps: piles below 10 g get a large rounding error |
| Bowl | Any bowl or jar | Seeds are weighed in it (after TARE) |
| Background | Plain white matte table or white paper | Dark seeds on white give the best contrast |
| Marker sheet | `marker_sheet_A4.pdf`, printed at 100 % (no "fit to page") | Two square markers of 50 mm: the program measures mm per pixel from them in every photo |
| Ruler or tape measure | Any, at least 40 cm | Only to check the camera height |
| Notes | Small sticky note + pen | The pile name, photographed before the seed photos |
| Phone | iPhone or Android, main camera **1x** (not 0.5x or 2x), no flash | Other lenses or zoom change the picture geometry |

Check the printed marker sheet once: the 100 mm line on the sheet must measure 100 mm with the ruler. If not,
print it again at 100 %.

Phone settings, once:
- iPhone: Settings > Camera > Formats > **Most Compatible** (gives JPEG photos; the program cannot read
  Apple's HEIC format). Settings > Camera > **Level** ON (on older iOS: Grid ON). When the phone points
  straight down, a white and a yellow crosshair appear; they merge into one yellow crosshair when the phone
  is level.
- Android: camera in JPEG (not RAW or HEIF), main lens 1x, grid or level on if available.

## Rules (each one comes from a measured problem)

1. **Press TARE right before every weighing.** Without it, the scale read 1 g too high (zero drift, coin test).
2. **No seed may touch another seed.** With seeds touching, the detector found 17 to 36 % fewer seeds (main
   collection and pilot, at the fixed scale).
3. **At most 24 g of seeds per photo.** That is the range we tested (10 to 24 g). A bigger sample is split
   into portions of 10 to 24 g; each portion is weighed and photographed on its own, and the weights are added.
4. **Marker sheet in every photo, flat, fully visible, at least 3 cm from the seeds.** The program needs the
   markers to fix the scale. Without them the count depends on the phone and the height: on 12 MP photos
   the detector found 18 % fewer seeds on average than on the full-resolution photo without the fixed
   scale, and stayed within about 2 % of it with the fixed scale.
5. **Camera straight down at about 40 cm**, crosshair yellow. The program corrects small height differences,
   but a tilted phone makes one side of the photo smaller than the other.
6. **Only the white background, the seeds and the marker sheet in the photo**: no note, no hands, feet,
   clothes, phones or other objects. The detector put false seed boxes on trousers and on handwriting.
7. **Keep the seeds as they come**: whole seeds and the small broken hull pieces stay in the sample (a real
   sample from a harvest contains them too). Do not clean the sample.
8. Same light during one session (daylight or room light). If the light changes, write it down.

## Steps for one pile

1. Stir the seed container with your hand.
2. Empty scale: **TARE**. Put the empty bowl on: **TARE** again.
3. Scoop seeds into the bowl until the target weight (for example 10, 14, 18, 22 g). Write down:
   `P01 before = ___ g`.
4. Pour the seeds on the white background and spread them so **no seed touches another**. Keep a compact
   area.
5. Lay the marker sheet flat next to the seeds, at least 3 cm away.
6. **Label photo**: write the pile name (`P01`) on the note, put it on the table and take one photo of the
   note only. Then take the note away. (The photo order now tells which seed photos belong to which pile.)
7. Check the height once per session: stand the ruler upright next to the seeds and hold the phone so its
   back camera lens is at the 40 cm mark, measured from the table top.
8. **Photo A**: phone straight down at about 40 cm, crosshair yellow, all seeds and both markers in the
   picture, nothing else.
9. **Photo B**: move the phone away, come back to 40 cm, take the same photo again.
10. Put the empty bowl on the scale, press TARE, then put **all** seeds back into the bowl. Write down:
    `P01 after = ___ g`. The `after` weight is the weight we use (the course defines a sample as photographed,
    then weighed). If before and after differ by more than 1 g, a seed was lost or added: write it down.
11. Pour the seeds back into the container.

Optional experiments (we did them for P03 and P08):
- **R photo** (re-spread): after photo B, sweep the seeds together, spread them again in a new way (still
  none touching), take one photo.
- **T photo** (touching): push the seeds together so they touch (none on top of another), take one photo.
  Then continue with step 10.

## Recording sheet

One line per pile:

| pile_id | target_g | before_g | after_g | photos (file names) | collector | phone | light | remarks |
|---|---|---|---|---|---|---|---|---|

Photo conditions: photos A and B = `main`, R = `re_spread`, T = `touching`.

## From photos to weight (the app)

1. Start the app (on Hadi's laptop: `2_START_APP_double_click.bat`) and open the **Inference** tab.
2. Upload the photos. Optionally fill in the crop (`sunflower`) and the measured weight per photo.
3. Keep **Fixed scale from the marker sheet** ticked (0.110 mm per pixel) and the weight model
   `crop_count_x_constant`. Tile 1500, score 0.38. The instructions for the photo are shown at the top.
4. Press **Run inference**. Each row shows a **light** and a **message**, then the weight with `low_g` and
   `high_g` (95 % range) and `range_pct`:
   - green: good photo; range +-8.7 % with the markers;
   - orange: the weight is shown, the message says what to change (seeds too close together, phone tilted,
     more seeds than tested, too few seeds, or no marker). Without a marker the seeds are used as the ruler
     (`scale_from` = seeds) and the range is +-9.4 %;
   - red: no weight (no seeds found, or no marker and the seed size of the crop is not known).
   Limits come from our 59 photos (`analysis/validate_light.py`: all 53 normal photos green, the 6 known
   problem photos orange).
5. For several photos of one sample (portions, rule 3): add the weights of the portions.

To add photos to the data set for analysis: put them in `data/photos/<date>_<what>/`, add one line per photo
to `data/samples.csv`, and run `analysis/build_project.py` (see the top of that file).

## Limits of this procedure (version 3)

- Tested for 10 to 34 g per photo (17 piles, Hadi and Jia, iPhone 15 Pro and iPhone 14), one seed lot (one bag), one white table, daylight, one phone (iPhone 15 Pro; 12 MP and 8 MP
  copies of its photos were also tested). Jia's task 4 photos (iPhone 14) are the first test with another
  phone and person. Other
  varieties, other backgrounds or seeds lying on top of each other are not covered.
- The scale has 1 g steps: a 10 g reading can be up to 0.5 g off (5 %); as a standard uncertainty this is
  1/sqrt(12) = 0.29 g, or 2.9 % of 10 g.
- The detector misses some seeds that lie close together even when they do not touch. This is part of the
  pile-to-pile spread that the 95 % interval covers.
- The 95 % interval was measured with one seed lot, one person and one phone. Another person or phone (task 4,
  Gauge R&R) or another seed lot can add error that the interval does not include yet.
