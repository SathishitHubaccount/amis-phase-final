@echo off
title AMIS Backend Server
cd /d "%~dp0backend"
echo Starting AMIS Backend on http://127.0.0.1:8080 ...
python -c "import uvicorn; uvicorn.run('main:app', host='127.0.0.1', port=8080, reload=False)"
pause
