@echo off
echo Updating the CNH sunflower toolkit with the latest code. This takes about 1 minute.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update_windows.ps1"
