@echo off
REM Bharat Career Twin - automatic job refresh
REM Keeps live jobs fresh every 6 hours. Leave this window open while demoing,
REM or set up Task Scheduler instead (see README "Automatic updates").
cd /d "%~dp0backend"
py -3.12 -m app.cron.auto_refresh %*
pause
