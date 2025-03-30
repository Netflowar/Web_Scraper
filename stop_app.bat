@echo off
echo Stopping WebScraperUI...

REM Find and kill the Python process running on port 8089
for /f "tokens=5" %%a in ('netstat -ano ^| find "8089" ^| find "LISTENING"') do (
    echo Killing process with PID: %%a
    taskkill /F /PID %%a
)

echo WebScraperUI stopped.
