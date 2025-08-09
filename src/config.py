"""
Configuration management for the translation tool.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration settings for the translation tool."""
    
    input_dir: Path
    output_dir: Path
    openai_api_key: Optional[str]
    target_language: str = "Farsi"
    glossary_file: Optional[Path] = None
    batch_size: int = 20  # Reliable batch size to avoid timeouts
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")
        
        if not self.input_dir.is_dir():
            raise ValueError(f"Input path is not a directory: {self.input_dir}")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        if self.batch_size < 1:
            raise ValueError("Batch size must be at least 1")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
