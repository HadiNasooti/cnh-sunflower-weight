# Data

What the data set is, how it was made and what it can be used for: [`DATASHEET.md`](DATASHEET.md).

All photos are the phone's JPEG files, cropped to the table area (people, floor and other objects around the
table removed), turned upright, and saved without location data. They are **not resized**: the detector
result depends on the number of pixels per seed. The crop box of every 17 Oct photo is in
`photos/crop_log_2026-10-17.json` (the 19 Oct photos were cropped on the phone; IMG_4165 and IMG_4166 also to 86 % of the height). One folder per collection session.

| Folder | What |
|---|---|
| `photos/2026-10-17_pilot/` | Pilot. IMG_4128 = jar with 150 g set aside for task 4; IMG_4129 / IMG_4130 = pilot pile on the scale (20 g, then topped up to 25 g); IMG_4131 to IMG_4133 = pilot photos (see `samples.csv`) |
| `photos/2026-10-17_batches/` | 3 batches of 200 hand-counted seeds, each at 40 cm and 25 cm |
| `photos/2026-10-19_main/` | Main collection: piles P01 to P08 (10 to 24 g), photos A and B, plus re-spread and touching photos for P03 and P08. `scale.csv` = mm per pixel measured from the two printed markers in each photo |

- `samples.csv`: one line per seed photo: pile, weight, hand count, condition, camera height, remarks.
  `condition`: `main` (main collection, used to fit the models), `pilot`, `touching`, `re_spread`, `batch`
  (hand-counted, used to measure the detector error).
- `lab_measurements.json`: measurements that are not photos (scale checks, repeated weighings, seed batches),
  read by `analysis/sunflower_analysis.py --lab`.
- The full time-stamped record is in `docs/group/lab_log.md`.

To add photos: put them in a new folder `photos/<date>_<what>/` and add one line per photo to
`samples.csv`. On the GitHub website: *Add file* > *Upload files* (each file at most 25 MiB).
