#!/bin/bash

echo "========================================"
echo "   Safe-Transaction App Setup & Run"
echo "========================================"

# Stop on errors
set -e

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source env/bin/activate

# Check if dependencies are installed
echo "Checking dependencies..."
if ! pip show flask > /dev/null 2>&1; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    pip install -e .
    pip install flask-mail
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm ci
fi

# Check if database exists
if [ ! -f "var/insta485.sqlite3" ]; then
    echo "Setting up database..."
    mkdir -p var/uploads
    sqlite3 var/insta485.sqlite3 < sql/schema.sql
    sqlite3 var/insta485.sqlite3 < sql/data.sql
    cp sql/uploads/* var/uploads/ 2>/dev/null || true
fi

echo ""
echo "========================================"
echo "Starting Safe-Transaction App..."
echo "========================================"
echo ""
echo "Starting webpack in background..."
npx webpack --watch &

echo "Starting Flask server..."
echo ""
echo "App will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

flask --app insta485 --debug run --host 0.0.0.0 --port 8000 