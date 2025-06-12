import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Adjust the path to import from the app directory
# This assumes the tests directory is at the same level as the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.components.content_analyzer import analyze_document_content

# Define expected JSON structure keys for validation
EXPECTED_KEYS = ["summary", "key_topics", "structure_outline", "extracted_keywords"]

class TestContentAnalyzer(unittest.TestCase):

    def test_analyze_document_success(self):
        """Test successful analysis with a valid mocked API response."""
        sample_text = "This is a test document about analyzing content."
        mock_api_response = json.dumps({
            "summary": "Test summary",
            "key_topics": ["testing", "analysis"],
            "structure_outline": ["Intro", "Conclusion"],
            "extracted_keywords": ["test", "document", "content"]
        })
        
        # Mock the API call function within the content_analyzer module
        with patch('app.components.content_analyzer.call_claude_sonnet_for_analysis') as mock_call:
            mock_call.return_value = mock_api_response
            
            result = analyze_document_content(sample_text)
            
            # Assert the API call was made once with the expected prompt structure (simplified check)
            mock_call.assert_called_once()
            # args, kwargs = mock_call.call_args
            # self.assertIn("analyze the following document text", args[1]) # Check user prompt contains instruction
            # self.assertIn(sample_text, args[1]) # Check user prompt contains sample text

            # Assert the result is a dictionary and not an error
            self.assertIsInstance(result, dict)
            self.assertNotIn("error", result, f"Expected successful analysis, but got error: {result.get('error')}")
            
            # Assert all expected keys are present
            for key in EXPECTED_KEYS:
                self.assertIn(key, result)
                
            # Assert the content matches the mocked response
            self.assertEqual(result["summary"], "Test summary")
            self.assertEqual(result["key_topics"], ["testing", "analysis"])

    def test_analyze_document_api_error(self):
        """Test handling when the API call returns None (simulating an error)."""
        sample_text = "This document should cause an API error."
        
        with patch('app.components.content_analyzer.call_claude_sonnet_for_analysis') as mock_call:
            mock_call.return_value = None  # Simulate API failure
            
            result = analyze_document_content(sample_text)
            
            mock_call.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
            self.assertIn("returned no result", result["error"])
            
    def test_analyze_document_json_error(self):
        """Test handling when the API returns invalid JSON."""
        sample_text = "This document should cause a JSON parsing error."
        mock_api_response = "This is not valid JSON { an object" 
        
        with patch('app.components.content_analyzer.call_claude_sonnet_for_analysis') as mock_call:
            mock_call.return_value = mock_api_response
            
            result = analyze_document_content(sample_text)
            
            mock_call.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
            self.assertIn("Failed to parse analysis result", result["error"])
            # Check if the raw response is included for debugging
            self.assertIn("raw_response", result)
            self.assertEqual(result["raw_response"], mock_api_response)
            
    def test_analyze_document_empty_input(self):
        """Test handling when empty text is provided."""
        sample_text = ""
        
        # No need to mock API call as it should be caught before the call
        result = analyze_document_content(sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("No document text provided", result["error"])

    # --- (Optional) Add Integration Test Case Here --- 

if __name__ == '__main__':
    unittest.main() 