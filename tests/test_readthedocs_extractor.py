import unittest
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from webscraperui.link_extractor import LinkExtractor

class TestReadTheDocsExtractor(unittest.TestCase):
    """Tests for extracting links from ReadTheDocs sites"""

    def setUp(self):
        """Set up test data"""
        self.extractor = LinkExtractor()
        
        # Test URL
        self.test_url = "https://acitoolkit.readthedocs.io/en/latest/modules.html"
        
        # Sample HTML content (simplified version of the actual page)
        self.sample_html = """
        <div class="section" id="api-reference">
            <h1>API Reference<a class="headerlink" href="#api-reference">¶</a></h1>
            <div class="toctree-wrapper compound">
                <ul>
                    <li class="toctree-l1"><a class="reference internal" href="acitoolkit.html">acitoolkit package</a>
                        <ul>
                            <li class="toctree-l2"><a class="reference internal" href="acitoolkit.html#submodules">Submodules</a>
                                <ul>
                                    <li class="toctree-l3"><a class="reference internal" href="acitoolkit.acibaseobject.html">acibaseobject module</a></li>
                                    <li class="toctree-l3"><a class="reference internal" href="acitoolkit.aciphysobject.html">aciphysobject module</a></li>
                                    <li class="toctree-l3"><a class="reference internal" href="acitoolkit.acisession.html">acisession module</a></li>
                                    <li class="toctree-l3"><a class="reference internal" href="acitoolkit.acitoolkit.html">acitoolkit module</a></li>
                                    <li class="toctree-l3"><a class="reference internal" href="acitoolkit.acitoolkitlib.html">acitoolkitlib module</a></li>
                                    <li class="toctree-l3"><a class="reference internal" href="acitoolkit.aciFaults.html">aciFaults module</a></li>
                                </ul>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
        """
        
    def test_extract_readthedocs_modules_from_sample(self):
        """Test extracting modules from sample HTML"""
        links = self.extractor.extract_readthedocs_modules(self.test_url, self.sample_html)
        
        # Check that all module links were extracted
        # The number of links might vary depending on extraction logic
        # but should be at least 7 (6 modules + 1 package)
        self.assertGreaterEqual(len(links), 7)
        
        # Check that specific module links were found
        module_names = [link['text'] for link in links]
        self.assertIn('acibaseobject module', module_names)
        self.assertIn('aciphysobject module', module_names)
        self.assertIn('acisession module', module_names)
        self.assertIn('acitoolkit module', module_names)
        self.assertIn('acitoolkitlib module', module_names)
        self.assertIn('aciFaults module', module_names)
        
        # Check that URLs were made absolute
        for link in links:
            self.assertTrue(link['url'].startswith('https://'))

    def test_extract_readthedocs_modules_live(self):
        """Test extracting modules from the live ReadTheDocs site"""
        # This test will be skipped if the site is unreachable
        try:
            response = requests.get(self.test_url, timeout=10)
            if response.status_code != 200:
                self.skipTest(f"Could not access {self.test_url}: Status code {response.status_code}")
            
            html_content = response.text
            links = self.extractor.extract_readthedocs_modules(self.test_url, html_content)
            
            # Should find at least the 6 module links
            self.assertGreaterEqual(len(links), 6)
            
            # Check that all links are absolute
            for link in links:
                self.assertTrue(link['url'].startswith('https://'))
                
            # Verify that at least some expected module links are found
            module_urls = [link['url'] for link in links]
            expected_modules = [
                'acitoolkit.acibaseobject.html',
                'acitoolkit.aciphysobject.html',
                'acitoolkit.acisession.html',
                'acitoolkit.acitoolkit.html'
            ]
            
            for module in expected_modules:
                self.assertTrue(
                    any(module in url for url in module_urls),
                    f"Module {module} not found in extracted links"
                )
        
        except requests.RequestException as e:
            self.skipTest(f"Network error accessing {self.test_url}: {e}")

if __name__ == '__main__':
    unittest.main()
