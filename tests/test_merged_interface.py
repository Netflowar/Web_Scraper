"""
Tests for the merged interface of the Web Scraper application.
This file defines the expected behavior of the merged interface
where the main page and doc_links page are combined into one.
"""
import os
import unittest
from flask import Flask
from webscraperui.app import app


class MergedInterfaceTests(unittest.TestCase):
    """Test class for the merged interface requirements."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Test output folder
        test_output_folder = os.path.join(os.path.dirname(__file__), 'test_output')
        if not os.path.exists(test_output_folder):
            os.makedirs(test_output_folder)
        self.app.config['OUTPUT_FOLDER'] = test_output_folder
    
    def test_main_page_contains_both_forms(self):
        """Test that the main page contains both scraping forms."""
        response = self.client.get('/')
        response_text = response.data.decode('utf-8')
        
        # Check for regular scraping form
        self.assertIn('Enter Website URL', response_text)
        self.assertIn('Crawl Depth', response_text)
        self.assertIn('Start Scraping', response_text)
        
        # Check for doc links extraction form
        self.assertIn('Documentation URL', response_text)
        self.assertIn('Filter Pattern', response_text)
        self.assertIn('Extract Documentation Links', response_text)
    
    def test_tabs_for_different_scraping_modes(self):
        """Test that the interface has tabs for different scraping modes."""
        response = self.client.get('/')
        response_text = response.data.decode('utf-8')
        
        # Check for tabs
        self.assertIn('nav-tabs', response_text)
        self.assertIn('Single URL', response_text)
        self.assertIn('Documentation Site', response_text)
    
    def test_form_submission_targets(self):
        """Test that form submission targets are correct."""
        response = self.client.get('/')
        response_text = response.data.decode('utf-8')
        
        # Check form action URLs
        self.assertIn('action="/scrape"', response_text)
        self.assertIn('action="/extract_doc_links"', response_text)
    
    def test_doc_links_page_redirects_to_main(self):
        """Test that accessing the doc_links page redirects to the main page with the correct tab active."""
        response = self.client.get('/doc_links', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response_text = response.data.decode('utf-8')
        # Check that we landed on the main page with docs tab active
        self.assertIn('Documentation Site', response_text)
        self.assertIn('class="nav-link active"', response_text)
    
    def test_tab_state_preserved(self):
        """Test that tab state is preserved after form submission errors."""
        # Test with regular scraper tab
        response = self.client.post('/scrape', data={'url': ''}, follow_redirects=True)
        response_text = response.data.decode('utf-8')
        self.assertIn('Please enter a URL to scrape', response_text)
        self.assertIn('class="nav-link active" id="single-url-tab"', response_text)
        
        # Test with doc links tab
        response = self.client.post('/extract_doc_links', data={'url': ''}, follow_redirects=True)
        response_text = response.data.decode('utf-8')
        self.assertIn('Please enter a URL to extract links from', response_text)
        self.assertIn('class="nav-link active" id="doc-links-tab"', response_text)
    
    def test_consistent_ui_between_tabs(self):
        """Test that the UI elements are consistent between tabs."""
        response = self.client.get('/')
        response_text = response.data.decode('utf-8')
        
        # Check that both forms have similar styling
        self.assertIn('card card-hover-effect shadow-lg', response_text)
        
        # Both forms should have similar button styling
        self.assertIn('btn btn-primary', response_text)
        
        # Both should use the same font awesome icons
        self.assertIn('fas fa-spider', response_text)
        self.assertIn('fas fa-link', response_text)
    
    def test_responsive_layout_tabs(self):
        """Test that the tabs layout is responsive."""
        response = self.client.get('/')
        response_text = response.data.decode('utf-8')
        
        # Check for responsive classes
        self.assertIn('tab-content', response_text)
        self.assertIn('tab-pane', response_text)
        self.assertIn('fade', response_text)
    
    def test_menu_item_active_state(self):
        """Test that the Doc Links menu item is no longer needed/active."""
        response = self.client.get('/')
        response_text = response.data.decode('utf-8')
        
        # The Doc Links nav item should not be highlighted as a separate page
        self.assertNotIn('<a class="nav-link active" href="/doc_links"', response_text)


if __name__ == '__main__':
    unittest.main()
