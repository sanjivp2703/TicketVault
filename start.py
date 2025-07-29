#!/usr/bin/env python3
"""Universal startup script for Safe-Transaction app."""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def run_command(cmd, shell=True, check=True):
    """Run a command and return the result."""
    try:
        if isinstance(cmd, str):
            print(f"Running: {cmd}")
        else:
            print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, shell=shell, check=check, text=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False

def check_python():
    """Check if Python is available."""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✓ Python found: {result.stdout.strip()}")
        return True
    except:
        print("✗ Python not found")
        return False

def check_node():
    """Check if Node.js is available."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✓ Node.js found: {result.stdout.strip()}")
        return True
    except:
        print("✗ Node.js not found")
        return False

def setup_venv():
    """Set up Python virtual environment."""
    if not Path("env").exists():
        print("[1/5] Creating Python virtual environment...")
        if not run_command([sys.executable, "-m", "venv", "env"]):
            print("Failed to create virtual environment")
            return False
    else:
        print("[1/5] Virtual environment exists ✓")
    return True

def get_pip_path():
    """Get the path to pip in the virtual environment."""
    if platform.system() == "Windows":
        return str(Path("env/Scripts/pip.exe"))
    else:
        return str(Path("env/bin/pip"))

def get_flask_path():
    """Get the path to flask in the virtual environment."""
    if platform.system() == "Windows":
        return str(Path("env/Scripts/flask.exe"))
    else:
        return str(Path("env/bin/flask"))

def get_python_path():
    """Get the path to python in the virtual environment."""
    if platform.system() == "Windows":
        return str(Path("env/Scripts/python.exe"))
    else:
        return str(Path("env/bin/python"))

def install_python_deps():
    """Install Python dependencies."""
    pip_path = get_pip_path()
    
    # Check if flask is already installed
    try:
        result = subprocess.run([pip_path, "show", "flask"], capture_output=True)
        if result.returncode == 0:
            print("[2/5] Python dependencies already installed ✓")
            return True
    except:
        pass
    
    print("[2/5] Installing Python dependencies...")
    commands = [
        [pip_path, "install", "-r", "requirements.txt"],
        [pip_path, "install", "-e", "."],
        [pip_path, "install", "flask-mail"]
    ]
    
    for cmd in commands:
        if not run_command(cmd, shell=False):
            print(f"Failed to run: {' '.join(cmd)}")
            return False
    return True

def install_node_deps():
    """Install Node.js dependencies."""
    if Path("node_modules").exists():
        print("[3/5] Node.js dependencies already installed ✓")
        return True
    
    print("[3/5] Installing Node.js dependencies...")
    return run_command(["npm", "ci"], shell=False)

def setup_database():
    """Set up the database."""
    if Path("var/insta485.sqlite3").exists():
        print("[4/5] Database already exists ✓")
        return True
    
    print("[4/5] Setting up database...")
    
    # Create directories
    Path("var").mkdir(exist_ok=True)
    Path("var/uploads").mkdir(exist_ok=True)
    
    # Create database
    commands = [
        ["sqlite3", "var/insta485.sqlite3", ".read sql/schema.sql"],
        ["sqlite3", "var/insta485.sqlite3", ".read sql/data.sql"]
    ]
    
    for cmd in commands:
        if not run_command(cmd, shell=False):
            print(f"Failed to run: {' '.join(cmd)}")
            return False
    
    # Copy uploads
    try:
        import shutil
        upload_files = Path("sql/uploads").glob("*")
        for file in upload_files:
            if file.is_file():
                shutil.copy2(file, "var/uploads/")
        print("Upload files copied ✓")
    except Exception as e:
        print(f"Warning: Could not copy upload files: {e}")
    
    return True

def start_webpack():
    """Start webpack in background."""
    print("[5/5] Starting webpack in background...")
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["cmd", "/c", "npx webpack --watch"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["npx", "webpack", "--watch"])
        time.sleep(2)  # Give webpack time to start
        return True
    except Exception as e:
        print(f"Warning: Could not start webpack: {e}")
        return False

def start_flask():
    """Start Flask server."""
    print("\n" + "="*50)
    print("    Starting Safe-Transaction App")
    print("="*50)
    print()
    print("• Webpack running in background")
    print("• Flask starting on http://localhost:8000")
    print("• Press Ctrl+C to stop everything")
    print()
    
    flask_path = get_flask_path()
    try:
        subprocess.run([flask_path, "--app", "insta485", "--debug", "run", 
                       "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print("Flask stopped.")
        print("Note: Webpack may still be running in background.")

def main():
    """Main function."""
    print("="*50)
    print("    Safe-Transaction Universal Starter")
    print("="*50)
    
    # Check prerequisites
    if not check_python():
        print("Please install Python 3.10+ first")
        sys.exit(1)
    
    if not check_node():
        print("Please install Node.js 18.0+ first")
        sys.exit(1)
    
    # Setup steps
    if not setup_venv():
        sys.exit(1)
    
    if not install_python_deps():
        sys.exit(1)
    
    if not install_node_deps():
        sys.exit(1)
    
    if not setup_database():
        sys.exit(1)
    
    # Start services
    start_webpack()
    start_flask()

if __name__ == "__main__":
    main() 