# ProjectScraper Pro - Quick Start Guide

This quick start guide will help you get up and running with ProjectScraper Pro in minutes.

## Installation

### On macOS/Linux:

1. Open Terminal
2. Navigate to the ProjectScraper-Production directory:
   ```
   cd path/to/ProjectScraper-Production
   ```
3. Run the setup script:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

### On Windows:

1. Open Command Prompt
2. Navigate to the ProjectScraper-Production directory:
   ```
   cd path\to\ProjectScraper-Production
   ```
3. Run the setup script:
   ```
   setup.bat
   ```

## Running the Application

### On macOS/Linux:

```
./run_app.sh
```

### On Windows:

```
run_app.bat
```

Then open your web browser and go to: `http://localhost:8089`

## Basic Usage

### To scrape a web page:

1. Enter a URL in the "Single URL" tab
2. Choose your settings:
   - **Depth**: 1 for just the page, 2-3 to follow links
   - **Format**: HTML, JSON, or TXT
   - **Type**: Basic for static sites, Enhanced for JavaScript-heavy sites
3. Click "Start Scraping"

### To extract from a PDF:

1. Go to "PDF Extraction" tab
2. Upload a PDF file or enter a PDF URL in the "Single URL" tab
3. Choose your output format
4. Click "Extract PDF Content" or "Start Scraping"

### To extract from a documentation site:

1. Go to "Documentation Site" tab
2. Enter the main URL of the documentation
3. Optional: Enter a filter pattern
4. Click "Extract Documentation Links"
5. Use "Scrape All" to process all links at once

## Viewing and Managing Results

- All results are saved automatically
- Click "History" to view all scraped files
- Use "Combine Docs" to merge multiple files

## Stopping the Application

### On macOS/Linux:

```
./stop_app.sh
```

### On Windows:

```
stop_app.bat
```

For detailed instructions, refer to the full USER_GUIDE.md file.
