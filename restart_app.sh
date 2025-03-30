#!/bin/bash
echo "Restarting WebScraperUI..."

# First, stop any running instance
./stop_app.sh

# Wait a moment to ensure ports are freed
sleep 2

# Start the application again
./run_app.sh
