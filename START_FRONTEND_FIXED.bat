@echo off
echo Starting AMIS Frontend Server...
echo.

REM Set Node.js in PATH
set "PATH=C:\Program Files\nodejs;%PATH%"

REM Navigate to frontend directory
cd /d "%~dp0frontend"

REM Start the frontend server
echo Running: npm run dev
npm run dev

pause
