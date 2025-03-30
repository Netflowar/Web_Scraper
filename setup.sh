#!/bin/bash

echo "Setting up ProjectScraper Pro..."

# Make all shell scripts executable
chmod +x *.sh

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 before continuing."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing required packages..."
pip install -r requirements.txt

# Create output directory if it doesn't exist
if [ ! -d "scraped_data" ]; then
    mkdir scraped_data
    echo "Created output directory: scraped_data"
fi

echo "Setup complete! You can now run the application with ./run_app.sh"
