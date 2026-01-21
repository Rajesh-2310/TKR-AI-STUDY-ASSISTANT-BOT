@echo off
REM TKR College Chatbot - Quick Start Script for Windows

echo ========================================
echo TKR College AI Chatbot - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version
echo.

REM Check if MySQL is installed
mysql --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: MySQL command not found in PATH
    echo Make sure MySQL is installed and accessible
    echo.
)

echo [2/5] Setting up backend...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit backend\.env with your MySQL credentials!
    echo Press any key after you've updated the .env file...
    pause
)

echo [3/5] Installing Python dependencies...
echo This may take a few minutes on first run...
pip install -r requirements.txt --quiet

echo.
echo [4/5] Starting Flask backend server...
echo Backend will run on http://localhost:5000
echo.
start "TKR Chatbot Backend" cmd /k "venv\Scripts\activate && python app.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo [5/5] Opening frontend...
cd ..\frontend
start "TKR Chatbot Frontend" cmd /k "python -m http.server 8000"

REM Wait a moment then open browser
timeout /t 3 /nobreak >nul
start http://localhost:8000

echo.
echo ========================================
echo TKR College Chatbot is now running!
echo ========================================
echo.
echo Backend API: http://localhost:5000
echo Frontend UI: http://localhost:8000
echo.
echo Two command windows have opened:
echo 1. Backend server (Flask)
echo 2. Frontend server (HTTP)
echo.
echo Keep both windows open while using the chatbot.
echo Close them to stop the servers.
echo.
echo Press any key to exit this window...
pause >nul
