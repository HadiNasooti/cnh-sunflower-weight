# Datasheet: sunflower seed photos with weights (October 2026)

Structure after "Datasheets for Datasets" (Gebru et al.), shortened to what applies to this small data set.

## Motivation
- **Why was it made?** To estimate the weight of sunflower seeds (with hulls) from one phone photo, using the
  detector of the CNH Data Collection course without retraining it. The data set is used to choose the
  feature (task 2), to measure the uncertainty (task 3) and to check that the procedure can be repeated
  (task 4).
- **Who made it?** Hadi Nasooti and Jia, KU Leuven, Master of AI in Business and Industry, CNH Data
  Collection module, group project.

## Composition
- **What is one item?** One photo of seeds spread on a white table, with the weight of all seeds in the photo
  (`total_weight_g`) and the pile it belongs to (`pile_id`). Several photos of one pile are not independent.
- **How many?** 33 seed photos and 3 other photos (jar and scale) on 17 and 19 Oct 2026:

| Folder | Photos | Content |
|---|---|---|
| `2026-10-17_pilot` | 6 | 3 seed photos of one 25 g pilot pile (apart, again, touching) plus 3 photos of the jar and scale |
| `2026-10-17_batches` | 6 | 3 batches of exactly 200 hand-counted seeds (11 g each), each at 40 cm and 25 cm |
| `2026-10-19_main` | 24 | 8 piles of 10 to 24 g (2 g steps), photos A and B each; plus re-spread and touching photos for P03 and P08 |

- **Labels:** weight from a kitchen scale (1 g steps); hand count for the batches only (`manual_count`). No
  boxes were drawn by hand: seed boxes come from the detector.
- **Extra fields:** `condition` (main, pilot, batch, re_spread, touching), collector, camera height, phone,
  remarks; `scale_mm_per_px` per photo in each folder's `scale.csv`: measured from the printed markers for
  the main collection, ESTIMATED from the seed size for the pilot and batch photos (no markers; column
  `scale_source` says so).
- **Known gaps:** one seed lot (one bag), one white table, one person and one phone so far, daylight only;
  no piles above 25 g; the pilot and batch photos have a ruler, not the marker sheet, so their scale was not
  measured automatically.
- **Sensitive data:** none. People, floor and other objects were cropped out; location data was removed.

## Collection process
- Written procedure: `docs/group/PROCEDURE.md`. 17 Oct: version 1 (ruler and pile note in the photo).
  19 Oct: version 1 with the printed marker sheet added and the pile note still in the photo; this is why
  version 2 (written after 19 Oct) takes the note out of the seed photos.
- Phone: iPhone 15 Pro, main camera 1x, JPEG, about 40 cm above the table, no flash, daylight.
- Weighing: TARE before every weighing; the pile is weighed in a bowl. Main collection: weights reported
  by the collector as equal to the target weight; the written before and after readings are still to be
  added.
- Full record with times and checks: `docs/group/lab_log.md`; measurements without photos (scale checks,
  repeated weighings, batches): `lab_measurements.json`.

## Preprocessing
- Photos turned upright and cropped to the table (crop boxes in `photos/crop_log_2026-10-17.json` for
  17 Oct; P06 photos IMG_4165 and IMG_4166 cropped to 86 % of the height to remove knees). Not resized.
- Before detection, the program resizes each photo to 0.110 mm per pixel using the markers
  (`detkit/scale.py`); the stored photos stay as taken.

## Uses
- Fits for: seeds spread on a white background, none touching, 10 to 24 g per photo, photographed from
  above with the marker sheet.
- Not for: piles where seeds overlap, other crops or varieties, other backgrounds, or claims about the
  detector's accuracy in general.

## Distribution and maintenance
- Kept in the private GitHub repository `HadiNasooti/cnh-sunflower-weight`, shared with the course
  team on request. New sessions are added as new folders `photos/<date>_<what>/` with lines in `samples.csv`.
