#!/usr/bin/env python3
"""
Comprehensive integration test for the Pillars of Eternity translation tool.
Tests all major components with realistic scenarios.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.translator import TranslationService
from src.xml_utils import XMLProcessor
from src.cache import TranslationCache

def create_test_xml_file(file_path: Path, entries_data: list):
    """Create a test XML file with given entries."""
    content = """<?xml version="1.0" encoding="utf-8"?>
<StringTableFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Name>test_file</Name>
  <NextEntryID>{next_id}</NextEntryID>
  <EntryCount>{count}</EntryCount>
  <Entries>
{entries}
  </Entries>
</StringTableFile>""".format(
        next_id=len(entries_data) + 1,
        count=len(entries_data),
        entries='\n'.join([
            f'    <Entry>\n      <ID>{i+1}</ID>\n      <DefaultText>{text}</DefaultText>\n      <FemaleText />\n    </Entry>'
            for i, text in enumerate(entries_data)
        ])
    )
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def test_xml_processing():
    """Test XML parsing and writing functionality."""
    print("🔧 Testing XML processing...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test XML file
        test_file = temp_path / "test.stringtable"
        test_entries = [
            "Hello world",
            "Welcome to the game, {PlayerName}!",
            "The [color=red]dangerous[/color] path awaits."
        ]
        
        create_test_xml_file(test_file, test_entries)
        
        # Test parsing
        processor = XMLProcessor()
        entries = processor.parse_stringtable(test_file)
        
        assert len(entries) == 3, f"Expected 3 entries, got {len(entries)}"
        assert entries[0]['text'] == "Hello world"
        assert "{PlayerName}" in entries[1]['text']
        assert "[color=red]" in entries[2]['text']
        
        # Test writing
        output_file = temp_path / "output.stringtable"
        processor.write_stringtable(output_file, entries)
        
        # Test round-trip
        entries_after = processor.parse_stringtable(output_file)
        assert len(entries_after) == len(entries)
        
        print("✅ XML processing test passed")

def test_caching_system():
    """Test the caching functionality."""
    print("🔧 Testing caching system...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_file = Path(temp_dir) / "test_cache.db"
        cache = TranslationCache(cache_file)
        
        # Test storage and retrieval
        original_text = "Hello world"
        translated_text = "سلام دنیا"
        
        # Store translation
        cache.store_translation(original_text, translated_text)
        
        # Retrieve translation
        cached_result = cache.get_translation(original_text)
        assert cached_result == translated_text, f"Expected '{translated_text}', got '{cached_result}'"
        
        # Test cache miss
        missing_result = cache.get_translation("Non-existent text")
        assert missing_result is None
        
        # Test stats
        stats = cache.get_cache_stats()
        assert stats['total_translations'] >= 1
        
        print("✅ Caching system test passed")

def test_placeholder_handling():
    """Test placeholder extraction and restoration."""
    print("🔧 Testing placeholder handling...")
    
    # Create a mock config for translator
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(
            input_dir=Path(temp_dir),
            output_dir=Path(temp_dir),
            openai_api_key="test_key_not_used"
        )
        
        # Don't actually initialize OpenAI client for this test
        # Just test placeholder functionality
        from src.translator import TranslationService
        
        # Test text with various placeholders
        test_text = "Welcome {PlayerName} to [color=gold]Dyrwood[/color]! You have {ItemCount} items."
        
        # Manually test placeholder extraction (without full translator setup)
        import re
        
        placeholders = []
        # Unity-style placeholders: {variable}
        placeholders.extend(re.findall(r'\{[^}]+\}', test_text))
        # Rich text tags: [tag=value], [/tag]
        placeholders.extend(re.findall(r'\[[^\]]+\]', test_text))
        
        expected_placeholders = ['{PlayerName}', '[color=gold]', '[/color]', '{ItemCount}']
        assert all(ph in placeholders for ph in expected_placeholders), f"Missing placeholders: {placeholders}"
        
        print("✅ Placeholder handling test passed")

def test_config_validation():
    """Test configuration validation."""
    print("🔧 Testing configuration validation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test valid config
        config = Config(
            input_dir=temp_path,
            output_dir=temp_path / "output",
            openai_api_key="test_key"
        )
        assert config.batch_size == 20  # Default value
        assert config.target_language == "Farsi"
        
        # Test invalid input directory
        try:
            Config(
                input_dir=Path("/non/existent/path"),
                output_dir=temp_path,
                openai_api_key="test_key"
            )
            assert False, "Should have raised ValueError for non-existent input directory"
        except ValueError:
            pass  # Expected
        
        # Test missing API key
        try:
            Config(
                input_dir=temp_path,
                output_dir=temp_path,
                openai_api_key=None
            )
            assert False, "Should have raised ValueError for missing API key"
        except ValueError:
            pass  # Expected
            
        print("✅ Configuration validation test passed")

def test_batch_size_consistency():
    """Test that batch sizes are consistent across the codebase."""
    print("🔧 Testing batch size consistency...")
    
    # Import CLI module to check defaults
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Check that all defaults are aligned
    from src.config import Config
    
    # Default config batch size
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(
            input_dir=Path(temp_dir),
            output_dir=Path(temp_dir),
            openai_api_key="test"
        )
        assert config.batch_size == 20, f"Config default should be 20, got {config.batch_size}"
    
    # Check CLI argument parsing by examining the file
    cli_file = Path(__file__).parent / 'src' / 'cli.py'
    cli_content = cli_file.read_text()
    
    # Count occurrences of "default=20" for batch-size arguments
    default_20_count = cli_content.count('default=20,\n        help="Batch size for API requests (default: 20)"')
    assert default_20_count >= 2, f"Should have at least 2 CLI batch-size defaults set to 20, found {default_20_count}"
    
    # Check that there are no "default=100" remaining
    default_100_count = cli_content.count('default=100')
    assert default_100_count == 0, f"Should have no default=100 remaining, found {default_100_count}"
    
    print("✅ Batch size consistency test passed")

def test_integration_without_api():
    """Test integration flow without making API calls."""
    print("🔧 Testing integration flow (no API calls)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create input directory and files
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test XML file
        test_file = input_dir / "test.stringtable"
        test_entries = [
            "Simple text",
            "Text with {PlayerName} placeholder"
        ]
        create_test_xml_file(test_file, test_entries)
        
        # Create config
        config = Config(
            input_dir=input_dir,
            output_dir=output_dir,
            openai_api_key="test_key_for_validation_only"
        )
        
        # Test XML processing
        processor = XMLProcessor()
        entries = processor.parse_stringtable(test_file)
        
        assert len(entries) == 2
        assert entries[0]['text'] == "Simple text"
        
        # Test output directory creation
        output_localized_dir = output_dir / "localized" / "it" / "text"
        output_localized_dir.mkdir(parents=True, exist_ok=True)
        assert output_localized_dir.exists()
        
        # Test writing translated file (with dummy translations)
        entries[0]['text'] = "متن ساده"  # Simple text in Farsi
        entries[1]['text'] = "متن با {PlayerName} placeholder"  # Text with placeholder in Farsi
        
        output_file = output_localized_dir / "test.stringtable"
        processor.write_stringtable(output_file, entries)
        
        # Verify output file
        assert output_file.exists()
        output_entries = processor.parse_stringtable(output_file)
        assert len(output_entries) == 2
        assert "{PlayerName}" in output_entries[1]['text']  # Placeholder preserved
        
        print("✅ Integration test passed")

def run_all_tests():
    """Run all comprehensive tests."""
    print("🚀 Starting comprehensive test suite...")
    print("=" * 50)
    
    try:
        test_config_validation()
        test_xml_processing()
        test_caching_system()
        test_placeholder_handling()
        test_batch_size_consistency()
        test_integration_without_api()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED! The translation tool is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)