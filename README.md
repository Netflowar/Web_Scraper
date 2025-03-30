# ProjectScraper Pro

A comprehensive web data extraction tool for scraping content from websites, documentation sites, and PDF files.

## Features

- **Web Page Scraping**: Extract content from regular websites with support for JavaScript-rendered pages
- **Documentation Site Extraction**: Specialized extraction for documentation sites with batch processing
- **PDF Extraction**: Extract text and metadata from PDF files (both local and online)
- **Multiple Output Formats**: Save extracted content as HTML, JSON, or TXT
- **Content Analysis**: Automatically analyze text for readability, word counts, and key information
- **Multi-level Crawling**: Follow links to specified depths for thorough data collection

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- Google Chrome (for Enhanced scraping mode with JavaScript support)

### Option 1: Using the Installation Script (Recommended)

1. Extract the ProjectScraper-Production.zip file to any location on your computer
2. Open a terminal or command prompt
3. Navigate to the extracted directory:
   ```
   cd path/to/ProjectScraper-Production
   ```
4. Run the setup script:
   ```
   # On macOS/Linux:
   ./setup.sh
   
   # On Windows:
   setup.bat
   ```

### Option 2: Manual Installation

1. Extract the ProjectScraper-Production.zip file to any location on your computer
2. Open a terminal or command prompt
3. Navigate to the extracted directory:
   ```
   cd path/to/ProjectScraper-Production
   ```
4. Create a virtual environment:
   ```
   # On macOS/Linux:
   python3 -m venv venv
   
   # On Windows:
   python -m venv venv
   ```
5. Activate the virtual environment:
   ```
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```
6. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

### Using the Convenience Scripts

1. Make sure you're in the ProjectScraper-Production directory
2. Run the application:
   ```
   # On macOS/Linux:
   ./run_app.sh
   
   # On Windows:
   run_app.bat
   ```
3. To stop the application:
   ```
   # On macOS/Linux:
   ./stop_app.sh
   
   # On Windows:
   stop_app.bat
   ```
4. To restart the application:
   ```
   # On macOS/Linux:
   ./restart_app.sh
   
   # On Windows:
   restart_app.bat
   ```

### Running Manually

1. Make sure the virtual environment is activated:
   ```
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```
2. Run the application:
   ```
   python3 run_scraper_ui.py
   ```
3. Access the web interface by opening a browser and navigating to:
   ```
   http://localhost:8089
   ```

## Usage Guide

### 1. Web Page Scraping

1. Open your browser and go to `http://localhost:8089`
2. In the "Single URL" tab:
   - Enter the URL you want to scrape
   - Select the crawl depth (1 for single page, 2-3 for following links)
   - Choose the output format (HTML, JSON, or TXT)
   - Select the scraper type:
     - Basic: Faster, but only works with static HTML
     - Enhanced: Handles JavaScript-rendered content
3. Click "Start Scraping" to begin the process
4. View the results and access the saved file

### 2. Documentation Site Extraction

1. Click on the "Documentation Site" tab
2. Enter the main URL of the documentation site
3. Optionally provide a filter pattern to include only specific links
4. Set the maximum number of links to process
5. Choose the output format
6. Check "Automatically scrape all extracted links" if you want to process all found links
7. Click "Extract Documentation Links"
8. Review the extracted links and choose to scrape them individually or all at once
9. After scraping, use the "Combine Documents" feature to merge multiple scraped files

### 3. PDF Extraction

1. Click on the "PDF Extraction" tab
2. Either:
   - Upload a PDF file using the file selector
   - Or enter a URL to a PDF in the "Single URL" tab (it will be detected automatically)
3. Select the output format (HTML, JSON, or TXT)
4. Optionally check "Extract images" (experimental feature)
5. Click "Extract PDF Content"
6. View the extracted content, metadata, and download the output file

### 4. History and File Management

1. Click on any saved file in the results page to view its content
2. Access the history page to view all previously scraped files
3. View, download, or combine files from the history page

## Troubleshooting

### Common Issues

1. **Address already in use**
   - Use the `stop_app.sh` or `stop_app.bat` script to stop any running instances
   - Or manually find and kill the process using port 8089

2. **Selenium/Chrome driver issues**
   - Ensure Google Chrome is installed on your system
   - Try reinstalling the dependencies: `pip install -r requirements.txt`

3. **Permission denied errors**
   - Make sure the scripts are executable:
     ```
     chmod +x *.sh
     ```

4. **Import errors**
   - Ensure you're running the app from the correct directory
   - Make sure the virtual environment is activated

## File Structure

- `run_scraper_ui.py`: The main application entry point
- `webscraperui/`: The core application code
- `pdf_extractor/`: PDF extraction functionality
- `scraped_data/`: Directory where scraped files are saved
- `tests/`: Test files for the application
- `requirements.txt`: List of Python dependencies
- `*.sh` / `*.bat`: Convenience scripts for running the application

## Notes

- The application runs on http://localhost:8089 by default
- All scraped data is saved in the `scraped_data` folder
- For enhanced scraping with JavaScript support, Google Chrome must be installed
