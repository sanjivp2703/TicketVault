@echo off
echo ========================================
echo    Safe-Transaction App Setup & Run
echo ========================================

REM Check if virtual environment exists
if not exist "env\" (
    echo Creating Python virtual environment...
    python -m venv env
    if errorlevel 1 (
        echo Error: Failed to create virtual environment. Make sure Python is installed.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .\env\Scripts\Activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    pip install -e .
    pip install flask-mail
)

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing Node.js dependencies...
    npm ci
)

REM Check if database exists
if not exist "var\insta485.sqlite3" (
    echo Setting up database...
    if not exist "var\" mkdir var
    if not exist "var\uploads\" mkdir var\uploads
    sqlite3 var\insta485.sqlite3 ".read sql\schema.sql"
    sqlite3 var\insta485.sqlite3 ".read sql\data.sql"
    copy sql\uploads\* var\uploads\ >nul 2>&1
)

echo.
echo ========================================
echo Starting Safe-Transaction App...
echo ========================================
echo.
echo Starting webpack in background...
start /min cmd /c ".\env\Scripts\Activate.bat && npx webpack --watch"

echo Starting Flask server...
echo.
echo App will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

flask --app insta485 --debug run --host 0.0.0.0 --port 8000 