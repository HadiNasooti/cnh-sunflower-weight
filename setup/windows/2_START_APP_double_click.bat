@echo off
rem Starts the course app. Open http://127.0.0.1:7860 in your browser. Close this window to stop it.
set REPO=%USERPROFILE%\cnh_grain\manama_data_collection_course
cd /d "%REPO%"
start "" http://127.0.0.1:7860
".venv\Scripts\python.exe" -m detkit app --workdir runs\sunflower --ckpt weights\grain_rfdetr_small_v1\final
pause
