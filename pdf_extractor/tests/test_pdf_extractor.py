#!/usr/bin/env python3
"""
Test suite for PDF Extractor functionality
"""
import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock

# The module we'll be testing
from pdf_extractor.extractor import PDFExtractor

class TestPDFExtractor(unittest.TestCase):
    """Test suite for PDFExtractor class"""
    
    def setUp(self):
        """Set up for tests"""
        # Create a temporary directory for output files
        self.output_dir = tempfile.mkdtemp()
        self.extractor = PDFExtractor(output_folder=self.output_dir)
        
        # Path to a test PDF file that we'll mock
        self.test_pdf_path = os.path.join(os.path.dirname(__file__), 'test_files', 'sample.pdf')
        
    def tearDown(self):
        """Clean up after tests"""
        # Remove test files if created
        if os.path.exists(self.output_dir):
            # Delete any test files
            for file_name in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file_name)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # Remove the directory
            os.rmdir(self.output_dir)
    
    def test_init(self):
        """Test the initialization of the PDFExtractor class"""
        # Check that the extractor was initialized correctly
        self.assertEqual(self.extractor.output_folder, self.output_dir)
        
        # Check that a default output folder is created if none is provided
        with patch('os.makedirs') as mock_makedirs:
            default_extractor = PDFExtractor()
            self.assertTrue(mock_makedirs.called)
    
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        """Test extracting text from a PDF"""
        # Mock the PDF reader and page extraction
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is test content from page 1."
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        
        mock_pdf_reader.return_value = mock_pdf
        
        # Test the extraction
        result = self.extractor.extract_text(self.test_pdf_path)
        
        # Check that the text was extracted correctly
        self.assertIn("This is test content from page 1.", result["content"])
        self.assertEqual(result["page_count"], 1)
        
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_extract_text_from_multipage_pdf(self, mock_pdf_reader):
        """Test extracting text from a multi-page PDF"""
        # Mock the PDF reader and page extraction
        mock_pages = []
        for i in range(3):
            page = MagicMock()
            page.extract_text.return_value = f"This is test content from page {i+1}."
            mock_pages.append(page)
        
        mock_pdf = MagicMock()
        mock_pdf.pages = mock_pages
        
        mock_pdf_reader.return_value = mock_pdf
        
        # Test the extraction
        result = self.extractor.extract_text(self.test_pdf_path)
        
        # Check that the text was extracted correctly from all pages
        self.assertIn("This is test content from page 1.", result["content"])
        self.assertIn("This is test content from page 2.", result["content"])
        self.assertIn("This is test content from page 3.", result["content"])
        self.assertEqual(result["page_count"], 3)
    
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_extract_metadata(self, mock_pdf_reader):
        """Test extracting metadata from a PDF"""
        # Mock the PDF reader and metadata
        mock_pdf = MagicMock()
        mock_pdf.metadata = {
            "/Title": "Test Document",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/Keywords": "test, pdf, extraction",
            "/Creator": "Test Creator",
            "/Producer": "Test Producer",
            "/CreationDate": "D:20230101000000",
            "/ModDate": "D:20230101000000"
        }
        mock_pdf.pages = []
        
        mock_pdf_reader.return_value = mock_pdf
        
        # Test the extraction
        result = self.extractor.extract_text(self.test_pdf_path)
        
        # Check that the metadata was extracted correctly
        self.assertEqual(result["metadata"]["title"], "Test Document")
        self.assertEqual(result["metadata"]["author"], "Test Author")
        self.assertEqual(result["metadata"]["subject"], "Test Subject")
        
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_save_as_text(self, mock_pdf_reader):
        """Test saving PDF content as a text file"""
        # Mock the PDF reader and page extraction
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is test content from the PDF."
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {"/Title": "Test Document"}
        
        mock_pdf_reader.return_value = mock_pdf
        
        # Test the extraction and saving
        result = self.extractor.extract_and_save(self.test_pdf_path, output_format="txt")
        
        # Check that the file was saved
        self.assertTrue(os.path.exists(result["output_path"]))
        self.assertTrue(result["output_path"].endswith(".txt"))
        
        # Check the content of the saved file
        with open(result["output_path"], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("This is test content from the PDF.", content)
    
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_save_as_json(self, mock_pdf_reader):
        """Test saving PDF content as a JSON file"""
        # Mock the PDF reader and page extraction
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is test content from the PDF."
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {"/Title": "Test Document"}
        
        mock_pdf_reader.return_value = mock_pdf
        
        # Test the extraction and saving
        result = self.extractor.extract_and_save(self.test_pdf_path, output_format="json")
        
        # Check that the file was saved
        self.assertTrue(os.path.exists(result["output_path"]))
        self.assertTrue(result["output_path"].endswith(".json"))
        
        # Check the content of the saved file
        import json
        with open(result["output_path"], 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn("This is test content from the PDF.", data["content"])
            self.assertEqual(data["metadata"]["title"], "Test Document")
    
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_save_as_html(self, mock_pdf_reader):
        """Test saving PDF content as an HTML file"""
        # Mock the PDF reader and page extraction
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is test content from the PDF."
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {"/Title": "Test Document"}
        
        mock_pdf_reader.return_value = mock_pdf
        
        # Test the extraction and saving
        result = self.extractor.extract_and_save(self.test_pdf_path, output_format="html")
        
        # Check that the file was saved
        self.assertTrue(os.path.exists(result["output_path"]))
        self.assertTrue(result["output_path"].endswith(".html"))
        
        # Check the content of the saved file
        with open(result["output_path"], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("This is test content from the PDF.", content)
            self.assertIn("<title>Test Document</title>", content)
    
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_error_handling(self, mock_pdf_reader):
        """Test handling errors when extracting from a PDF"""
        # Mock the PDF reader to raise an exception
        mock_pdf_reader.side_effect = Exception("Test exception")
        
        # Test the extraction with the mocked exception
        with self.assertRaises(Exception):
            self.extractor.extract_text(self.test_pdf_path)
    
    @patch('pdf_extractor.extractor.PyPDF2.PdfReader')
    def test_extract_images(self, mock_pdf_reader):
        """Test extracting images from a PDF"""
        # This test is more complex and would require mocking the image extraction process
        # For now, we'll just test that the method exists and is called correctly
        self.assertTrue(hasattr(self.extractor, 'extract_images'))
        
        # Mock image extraction to return empty list for now
        self.extractor.extract_images = MagicMock(return_value=[])
        
        # Call the method
        result = self.extractor.extract_and_save(self.test_pdf_path, output_format="html", extract_images=True)
        
        # Check that the image extraction method was called
        self.extractor.extract_images.assert_called_once()

if __name__ == '__main__':
    unittest.main()
