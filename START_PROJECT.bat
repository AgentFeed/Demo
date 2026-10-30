@echo off
REM Bharat Career Twin - start everything (backend + website)
REM Keep this window open while using the project. Close it to stop the servers.
title Bharat Career Twin - running
cd /d "%~dp0backend"
echo Starting backend API on http://127.0.0.1:8000 ...
start "BCT backend" cmd /c "py -3.12 -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
cd /d "%~dp0website"
echo Starting website on http://127.0.0.1:5500 ...
start "BCT website" cmd /c "py -3.12 -m http.server 5500 --bind 127.0.0.1"
timeout /t 3 >nul
start http://127.0.0.1:5500/index.html
echo.
echo Both servers are running. Two small windows opened - keep them open.
echo Website:  http://127.0.0.1:5500/index.html
echo API docs: http://127.0.0.1:8000/docs
pause
