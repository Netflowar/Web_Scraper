# ProjectScraper Pro - User Guide

This guide walks you through the main features of ProjectScraper Pro and how to use them effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Web Page Scraping](#web-page-scraping)
3. [Documentation Site Extraction](#documentation-site-extraction)
4. [PDF Extraction](#pdf-extraction)
5. [History and File Management](#history-and-file-management)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Launching the Application

1. Open a terminal/command prompt
2. Navigate to the ProjectScraper-Production directory
3. Run the application using:
   ```
   # On macOS/Linux:
   ./run_app.sh
   
   # On Windows:
   run_app.bat
   ```
4. Open your web browser and go to: `http://localhost:8089`

### Understanding the Interface

The application has a tabbed interface with three main modes:

1. **Single URL**: For scraping individual web pages or PDFs
2. **Documentation Site**: For extracting content from documentation websites
3. **PDF Extraction**: For processing PDF files you upload

The navigation bar at the top provides access to:
- **Home**: Return to the main page
- **History**: View previously scraped files
- **Combine Docs**: Merge multiple scraped files

## Web Page Scraping

### Basic Scraping

1. On the main page, ensure you're on the "Single URL" tab
2. Enter a complete URL (including http:// or https://)
3. Configure your scraping:
   - **Crawl Depth**:
     - 1: Only the page you entered
     - 2: The page plus any linked pages (1 level)
     - 3: Deep crawl (2 levels of links)
   - **Output Format**:
     - HTML: Formatted report with styling
     - JSON: Structured data for further processing
     - TXT: Plain text format
   - **Scraper Type**:
     - Basic: Fast scraping for static sites
     - Enhanced: For JavaScript-heavy sites (uses headless browser)
4. Click "Start Scraping"
5. Wait for the process to complete (time varies based on depth and site complexity)
6. Review the results page showing extracted content, links, and analysis

### Tips for Web Scraping

- **Start with shallow depths** (1 or 2) to avoid long processing times
- **Use Enhanced scraper** for modern websites with dynamic content
- **HTML output** is best for human reading, while **JSON** is ideal for data processing
- URLs to PDF files will be automatically detected and processed with the PDF extractor

## Documentation Site Extraction

Documentation sites often have specific structures that ProjectScraper Pro can identify and process efficiently.

### Extracting Documentation Links

1. Click on the "Documentation Site" tab
2. Enter the main URL of the documentation site (e.g., a ReadTheDocs site)
3. Optional: Enter a filter pattern (e.g., "api", "reference", "module") to focus on specific content
4. Set the maximum number of links to process (start with 10-15 to test)
5. Choose your preferred output format
6. Click "Extract Documentation Links"

### Batch Processing

After extracting links, you'll see them organized by category:
- **Main**: Primary documentation pages
- **Modules**: Core module documentation
- **Submodules**: Component-level documentation
- **Other**: Miscellaneous pages

You can:
1. Click "Scrape All" to process all identified links
2. Click individual "Scrape" buttons to process specific links
3. After batch scraping completes, review the results summary
4. Click "Combine All" to merge the scraped files into a single document

### Tips for Documentation Extraction

- The tool has specialized handling for ReadTheDocs and similar platforms
- For large documentation sites, use the filter pattern to target specific sections
- The batch scraping process can take several minutes for larger sets of pages
- Combined documentation files are saved in the history and can be downloaded

## PDF Extraction

ProjectScraper Pro can extract text and metadata from PDF files, either uploaded directly or accessed via URL.

### Uploading a PDF

1. Click on the "PDF Extraction" tab
2. Click "Choose File" and select a PDF from your computer
3. Select your preferred output format
4. Optionally check "Extract images" (experimental feature)
5. Click "Extract PDF Content"
6. Review the extracted content, including:
   - PDF metadata (title, author, creation date, etc.)
   - Page content
   - Text analysis

### Processing a PDF URL

1. Go to the "Single URL" tab
2. Enter a URL that points to a PDF file
3. Configure the output format
4. Click "Start Scraping"
5. The system will automatically detect that it's a PDF and use the appropriate extractor

### Tips for PDF Extraction

- Some PDFs may contain image-based text that can't be extracted without OCR
- Complex formatting in PDFs may not be preserved in the extracted content
- Metadata extraction depends on the PDF having proper metadata embedded
- The image extraction feature is experimental and may not work on all PDFs

## History and File Management

### Viewing History

1. Click "History" in the navigation bar
2. See a list of all previously scraped files, sorted by date
3. Each entry shows:
   - Filename
   - Date/time of scraping
   - File size
   - Format (HTML, JSON, TXT)

### Managing Files

From the history page, you can:
1. Click on any file to view its content
2. Use the "Combine" checkbox to select files for combining
3. Click "Combine Selected" to merge multiple files
4. Enter a title for the combined document
5. Select the output format
6. Click "Combine Files" to create the merged document

### Tips for File Management

- Regularly clean up old or unneeded files to maintain system performance
- Use meaningful names when combining documents
- HTML format is best for combined documents as it preserves structure
- The scraped_data folder contains all your extracted files if you need to access them directly

## Advanced Features

### Content Analysis

All scraped content is automatically analyzed to provide:
- Word count and sentence count
- Reading time estimate
- Common words and their frequencies
- Basic sentiment analysis

### Multi-level Crawling

When using crawl depths greater than 1:
- The scraper follows links within the same domain
- Each linked page is processed according to your settings
- Results include summaries of linked content
- This is useful for comprehensive site extraction

### PDF Features

Advanced PDF processing includes:
- Extraction of embedded metadata
- Page-by-page content organization
- Detection of text vs. image-based PDFs
- Content analysis of the extracted text

## Troubleshooting

### Common Issues

**The application won't start**
- Check if it's already running (try accessing http://localhost:8089)
- Use `./stop_app.sh` to kill any existing instances, then try again
- Ensure you have the correct permissions (`chmod +x *.sh` on Linux/macOS)

**Enhanced scraping doesn't work**
- Ensure Google Chrome is installed on your system
- Check the console output for specific error messages
- Try reinstalling dependencies: `pip install -r requirements.txt`

**PDF extraction fails**
- Make sure the PDF isn't password-protected
- Try with a different PDF to see if it's a file-specific issue
- Some highly secure or damaged PDFs may not be extractable

**Scraping takes too long**
- Reduce the crawl depth (start with 1)
- Use Basic scraper for simple HTML sites
- For documentation sites, use more specific filter patterns
- Batch scraping can take several minutes depending on the number of pages

**Results are incomplete**
- Some sites block scraping attempts
- JavaScript-heavy sites may need the Enhanced scraper
- Some content may be loaded dynamically or require user interaction

### Getting Help

If you encounter issues not covered in this guide:
1. Check the console output for error messages
2. Verify your Python environment and dependencies
3. Try with a simpler website or PDF as a test
4. Refer to the README.md file for additional information

## Conclusion

ProjectScraper Pro provides powerful tools for extracting and processing content from websites and PDFs. By understanding the different extraction modes and their settings, you can efficiently gather the information you need for your research, documentation, or data collection projects.

Remember that web scraping should be done responsibly, respecting website terms of service and avoiding excessive requests that might burden web servers.
