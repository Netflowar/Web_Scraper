#!/bin/bash
echo "Stopping WebScraperUI..."

# Find the PID of the Python process running run_scraper_ui.py
PIDS=$(ps -ef | grep "python[3]* run_scraper_ui.py" | awk '{print $2}')

if [ -z "$PIDS" ]; then
  echo "No main WebScraperUI processes found."
else
  for PID in $PIDS; do
    echo "Killing WebScraperUI process (PID: $PID)..."
    kill $PID 2>/dev/null
  done
fi

# Check if port 8089 is still in use and kill those processes too
PORT_PIDS=$(lsof -ti:8089)
if [ -n "$PORT_PIDS" ]; then
  echo "Found additional processes using port 8089..."
  for PID in $PORT_PIDS; do
    echo "Killing process using port 8089 (PID: $PID)..."
    kill -9 $PID 2>/dev/null
  done
fi

# Wait a moment to ensure processes are terminated
sleep 2

# Final check if port 8089 is still in use
if nc -z localhost 8089 2>/dev/null; then
  echo "Warning: Port 8089 is still in use by another process."
  echo "Try manually finding and killing the process with:"
  echo "  lsof -i:8089"
  echo "  kill -9 [PID]"
else
  echo "Port 8089 is now available."
fi

echo "WebScraperUI stopped."
