"""
Tests for the script humanization feature
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.humanize_script import humanize_script, preview_humanized_markup

class TestHumanizeScript(unittest.TestCase):
    """Tests for the humanize_script function"""
    
    def test_empty_script(self):
        """Test with an empty script"""
        result = humanize_script("")
        self.assertIn("error", result)
        self.assertEqual(result["content"], "")
        self.assertEqual(result["model_used"], "none")
    
    @patch('app.utils.humanize_script.anthropic_client')
    def test_no_anthropic_client(self, mock_anthropic):
        """Test when Anthropic client is not available"""
        # Set the anthropic_client to None for this test
        mock_anthropic.return_value = None
        
        result = humanize_script("Test script")
        self.assertIn("error", result)
        self.assertEqual(result["content"], "Test script")
        self.assertEqual(result["model_used"], "none")
    
    @patch('app.utils.humanize_script.anthropic_client')
    @patch('app.utils.humanize_script.token_tracker')
    def test_successful_humanization(self, mock_tracker, mock_anthropic):
        """Test successful humanization"""
        # Mock the Anthropic client response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is a / humanized // script with *emphasis*.")]
        mock_anthropic.messages.create.return_value = mock_response
        
        # Mock the token tracker
        mock_tracker.track_generation.return_value = {"input_tokens": 100, "output_tokens": 50}
        
        result = humanize_script("This is a test script.")
        
        # Verify the result
        self.assertEqual(result["content"], "This is a / humanized // script with *emphasis*.")
        self.assertEqual(result["model_used"], "claude")
        self.assertEqual(result["token_metrics"], {"input_tokens": 100, "output_tokens": 50})
        
        # Verify the Anthropic client was called with the right parameters
        mock_anthropic.messages.create.assert_called_once()
        args, kwargs = mock_anthropic.messages.create.call_args
        self.assertEqual(kwargs["temperature"], 0.3)
        self.assertIn("script", kwargs["messages"][0]["content"])
    
    def test_preview_html_generation(self):
        """Test HTML preview generation"""
        original = "This is a test script."
        humanized = "This is a / test // script with *emphasis*."
        
        html = preview_humanized_markup(original, humanized)
        
        # Simple checks for expected content
        self.assertIn("Original Script", html)
        self.assertIn("Humanized Script", html)
        self.assertIn("humanize-pause", html)
        self.assertIn("humanize-emphasis", html)
        self.assertIn(original, html)

if __name__ == '__main__':
    unittest.main() 