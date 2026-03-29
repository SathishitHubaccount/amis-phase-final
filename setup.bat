@echo off
echo ================================================
echo AMIS - Autonomous Manufacturing Intelligence
echo Quick Setup Script for Windows
echo ================================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file with your API key:
    echo     ANTHROPIC_API_KEY=your-key-here
    echo.
    echo See .env.example for template
    pause
    exit /b 1
)

echo [1/4] Checking .env file... OK
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+
    pause
    exit /b 1
)
echo [2/4] Python found... OK
echo.

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)
echo [3/4] Node.js found... OK
echo.

REM Install dependencies
echo [4/4] Installing dependencies...
echo.

echo Installing backend dependencies...
cd backend
pip install -r requirements.txt --quiet
cd ..
echo Backend dependencies installed!
echo.

echo Installing frontend dependencies (this may take a minute)...
cd frontend
call npm install --silent
cd ..
echo Frontend dependencies installed!
echo.

echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo To start AMIS:
echo.
echo 1. Open TWO terminal windows
echo.
echo 2. Terminal 1 - Backend:
echo    cd backend
echo    python main.py
echo.
echo 3. Terminal 2 - Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open browser to: http://localhost:5173
echo.
echo ================================================
pause
