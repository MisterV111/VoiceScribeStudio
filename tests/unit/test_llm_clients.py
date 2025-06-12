import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust the path to import from the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the function to test
from app.utils.llm_clients import generate_script

# Import other necessary components if needed for setup (e.g., config)
# from app.config import ... 

class TestGenerateScript(unittest.TestCase):

    # Basic setup for default arguments, can be overridden in tests
    default_args = {
        "prompt": "Write a script about testing.",
        "subject": "Unit Testing",
        "length": "short",
        "audience": "developer",
        "tone": "informative",
        "template": "Technical Tutorial",
        "context": "Some basic context.",
        "force_fallback": False,
        "is_test": True
    }

    @patch('app.utils.llm_clients.get_template_guidance') # Mock template guidance lookup
    @patch('app.utils.llm_clients._generate_with_openai_sdk') # Mock the internal DeepSeek call
    @patch('app.utils.llm_clients.deepseek_client_via_openai_sdk', MagicMock()) # Mock the client instance check
    def test_generate_script_without_analysis(self, mock_deepseek_call, mock_get_guidance):
        """Test generate_script works correctly when no analysis_results are provided."""
        # Setup mocks
        mock_get_guidance.return_value = "Template guidance for testing."
        mock_deepseek_call.return_value = {"content": "Mocked script without analysis", "model_used": "deepseek", "token_metrics": {}}
        
        # Call the function
        result = generate_script(**self.default_args, analysis_results=None)
        
        # Assertions
        mock_deepseek_call.assert_called_once()
        args, kwargs = mock_deepseek_call.call_args
        
        system_message = args[1] # system_message is the second positional argument
        params = kwargs.get('params', {})
        
        # Check that analysis context is NOT in the system message
        self.assertNotIn("CONTEXTUAL ANALYSIS", system_message)
        
        # Check params dictionary
        self.assertIn("analysis_provided", params)
        self.assertFalse(params["analysis_provided"])
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result["content"], "Mocked script without analysis")
        self.assertEqual(result["model_used"], "deepseek")

    @patch('app.utils.llm_clients.get_template_guidance')
    @patch('app.utils.llm_clients._generate_with_openai_sdk')
    @patch('app.utils.llm_clients.deepseek_client_via_openai_sdk', MagicMock())
    def test_generate_script_with_analysis(self, mock_deepseek_call, mock_get_guidance):
        """Test generate_script incorporates analysis_results into the system prompt."""
        # Setup mocks
        mock_get_guidance.return_value = "Template guidance for testing."
        mock_deepseek_call.return_value = {"content": "Mocked script with analysis", "model_used": "deepseek", "token_metrics": {}}
        
        # Sample analysis results
        sample_analysis = {
            "summary": "Test summary from analysis.",
            "key_topics": ["analyzed topic 1", "analyzed topic 2"],
            "structure_outline": ["Analyzed Intro", "Analyzed Body"],
            "extracted_keywords": ["analysis_kw1", "analysis_kw2"]
        }
        
        # Call the function WITH analysis_results
        result = generate_script(**self.default_args, analysis_results=sample_analysis)
        
        # Assertions
        mock_deepseek_call.assert_called_once()
        args, kwargs = mock_deepseek_call.call_args
        
        system_message = args[1] # system_message is the second positional argument
        params = kwargs.get('params', {})
        
        # Check that analysis context IS IN the system message
        self.assertIn("CONTEXTUAL ANALYSIS", system_message)
        self.assertIn("Test summary from analysis.", system_message) # Check specific content
        self.assertIn("analyzed topic 1, analyzed topic 2", system_message) # Check joined list
        self.assertIn("analysis_kw1, analysis_kw2", system_message)
        self.assertIn("incorporates insights from this contextual analysis", system_message)
        
        # Check params dictionary
        self.assertIn("analysis_provided", params)
        self.assertTrue(params["analysis_provided"])
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result["content"], "Mocked script with analysis")
        self.assertEqual(result["model_used"], "deepseek")

    # --- Add test cases for fallback scenarios if needed --- 

if __name__ == '__main__':
    unittest.main() 