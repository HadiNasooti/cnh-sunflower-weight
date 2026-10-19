# Windows setup (used on Hadi's laptop)

`1_SETUP_double_click.bat` runs `setup_windows.ps1`: installs uv and Python 3.12, clones the course code into
`%USERPROFILE%\cnh_grain`, installs the CPU packages, runs the tests, downloads the detector and creates the
project folder. `2_START_APP_double_click.bat` starts the app at http://127.0.0.1:7860.
These scripts were written for a layout where the group code is copied in from a Google Drive folder
(`..\code`); when working from this repository, clone it and run `uv sync` as in the main README instead.

`3_UPDATE_double_click.bat` runs `update_windows.ps1`: copies the newest group code (from `code_update.zip` next to the script if present, else from `..\code`) into the
install, puts the calibrated `weight_config.json` (copy of `analysis/results/main_std/weight_config.json`) into
`runs\sunflower` (the old one is kept as `weight_config_before_update.json`) and runs the tests.
