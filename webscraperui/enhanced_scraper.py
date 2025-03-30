"""
Enhanced Web Scraper module for the WebScraperUI application
Uses Selenium for JavaScript-rendered content
"""
import os
import json
import logging
import re
import time
import io
import tempfile
from collections import defaultdict
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import PyPDF2

from webscraperui.analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)

class EnhancedWebScraper:
    """Enhanced Web Scraper class for fetching and processing web content with JavaScript support"""
    
    def __init__(self, output_folder="./scraped_data", headless=True):
        """
        Initialize the EnhancedWebScraper
        
        Args:
            output_folder: Folder to save scraped data
            headless: Whether to run browser in headless mode
        """
        self.output_folder = output_folder
        self.analyzer = ContentAnalyzer()
        self.visited_urls = set()
        self.headless = headless
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
    def get_html_content(self, url, scroll=True, wait_time=5):
        """
        Fetch HTML content from a URL using Selenium without saving to a file
        
        Args:
            url: URL to fetch content from
            scroll: Whether to scroll the page to load lazy content
            wait_time: How many seconds to wait for the page to load
            
        Returns:
            dict: HTML content and metadata
        """
        try:
            logger.info(f"Fetching HTML content from {url}")
            
            # Set up the driver
            driver = self._setup_driver()
            
            # Fetch the page
            driver.get(url)
            
            # Wait for the page to load
            logger.info(f"Waiting {wait_time} seconds for page to load...")
            time.sleep(wait_time)
            
            # Check if we're on a Cloudflare challenge page
            if "Just a moment" in driver.title and "Cloudflare" in driver.page_source:
                logger.info("Detected Cloudflare challenge, waiting additional time...")
                # Wait longer for Cloudflare challenge
                cloudflare_wait = 10
                time.sleep(cloudflare_wait)
            
            # Scroll to load lazy content if needed
            if scroll:
                self._scroll_page(driver)
            
            # Get the page source after JavaScript execution
            html_content = driver.page_source
            
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract basic metadata
            title = soup.find("title")
            title_text = title.text.strip() if title else "No title found"
            
            meta_desc = soup.find("meta", attrs={"name": "description"})
            meta_description = meta_desc.get("content", "") if meta_desc else ""
            
            # Extract headings for context
            headings = []
            for heading_level in range(1, 7):
                for heading in soup.find_all(f"h{heading_level}"):
                    headings.append({
                        "level": heading_level,
                        "text": heading.text.strip()
                    })
            
            # Close the driver
            driver.quit()
            
            # Return the content and metadata
            return {
                "html": html_content,
                "title": title_text,
                "meta_description": meta_description,
                "url": url,
                "headings": headings[:10]  # First 10 headings for context
            }
            
        except Exception as e:
            logger.error(f"Error fetching HTML from {url}: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            raise
    
    def _setup_driver(self):
        """Set up the Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Add additional options to better handle Cloudflare protection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Initialize the driver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Set navigator webdriver property to undefined
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _is_pdf_url(self, url):
        """
        Check if a URL points to a PDF file
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if URL is a PDF, False otherwise
        """
        # First check the URL extension and path
        url_path = urlparse(url).path.lower()
        if url_path.endswith('.pdf') or '/pdf/' in url_path:
            return True
            
        # If the URL has a query string, check if it contains pdf references
        query = urlparse(url).query.lower()
        if query and ('format=pdf' in query or 'file=pdf' in query or 'type=pdf' in query):
            return True
            
        # If the extension doesn't clearly indicate, make a HEAD request to check Content-Type
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Check for various PDF content type formats
            pdf_content_types = [
                'application/pdf',
                'application/x-pdf',
                'application/acrobat',
                'application/vnd.pdf',
                'text/pdf',
                'text/x-pdf'
            ]
            
            return any(pdf_type in content_type for pdf_type in pdf_content_types)
        except Exception as e:
            logger.warning(f"Error checking content type for {url}: {e}")
            # If we can't determine for sure, use URL patterns as fallback
            return url_path.endswith('.pdf')
    
    def _extract_pdf_content(self, url):
        """
        Extract content from a PDF file
        
        Args:
            url: URL of the PDF
            
        Returns:
            dict: Extracted PDF data
        """
        try:
            logger.info(f"Extracting content from PDF: {url}")
            
            # Download the PDF file
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Basic PDF info even if we can't extract text
            pdf_data = {
                "url": url,
                "domain": urlparse(url).netloc,
                "path": urlparse(url).path,
                "title": os.path.basename(urlparse(url).path),
                "content": "",
                "metadata": {},
                "pages": [],
                "content_extracted": False,
                "file_size_bytes": len(response.content)
            }
            
            # Save to a temporary file because PyPDF2 works better with file paths
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Extract content using PyPDF2
            try:
                with open(temp_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    
                    # Get metadata
                    pdf_data["metadata"] = reader.metadata if reader.metadata else {}
                    pdf_data["page_count"] = len(reader.pages)
                    
                    # Get content from all pages
                    full_text = []
                    valid_text_pages = 0
                    
                    for i, page in enumerate(reader.pages):
                        try:
                            page_text = page.extract_text()
                            
                            # Check if the extracted text looks valid
                            # It should have a reasonable ratio of valid characters to total characters
                            if page_text:
                                # Count alphanumeric, punctuation, and whitespace characters
                                clean_chars = sum(1 for c in page_text if c.isalnum() or c.isspace() or c in '.,;:!?-()[]{}"/\'')
                                total_chars = len(page_text)
                                
                                # If at least 60% of characters are "normal", consider it valid text
                                if total_chars > 0 and clean_chars / total_chars >= 0.6:
                                    valid_text_pages += 1
                                    full_text.append(page_text)
                                    # Store first 1000 chars of each page
                                    pdf_data["pages"].append({
                                        "number": i + 1,
                                        "text": page_text[:1000] + "..." if len(page_text) > 1000 else page_text,
                                        "is_valid": True
                                    })
                                else:
                                    # Store as potentially corrupted text
                                    pdf_data["pages"].append({
                                        "number": i + 1,
                                        "text": "Page contains non-standard characters or encoding issues.",
                                        "is_valid": False,
                                        "sample": page_text[:100] if page_text else ""
                                    })
                        except Exception as e:
                            # If we can't extract text from this page
                            pdf_data["pages"].append({
                                "number": i + 1,
                                "text": f"Error extracting text: {str(e)}",
                                "is_valid": False
                            })
                    
                    if full_text:
                        pdf_data["content"] = "\n\n".join(full_text)
                        pdf_data["content_extracted"] = True
                    else:
                        pdf_data["content"] = "This PDF appears to contain non-standard text encoding or images that cannot be extracted as text."
                    
                    # Add a summary of what we found
                    pdf_data["valid_text_pages"] = valid_text_pages
                    pdf_data["extraction_success_rate"] = valid_text_pages / pdf_data["page_count"] if pdf_data["page_count"] > 0 else 0
                    
            except Exception as e:
                logger.error(f"Error extracting PDF content: {e}")
                pdf_data["content"] = f"Error extracting PDF content: {e}"
                pdf_data["error"] = str(e)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            # Run the content through our analyzer if we have valid text
            if pdf_data["content_extracted"] and pdf_data["content"]:
                try:
                    pdf_data["analysis"] = self.analyzer.analyze_text(pdf_data["content"])
                except Exception as e:
                    logger.error(f"Error analyzing PDF content: {e}")
            
            return pdf_data
            
        except Exception as e:
            logger.error(f"Error downloading PDF {url}: {e}")
            return {
                "url": url,
                "title": "PDF Processing Error",
                "content": f"Failed to process PDF: {str(e)}",
                "error": str(e)
            }
    
    def scrape(self, url, depth=1, output_format="txt", scroll=True, wait_time=5):
        """
        Scrape a website starting from the given URL using Selenium for JavaScript rendering
        
        Args:
            url: Starting URL to scrape
            depth: How many levels deep to scrape (default: 1)
            output_format: Format for saving output (txt, json, html)
            scroll: Whether to scroll the page to load lazy content
            wait_time: How many seconds to wait for the page to load
            
        Returns:
            dict: Scraped data and status
        """
        try:
            logger.info(f"Starting enhanced scrape of {url} with depth {depth}")
            
            # Reset visited URLs
            self.visited_urls = set()
            
            # Check if the URL is a PDF
            if self._is_pdf_url(url):
                logger.info(f"Detected PDF URL: {url}")
                data = self._extract_pdf_content(url)
            else:
                # Set up the driver for HTML content
                driver = self._setup_driver()
                
                # Fetch and parse the content
                driver.get(url)
                
                # Wait for the page to load - with special handling for Cloudflare
                logger.info(f"Waiting {wait_time} seconds for page to load (including possible Cloudflare challenge)...")
                time.sleep(wait_time)

                # Check if we're on a Cloudflare challenge page
                if "Just a moment" in driver.title and "Cloudflare" in driver.page_source:
                    logger.info("Detected Cloudflare challenge, waiting additional time...")
                    # Wait longer for Cloudflare challenge
                    cloudflare_wait = 10
                    time.sleep(cloudflare_wait)
                
                # Scroll to load lazy content if needed
                if scroll:
                    self._scroll_page(driver)
                
                # Get the page source after JavaScript execution
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Extract data from the page
                data = self._extract_data(soup, url, driver)
                
                # Close the driver
                driver.quit()
            
            # Add timestamp and parameters
            data["timestamp"] = datetime.now().isoformat()
            data["scrape_depth"] = depth
            data["url"] = url
            
            # Analyze the content
            data = self._analyze_content(data)
            
            # Crawl additional pages if depth > 1 and not a PDF
            if depth > 1 and not self._is_pdf_url(url):
                data["linked_pages"] = self._crawl_links(url, soup, driver, depth - 1, wait_time)
            
            # Save the results
            output_path = self._save_output(data, output_format)
            
            return {
                "url": url,
                "title": data.get("title", ""),
                "content": data.get("content", ""),
                "output_path": output_path,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            raise
    
    def _scroll_page(self, driver, max_scrolls=10):
        """
        Scroll the page to load lazy content
        
        Args:
            driver: Selenium WebDriver
            max_scrolls: Maximum number of scrolls
        """
        for _ in range(max_scrolls):
            # Scroll down
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(1)
    
    def _extract_data(self, soup, url, driver):
        """
        Extract data from parsed HTML
        
        Args:
            soup: BeautifulSoup object
            url: URL being scraped
            driver: Selenium WebDriver
            
        Returns:
            dict: Extracted data
        """
        # Extract basic page information
        data = {
            "url": url,
            "domain": urlparse(url).netloc,
            "path": urlparse(url).path,
        }
        
        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            data["title"] = title_tag.text.strip()
        else:
            data["title"] = "No title found"
        
        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            data["meta_description"] = meta_desc.get("content", "")
        
        # Extract main content - try to find specific content containers first
        content_selectors = [
            "main", "article", "#content", ".content", 
            "#main", ".main", ".post", ".entry", 
            "[role='main']", "[role='article']", ".document-content",
            ".docContent", "#documentation", ".documentation"
        ]
        
        content = ""
        for selector in content_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Get text from all matching elements
                    content = "\n".join([elem.text for elem in elements])
                    break
            except:
                continue
        
        # If no content found with selectors, use the body
        if not content:
            content = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
            
        data["content"] = content
        
        # Extract links
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if href and not href.startswith("#") and not href.startswith("javascript:"):
                links.append({
                    "text": link.text.strip(),
                    "href": urljoin(url, href)
                })
        
        data["links"] = links
        
        # Extract headings - Include level and text for all h1-h6 tags
        headings = []
        for heading_level in range(1, 7):
            for heading in soup.find_all(f"h{heading_level}"):
                headings.append({
                    "level": heading_level,
                    "text": heading.text.strip()
                })
        
        data["headings"] = headings
        
        # Extract images
        images = []
        for img in soup.find_all("img", src=True):
            src = img.get("src", "")
            if src:
                images.append({
                    "src": urljoin(url, src),
                    "alt": img.get("alt", ""),
                    "title": img.get("title", "")
                })
        
        data["images"] = images
        
        # Extract tables
        tables = []
        for table in soup.find_all("table"):
            tables.append(str(table))
        
        data["tables"] = tables
        
        # Extract code blocks
        code_blocks = []
        for code in soup.find_all(["code", "pre"]):
            code_blocks.append(code.text.strip())
        
        data["code_blocks"] = code_blocks
        
        return data
    
    def _crawl_links(self, base_url, soup, driver, depth, wait_time):
        """
        Crawl links from the page using Selenium
        
        Args:
            base_url: Base URL for resolving relative links
            soup: BeautifulSoup object
            driver: Selenium WebDriver
            depth: Remaining crawl depth
            wait_time: How many seconds to wait for each page
            
        Returns:
            list: Data from linked pages
        """
        if depth <= 0:
            return []
        
        # Extract links from the page
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if href and not href.startswith("#") and not href.startswith("javascript:"):
                absolute_url = urljoin(base_url, href)
                # Only include links from the same domain
                if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                    links.append(absolute_url)
        
        # Remove duplicate links and already visited URLs
        links = [link for link in set(links) if link not in self.visited_urls]
        
        # Limit to 10 links per page to avoid excessive crawling
        links = links[:10]
        
        # Crawl each link
        linked_data = []
        for link in links:
            try:
                # Mark URL as visited
                self.visited_urls.add(link)
                
                # Navigate to the link
                driver.get(link)
                time.sleep(wait_time)
                
                # Parse the page
                link_soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # Extract data from the page
                data = self._extract_data(link_soup, link, driver)
                
                # Add to the results
                linked_data.append({
                    "url": link,
                    "title": data.get("title", ""),
                    "content_summary": data.get("content", "")[:300] + "...",
                    "headings": data.get("headings", [])[:5]  # Include first 5 headings for context
                })
                
            except Exception as e:
                logger.error(f"Error crawling {link}: {str(e)}")
        
        return linked_data
    
    def _analyze_content(self, data):
        """
        Analyze the scraped content
        
        Args:
            data: Dictionary of scraped data
            
        Returns:
            dict: Data with analysis results added
        """
        content = data.get("content", "")
        
        if content:
            # Analyze the text content
            analysis_results = self.analyzer.analyze_text(content)
            data["analysis"] = analysis_results
        
        return data
    
    def _save_output(self, data, output_format):
        """
        Save scraped data to a file
        
        Args:
            data: Dictionary of scraped data
            output_format: Format to save in (txt, json, html)
            
        Returns:
            str: Path to the saved file
        """
        # Create a filename based on the URL and timestamp
        domain = data.get("domain", "unknown").replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{timestamp}"
        
        # Handle PDF data specially
        is_pdf = "metadata" in data and "page_count" in data
        
        if output_format == "json":
            # Save as JSON
            file_path = os.path.join(self.output_folder, f"{filename}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        elif output_format == "html":
            # Save as HTML
            file_path = os.path.join(self.output_folder, f"{filename}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                if is_pdf:
                    # PDF-specific HTML template
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>{data.get('title', 'PDF Content')}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                            h1 {{ color: #333; }}
                            .metadata {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                            .content {{ line-height: 1.6; }}
                            .analysis {{ background-color: #e6f3ff; padding: 10px; border-radius: 5px; margin-top: 20px; }}
                            .pages {{ margin-top: 20px; }}
                            .page {{ background-color: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 5px; border-left: 4px solid #007bff; }}
                            pre {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                            .pdf-info {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                        </style>
                    </head>
                    <body>
                        <h1>{data.get('title', 'PDF Content')}</h1>
                        
                        <div class="metadata">
                            <p><strong>URL:</strong> <a href="{data.get('url', '')}">{data.get('url', '')}</a></p>
                            <p><strong>Scraped:</strong> {data.get('timestamp', '')}</p>
                            <p><strong>Content Type:</strong> PDF Document</p>
                        </div>
                        
                        <div class="pdf-info">
                            <h2>PDF Information</h2>
                            <p><strong>Pages:</strong> {data.get('page_count', 'Unknown')}</p>
                            <p><strong>File Size:</strong> {data.get('file_size_bytes', 0) / 1024:.1f} KB</p>
                            <p><strong>Author:</strong> {data.get('metadata', {}).get('/Author', 'Unknown')}</p>
                            <p><strong>Creator:</strong> {data.get('metadata', {}).get('/Creator', 'Unknown')}</p>
                            <p><strong>Producer:</strong> {data.get('metadata', {}).get('/Producer', 'Unknown')}</p>
                            <p><strong>Creation Date:</strong> {data.get('metadata', {}).get('/CreationDate', 'Unknown')}</p>
                            
                            <div class="extraction-info">
                                <h3>Text Extraction</h3>
                                <p><strong>Success Rate:</strong> {data.get('extraction_success_rate', 0) * 100:.1f}% ({data.get('valid_text_pages', 0)} of {data.get('page_count', 0)} pages)</p>
                                <div class="alert {'alert-success' if data.get('content_extracted', False) else 'alert-warning'}">
                                    {
                                    'Successfully extracted text content.' 
                                    if data.get('content_extracted', False) 
                                    else 'This PDF contains encoding issues or image-based content that cannot be fully extracted as text.'
                                    }
                                </div>
                            </div>
                        </div>
                        
                        <div class="content">
                            <h2>Content Overview</h2>
                            {'<div>' + data.get('content', 'No content found.')[:2000].replace('\n', '<br>') + '...</div>' if data.get('content_extracted', False) else '<div class="alert alert-warning">Text extraction failed due to encoding issues or image-based content.</div>'}
                            <p><em>(Content truncated for readability. Full content available in text format.)</em></p>
                        </div>
                        
                        <div class="pages">
                            <h2>Pages Preview</h2>
                    """
                    
                    # Add page previews
                    for page in data.get('pages', []):
                        html += f"""
                        <div class="page">
                            <h3>Page {page.get('number', '?')}</h3>
                            <div>{page.get('text', '').replace('\n', '<br>')}</div>
                        </div>
                        """
                    
                    html += """
                        </div>
                    </body>
                    </html>
                    """
                else:
                    # Standard HTML template for web pages
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>{data.get('title', 'Scraped Content')}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                            h1 {{ color: #333; }}
                            .metadata {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                            .content {{ line-height: 1.6; }}
                            .analysis {{ background-color: #e6f3ff; padding: 10px; border-radius: 5px; margin-top: 20px; }}
                            .links, .headings, .images, .tables, .code-blocks {{ margin-top: 20px; }}
                            pre {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                            table {{ border-collapse: collapse; width: 100%; }}
                            th, td {{ border: 1px solid #ddd; padding: 8px; }}
                            th {{ background-color: #f2f2f2; }}
                        </style>
                    </head>
                    <body>
                        <h1>{data.get('title', 'Scraped Content')}</h1>
                        
                        <div class="metadata">
                            <p><strong>URL:</strong> <a href="{data.get('url', '')}">{data.get('url', '')}</a></p>
                            <p><strong>Scraped:</strong> {data.get('timestamp', '')}</p>
                            <p><strong>Depth:</strong> {data.get('scrape_depth', 1)}</p>
                        </div>
                        
                        <div class="content">
                            <h2>Content</h2>
                            <div>{data.get('content', 'No content found.').replace('\n', '<br>')}</div>
                        </div>
                    
                    <div class="analysis">
                        <h2>Content Analysis</h2>
                        <p><strong>Word Count:</strong> {data.get('analysis', {}).get('word_count', 0)}</p>
                        <p><strong>Sentence Count:</strong> {data.get('analysis', {}).get('sentence_count', 0)}</p>
                        <p><strong>Reading Time:</strong> {data.get('analysis', {}).get('reading_time_min', 0)} minutes</p>
                        <p><strong>Sentiment:</strong> {data.get('analysis', {}).get('sentiment', 'neutral')}</p>
                        <p><strong>Common Words:</strong></p>
                        <ul>
                """
                
                # Add common words
                common_words = data.get('analysis', {}).get('common_words', [])
                for word, count in common_words[:20]:
                    html += f"<li>{word}: {count}</li>"
                
                html += """
                        </ul>
                    </div>
                    
                    <div class="headings">
                        <h2>Headings</h2>
                        <ul>
                """
                
                # Add headings
                headings = data.get('headings', [])
                for heading in headings:
                    html += f"<li>[H{heading.get('level', '')}] {heading.get('text', '')}</li>"
                
                html += """
                        </ul>
                    </div>
                    
                    <div class="links">
                        <h2>Links</h2>
                        <ul>
                """
                
                # Add links
                links = data.get('links', [])
                for link in links[:50]:  # Limit to 50 links
                    html += f"<li><a href='{link.get('href', '')}'>{link.get('text', 'No text')}</a></li>"
                
                html += """
                        </ul>
                    </div>
                    
                    <div class="tables">
                        <h2>Tables</h2>
                """
                
                # Add tables
                tables = data.get('tables', [])
                for table in tables:
                    html += table
                
                html += """
                    </div>
                    
                    <div class="code-blocks">
                        <h2>Code Blocks</h2>
                """
                
                # Add code blocks
                code_blocks = data.get('code_blocks', [])
                for code in code_blocks:
                    html += f"<pre>{code}</pre>"
                
                html += """
                    </div>
                </body>
                </html>
                """
                
                f.write(html)
                
        else:
            # Default to TXT format
            file_path = os.path.join(self.output_folder, f"{filename}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Title: {data.get('title', 'No title')}\n")
                f.write(f"URL: {data.get('url', '')}\n")
                f.write(f"Scraped: {data.get('timestamp', '')}\n")
                
                # PDF-specific info
                if is_pdf:
                    f.write(f"Content Type: PDF Document\n")
                    f.write(f"Pages: {data.get('page_count', 'Unknown')}\n")
                    f.write(f"File Size: {data.get('file_size_bytes', 0) / 1024:.1f} KB\n")
                    
                    # Extraction info
                    if 'extraction_success_rate' in data:
                        f.write(f"Text Extraction Success: {data.get('extraction_success_rate', 0) * 100:.1f}% ({data.get('valid_text_pages', 0)} of {data.get('page_count', 0)} pages)\n")
                    
                    # Metadata
                    metadata = data.get('metadata', {})
                    if metadata:
                        f.write("\n=== PDF METADATA ===\n\n")
                        for key, value in metadata.items():
                            if key and value:
                                f.write(f"{key.strip('/')}: {value}\n")
                else:
                    f.write(f"Depth: {data.get('scrape_depth', 1)}\n")
                
                f.write("\n=== CONTENT ===\n\n")
                f.write(data.get('content', 'No content found.'))
                f.write("\n\n")
                
                # Only write analysis for non-PDFs or PDFs with content
                if not is_pdf or data.get('analysis'):
                    f.write("=== ANALYSIS ===\n\n")
                    f.write(f"Word Count: {data.get('analysis', {}).get('word_count', 0)}\n")
                    f.write(f"Sentence Count: {data.get('analysis', {}).get('sentence_count', 0)}\n")
                    f.write(f"Reading Time: {data.get('analysis', {}).get('reading_time_min', 0)} minutes\n")
                    f.write(f"Sentiment: {data.get('analysis', {}).get('sentiment', 'neutral')}\n\n")
                    
                    f.write("Common Words:\n")
                    common_words = data.get('analysis', {}).get('common_words', [])
                    for word, count in common_words[:10]:
                        f.write(f"- {word}: {count}\n")
                
                # PDF pages summary
                if is_pdf and data.get('pages'):
                    f.write("\n=== PAGES ===\n\n")
                    for page in data.get('pages', []):
                        f.write(f"--- Page {page.get('number', '?')} ---\n")
                        # Truncate page text for readability
                        page_preview = page.get('text', '')[:500]
                        if len(page.get('text', '')) > 500:
                            page_preview += "..."
                        f.write(f"{page_preview}\n\n")
                else:
                    # Only include these sections for non-PDF content
                    f.write("\n=== HEADINGS ===\n\n")
                    headings = data.get('headings', [])
                    for heading in headings:
                        f.write(f"[H{heading.get('level', '')}] {heading.get('text', '')}\n")
                    
                    f.write("\n=== LINKS ===\n\n")
                    links = data.get('links', [])
                    for link in links[:50]:  # Limit to 50 links
                        f.write(f"- {link.get('text', 'No text')}: {link.get('href', '')}\n")
                    
                    f.write("\n=== CODE BLOCKS ===\n\n")
                    code_blocks = data.get('code_blocks', [])
                    for i, code in enumerate(code_blocks):
                        f.write(f"--- Code Block {i+1} ---\n")
                        f.write(code)
                        f.write("\n\n")
        
        logger.info(f"Saved output to {file_path}")
        return file_path
