@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo    Safe-Transaction Quick Start
echo ==========================================

REM Setup virtual environment if needed
if not exist "env\" (
    echo [1/5] Creating virtual environment...
    python -m venv env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. Install Python first.
        pause
        exit /b 1
    )
) else (
    echo [1/5] Virtual environment exists ✓
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call .\env\Scripts\Activate.bat

REM Install Python dependencies if needed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [3/5] Installing Python dependencies...
    pip install -r requirements.txt
    pip install -e .
    pip install flask-mail
) else (
    echo [3/5] Python dependencies installed ✓
)

REM Install Node dependencies if needed
if not exist "node_modules\" (
    echo [4/5] Installing Node.js dependencies...
    npm ci
) else (
    echo [4/5] Node.js dependencies installed ✓
)

REM Setup database if needed
if not exist "var\insta485.sqlite3" (
    echo [5/5] Setting up database...
    if not exist "var\" mkdir var
    if not exist "var\uploads\" mkdir var\uploads
    sqlite3 var\insta485.sqlite3 ".read sql\schema.sql"
    sqlite3 var\insta485.sqlite3 ".read sql\data.sql"
    copy sql\uploads\* var\uploads\ >nul 2>&1
) else (
    echo [5/5] Database exists ✓
)

echo.
echo ==========================================
echo    Starting Safe-Transaction App
echo ==========================================
echo.
echo • Webpack will run in background
echo • Flask will start on http://localhost:8000
echo • Press Ctrl+C to stop everything
echo.

REM Start webpack in background
start /min "Webpack" cmd /c ".\env\Scripts\Activate.bat && npx webpack --watch"

REM Wait a moment for webpack to start
timeout /t 2 /nobreak >nul

REM Start Flask (this will block and handle Ctrl+C)
echo Starting Flask server...
flask --app insta485 --debug run --host 0.0.0.0 --port 8000

REM This runs when Flask stops (Ctrl+C)
echo.
echo ==========================================
echo    Shutting down...
echo ==========================================
echo Flask stopped.
echo Note: Webpack may still be running in background.
echo Check Task Manager if needed.
pause 