import unittest
import os
import sys
import tempfile
from bs4 import BeautifulSoup

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test (we'll create this later)
from webscraperui.link_extractor import LinkExtractor

class TestLinkExtractor(unittest.TestCase):
    """Tests for the LinkExtractor class"""

    def setUp(self):
        """Set up test data"""
        self.extractor = LinkExtractor()
        
        # Sample HTML for documentation pages
        self.doc_html = """
        <html>
            <body>
                <div class="section">
                    <h1>API Reference</h1>
                    <ul>
                        <li><a href="/docs/module1.html">Module 1</a></li>
                        <li><a href="/docs/module2.html">Module 2</a></li>
                        <li><a href="/docs/module3.html">Module 3</a></li>
                    </ul>
                    <div class="subsection">
                        <h2>Submodules</h2>
                        <ul>
                            <li><a href="/docs/submodule1.html">Submodule 1</a></li>
                            <li><a href="/docs/submodule2.html">Submodule 2</a></li>
                        </ul>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Create a temporary file with the HTML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        self.temp_file.write(self.doc_html.encode('utf-8'))
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up after tests"""
        os.unlink(self.temp_file.name)
    
    def test_extract_links_from_html(self):
        """Test extracting links from HTML content"""
        links = self.extractor.extract_links_from_html(self.doc_html)
        
        # Check that links were extracted correctly
        self.assertEqual(len(links), 5)
        self.assertIn({'url': '/docs/module1.html', 'text': 'Module 1'}, links)
        self.assertIn({'url': '/docs/module2.html', 'text': 'Module 2'}, links)
        self.assertIn({'url': '/docs/submodule1.html', 'text': 'Submodule 1'}, links)
    
    def test_extract_links_from_file(self):
        """Test extracting links from an HTML file"""
        links = self.extractor.extract_links_from_file(self.temp_file.name)
        
        # Check that links were extracted correctly
        self.assertEqual(len(links), 5)
        self.assertIn({'url': '/docs/module1.html', 'text': 'Module 1'}, links)
    
    def test_make_links_absolute(self):
        """Test converting relative links to absolute URLs"""
        base_url = 'https://example.com'
        relative_links = [
            {'url': '/docs/module1.html', 'text': 'Module 1'},
            {'url': 'relative/path.html', 'text': 'Relative Path'},
            {'url': 'https://another-domain.com/page.html', 'text': 'Already Absolute'}
        ]
        
        absolute_links = self.extractor.make_links_absolute(relative_links, base_url)
        
        # Check that relative links were made absolute
        self.assertEqual(absolute_links[0]['url'], 'https://example.com/docs/module1.html')
        self.assertEqual(absolute_links[1]['url'], 'https://example.com/relative/path.html')
        # Already absolute URLs should remain unchanged
        self.assertEqual(absolute_links[2]['url'], 'https://another-domain.com/page.html')
    
    def test_filter_links_by_pattern(self):
        """Test filtering links by a pattern"""
        links = [
            {'url': 'https://example.com/docs/module1.html', 'text': 'Module 1'},
            {'url': 'https://example.com/docs/module2.html', 'text': 'Module 2'},
            {'url': 'https://example.com/about.html', 'text': 'About'}
        ]
        
        # Filter links containing 'module' in the URL
        filtered_links = self.extractor.filter_links_by_pattern(links, 'module')
        
        # Check that only matching links were returned
        self.assertEqual(len(filtered_links), 2)
        self.assertIn({'url': 'https://example.com/docs/module1.html', 'text': 'Module 1'}, filtered_links)
        self.assertIn({'url': 'https://example.com/docs/module2.html', 'text': 'Module 2'}, filtered_links)
        
if __name__ == '__main__':
    unittest.main()
