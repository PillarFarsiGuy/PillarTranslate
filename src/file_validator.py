"""
File validation utilities to ensure safe processing of translation files.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET


class FileValidator:
    """Validates files before and after processing to ensure integrity."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_input_file(self, file_path: Path) -> bool:
        """Validate that an input file is a proper stringtable file."""
        try:
            # Check file extension
            if not file_path.suffix.lower() == '.stringtable':
                self.logger.warning(f"File does not have .stringtable extension: {file_path}")
                return False
            
            # Check if file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                self.logger.error(f"File does not exist or is not a file: {file_path}")
                return False
            
            # Check file size (reasonable limits)
            file_size = file_path.stat().st_size
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                self.logger.warning(f"File is very large ({file_size} bytes): {file_path}")
                return False
            
            if file_size == 0:
                self.logger.warning(f"File is empty: {file_path}")
                return False
            
            # Try to parse as XML
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Check if it looks like a stringtable file
                if root.tag not in ['StringTableFile', 'StringTable']:
                    self.logger.warning(f"File does not appear to be a stringtable (root: {root.tag}): {file_path}")
                    return False
                
                return True
                
            except ET.ParseError as e:
                self.logger.error(f"XML parsing error in {file_path}: {e}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error validating input file {file_path}: {e}")
            return False
    
    def validate_output_file(self, file_path: Path) -> bool:
        """Validate that an output file was created successfully."""
        try:
            if not file_path.exists():
                return False
            
            # Check if file is readable and has content
            if file_path.stat().st_size == 0:
                return False
            
            # Try to parse the output file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            return root.tag in ['StringTableFile', 'StringTable']
            
        except Exception as e:
            self.logger.error(f"Error validating output file {file_path}: {e}")
            return False
    
    def backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a file before processing."""
        try:
            backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
            
            # Only create backup if it doesn't exist
            if not backup_path.exists():
                import shutil
                shutil.copy2(file_path, backup_path)
                self.logger.debug(f"Created backup: {backup_path}")
                return backup_path
            
            return backup_path
            
        except Exception as e:
            self.logger.warning(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def is_file_corrupted(self, file_path: Path) -> bool:
        """Check if a file appears to be corrupted."""
        try:
            if not file_path.exists():
                return True
            
            # Check for minimum file size
            if file_path.stat().st_size < 50:  # Very small files are likely corrupted
                return True
            
            # Try to parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Basic structure validation
            if root.tag not in ['StringTableFile', 'StringTable']:
                return True
            
            return False
            
        except Exception:
            return True