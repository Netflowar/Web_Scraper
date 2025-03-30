"""
Flask web application for WebScraperUI
"""
import os
import logging
import datetime
import json
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename

from webscraperui.scraper import WebScraper
from webscraperui.enhanced_scraper import EnhancedWebScraper
from webscraperui.link_extractor import LinkExtractor
from webscraperui.doc_combiner import DocumentCombiner
# Import the PDF Extractor
from pdf_extractor import PDFExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', os.path.join(os.getcwd(), 'scraped_data'))

# Template filter for timestamps
@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(timestamp):
    """Convert a timestamp to a formatted datetime string"""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Ensure output directory exists
output_folder = os.environ.get('OUTPUT_FOLDER', os.path.join(os.path.expanduser('~'), 'Documents', 'WebScraperUI', 'scraped_data'))
app.config['OUTPUT_FOLDER'] = output_folder
if not os.path.exists(app.config['OUTPUT_FOLDER']):
    os.makedirs(app.config['OUTPUT_FOLDER'])

# Initialize scrapers
scraper = WebScraper(output_folder=app.config['OUTPUT_FOLDER'])
enhanced_scraper = None  # We'll initialize it on demand to avoid loading Selenium unnecessarily

@app.route('/')
def index():
    """Render the merged main page with tabs for different scraping modes"""
    # Determine active tab from query parameter or default to single-url
    active_tab = request.args.get('tab', 'single-url')
    return render_template('index_merged.html', active_tab=active_tab)

@app.route('/quit')
def quit_app():
    """Shutdown the server and exit the application"""
    import os
    import signal
    import threading
    
    def shutdown():
        # Wait a moment for the response to be sent
        import time
        time.sleep(0.5)
        # Exit the application
        os.kill(os.getpid(), signal.SIGTERM)
    
    # Start a thread to shutdown the server
    threading.Thread(target=shutdown).start()
    
    return "Application is shutting down..."

@app.route('/scrape', methods=['POST'])
def scrape():
    """Handle form submission and run the scraper"""
    if request.method == 'POST':
        url = request.form.get('url', '')
        depth = int(request.form.get('depth', 1))
        output_format = request.form.get('output_format', 'txt')
        scraper_type = request.form.get('scraper_type', 'basic')
        
        if not url:
            flash('Please enter a URL to scrape', 'error')
            return redirect(url_for('index', tab='single-url'))
        
        try:
            # First check if the URL is a PDF
            pdf_extractor = PDFExtractor(output_folder=app.config['OUTPUT_FOLDER'])
            if pdf_extractor.is_pdf_url(url):
                logger.info(f"Detected PDF URL: {url}, redirecting to PDF extractor")
                # Extract the PDF content
                extract_images = True  # Default for PDFs
                result = pdf_extractor.extract_from_url(
                    url, 
                    output_format=output_format,
                    extract_images=extract_images
                )
                
                # Add output format to the result
                result['output_format'] = output_format
                
                flash('PDF extraction completed successfully', 'success')
                return render_template('pdf_results.html', result=result)
            
            # If not a PDF, use the appropriate web scraper
            if scraper_type == 'enhanced':
                # Initialize enhanced scraper if needed
                global enhanced_scraper
                if enhanced_scraper is None:
                    enhanced_scraper = EnhancedWebScraper(output_folder=app.config['OUTPUT_FOLDER'])
                
                # Run the enhanced scraper
                result = enhanced_scraper.scrape(
                    url, 
                    depth=depth, 
                    output_format=output_format,
                    scroll=True,
                    wait_time=5
                )
            else:
                # Run the basic scraper
                result = scraper.scrape(url, depth=depth, output_format=output_format)
            
            # Store the result in session for display
            session['result'] = result
            
            flash('Scraping completed successfully', 'success')
            return render_template('results_enhanced.html', result=result)
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            flash(f'Error during scraping: {str(e)}', 'error')
            return redirect(url_for('index', tab='single-url'))
    
    return redirect(url_for('index', tab='single-url'))

@app.route('/results')
def results():
    """Display scraping results"""
    result = session.get('result')
    if not result:
        flash('No scraping results available', 'warning')
        return redirect(url_for('index', tab='single-url'))
    
    return render_template('results_enhanced.html', result=result)

@app.route('/view/<path:filename>')
def view_file(filename):
    """View a scraped file"""
    try:
        full_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Security check to prevent directory traversal
        if not os.path.normpath(full_path).startswith(os.path.normpath(app.config['OUTPUT_FOLDER'])):
            flash('Invalid file path', 'error')
            return redirect(url_for('index', tab='single-url'))
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext == '.json':
            return render_template('view_text_enhanced.html', filename=filename, content=content)
        elif file_ext == '.html':
            # Use HTML wrapper template with iframe
            return render_template('html_wrapper.html', filename=filename)
        else:
            return render_template('view_text_enhanced.html', filename=filename, content=content)
            
    except Exception as e:
        logger.error(f"Error viewing file {filename}: {str(e)}")
        flash(f'Error viewing file: {str(e)}', 'error')
        return redirect(url_for('index', tab='single-url'))

@app.route('/raw_html/<path:filename>')
def raw_html(filename):
    """Serve raw HTML content for iframe"""
    try:
        full_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Security check to prevent directory traversal
        if not os.path.normpath(full_path).startswith(os.path.normpath(app.config['OUTPUT_FOLDER'])):
            return "Access denied", 403
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return content
            
    except Exception as e:
        logger.error(f"Error viewing raw HTML file {filename}: {str(e)}")
        return f"Error loading file: {str(e)}", 500

@app.route('/history')
def history():
    """View history of scraped files"""
    try:
        files = []
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], filename)):
                files.append({
                    'name': filename,
                    'path': filename,
                    'size': os.path.getsize(os.path.join(app.config['OUTPUT_FOLDER'], filename)),
                    'date': os.path.getmtime(os.path.join(app.config['OUTPUT_FOLDER'], filename))
                })
        
        # Sort by date (newest first)
        files.sort(key=lambda x: x['date'], reverse=True)
        
        return render_template('history_enhanced.html', files=files)
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        flash(f'Error listing files: {str(e)}', 'error')
        return redirect(url_for('index', tab='single-url'))

# Documentation Link Extraction routes
@app.route('/doc_links')
def extract_doc_links_page():
    """Redirect to main page with the doc-links tab active"""
    return redirect(url_for('index', tab='doc-links'))

@app.route('/pdf')
def pdf_extract_page():
    """Redirect to main page with the pdf-extract tab active"""
    return redirect(url_for('index', tab='pdf-extract'))

@app.route('/extract_doc_links', methods=['POST'])
def extract_doc_links():
    """Handle form submission and extract documentation links"""
    if request.method == 'POST':
        url = request.form.get('url', '')
        filter_pattern = request.form.get('filter_pattern', '')
        auto_scrape = request.form.get('auto_scrape') == 'true'
        max_links = int(request.form.get('max_links', 10))
        output_format = request.form.get('output_format', 'html')
        
        if not url:
            flash('Please enter a URL to extract links from', 'error')
            return redirect(url_for('index', tab='doc-links'))
        
        try:
            # Initialize the link extractor
            extractor = LinkExtractor()
            
            # Initialize the appropriate scraper
            global enhanced_scraper
            if enhanced_scraper is None:
                enhanced_scraper = EnhancedWebScraper(output_folder=app.config['OUTPUT_FOLDER'])
            
            # Get the HTML content from the URL
            result = enhanced_scraper.get_html_content(url)
            html_content = result.get('html', '')
            
            if not html_content:
                flash('Failed to retrieve content from the URL', 'error')
                return redirect(url_for('index', tab='doc-links'))
            
            # Detect if this is a ReadTheDocs site or similar documentation platform
            is_readthedocs = 'readthedocs.io' in url.lower()
            
            links = []
            
            # Extract links with specialized handling for documentation sites
            if is_readthedocs:
                logger.info("Detected ReadTheDocs site, using specialized extraction")
                # Get module links specifically for ReadTheDocs
                module_links = extractor.extract_readthedocs_modules(url, html_content)
                
                # Also get regular links from the page
                regular_links = extractor.extract_links_from_html(html_content)
                regular_links = extractor.make_links_absolute(regular_links, url)
                
                # Combine links, prioritizing the specialized module links
                seen_urls = set(link['url'] for link in module_links)
                for link in regular_links:
                    if link['url'] not in seen_urls:
                        module_links.append(link)
                
                links = module_links
            else:
                # Extract links normally for non-ReadTheDocs sites
                links = extractor.extract_links_from_html(html_content)
                links = extractor.make_links_absolute(links, url)
            
            # Filter links to the same domain (avoid external links)
            base_domain = urlparse(url).netloc
            links = [link for link in links if urlparse(link['url']).netloc == base_domain]
            
            # Filter links if a pattern is specified
            if filter_pattern:
                links = extractor.filter_links_by_pattern(links, filter_pattern)
            
            # Get the structure of the documentation
            structure = extractor.get_doc_structure(links)
            
            # If there are too few links categorized as modules or submodules,
            # check if we might have missed them and try harder
            total_modules = len(structure['modules']) + len(structure['submodules'])
            if is_readthedocs and total_modules < 3:
                logger.info("Few modules found, trying deeper extraction")
                # Try to find module links in the sidebar or navigation
                sidebar_links = []
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Check sidebar navigation (common in ReadTheDocs)
                sidebar = soup.find('div', class_='sphinxsidebar') or soup.find('div', class_='sidebar')
                if sidebar:
                    for a in sidebar.find_all('a', href=True):
                        href = a.get('href', '')
                        text = a.get_text(strip=True)
                        
                        # Only include internal links
                        if href and not href.startswith(('http://', 'https://')) or href.startswith(url):
                            abs_url = urljoin(url, href)
                            sidebar_links.append({
                                'url': abs_url,
                                'text': text
                            })
                
                # Add these links to our collection
                for link in sidebar_links:
                    if link['url'] not in [l['url'] for l in links]:
                        links.append(link)
                
                # Recategorize
                structure = extractor.get_doc_structure(links)
            
            # Limit the number of links per category
            max_per_category = max(3, max_links // 4)  # At least 3 per category
            for category in structure:
                structure[category] = structure[category][:max_per_category]
            
            # Flatten structure for total link count
            all_links = []
            for category in structure:
                all_links.extend(structure[category])
            
            # Ensure we don't exceed max_links
            if len(all_links) > max_links:
                all_links = all_links[:max_links]
                
                # Rebuild structure with limited links
                new_structure = {category: [] for category in structure}
                for link in all_links:
                    for category in structure:
                        if link in structure[category]:
                            new_structure[category].append(link)
                            break
                structure = new_structure
            
            # Store the results in session
            session['doc_links'] = {
                'base_url': url,
                'links': all_links,
                'structure': structure,
                'output_format': output_format
            }
            
            # If auto_scrape is enabled, queue up all links for scraping
            if auto_scrape:
                return redirect(url_for('scrape_all_links', output_format=output_format))
            
            flash('Successfully extracted documentation links', 'success')
            return render_template(
                'doc_links_results.html', 
                links=all_links,
                structure=structure,
                base_url=url,
                output_format=output_format
            )
            
        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")
            flash(f'Error extracting links: {str(e)}', 'error')
            return redirect(url_for('index', tab='doc-links'))
    
    return redirect(url_for('index', tab='doc-links'))

@app.route('/scrape_link')
def scrape_link():
    """Scrape a single link"""
    url = request.args.get('url', '')
    output_format = request.args.get('output_format', 'html')
    
    if not url:
        flash('No URL provided for scraping', 'error')
        return redirect(url_for('index', tab='doc-links'))
    
    try:
        # Use the enhanced scraper for better compatibility
        global enhanced_scraper
        if enhanced_scraper is None:
            enhanced_scraper = EnhancedWebScraper(output_folder=app.config['OUTPUT_FOLDER'])
        
        # Detect if this is a ReadTheDocs site for specialized handling
        is_readthedocs = 'readthedocs.io' in url.lower()
        
        # For ReadTheDocs, use a higher depth to capture module content
        depth = 2 if is_readthedocs else 1
        
        # Use longer wait time and ensure scrolling for JavaScript-heavy sites
        wait_time = 8 if is_readthedocs else 5
        
        # Scrape the URL with optimized parameters
        result = enhanced_scraper.scrape(
            url, 
            depth=depth, 
            output_format=output_format,
            scroll=True,
            wait_time=wait_time
        )
        
        flash(f'Successfully scraped: {url}', 'success')
        return render_template('results_improved.html', result=result)
        
    except Exception as e:
        logger.error(f"Error scraping link: {str(e)}")
        flash(f'Error scraping link: {str(e)}', 'error')
        return redirect(url_for('index', tab='doc-links'))

@app.route('/scrape_all_links')
def scrape_all_links():
    """Scrape all links extracted from documentation"""
    output_format = request.args.get('output_format', 'html')
    
    # Get stored links from session
    doc_links_data = session.get('doc_links', {})
    links = []
    
    # Gather all links from the structure
    structure = doc_links_data.get('structure', {})
    for category in structure:
        links.extend(structure[category])
    
    if not links:
        flash('No links found to scrape', 'warning')
        return redirect(url_for('index', tab='doc-links'))
    
    try:
        # Use the enhanced scraper for better compatibility
        global enhanced_scraper
        if enhanced_scraper is None:
            enhanced_scraper = EnhancedWebScraper(output_folder=app.config['OUTPUT_FOLDER'])
        
        # Create a results summary
        results = []
        scrape_count = 0
        error_count = 0
        
        # Check if this is a documentation site for specialized handling
        base_url = doc_links_data.get('base_url', '')
        is_readthedocs = 'readthedocs.io' in base_url.lower()
        
        # For ReadTheDocs sites, prioritize module and API links first
        if is_readthedocs:
            # Prioritize API and module links
            prioritized_links = []
            
            # First add module links
            for link in structure.get('modules', []):
                prioritized_links.append(link)
            
            # Then add submodule links
            for link in structure.get('submodules', []):
                prioritized_links.append(link)
            
            # Then add main links
            for link in structure.get('main', []):
                if link not in prioritized_links:
                    prioritized_links.append(link)
            
            # Then add other links
            for link in structure.get('other', []):
                if link not in prioritized_links:
                    prioritized_links.append(link)
            
            links = prioritized_links
        
        # Determine reasonable batch size based on total links
        # For ReadTheDocs sites, we want to get all module documentation
        max_links = min(len(links), 30) if is_readthedocs else min(len(links), 15)
        
        # Show progress info to user
        flash(f'Starting batch scrape of {max_links} links. This may take a few minutes...', 'info')
        
        # Scrape each link
        for i, link in enumerate(links[:max_links]):
            try:
                logger.info(f"Scraping link {i+1}/{max_links}: {link['url']}")
                
                # For ReadTheDocs, use specialized parameters
                # Use higher depth for module pages to capture related content
                depth = 2 if is_readthedocs else 1
                
                # Longer wait time for documentation sites with complex JavaScript
                wait_time = 10 if is_readthedocs else 5
                
                # Set scroll to True for all documentation pages to ensure complete content capture
                scroll = True
                
                result = enhanced_scraper.scrape(
                    link['url'], 
                    depth=depth, 
                    output_format=output_format,
                    scroll=scroll,
                    wait_time=wait_time
                )
                
                results.append({
                    'url': link['url'],
                    'text': link['text'],
                    'status': 'success',
                    'file': result.get('output_path', '')
                })
                scrape_count += 1
            except Exception as e:
                logger.error(f"Error scraping {link['url']}: {str(e)}")
                results.append({
                    'url': link['url'],
                    'text': link['text'],
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        # Create a summary result
        summary = {
            'total_links': len(links),
            'processed_links': max_links,
            'successful': scrape_count,
            'failed': error_count,
            'results': results,
            'output_format': output_format,
            'is_readthedocs': is_readthedocs
        }
        
        # Store the summary in session
        session['scrape_summary'] = summary
        
        # Show a success message
        flash(f'Successfully scraped {scrape_count} out of {max_links} links', 'success')
        
        # Render the batch results template
        return render_template('batch_results.html', result={
            'title': 'Batch Scraping Results',
            'url': base_url,
            'output_path': 'Multiple files',
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error during batch scraping: {str(e)}")
        flash(f'Error during batch scraping: {str(e)}', 'error')
        return redirect(url_for('index', tab='doc-links'))

# Documentation Combination routes
@app.route('/combine_docs', methods=['GET', 'POST'])
def combine_docs_page():
    """Render the documentation combination page or process the form submission"""
    if request.method == 'POST':
        # Get form data
        selected_files = request.form.getlist('files')
        output_format = request.form.get('output_format', 'html')
        title = request.form.get('title', 'Combined Documentation')
        
        if not selected_files:
            flash('Please select at least one file to combine', 'warning')
            return redirect(url_for('combine_docs_page'))
        
        try:
            # Get full paths
            file_paths = [os.path.join(app.config['OUTPUT_FOLDER'], filename) for filename in selected_files]
            
            # Initialize the document combiner
            combiner = DocumentCombiner(output_folder=app.config['OUTPUT_FOLDER'])
            
            # Combine the files
            output_path = combiner.combine_files(file_paths, output_format, title)
            
            # Get the filename from the full path
            output_filename = os.path.basename(output_path)
            
            flash(f'Successfully combined {len(selected_files)} files', 'success')
            
            # Redirect to view the combined file
            return redirect(url_for('view_file', filename=output_filename))
            
        except Exception as e:
            logger.error(f"Error combining files: {str(e)}")
            flash(f'Error combining files: {str(e)}', 'error')
            return redirect(url_for('combine_docs_page'))
    
    # GET request - display the form
    try:
        # Get all files in the output folder
        files = []
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            if os.path.isfile(file_path):
                # Only include HTML and TXT files
                if filename.endswith(('.html', '.txt')):
                    files.append({
                        'name': filename,
                        'path': filename,
                        'size': os.path.getsize(file_path),
                        'date': os.path.getmtime(file_path)
                    })
        
        # Sort by date (newest first)
        files.sort(key=lambda x: x['date'], reverse=True)
        
        # Get batch info from session if coming from batch scraping
        batch_info = session.get('scrape_summary', {})
        
        return render_template('combine_docs.html', files=files, batch_info=batch_info)
        
    except Exception as e:
        logger.error(f"Error getting files for combination: {str(e)}")
        flash(f'Error getting files: {str(e)}', 'error')
        return redirect(url_for('index', tab='single-url'))

@app.route('/combine_batch')
def combine_batch():
    """Combine files from the most recent batch scraping"""
    batch_info = session.get('scrape_summary', {})
    
    if not batch_info or 'results' not in batch_info:
        flash('No batch scraping results found', 'warning')
        return redirect(url_for('combine_docs_page'))
    
    try:
        # Get successfully scraped files
        successful_results = [result for result in batch_info['results'] if result['status'] == 'success' and 'file' in result]
        
        if not successful_results:
            flash('No successful scrapes found in the batch', 'warning')
            return redirect(url_for('combine_docs_page'))
        
        # Get file paths
        file_paths = [os.path.join(app.config['OUTPUT_FOLDER'], result['file'].split('/')[-1]) 
                     for result in successful_results]
        
        # Get the output format from the batch
        output_format = batch_info.get('output_format', 'html')
        
        # Generate a title based on the base URL if available
        base_url = session.get('doc_links', {}).get('base_url', '')
        if base_url:
            site_name = urlparse(base_url).netloc.split('.')[0].capitalize()
            title = f"{site_name} Documentation"
        else:
            title = "Combined Documentation"
        
        # Initialize the document combiner
        combiner = DocumentCombiner(output_folder=app.config['OUTPUT_FOLDER'])
        
        # Combine the files
        output_path = combiner.combine_files(file_paths, output_format, title)
        
        # Get the filename from the full path
        output_filename = os.path.basename(output_path)
        
        flash(f'Successfully combined {len(file_paths)} files from batch scraping', 'success')
        
        # Redirect to view the combined file
        return redirect(url_for('view_file', filename=output_filename))
        
    except Exception as e:
        logger.error(f"Error combining batch files: {str(e)}")
        flash(f'Error combining batch files: {str(e)}', 'error')
        return redirect(url_for('combine_docs_page'))

# PDF Extraction routes
@app.route('/pdf_extract', methods=['GET', 'POST'])
def pdf_extract():
    """Render the PDF extraction page or process the form submission"""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'pdf_file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if pdf_file and pdf_file.filename.lower().endswith('.pdf'):
            # Secure the filename
            filename = secure_filename(pdf_file.filename)
            
            # Create a temporary folder for uploaded PDFs
            upload_folder = os.path.join(app.config['OUTPUT_FOLDER'], 'temp_uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Save the uploaded file
            file_path = os.path.join(upload_folder, filename)
            pdf_file.save(file_path)
            
            try:
                # Get form data
                output_format = request.form.get('output_format', 'txt')
                extract_images = request.form.get('extract_images') == 'true'
                
                # Initialize the PDF extractor
                pdf_extractor = PDFExtractor(output_folder=app.config['OUTPUT_FOLDER'])
                
                # Extract and save the PDF content
                result = pdf_extractor.extract_and_save(
                    file_path, 
                    output_format=output_format,
                    extract_images=extract_images
                )
                
                # Add output format to the result
                result['output_format'] = output_format
                
                flash('PDF extraction completed successfully', 'success')
                return render_template('pdf_results.html', result=result)
                
            except Exception as e:
                logger.error(f"Error extracting PDF: {str(e)}")
                flash(f'Error extracting PDF: {str(e)}', 'error')
                return redirect(request.url)
            
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            flash('Please upload a PDF file', 'error')
            return redirect(request.url)
    
    # GET request - display the form
    return render_template('pdf_extract.html')

@app.route('/pdf_url', methods=['POST'])
def extract_pdf_url():
    """Extract content from a PDF URL"""
    if request.method == 'POST':
        url = request.form.get('url', '')
        output_format = request.form.get('output_format', 'html')
        extract_images = request.form.get('extract_images') == 'true'
        
        if not url:
            flash('Please enter a URL to a PDF file', 'error')
            return redirect(url_for('index', tab='single-url'))
        
        try:
            # Initialize the PDF extractor
            pdf_extractor = PDFExtractor(output_folder=app.config['OUTPUT_FOLDER'])
            
            # Check if the URL is a PDF
            if not pdf_extractor.is_pdf_url(url):
                flash('The provided URL does not appear to be a PDF. Please try the web scraper instead.', 'warning')
                return redirect(url_for('index', tab='single-url'))
            
            # Extract and save the PDF content
            result = pdf_extractor.extract_from_url(
                url, 
                output_format=output_format,
                extract_images=extract_images
            )
            
            # Add output format to the result
            result['output_format'] = output_format
            
            flash('PDF extraction completed successfully', 'success')
            return render_template('pdf_results.html', result=result)
            
        except Exception as e:
            logger.error(f"Error extracting PDF from URL: {str(e)}")
            flash(f'Error extracting PDF: {str(e)}', 'error')
            return redirect(url_for('index', tab='single-url'))
    
    return redirect(url_for('index', tab='single-url'))

@app.route('/serve_image/<path:image_path>')
def serve_image(image_path):
    """Serve extracted images from PDF"""
    try:
        # Full path to the image
        full_path = os.path.join(app.config['OUTPUT_FOLDER'], image_path)
        
        # Security check to prevent directory traversal
        if not os.path.normpath(full_path).startswith(os.path.normpath(app.config['OUTPUT_FOLDER'])):
            return "Access denied", 403
        
        # Serve the image file
        return send_file(full_path)
            
    except Exception as e:
        logger.error(f"Error serving image {image_path}: {str(e)}")
        return f"Error loading image: {str(e)}", 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_improved.html'), 404

def main():
    """
    Entry point for the application when used as a console script
    """
    # Set the output folder
    output_folder = os.path.join(os.getcwd(), 'scraped_data')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    app.config['OUTPUT_FOLDER'] = output_folder
    
    # Run the app
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    main()
