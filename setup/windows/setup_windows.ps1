# Sets up the CNH grain-weight toolkit on this PC.
# Code + virtual environment go to %USERPROFILE%\cnh_grain (NOT Google Drive: the environment is several GB).
# Our own code changes are copied in from ..\code. A log is written to ..\logs\setup_log.txt.
$ErrorActionPreference = "Continue"
$Assign  = Split-Path -Parent $PSScriptRoot          # ...\03_Assignment
$Home2   = $env:USERPROFILE
$Repo    = Join-Path $Home2 "cnh_grain\manama_data_collection_course"
$LogDir  = Join-Path $Assign "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log     = Join-Path $LogDir "setup_log.txt"
Start-Transcript -Path $Log -Force | Out-Null

function Step($t) { Write-Host ""; Write-Host "==== $t ====" -ForegroundColor Cyan }
# Run a program and copy all its output (also errors) into the window AND the log file
function Run {
    # simple function (no param block): every argument, also "-m" or "--extra", lands in $args unchanged
    $exe = $args[0]
    $rest = @()
    if ($args.Count -gt 1) { $rest = $args[1..($args.Count - 1)] }
    & $exe @rest 2>&1 | ForEach-Object { Write-Host "$_" }
    Write-Host "(exit code $LASTEXITCODE)" }

Step "1. uv (Python package manager)"
$env:Path = "$Home2\.local\bin;$env:Path"
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$Home2\.local\bin;$env:Path"
}
Run uv --version

Step "2. Course code from GitHub"
New-Item -ItemType Directory -Force -Path (Split-Path $Repo) | Out-Null
if (-not (Test-Path (Join-Path $Repo "pyproject.toml"))) {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Run git clone https://github.com/niru-5/manama_data_collection_course.git $Repo
    } else {
        $zip = Join-Path $env:TEMP "manama_course.zip"
        Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/niru-5/manama_data_collection_course/archive/refs/heads/main.zip" -OutFile $zip
        $tmp = Join-Path $env:TEMP "manama_course_unzip"
        if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
        Expand-Archive -Path $zip -DestinationPath $tmp
        Move-Item (Join-Path $tmp "manama_data_collection_course-main") $Repo
    }
} else { Write-Host "already there: $Repo" }

Step "3. Our code (tasks 2 and 3) from Google Drive"
$Code = Join-Path $Assign "code"
if (Test-Path $Code) {
    Get-ChildItem -Path $Code -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($Code.Length + 1)
        $dst = Join-Path $Repo $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
        Copy-Item $_.FullName $dst -Force
        Write-Host "copied $rel"
    }
}

Step "4. Install packages (CPU version, can take 5 to 15 minutes)"
Set-Location $Repo
# torch has no wheels for the newest Python (3.15), so use Python 3.12 (uv downloads it if needed)
$env:UV_PYTHON = "3.12"
$cfg = Join-Path $Repo ".venv\pyvenv.cfg"
if ((Test-Path $cfg) -and -not (Select-String -Path $cfg -Pattern "version_info = 3\.12" -Quiet)) {
    Write-Host "removing the old environment (wrong Python version)"
    Remove-Item -Recurse -Force (Join-Path $Repo ".venv")
}
Run uv python install 3.12
Run uv sync --python 3.12 --extra cpu --extra app --extra dev
$SyncOk = ($LASTEXITCODE -eq 0)

Step "5. Checks"
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { Write-Host "ERROR: no Python environment was created (see step 4 above)." -ForegroundColor Red }
Run $Py -m detkit doctor
Run $Py -m pytest -q
Run $Py -m pytest tests\test_student_tasks.py -q -rs

Step "6. Download the detector model"
$Final = Join-Path $Repo "weights\grain_rfdetr_small_v1\final"
if (-not (Test-Path (Join-Path $Final "model.safetensors"))) {
    Run $Py -c "from huggingface_hub import snapshot_download as s; print(s('niru-5/manama_course_rfdetr_grain_detection', local_dir=r'$Final'))"
}
if (Test-Path $Final) { Get-ChildItem $Final | Format-Table Name, Length | Out-String | Write-Host }

Step "7. Copy of the model to Google Drive (so the analysis can also run in the cloud)"
$ModelCopy = Join-Path $Assign "model\final"
New-Item -ItemType Directory -Force -Path $ModelCopy | Out-Null
if (Test-Path $Final) { Copy-Item (Join-Path $Final "*") $ModelCopy -Recurse -Force }
Get-ChildItem $ModelCopy | Format-Table Name, Length | Out-String | Write-Host

Step "8. Project folder for our sunflower photos"
$W = Join-Path $Repo "runs\sunflower"
if (-not (Test-Path (Join-Path $W "project.json"))) {
    Run $Py -m detkit init --workdir $W --classes corn,peanuts,popcorn_corn,pumpkin,sunflower,wheat --flow cpu --tile 1500 --proposer-ckpt $Final
}

Step "DONE"
Write-Host "Code: $Repo"
Write-Host "Log:  $Log"
Stop-Transcript | Out-Null
Write-Host ""
$ModelOk = Test-Path (Join-Path $Final "model.safetensors")
if ($SyncOk -and $ModelOk) {
    Write-Host "SETUP OK. You can close this window." -ForegroundColor Green
} else {
    Write-Host "SETUP FAILED (packages ok: $SyncOk, model ok: $ModelOk). Send the log in 03_Assignment\logs to Hadi." -ForegroundColor Red
}
Read-Host "Press Enter to close"
