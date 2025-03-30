#!/bin/bash
echo "Launching WebScraperUI..."

# Check if the app is already running
if nc -z localhost 8089 2>/dev/null; then
  echo "Error: WebScraperUI is already running on port 8089."
  echo "Use ./stop_app.sh to stop the running instance first."
  exit 1
fi

# Run the application
echo "Starting WebScraperUI on http://localhost:8089"
python3 run_scraper_ui.py
