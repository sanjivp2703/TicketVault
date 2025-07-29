# Safe-Transaction

A secure transaction management application built with Flask and React.

## 🚀 Quick Start

**Just one command to run everything!**

### For Windows:
```powershell
.\run.bat
```

### For Mac/Linux:
```bash
./run.sh
```

That's it! The script will automatically:
- ✅ Set up Python virtual environment
- ✅ Install all dependencies (Python + Node.js)
- ✅ Create and populate the database
- ✅ Start webpack bundler
- ✅ Start Flask development server

**App will be available at: http://localhost:8000**

## 📋 Prerequisites

Make sure you have these installed:
- **Python 3.10+**
- **Node.js 18.0+**
- **SQLite3**

## 🛠️ Manual Setup (Optional)

If you prefer to run setup manually:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Safe-Transaction
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   ```

3. **Activate virtual environment**
   - Windows: `.\env\Scripts\Activate.ps1`
   - Mac/Linux: `source env/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   pip install flask-mail
   npm ci
   ```

5. **Set up database**
   ```bash
   mkdir -p var/uploads
   sqlite3 var/insta485.sqlite3 < sql/schema.sql
   sqlite3 var/insta485.sqlite3 < sql/data.sql
   cp sql/uploads/* var/uploads/
   ```

6. **Run the application**
   ```bash
   # Terminal 1: Start webpack
   npx webpack --watch
   
   # Terminal 2: Start Flask
   flask --app insta485 --debug run --host 0.0.0.0 --port 8000
   ```

## 🔧 Development

The app runs in development mode with:
- Hot reloading for frontend changes (webpack --watch)
- Auto-restart for backend changes (Flask debug mode)
- Debug tools enabled

**To stop the app:** Press `Ctrl+C` in the terminal

## 🤝 Contributing

1. Pull the latest changes: `git pull`
2. Run the app: `run.bat` (Windows) or `./run.sh` (Mac/Linux)
3. Make your changes
4. The app will automatically reload!
