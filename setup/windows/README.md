# Windows setup (used on Hadi's laptop)

`1_SETUP_double_click.bat` runs `setup_windows.ps1`: installs uv and Python 3.12, clones the course code into
`%USERPROFILE%\cnh_grain`, installs the CPU packages, runs the tests, downloads the detector and creates the
project folder. `2_START_APP_double_click.bat` starts the app at http://127.0.0.1:7860.
These scripts were written for a layout where the group code is copied in from a Google Drive folder
(`..\code`); when working from this repository, clone it and run `uv sync` as in the main README instead.
