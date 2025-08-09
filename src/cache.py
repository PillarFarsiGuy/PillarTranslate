"""
SQLite-based caching system for translations.
"""

import hashlib
import logging
import sqlite3
from pathlib import Path
from typing import Optional


class TranslationCache:
    """SQLite-based cache for storing translations."""
    
    def __init__(self, cache_file: Path = Path("translation_cache.db")):
        self.cache_file = cache_file
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS translations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text_hash TEXT UNIQUE NOT NULL,
                        original_text TEXT NOT NULL,
                        translated_text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for faster lookups
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_text_hash 
                    ON translations(text_hash)
                """)
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def _hash_text(self, text: str) -> str:
        """Create a hash of the text for efficient lookup."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get_translation(self, original_text: str) -> Optional[str]:
        """Get cached translation for the given text."""
        text_hash = self._hash_text(original_text)
        
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT translated_text FROM translations WHERE text_hash = ?",
                    (text_hash,)
                )
                result = cursor.fetchone()
                
                if result:
                    return result[0]
                
        except sqlite3.Error as e:
            self.logger.error(f"Cache lookup failed: {e}")
        
        return None
    
    def store_translation(self, original_text: str, translated_text: str) -> None:
        """Store a translation in the cache."""
        text_hash = self._hash_text(original_text)
        
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO translations 
                    (text_hash, original_text, translated_text)
                    VALUES (?, ?, ?)
                """, (text_hash, original_text, translated_text))
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Cache storage failed: {e}")
    
    def get_cache_stats(self) -> dict:
        """Get statistics about the cache."""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM translations")
                total_count = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM translations 
                    WHERE created_at >= datetime('now', '-1 day')
                """)
                recent_count = cursor.fetchone()[0]
                
                return {
                    "total_translations": total_count,
                    "recent_translations": recent_count
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Cache stats failed: {e}")
            return {"total_translations": 0, "recent_translations": 0}
    
    def clear_cache(self) -> None:
        """Clear all cached translations."""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM translations")
                conn.commit()
                
            self.logger.info("Cache cleared successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"Cache clearing failed: {e}")
