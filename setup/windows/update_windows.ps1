# Updates the CNH sunflower toolkit on this PC with the newest code of our group repository.
# Source: the ZIP of https://github.com/HadiNasooti/cnh-sunflower-weight (green "Code" button > "Download ZIP"),
# found in this setup folder or in your Downloads folder (newest one), else the old ..\code folder.
# Copies detkit, analysis, tools and tests into %USERPROFILE%\cnh_grain\manama_data_collection_course, puts the
# calibrated weight_config.json into runs\sunflower and runs the tests. Log: ..\logs\update_log.txt
$ErrorActionPreference = "Continue"
$Assign = Split-Path -Parent $PSScriptRoot
$Repo   = Join-Path $env:USERPROFILE "cnh_grain\manama_data_collection_course"
$LogDir = Join-Path $Assign "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log    = Join-Path $LogDir "update_log.txt"
Start-Transcript -Path $Log -Force | Out-Null

function Step($t) { Write-Host ""; Write-Host "==== $t ====" -ForegroundColor Cyan }
function Run {
    $exe = $args[0]
    $rest = @()
    if ($args.Count -gt 1) { $rest = $args[1..($args.Count - 1)] }
    & $exe @rest 2>&1 | ForEach-Object { Write-Host "$_" }
    Write-Host "(exit code $LASTEXITCODE)" }

$Ok = $true
if (-not (Test-Path (Join-Path $Repo "pyproject.toml"))) {
    Write-Host "ERROR: the toolkit is not installed yet. Run 1_SETUP_double_click.bat first." -ForegroundColor Red
    $Ok = $false
} else {
    Write-Host "Close the app window (2_START_APP) before updating." -ForegroundColor Yellow

    Step "1. Find the newest code"
    $Src = $null
    $Zips = @()
    foreach ($d in @($PSScriptRoot, (Join-Path $env:USERPROFILE "Downloads"))) {
        if (Test-Path $d) { $Zips += Get-ChildItem -Path $d -Filter "cnh-sunflower-weight*.zip" -File -ErrorAction SilentlyContinue }
    }
    if ($Zips.Count -gt 0) {
        $Zip = $Zips | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        Write-Host "using $($Zip.FullName) (saved $($Zip.LastWriteTime))"
        $Tmp = Join-Path $env:TEMP "cnh_code_update"
        if (Test-Path $Tmp) { Remove-Item -Recurse -Force $Tmp }
        try {
            Expand-Archive -Path $Zip.FullName -DestinationPath $Tmp -Force -ErrorAction Stop
            $Top = Get-ChildItem -Path $Tmp -Directory | Select-Object -First 1     # cnh-sunflower-weight-main
            $Src = $Top.FullName
        } catch {
            Write-Host "ERROR unpacking the ZIP: $_" -ForegroundColor Red
            $Ok = $false
        }
    } else {
        Write-Host "No cnh-sunflower-weight ZIP found. Download it: github.com/HadiNasooti/cnh-sunflower-weight," -ForegroundColor Red
        Write-Host "green 'Code' button > 'Download ZIP', then run this again." -ForegroundColor Red
        $Ok = $false
    }

    if ($Src) {
        Step "2. Copy the code"
        $n = 0
        foreach ($dir in @("detkit", "analysis", "tools", "tests")) {
            $From = Join-Path $Src $dir
            if (-not (Test-Path $From)) { Write-Host "ERROR: $dir missing in the ZIP" -ForegroundColor Red; $Ok = $false; continue }
            Get-ChildItem -Path $From -Recurse -File | Where-Object { $_.Extension -in ".py", ".json", ".md" } | ForEach-Object {
                $rel = $_.FullName.Substring($Src.Length + 1)
                $dst = Join-Path $Repo $rel
                try {
                    New-Item -ItemType Directory -Force -Path (Split-Path $dst) -ErrorAction Stop | Out-Null
                    Copy-Item $_.FullName $dst -Force -ErrorAction Stop
                    $n++
                } catch {
                    Write-Host "ERROR copying $rel : $_" -ForegroundColor Red
                    $script:Ok = $false
                }
            }
        }
        Write-Host "$n files copied"
        if ($n -eq 0) { Write-Host "ERROR: nothing was copied" -ForegroundColor Red; $Ok = $false }

        Step "3. Calibrated weight constants"
        $W = Join-Path $Repo "runs\sunflower"
        New-Item -ItemType Directory -Force -Path $W | Out-Null
        $Cfg = Join-Path $Src "analysis\results\main_std\weight_config.json"
        if (Test-Path $Cfg) {
            $Old = Join-Path $W "weight_config.json"
            try {
                if (Test-Path $Old) { Copy-Item $Old (Join-Path $W "weight_config_before_update.json") -Force -ErrorAction Stop }
                Copy-Item $Cfg $Old -Force -ErrorAction Stop
                Get-Content $Old | Write-Host
            } catch {
                Write-Host "ERROR copying weight_config.json : $_" -ForegroundColor Red
                $Ok = $false
            }
        } else {
            Write-Host "ERROR: $Cfg not found in the ZIP" -ForegroundColor Red
            $Ok = $false
        }

        Step "4. Tests"
        $Py = Join-Path $Repo ".venv\Scripts\python.exe"
        Set-Location $Repo
        & $Py -m pytest -q 2>&1 | ForEach-Object { Write-Host "$_" }
        if ($LASTEXITCODE -ne 0) { $Ok = $false }
        Write-Host "(exit code $LASTEXITCODE)"
        Run $Py -c "import cv2; from detkit.scale import measure_scale; print('OpenCV', cv2.__version__, 'marker reader OK')"
        if ($LASTEXITCODE -ne 0) { $Ok = $false }
    }
}

Stop-Transcript | Out-Null
Write-Host ""
if ($Ok) {
    Write-Host "UPDATE OK. Start the app with 2_START_APP_double_click.bat. You can close this window." -ForegroundColor Green
} else {
    Write-Host "UPDATE FAILED. The log is in 03_Assignment\logs\update_log.txt." -ForegroundColor Red
}
Read-Host "Press Enter to close"
