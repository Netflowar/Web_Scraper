@echo off
echo Restarting WebScraperUI...

REM Stop the app
call stop_app.bat

REM Wait a moment to ensure port is freed
timeout /t 2

REM Start the app again
call run_app.bat
