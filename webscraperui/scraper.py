"""
Web Scraper module for the WebScraperUI application
"""
import os
import json
import logging
import re
import time
from collections import defaultdict
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from webscraperui.analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)

class WebScraper:
    """Web Scraper class for fetching and processing web content"""
    
    def __init__(self, output_folder="./scraped_data"):
        """
        Initialize the WebScraper
        
        Args:
            output_folder: Folder to save scraped data
        """
        self.output_folder = output_folder
        self.analyzer = ContentAnalyzer()
        self.visited_urls = set()
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    def scrape(self, url, depth=1, output_format="txt"):
        """
        Scrape a website starting from the given URL
        
        Args:
            url: Starting URL to scrape
            depth: How many levels deep to scrape (default: 1)
            output_format: Format for saving output (txt, json, html)
            
        Returns:
            dict: Scraped data and status
        """
        try:
            logger.info(f"Starting scrape of {url} with depth {depth}")
            
            # Reset visited URLs
            self.visited_urls = set()
            
            # Fetch and parse the content
            html_content = self._fetch_content(url)
            soup = self._parse_html(html_content)
            
            # Extract data from the page
            data = self._extract_data(soup, url)
            
            # Add timestamp and parameters
            data["timestamp"] = datetime.now().isoformat()
            data["scrape_depth"] = depth
            data["url"] = url
            
            # Analyze the content
            data = self._analyze_content(data)
            
            # Crawl additional pages if depth > 1
            if depth > 1:
                data["linked_pages"] = self._crawl_links(url, soup, depth - 1)
            
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
            raise
    
    def _fetch_content(self, url):
        """
        Fetch content from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            str: HTML content
        """
        logger.info(f"Fetching content from {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebScraperUI/1.0.0"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.text
    
    def _parse_html(self, html):
        """
        Parse HTML content using BeautifulSoup
        
        Args:
            html: HTML content as string
            
        Returns:
            BeautifulSoup: Parsed HTML
        """
        return BeautifulSoup(html, "html.parser")
    
    def _extract_data(self, soup, url):
        """
        Extract data from parsed HTML
        
        Args:
            soup: BeautifulSoup object
            url: URL being scraped
            
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
        
        # Extract main content
        # Try to find main content using common content containers
        content_selectors = [
            "main", "article", "#content", ".content", 
            "#main", ".main", ".post", ".entry", "body"
        ]
        
        content = ""
        for selector in content_selectors:
            content_tag = soup.select_one(selector)
            if content_tag:
                content = content_tag.get_text(separator=" ", strip=True)
                break
        
        # If no content found with selectors, use the body
        if not content and soup.body:
            content = soup.body.get_text(separator=" ", strip=True)
            
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
        
        # Extract headings
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
        
        return data
    
    def _crawl_links(self, base_url, soup, depth):
        """
        Crawl links from the page
        
        Args:
            base_url: Base URL for resolving relative links
            soup: BeautifulSoup object
            depth: Remaining crawl depth
            
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
        
        # Limit to 5 links per page to avoid excessive crawling
        links = links[:5]
        
        # Crawl each link
        linked_data = []
        for link in links:
            try:
                # Mark URL as visited
                self.visited_urls.add(link)
                
                # Fetch and parse the page
                html_content = self._fetch_content(link)
                link_soup = self._parse_html(html_content)
                
                # Extract data from the page
                data = self._extract_data(link_soup, link)
                
                # Add to the results
                linked_data.append({
                    "url": link,
                    "title": data.get("title", ""),
                    "content_summary": data.get("content", "")[:200] + "..."
                })
                
                # Respect crawl delay
                time.sleep(1)
                
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
        
        if output_format == "json":
            # Save as JSON
            file_path = os.path.join(self.output_folder, f"{filename}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        elif output_format == "html":
            # Save as HTML
            file_path = os.path.join(self.output_folder, f"{filename}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>{data.get('title', 'Scraped Content')}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #333; }}
                        .metadata {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                        .content {{ line-height: 1.6; }}
                        .analysis {{ background-color: #e6f3ff; padding: 10px; border-radius: 5px; margin-top: 20px; }}
                        .links, .images {{ margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <h1>{data.get('title', 'Scraped Content')}</h1>
                    
                    <div class="metadata">
                        <p><strong>URL:</strong> {data.get('url', '')}</p>
                        <p><strong>Scraped:</strong> {data.get('timestamp', '')}</p>
                        <p><strong>Depth:</strong> {data.get('scrape_depth', 1)}</p>
                    </div>
                    
                    <div class="content">
                        <h2>Content</h2>
                        <p>{data.get('content', 'No content found.')}</p>
                    </div>
                    
                    <div class="analysis">
                        <h2>Content Analysis</h2>
                        <p><strong>Word Count:</strong> {data.get('analysis', {}).get('word_count', 0)}</p>
                        <p><strong>Sentence Count:</strong> {data.get('analysis', {}).get('sentence_count', 0)}</p>
                        <p><strong>Common Words:</strong></p>
                        <ul>
                """
                
                # Add common words
                common_words = data.get('analysis', {}).get('common_words', [])
                for word, count in common_words[:10]:
                    html += f"<li>{word}: {count}</li>"
                
                html += """
                        </ul>
                    </div>
                    
                    <div class="links">
                        <h2>Links</h2>
                        <ul>
                """
                
                # Add links
                links = data.get('links', [])
                for link in links[:20]:  # Limit to 20 links
                    html += f"<li><a href='{link.get('href', '')}'>{link.get('text', 'No text')}</a></li>"
                
                html += """
                        </ul>
                    </div>
                    
                    <div class="images">
                        <h2>Images</h2>
                        <ul>
                """
                
                # Add images
                images = data.get('images', [])
                for img in images[:10]:  # Limit to 10 images
                    html += f"<li>{img.get('alt', 'No alt text')} - {img.get('src', '')}</li>"
                
                html += """
                        </ul>
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
                f.write(f"Depth: {data.get('scrape_depth', 1)}\n\n")
                
                f.write("=== CONTENT ===\n\n")
                f.write(data.get('content', 'No content found.'))
                f.write("\n\n")
                
                f.write("=== ANALYSIS ===\n\n")
                f.write(f"Word Count: {data.get('analysis', {}).get('word_count', 0)}\n")
                f.write(f"Sentence Count: {data.get('analysis', {}).get('sentence_count', 0)}\n")
                
                f.write("Common Words:\n")
                common_words = data.get('analysis', {}).get('common_words', [])
                for word, count in common_words[:10]:
                    f.write(f"- {word}: {count}\n")
                
                f.write("\n=== HEADINGS ===\n\n")
                headings = data.get('headings', [])
                for heading in headings:
                    f.write(f"[H{heading.get('level', '')}] {heading.get('text', '')}\n")
                
                f.write("\n=== LINKS ===\n\n")
                links = data.get('links', [])
                for link in links[:20]:  # Limit to 20 links
                    f.write(f"- {link.get('text', 'No text')}: {link.get('href', '')}\n")
        
        logger.info(f"Saved output to {file_path}")
        return file_path
