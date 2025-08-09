"""
Tests for translation service.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.config import Config
from src.translator import TranslationService


class TestTranslationService(unittest.TestCase):
    """Test cases for TranslationService."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock config
        self.config = Config(
            input_dir=self.temp_dir,
            output_dir=self.temp_dir / "output",
            openai_api_key="test-key-123"
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_extract_placeholders(self):
        """Test placeholder extraction."""
        service = TranslationService(self.config)
        
        text = "Hello {PlayerName}, welcome to [color=red]Caed Nua[/color]!"
        placeholders = service._extract_placeholders(text)
        
        expected = ['{PlayerName}', '[color=red]', '[/color]']
        self.assertEqual(set(placeholders), set(expected))
    
    def test_placeholder_replacement_and_restoration(self):
        """Test placeholder token replacement and restoration."""
        service = TranslationService(self.config)
        
        original_text = "Hello {PlayerName}, welcome to [color=red]Caed Nua[/color]!"
        
        # Replace with tokens
        text_with_tokens, placeholder_map = service._replace_placeholders_with_tokens(original_text)
        
        # Should have tokens
        self.assertIn("__PLACEHOLDER_", text_with_tokens)
        self.assertNotIn("{PlayerName}", text_with_tokens)
        
        # Restore placeholders
        restored_text = service._restore_placeholders(text_with_tokens, placeholder_map)
        
        # Should match original
        self.assertEqual(restored_text, original_text)
    
    def test_apply_glossary(self):
        """Test glossary application."""
        # Create a test glossary file
        glossary_file = self.temp_dir / "glossary.csv"
        with open(glossary_file, 'w', encoding='utf-8') as f:
            f.write("english,farsi\n")
            f.write("hello,سلام\n")
            f.write("world,جهان\n")
        
        # Update config with glossary
        self.config.glossary_file = glossary_file
        
        service = TranslationService(self.config)
        
        text = "Hello world!"
        result = service._apply_glossary(text)
        
        self.assertIn("سلام", result)
        self.assertIn("جهان", result)
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        service = TranslationService(self.config)
        
        text = "This is a sample text for token estimation."
        tokens = service.estimate_tokens(text)
        
        # Should return a reasonable number
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, len(text))  # Should be less than character count
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        service = TranslationService(self.config)
        
        # Test with 1000 tokens
        cost = service.estimate_cost(1000)
        
        # Should return a reasonable cost
        self.assertGreater(cost, 0)
        self.assertLess(cost, 1)  # Should be less than $1 for 1000 tokens
    
    @patch('src.translator.OpenAI')
    def test_translate_text_with_mock(self, mock_openai_class):
        """Test text translation with mocked OpenAI API."""
        # Mock the OpenAI client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "سلام {PlayerName}!"
        mock_client.chat.completions.create.return_value = mock_response
        
        service = TranslationService(self.config)
        
        result = service.translate_text("Hello {PlayerName}!")
        
        # Should preserve placeholder
        self.assertIn("{PlayerName}", result)
        # Should be translated
        self.assertIn("سلام", result)
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()


if __name__ == '__main__':
    unittest.main()
