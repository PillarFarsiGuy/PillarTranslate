"""
Tests for XML utilities.
"""

import tempfile
import unittest
from pathlib import Path

from src.xml_utils import XMLProcessor


class TestXMLProcessor(unittest.TestCase):
    """Test cases for XMLProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = XMLProcessor()
        
        # Sample XML content
        self.sample_xml = """<?xml version="1.0" encoding="utf-8"?>
<StringTableFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Name>test_strings</Name>
  <NextEntryID>3</NextEntryID>
  <EntryCount>2</EntryCount>
  <Entries>
    <Entry ID="1">
      <DefaultText>Hello, {PlayerName}!</DefaultText>
      <FemaleText />
    </Entry>
    <Entry ID="2">
      <DefaultText>Welcome to the [color=gold]Golden City[/color].</DefaultText>
      <FemaleText />
    </Entry>
  </Entries>
</StringTableFile>"""
    
    def test_parse_stringtable(self):
        """Test parsing a stringtable XML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.stringtable', delete=False) as f:
            f.write(self.sample_xml)
            temp_path = Path(f.name)
        
        try:
            entries = self.processor.parse_stringtable(temp_path)
            
            self.assertEqual(len(entries), 2)
            
            self.assertEqual(entries[0]['id'], '1')
            self.assertEqual(entries[0]['text'], 'Hello, {PlayerName}!')
            
            self.assertEqual(entries[1]['id'], '2')
            self.assertEqual(entries[1]['text'], 'Welcome to the [color=gold]Golden City[/color].')
            
        finally:
            temp_path.unlink()
    
    def test_write_stringtable(self):
        """Test writing a stringtable XML file."""
        entries = [
            {'id': '1', 'text': 'سلام، {PlayerName}!'},
            {'id': '2', 'text': 'به [color=gold]شهر طلایی[/color] خوش آمدید.'}
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.stringtable', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            self.processor.write_stringtable(temp_path, entries)
            
            # Verify the file was written correctly
            self.assertTrue(temp_path.exists())
            
            # Parse it back to check
            parsed_entries = self.processor.parse_stringtable(temp_path)
            
            self.assertEqual(len(parsed_entries), 2)
            self.assertEqual(parsed_entries[0]['text'], 'سلام، {PlayerName}!')
            self.assertEqual(parsed_entries[1]['text'], 'به [color=gold]شهر طلایی[/color] خوش آمدید.')
            
        finally:
            temp_path.unlink()
    
    def test_xml_roundtrip(self):
        """Test that XML can be parsed and written back correctly."""
        # Create original file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.stringtable', delete=False) as f:
            f.write(self.sample_xml)
            original_path = Path(f.name)
        
        # Create new file
        with tempfile.NamedTemporaryFile(suffix='.stringtable', delete=False) as f:
            new_path = Path(f.name)
        
        try:
            # Parse and write
            entries = self.processor.parse_stringtable(original_path)
            self.processor.write_stringtable(new_path, entries)
            
            # Validate roundtrip
            is_valid = self.processor.validate_xml_roundtrip(original_path, new_path)
            self.assertTrue(is_valid)
            
        finally:
            original_path.unlink()
            new_path.unlink()


if __name__ == '__main__':
    unittest.main()
