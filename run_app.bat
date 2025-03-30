@echo off
echo Launching WebScraperUI...
echo Starting WebScraperUI on http://localhost:8089

REM Check if virtual environment exists, create if it doesn't
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

REM Run the application
python run_scraper_ui.py
