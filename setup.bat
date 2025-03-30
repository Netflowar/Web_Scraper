@echo off
echo Setting up ProjectScraper Pro...

REM Check if Python is installed
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH. Please install Python before continuing.
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing required packages...
pip install -r requirements.txt

REM Create output directory if it doesn't exist
if not exist scraped_data (
    mkdir scraped_data
    echo Created output directory: scraped_data
)

echo Setup complete! You can now run the application with run_app.bat
pause
