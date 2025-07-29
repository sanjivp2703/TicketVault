@echo off
echo Starting Safe-Transaction App...
cd /d "%~dp0"
call .\env\Scripts\Activate.bat
echo Starting webpack in background...
start /min cmd /c ".\env\Scripts\Activate.bat && npx webpack --watch"
echo Starting Flask server...
echo App will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
flask --app insta485 --debug run --host 0.0.0.0 --port 8000 