#!/usr/bin/env python3
"""
PDF Extractor module for extracting content from PDF files
"""
import os
import json
import logging
import datetime
import tempfile
import requests
import PyPDF2
from urllib.parse import urlparse
from io import BytesIO

from webscraperui.analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Class for extracting content from PDF files"""
    
    def __init__(self, output_folder="./pdf_output"):
        """
        Initialize the PDF Extractor
        
        Args:
            output_folder: Folder to save extracted data
        """
        self.output_folder = output_folder
        self.analyzer = ContentAnalyzer()
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    def extract_text(self, pdf_path, extract_images=False):
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            extract_images: Whether to extract images (default: False)
            
        Returns:
            dict: Extracted data
        """
        try:
            logger.info(f"Extracting text from {pdf_path}")
            
            # Open the PDF file
            pdf = PyPDF2.PdfReader(pdf_path)
            
            # Extract metadata
            metadata = self._extract_metadata(pdf)
            
            # Extract text content from all pages
            content = ""
            page_texts = []
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    page_texts.append({
                        "page_number": i + 1,
                        "content": page_text
                    })
                    content += page_text + "\n\n"
            
            # Extract images if requested
            images = []
            if extract_images:
                images = self.extract_images(pdf_path)
            
            # Analyze the content if there's text to analyze
            analysis_results = {}
            if content.strip():
                try:
                    analysis_results = self.analyzer.analyze_text(content)
                except Exception as e:
                    logger.error(f"Error analyzing PDF content: {str(e)}")
            
            # Create result dictionary
            result = {
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "content": content.strip(),
                "page_count": len(pdf.pages),
                "page_texts": page_texts,
                "metadata": metadata,
                "extracted_images": images,
                "analysis": analysis_results,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def extract_images(self, pdf_path):
        """
        Extract images from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            list: List of extracted image info
        """
        # This is a placeholder for the image extraction functionality
        # Implementing full image extraction is complex and would require additional libraries
        # like fitz (PyMuPDF) for better image extraction
        logger.info(f"Image extraction from {pdf_path} not implemented yet")
        return []
    
    def extract_from_url(self, url, output_format="txt", extract_images=False):
        """
        Extract text content from a PDF file at the given URL
        
        Args:
            url: URL to the PDF file
            output_format: Format for saving output (txt, json, html)
            extract_images: Whether to extract images
            
        Returns:
            dict: Extracted data
        """
        try:
            logger.info(f"Downloading and extracting PDF from {url}")
            
            # Download the PDF
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Create a temporary file to store the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Extract and save the content
            try:
                result = self.extract_and_save(temp_path, output_format, extract_images)
                # Add URL to the result
                result["url"] = url
                return result
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except Exception as e:
            logger.error(f"Error extracting PDF from URL {url}: {str(e)}")
            raise
    
    def is_pdf_url(self, url):
        """
        Check if a URL points to a PDF file
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if URL is a PDF, False otherwise
        """
        # First check the URL extension and path
        url_path = urlparse(url).path.lower()
        if url_path.endswith('.pdf'):
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
    
    def _extract_metadata(self, pdf):
        """
        Extract metadata from a PDF document
        
        Args:
            pdf: PyPDF2 PdfReader object
            
        Returns:
            dict: Extracted metadata
        """
        raw_metadata = pdf.metadata or {}
        
        # Convert PDF metadata to a more user-friendly format
        metadata = {
            "title": raw_metadata.get("/Title", ""),
            "author": raw_metadata.get("/Author", ""),
            "subject": raw_metadata.get("/Subject", ""),
            "keywords": raw_metadata.get("/Keywords", ""),
            "creator": raw_metadata.get("/Creator", ""),
            "producer": raw_metadata.get("/Producer", ""),
            "creation_date": raw_metadata.get("/CreationDate", ""),
            "modification_date": raw_metadata.get("/ModDate", "")
        }
        
        return metadata
    
    def extract_and_save(self, pdf_path, output_format="txt", extract_images=False):
        """
        Extract content from a PDF and save it to a file
        
        Args:
            pdf_path: Path to the PDF file
            output_format: Format to save in (txt, json, html)
            extract_images: Whether to extract images
            
        Returns:
            dict: Result info including output path
        """
        try:
            # Extract content from the PDF
            result = self.extract_text(pdf_path, extract_images=extract_images)
            
            # Create a filename based on the PDF filename and timestamp
            pdf_filename = os.path.basename(pdf_path)
            filename_base = os.path.splitext(pdf_filename)[0]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_base}_{timestamp}"
            
            # Determine the output path based on the format
            if output_format == "json":
                output_path = os.path.join(self.output_folder, f"{filename}.json")
                self._save_as_json(result, output_path)
            elif output_format == "html":
                output_path = os.path.join(self.output_folder, f"{filename}.html")
                self._save_as_html(result, output_path)
            else:
                # Default to TXT format
                output_path = os.path.join(self.output_folder, f"{filename}.txt")
                self._save_as_text(result, output_path)
            
            # Add the output path to the result
            result["output_path"] = output_path
            
            logger.info(f"Saved PDF content to {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error saving PDF content: {str(e)}")
            raise
    
    def _save_as_text(self, data, output_path):
        """
        Save extracted PDF data as a text file
        
        Args:
            data: Extracted PDF data
            output_path: Path to save the output file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            # Write metadata
            f.write(f"Title: {data['metadata']['title']}\n")
            f.write(f"Author: {data['metadata']['author']}\n")
            f.write(f"Subject: {data['metadata']['subject']}\n")
            f.write(f"Keywords: {data['metadata']['keywords']}\n")
            f.write(f"Creator: {data['metadata']['creator']}\n")
            f.write(f"Producer: {data['metadata']['producer']}\n")
            f.write(f"Creation Date: {data['metadata']['creation_date']}\n")
            f.write(f"Modification Date: {data['metadata']['modification_date']}\n")
            f.write(f"Pages: {data['page_count']}\n")
            f.write(f"Extracted: {data['timestamp']}\n")
            f.write("\n")
            
            # Write content
            f.write("=== CONTENT ===\n\n")
            f.write(data['content'])
    
    def _save_as_json(self, data, output_path):
        """
        Save extracted PDF data as a JSON file
        
        Args:
            data: Extracted PDF data
            output_path: Path to save the output file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def _save_as_html(self, data, output_path):
        """
        Save extracted PDF data as an HTML file
        
        Args:
            data: Extracted PDF data
            output_path: Path to save the output file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{data['metadata']['title'] or data['file_name']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #333; }}
                    .metadata {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                    .content {{ line-height: 1.6; white-space: pre-wrap; }}
                    .page {{ margin-top: 20px; padding: 10px; border-top: 1px solid #ccc; }}
                </style>
            </head>
            <body>
                <h1>{data['metadata']['title'] or 'PDF Content'}</h1>
                
                <div class="metadata">
                    <p><strong>File:</strong> {data['file_name']}</p>
                    <p><strong>Author:</strong> {data['metadata']['author']}</p>
                    <p><strong>Subject:</strong> {data['metadata']['subject']}</p>
                    <p><strong>Keywords:</strong> {data['metadata']['keywords']}</p>
                    <p><strong>Pages:</strong> {data['page_count']}</p>
                    <p><strong>Extracted:</strong> {data['timestamp']}</p>
                </div>
                
                <div class="content">
                    <h2>Content</h2>
            """
            
            # Add page-by-page content
            for page in data['page_texts']:
                html += f"""
                    <div class="page">
                        <h3>Page {page['page_number']}</h3>
                        <div class="page-content">{page['content']}</div>
                    </div>
                """
            
            html += """
                </div>
            </body>
            </html>
            """
            
            f.write(html)
