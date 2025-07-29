Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "    Safe-Transaction Quick Start" -ForegroundColor Cyan  
Write-Host "==========================================" -ForegroundColor Cyan

# Setup virtual environment if needed
if (-not (Test-Path "env")) {
    Write-Host "[1/5] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment. Install Python first." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[1/5] Virtual environment exists ✓" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[2/5] Activating virtual environment..." -ForegroundColor Yellow
& .\env\Scripts\Activate.ps1

# Check if Flask is available in the activated environment
Write-Host "[3/5] Checking Python dependencies..." -ForegroundColor Yellow
$env:Path = ".\env\Scripts;" + $env:Path
try {
    & .\env\Scripts\pip.exe show flask | Out-Null
    Write-Host "[3/5] Python dependencies installed ✓" -ForegroundColor Green
} catch {
    Write-Host "[3/5] Installing Python dependencies..." -ForegroundColor Yellow
    & .\env\Scripts\pip.exe install -r requirements.txt
    & .\env\Scripts\pip.exe install -e .
    & .\env\Scripts\pip.exe install flask-mail
}

# Install Node dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "[4/5] Installing Node.js dependencies..." -ForegroundColor Yellow
    npm ci
} else {
    Write-Host "[4/5] Node.js dependencies installed ✓" -ForegroundColor Green
}

# Setup database if needed
if (-not (Test-Path "var\insta485.sqlite3")) {
    Write-Host "[5/5] Setting up database..." -ForegroundColor Yellow
    if (-not (Test-Path "var")) { New-Item -ItemType Directory -Path "var" }
    if (-not (Test-Path "var\uploads")) { New-Item -ItemType Directory -Path "var\uploads" }
    sqlite3 var\insta485.sqlite3 ".read sql\schema.sql"
    sqlite3 var\insta485.sqlite3 ".read sql\data.sql"
    Copy-Item sql\uploads\* var\uploads\ -Force 2>$null
} else {
    Write-Host "[5/5] Database exists ✓" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "    Starting Safe-Transaction App" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "• Webpack will run in background" -ForegroundColor Gray
Write-Host "• Flask will start on http://localhost:8000" -ForegroundColor Gray
Write-Host "• Press Ctrl+C to stop everything" -ForegroundColor Gray
Write-Host ""

# Start webpack in background
Write-Host "Starting webpack in background..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/c", ".\env\Scripts\Activate.bat && npx webpack --watch" -WindowStyle Minimized

# Wait a moment for webpack to start
Start-Sleep -Seconds 2

# Start Flask using the virtual environment's flask
Write-Host "Starting Flask server..." -ForegroundColor Yellow
Write-Host "App available at: http://localhost:8000" -ForegroundColor Green

try {
    & .\env\Scripts\flask.exe --app insta485 --debug run --host 0.0.0.0 --port 8000
} catch {
    Write-Host "Error starting Flask: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "    Shutting down..." -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Flask stopped." -ForegroundColor Yellow
    Write-Host "Note: Webpack may still be running in background." -ForegroundColor Gray
} 