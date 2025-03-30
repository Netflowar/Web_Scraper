#!/usr/bin/env python3
"""
Run the Web Scraper UI application
"""
import os
import sys
import logging

# Add the project directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from webscraperui.app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scraper_ui.log'
)

if __name__ == '__main__':
    # Set the output folder
    output_folder = os.path.join(os.getcwd(), 'scraped_data')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    app.config['OUTPUT_FOLDER'] = output_folder
    
    # Run the app
    app.run(host='0.0.0.0', port=8089, debug=True)
