"""
XML utilities for parsing and writing .stringtable files.
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List


class XMLProcessor:
    """Processor for handling .stringtable XML files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_stringtable(self, file_path: Path) -> List[Dict[str, str]]:
        """Parse a .stringtable XML file and extract entries."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            entries = []
            
            # Handle different XML structures
            if root.tag == "StringTableFile":
                # Standard Pillars of Eternity format
                for entry in root.findall(".//Entry"):
                    entry_data = {
                        "id": entry.get("ID", ""),
                        "text": ""
                    }
                    
                    # Find DefaultText element
                    default_text = entry.find("DefaultText")
                    if default_text is not None and default_text.text:
                        entry_data["text"] = default_text.text
                    
                    entries.append(entry_data)
            
            else:
                # Try to parse generic structure
                for entry in root.findall(".//Entry"):
                    entry_data = {
                        "id": entry.get("ID", entry.get("id", "")),
                        "text": entry.text or ""
                    }
                    entries.append(entry_data)
            
            self.logger.debug(f"Parsed {len(entries)} entries from {file_path}")
            return entries
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error in {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            raise
    
    def write_stringtable(self, file_path: Path, entries: List[Dict[str, str]]) -> None:
        """Write entries to a .stringtable XML file."""
        try:
            # Create root element
            root = ET.Element("StringTableFile")
            root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
            
            # Add Name element (use filename without extension)
            name_elem = ET.SubElement(root, "Name")
            name_elem.text = file_path.stem
            
            # Add NextEntryID (use number of entries + 1)
            next_id_elem = ET.SubElement(root, "NextEntryID")
            next_id_elem.text = str(len(entries) + 1)
            
            # Add EntryCount
            count_elem = ET.SubElement(root, "EntryCount")
            count_elem.text = str(len(entries))
            
            # Add Entries container
            entries_elem = ET.SubElement(root, "Entries")
            
            # Add each entry
            for entry in entries:
                entry_elem = ET.SubElement(entries_elem, "Entry")
                entry_elem.set("ID", str(entry.get("id", "")))
                
                # Add DefaultText
                default_text_elem = ET.SubElement(entry_elem, "DefaultText")
                default_text_elem.text = entry.get("text", "")
                
                # Add FemaleText (copy from DefaultText for consistency)
                female_text_elem = ET.SubElement(entry_elem, "FemaleText")
                female_text_elem.text = entry.get("text", "")
            
            # Create the tree and write to file
            tree = ET.ElementTree(root)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with proper encoding and formatting
            tree.write(
                file_path,
                encoding="utf-8",
                xml_declaration=True,
                method="xml"
            )
            
            self.logger.debug(f"Wrote {len(entries)} entries to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error writing {file_path}: {e}")
            raise
    
    def validate_xml_roundtrip(self, original_path: Path, new_path: Path) -> bool:
        """Validate that XML can be parsed after writing."""
        try:
            original_entries = self.parse_stringtable(original_path)
            new_entries = self.parse_stringtable(new_path)
            
            if len(original_entries) != len(new_entries):
                self.logger.warning(f"Entry count mismatch: {len(original_entries)} vs {len(new_entries)}")
                return False
            
            for orig, new in zip(original_entries, new_entries):
                if orig.get("id") != new.get("id"):
                    self.logger.warning(f"ID mismatch: {orig.get('id')} vs {new.get('id')}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False
