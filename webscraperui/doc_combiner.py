"""
Document Combiner module for WebScraperUI

This module provides functionality to combine multiple scraped documentation files
into a single comprehensive document.
"""
import os
import json
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DocumentCombiner:
    """
    A class to combine multiple scraped documentation files into a single document.
    
    This is particularly useful for creating comprehensive documentation from
    multiple separate module pages.
    """
    
    def __init__(self, output_folder):
        """
        Initialize the DocumentCombiner.
        
        Args:
            output_folder: Folder where scraped files are stored and where
                           the combined document will be saved
        """
        self.output_folder = output_folder
    
    def combine_html_files(self, file_paths, title="Combined Documentation"):
        """
        Combine multiple HTML files into a single HTML document with navigation.
        
        Args:
            file_paths: List of file paths to combine
            title: Title for the combined document
            
        Returns:
            str: Path to the combined HTML file
        """
        try:
            # Create container HTML
            combined_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>{title}</title>
                <style>
                    /* Basic styles */
                    body {{
                        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        color: #333;
                        display: flex;
                        min-height: 100vh;
                    }}
                    
                    /* Navigation styles */
                    .nav-sidebar {{
                        width: 280px;
                        background: #f8f9fa;
                        border-right: 1px solid #e9ecef;
                        padding: 20px;
                        height: 100vh;
                        position: fixed;
                        overflow-y: auto;
                    }}
                    
                    .nav-sidebar h1 {{
                        font-size: 1.25rem;
                        margin-top: 0;
                        margin-bottom: 1.5rem;
                        padding-bottom: 10px;
                        border-bottom: 1px solid #dee2e6;
                    }}
                    
                    .nav-sidebar ul {{
                        list-style: none;
                        padding-left: 0;
                        margin-bottom: 1.5rem;
                    }}
                    
                    .nav-sidebar li {{
                        margin-bottom: 8px;
                    }}
                    
                    .nav-sidebar a {{
                        color: #495057;
                        text-decoration: none;
                        display: block;
                        padding: 8px 12px;
                        border-radius: 4px;
                        transition: background-color 0.2s;
                    }}
                    
                    .nav-sidebar a:hover {{
                        background-color: #e9ecef;
                        color: #212529;
                    }}
                    
                    .nav-sidebar a.active {{
                        background-color: #4361ee;
                        color: white;
                    }}
                    
                    /* Content styles */
                    .content {{
                        flex-grow: 1;
                        padding: 30px;
                        margin-left: 280px; /* Match sidebar width */
                    }}
                    
                    .section {{
                        margin-bottom: 40px;
                        padding-bottom: 20px;
                        border-bottom: 1px solid #e9ecef;
                    }}
                    
                    .section:last-child {{
                        border-bottom: none;
                    }}
                    
                    .section h2 {{
                        color: #3a0ca3;
                        margin-top: 0;
                        padding-top: 20px;
                    }}
                    
                    /* Top bar styles */
                    .topbar {{
                        position: sticky;
                        top: 0;
                        background: white;
                        padding: 15px 30px;
                        border-bottom: 1px solid #e9ecef;
                        margin-bottom: 20px;
                        z-index: 100;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}
                    
                    .topbar h1 {{
                        margin: 0;
                        font-size: 1.5rem;
                        color: #3a0ca3;
                    }}
                    
                    .topbar .meta {{
                        color: #6c757d;
                        font-size: 0.9rem;
                    }}
                    
                    /* Code block styling */
                    pre {{
                        background-color: #f8f9fa;
                        border: 1px solid #e9ecef;
                        border-radius: 4px;
                        padding: 15px;
                        overflow-x: auto;
                    }}
                    
                    code {{
                        font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
                        color: #e83e8c;
                    }}
                    
                    /* Table styling */
                    table {{
                        width: 100%;
                        margin-bottom: 1rem;
                        color: #212529;
                        border-collapse: collapse;
                    }}
                    
                    th, td {{
                        padding: 0.75rem;
                        vertical-align: top;
                        border-top: 1px solid #dee2e6;
                    }}
                    
                    thead th {{
                        vertical-align: bottom;
                        border-bottom: 2px solid #dee2e6;
                        background-color: #f8f9fa;
                    }}
                    
                    /* Mobile responsiveness */
                    @media (max-width: 768px) {{
                        body {{
                            display: block;
                        }}
                        
                        .nav-sidebar {{
                            width: 100%;
                            height: auto;
                            position: relative;
                        }}
                        
                        .content {{
                            margin-left: 0;
                        }}
                    }}
                </style>
                <!-- Additional script for navigation interactions -->
                <script>
                    document.addEventListener('DOMContentLoaded', function() {{
                        // Add active class to the current section link
                        const navLinks = document.querySelectorAll('.nav-sidebar a');
                        const sections = document.querySelectorAll('.section');
                        
                        window.addEventListener('scroll', function() {{
                            let current = '';
                            
                            sections.forEach(section => {{
                                const sectionTop = section.offsetTop;
                                const sectionHeight = section.clientHeight;
                                if(pageYOffset >= (sectionTop - 200)) {{
                                    current = section.getAttribute('id');
                                }}
                            }});
                            
                            navLinks.forEach(link => {{
                                link.classList.remove('active');
                                if(link.getAttribute('href') === '#' + current) {{
                                    link.classList.add('active');
                                }}
                            }});
                        }});
                    }});
                </script>
            </head>
            <body>
                <div class="nav-sidebar">
                    <h1>Documentation Contents</h1>
                    <ul>
            """
            
            # Process each file and extract content
            sections = []
            for i, file_path in enumerate(file_paths):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Parse HTML
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Get the title or use filename as fallback
                    section_title = soup.find('title')
                    if section_title:
                        section_title = section_title.text.split(' - ')[0].strip()
                    else:
                        section_title = os.path.basename(file_path).split('.')[0]
                    
                    # Clean up titles that come from ReadTheDocs
                    if " — " in section_title:
                        section_title = section_title.split(" — ")[0].strip()
                    
                    # Remove "module" suffix if this is a module doc
                    if section_title.endswith(' module'):
                        section_title = section_title[:-7]
                    
                    # Create section ID
                    section_id = f"section-{i + 1}"
                    
                    # Add to navigation
                    combined_html += f'<li><a href="#{section_id}">{section_title}</a></li>\n'
                    
                    # Extract main content
                    content = None
                    
                    # Try to find the main content area - checking common content containers
                    content_areas = [
                        soup.find('div', class_='document'),
                        soup.find('div', {'role': 'main'}),
                        soup.find('article'),
                        soup.find('div', class_='content'),
                        soup.find('div', class_='section'),
                        soup.body  # Fallback to body if no specific content area found
                    ]
                    
                    for area in content_areas:
                        if area:
                            content = area
                            break
                    
                    # If still no content, use the entire body
                    if not content:
                        content = soup.body
                    
                    # Store the section data
                    sections.append({
                        'id': section_id,
                        'title': section_title,
                        'content': str(content)
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    sections.append({
                        'id': f"section-{i + 1}",
                        'title': f"Error in file {os.path.basename(file_path)}",
                        'content': f"<p>Error processing this file: {str(e)}</p>"
                    })
            
            # Complete the navigation
            combined_html += """
                    </ul>
                </div>
                
                <div class="content">
                    <div class="topbar">
                        <h1>""" + title + """</h1>
                        <div class="meta">
                            Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
                        </div>
                    </div>
            """
            
            # Add each section
            for section in sections:
                combined_html += f"""
                    <div id="{section['id']}" class="section">
                        <h2>{section['title']}</h2>
                        {section['content']}
                    </div>
                """
            
            # Close the HTML
            combined_html += """
                </div>
            </body>
            </html>
            """
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            output_path = os.path.join(self.output_folder, f"combined_{clean_title}_{timestamp}.html")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_html)
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error combining HTML files: {e}")
            raise
    
    def combine_txt_files(self, file_paths, title="Combined Documentation"):
        """
        Combine multiple text files into a single text document.
        
        Args:
            file_paths: List of file paths to combine
            title: Title for the combined document
            
        Returns:
            str: Path to the combined text file
        """
        try:
            combined_text = f"# {title}\n"
            combined_text += f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Process each file
            for i, file_path in enumerate(file_paths):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Extract title from the first line or use filename
                    title_match = re.search(r"Title: (.*)", file_content)
                    if title_match:
                        section_title = title_match.group(1)
                    else:
                        section_title = os.path.basename(file_path)
                    
                    # Add section separator and title
                    combined_text += f"\n\n{'=' * 80}\n"
                    combined_text += f"# {section_title}\n"
                    combined_text += f"{'=' * 80}\n\n"
                    
                    # Add content
                    combined_text += file_content
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    combined_text += f"\n\nError processing file {os.path.basename(file_path)}: {str(e)}\n\n"
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            output_path = os.path.join(self.output_folder, f"combined_{clean_title}_{timestamp}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_text)
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error combining text files: {e}")
            raise
            
    def combine_files(self, file_paths, output_format="html", title="Combined Documentation"):
        """
        Combine multiple files into a single document.
        
        Args:
            file_paths: List of file paths to combine
            output_format: Format of the output file (html, txt)
            title: Title for the combined document
            
        Returns:
            str: Path to the combined file
        """
        if not file_paths:
            raise ValueError("No files provided to combine")
        
        if output_format == "html":
            return self.combine_html_files(file_paths, title)
        elif output_format == "txt":
            return self.combine_txt_files(file_paths, title)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
