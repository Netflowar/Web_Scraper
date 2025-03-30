"""
Link Extractor module for WebScraperUI

This module provides functionality to extract links from HTML content, 
particularly targeting documentation sites with similar structures.
"""
import os
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class LinkExtractor:
    """
    A class to extract and process links from HTML content.
    
    This can be used to extract links from documentation websites and
    prepare them for further scraping or analysis.
    """
    
    def __init__(self):
        """Initialize the LinkExtractor."""
        pass
    
    def extract_links_from_html(self, html_content):
        """
        Extract all links from HTML content.
        
        Args:
            html_content (str): HTML content as a string
            
        Returns:
            list: List of dictionaries containing URL and text for each link
        """
        links = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all anchor tags
        for anchor in soup.find_all('a', href=True):
            link = {
                'url': anchor['href'],
                'text': anchor.get_text(strip=True)
            }
            links.append(link)
            
        return links
    
    def extract_links_from_file(self, file_path):
        """
        Extract links from an HTML file.
        
        Args:
            file_path (str): Path to the HTML file
            
        Returns:
            list: List of dictionaries containing URL and text for each link
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            return self.extract_links_from_html(html_content)
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []
    
    def make_links_absolute(self, links, base_url):
        """
        Convert relative URLs to absolute URLs.
        
        Args:
            links (list): List of link dictionaries
            base_url (str): Base URL to use for relative links
            
        Returns:
            list: List of link dictionaries with absolute URLs
        """
        absolute_links = []
        
        for link in links:
            # Skip links that are already absolute
            if bool(urlparse(link['url']).netloc):
                absolute_links.append(link)
            else:
                # Convert relative link to absolute
                absolute_url = urljoin(base_url, link['url'])
                absolute_link = {
                    'url': absolute_url,
                    'text': link['text']
                }
                absolute_links.append(absolute_link)
                
        return absolute_links
    
    def filter_links_by_pattern(self, links, pattern):
        """
        Filter links by a pattern in the URL or text.
        
        Args:
            links (list): List of link dictionaries
            pattern (str): Pattern to match in URL or text
            
        Returns:
            list: Filtered list of link dictionaries
        """
        filtered_links = []
        
        for link in links:
            if pattern.lower() in link['url'].lower() or pattern.lower() in link['text'].lower():
                filtered_links.append(link)
                
        return filtered_links
    
    def extract_doc_links(self, html_content, base_url, filter_pattern=None):
        """
        Extract and process documentation links in one go.
        
        Args:
            html_content (str): HTML content as a string
            base_url (str): Base URL to use for relative links
            filter_pattern (str, optional): Pattern to filter links
            
        Returns:
            list: Processed list of link dictionaries
        """
        # Extract all links
        links = self.extract_links_from_html(html_content)
        
        # Make links absolute
        links = self.make_links_absolute(links, base_url)
        
        # Filter links if a pattern is specified
        if filter_pattern:
            links = self.filter_links_by_pattern(links, filter_pattern)
            
        return links
    
    def get_doc_structure(self, links):
        """
        Analyze links to determine documentation structure.
        
        This attempts to identify the hierarchy of documentation pages
        based on URL patterns and link text.
        
        Args:
            links (list): List of link dictionaries
            
        Returns:
            dict: Hierarchical structure of documentation
        """
        structure = {
            'main': [],
            'modules': [],
            'submodules': [],
            'other': []
        }
        
        # Detect ReadTheDocs.io sites for special handling
        is_readthedocs = any('readthedocs.io' in link['url'].lower() for link in links)
        
        # Process each link
        for link in links:
            url = link['url'].lower()
            text = link['text'].lower()
            
            # Special handling for ReadTheDocs
            if is_readthedocs:
                # Module pages typically have 'module' in the URL or text
                if 'module' in url or 'module' in text:
                    # Check if it's specifically a submodule
                    if ('sub' in text and 'module' in text) or ('acitoolkit' not in text and text.endswith('module')):
                        structure['submodules'].append(link)
                    else:
                        structure['modules'].append(link)
                
                # Main navigation pages
                elif any(keyword in text for keyword in ['introduction', 'index', 'overview', 'getting started']):
                    structure['main'].append(link)
                
                # API Reference pages
                elif 'api' in text or 'reference' in text or 'class' in text or 'object' in text:
                    if text not in [link['text'].lower() for link in structure['main']]:
                        structure['main'].append(link)
                
                # Everything else
                else:
                    structure['other'].append(link)
            
            # Generic handling for other sites
            else:
                # Identify main pages
                if 'index' in url or 'home' in url or 'introduction' in text:
                    structure['main'].append(link)
                # Identify modules
                elif 'module' in url or 'module' in text:
                    structure['modules'].append(link)
                # Identify submodules
                elif 'sub' in text and ('module' in text or 'class' in text):
                    structure['submodules'].append(link)
                # Everything else
                else:
                    structure['other'].append(link)
                
        return structure
        
    def extract_readthedocs_modules(self, url, html_content):
        """
        Special method to extract module links from ReadTheDocs.io sites.
        
        Args:
            url: Base URL of the documentation
            html_content: HTML content of the page
            
        Returns:
            list: Links to module pages with absolute URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        # First, try to find links in the toctree structure which contains 
        # the most reliable module links in ReadTheDocs
        toctrees = soup.find_all('div', class_='toctree-wrapper')
        for toctree in toctrees:
            # Find all links in the toctree at any level
            for a in toctree.find_all('a', class_='reference', href=True):
                href = a.get('href', '')
                text = a.get_text(strip=True)
                
                # Make URL absolute
                abs_url = urljoin(url, href)
                links.append({
                    'url': abs_url,
                    'text': text
                })
        
        # If we didn't find links in toctrees, look in other common areas
        if not links:
            # Look for the module list in content areas
            content_areas = [
                soup.find('div', class_='section'),  # Common in RTD
                soup.find('div', class_='document'),
                soup.find('div', id='content'),
                soup.find('div', class_='content'),
                soup.find('div', role='main'),
                soup # Fallback to entire document
            ]
            
            for content in content_areas:
                if content:
                    # Find all links within list items that might be modules
                    for li in content.find_all('li'):
                        for a in li.find_all('a', href=True):
                            href = a.get('href', '')
                            text = a.get_text(strip=True)
                            
                            # Filter for likely module links
                            if href and ('module' in href.lower() or 
                                        'module' in text.lower() or 
                                        text.endswith('module') or
                                        '.html' in href.lower()):
                                # Make URL absolute
                                abs_url = urljoin(url, href)
                                links.append({
                                    'url': abs_url,
                                    'text': text
                                })
        
        # If still no links, look for links in the sidebar
        if not links:
            # ReadTheDocs sidebar navigation
            sidebar = soup.find('div', class_='sphinxsidebar') or soup.find('nav', class_='wy-nav-side')
            if sidebar:
                for a in sidebar.find_all('a', href=True):
                    href = a.get('href', '')
                    text = a.get_text(strip=True)
                    
                    # Focus on likely module links
                    if href and not href.startswith('#') and ('.html' in href or 'module' in href.lower() or 'module' in text.lower()):
                        # Make URL absolute
                        abs_url = urljoin(url, href)
                        links.append({
                            'url': abs_url,
                            'text': text
                        })
        
        # If we still have no links, grab all HTML links as a last resort
        if not links:
            # Get all links from the page
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                text = a.get_text(strip=True)
                
                # Exclude anchor links and non-HTML links
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    # Only include internal links to the same domain
                    if not href.startswith(('http://', 'https://')) or url in href:
                        abs_url = urljoin(url, href)
                        # Only get .html links or links that look like documentation
                        if '.html' in abs_url or 'module' in abs_url.lower() or 'api' in abs_url.lower():
                            links.append({
                                'url': abs_url,
                                'text': text
                            })
        
        # Remove duplicates while preserving order
        unique_links = []
        seen_urls = set()
        for link in links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        return unique_links
