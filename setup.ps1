# ============================================================
#  TrueFit — One-Click Setup (Windows PowerShell)
# ============================================================
#
#  This script does everything for you:
#    1. Checks that Git, Python, and Node.js are installed
#    2. Creates a Python virtual environment
#    3. Installs backend (Python) dependencies
#    4. Installs frontend (Node.js) dependencies
#    5. Starts both servers so you can open the app
#
#  HOW TO RUN:
#    1. Open PowerShell (right-click Start → "Windows PowerShell")
#    2. Navigate to the truefit folder:
#         cd C:\path\to\personal_bootstrap\truefit
#    3. Allow scripts to run (one-time):
#         Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#    4. Run this script:
#         .\setup.ps1
#
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TrueFit — Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ----------------------------------------------------------
# Helper: check if a command exists
# ----------------------------------------------------------
function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

# ----------------------------------------------------------
# [1/6] Check required software
# ----------------------------------------------------------
Write-Host "[1/6] Checking required software..." -ForegroundColor Yellow
Write-Host ""

$missing = @()

# Git
if (Test-Command "git") {
    $gitVer = git --version
    Write-Host "  OK  Git           — $gitVer" -ForegroundColor Green
} else {
    Write-Host "  MISSING  Git" -ForegroundColor Red
    $missing += "Git — download from https://git-scm.com/downloads"
}

# Python
$pythonCmd = $null
if (Test-Command "python") {
    $pythonCmd = "python"
} elseif (Test-Command "python3") {
    $pythonCmd = "python3"
}

if ($pythonCmd) {
    $pyVer = & $pythonCmd --version
    Write-Host "  OK  Python        — $pyVer" -ForegroundColor Green
} else {
    Write-Host "  MISSING  Python" -ForegroundColor Red
    $missing += "Python 3.12+ — download from https://www.python.org/downloads/"
}

# Node.js
if (Test-Command "node") {
    $nodeVer = node --version
    Write-Host "  OK  Node.js       — $nodeVer" -ForegroundColor Green
} else {
    Write-Host "  MISSING  Node.js" -ForegroundColor Red
    $missing += "Node.js 20+ — download from https://nodejs.org/"
}

# npm (comes with Node)
if (Test-Command "npm") {
    $npmVer = npm --version
    Write-Host "  OK  npm           — v$npmVer" -ForegroundColor Green
} else {
    if (Test-Command "node") {
        Write-Host "  MISSING  npm (should come with Node.js — try reinstalling)" -ForegroundColor Red
        $missing += "npm — reinstall Node.js from https://nodejs.org/"
    }
}

Write-Host ""

if ($missing.Count -gt 0) {
    Write-Host "Some required software is missing. Please install:" -ForegroundColor Red
    Write-Host ""
    foreach ($item in $missing) {
        Write-Host "  •  $item" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "After installing, close this window, open a NEW PowerShell, and run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "All required software found!" -ForegroundColor Green
Write-Host ""

# ----------------------------------------------------------
# [2/6] Create Python virtual environment
# ----------------------------------------------------------
Write-Host "[2/6] Setting up Python virtual environment..." -ForegroundColor Yellow

$venvPath = Join-Path $PSScriptRoot ".venv"

if (Test-Path $venvPath) {
    Write-Host "  Virtual environment already exists at .venv — skipping creation" -ForegroundColor Gray
} else {
    Write-Host "  Creating virtual environment..."
    & $pythonCmd -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "  OK  Created .venv" -ForegroundColor Green
}

# ----------------------------------------------------------
# [3/6] Activate virtual environment & install Python deps
# ----------------------------------------------------------
Write-Host ""
Write-Host "[3/6] Installing Python (backend) dependencies..." -ForegroundColor Yellow

$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "  ERROR: Cannot find $activateScript" -ForegroundColor Red
    Write-Host "  Try deleting the .venv folder and running this script again." -ForegroundColor Yellow
    exit 1
}

# Activate
& $activateScript

# Install
$requirementsPath = Join-Path $PSScriptRoot "api\requirements.txt"
pip install -r $requirementsPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: pip install failed." -ForegroundColor Red
    exit 1
}
Write-Host "  OK  Python dependencies installed" -ForegroundColor Green

# ----------------------------------------------------------
# [4/6] Install frontend (Node.js) dependencies
# ----------------------------------------------------------
Write-Host ""
Write-Host "[4/6] Installing frontend (Node.js) dependencies..." -ForegroundColor Yellow

$webDir = Join-Path $PSScriptRoot "web"
Push-Location $webDir
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: npm install failed." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "  OK  Frontend dependencies installed" -ForegroundColor Green

# ----------------------------------------------------------
# [5/6] Start the backend (API server)
# ----------------------------------------------------------
Write-Host ""
Write-Host "[5/6] Starting backend server (port 8100)..." -ForegroundColor Yellow

$apiDir = Join-Path $PSScriptRoot "api"
$backendJob = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/k", "cd /d `"$apiDir`" && `"$venvPath\Scripts\python.exe`" -m uvicorn main:app --host 0.0.0.0 --port 8100 --reload" `
    -PassThru

Write-Host "  OK  Backend starting in a new window (PID: $($backendJob.Id))" -ForegroundColor Green

# Give the backend a moment to boot
Start-Sleep -Seconds 3

# ----------------------------------------------------------
# [6/6] Start the frontend (Vite dev server)
# ----------------------------------------------------------
Write-Host ""
Write-Host "[6/6] Starting frontend server (port 5173)..." -ForegroundColor Yellow

$frontendJob = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/k", "cd /d `"$webDir`" && npm run dev" `
    -PassThru

Write-Host "  OK  Frontend starting in a new window (PID: $($frontendJob.Id))" -ForegroundColor Green

# ----------------------------------------------------------
# Done!
# ----------------------------------------------------------
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Two new windows opened:" -ForegroundColor White
Write-Host "    1. Backend  (Python API)    — http://localhost:8100/health" -ForegroundColor White
Write-Host "    2. Frontend (React web app) — http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "  Open your browser and go to:" -ForegroundColor Yellow
Write-Host ""
Write-Host "    http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "  To stop everything, just close those two command windows." -ForegroundColor Gray
Write-Host ""
