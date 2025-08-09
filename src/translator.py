"""
Translation service using OpenAI API with caching and glossary support.
"""

import csv
import json
import logging
import re
import time
from typing import Dict, List, Optional

import tiktoken
from openai import OpenAI

from .cache import TranslationCache
from .config import Config


class TranslationService:
    """Service for translating text using OpenAI API with caching."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if not config.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI client
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = "gpt-4o"
        
        # Initialize tokenizer for cost estimation
        self.tokenizer = tiktoken.encoding_for_model(self.model)
        
        # Initialize cache
        self.cache = TranslationCache()
        
        # Load glossary if provided
        self.glossary = self._load_glossary()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests to avoid rate limits
    
    def _load_glossary(self) -> Dict[str, str]:
        """Load glossary from CSV file."""
        glossary = {}
        
        if not self.config.glossary_file or not self.config.glossary_file.exists():
            return glossary
        
        try:
            with open(self.config.glossary_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'english' in row and 'farsi' in row:
                        glossary[row['english'].strip()] = row['farsi'].strip()
                    elif 'en' in row and 'fa' in row:
                        glossary[row['en'].strip()] = row['fa'].strip()
            
            self.logger.info(f"Loaded {len(glossary)} entries from glossary")
            
        except Exception as e:
            self.logger.warning(f"Failed to load glossary: {e}")
        
        return glossary
    
    def _extract_placeholders(self, text: str) -> List[str]:
        """Extract placeholders from text (e.g., {PlayerName}, [color=red], etc.)."""
        placeholders = []
        
        # Unity-style placeholders: {variable}
        placeholders.extend(re.findall(r'\{[^}]+\}', text))
        
        # Rich text tags: [tag=value], [/tag]
        placeholders.extend(re.findall(r'\[[^\]]+\]', text))
        
        # HTML-style tags: <tag>, </tag>
        placeholders.extend(re.findall(r'<[^>]+>', text))
        
        # Numbered placeholders: {0}, {1}, etc.
        placeholders.extend(re.findall(r'\{\d+\}', text))
        
        return placeholders
    
    def _replace_placeholders_with_tokens(self, text: str) -> tuple[str, Dict[str, str]]:
        """Replace placeholders with temporary tokens for translation."""
        placeholders = self._extract_placeholders(text)
        placeholder_map = {}
        modified_text = text
        
        for i, placeholder in enumerate(placeholders):
            token = f"__PLACEHOLDER_{i}__"
            placeholder_map[token] = placeholder
            modified_text = modified_text.replace(placeholder, token, 1)
        
        return modified_text, placeholder_map
    
    def _restore_placeholders(self, text: str, placeholder_map: Dict[str, str]) -> str:
        """Restore placeholders from temporary tokens."""
        for token, placeholder in placeholder_map.items():
            text = text.replace(token, placeholder)
        return text
    
    def _apply_glossary(self, text: str) -> str:
        """Apply glossary translations to text."""
        if not self.glossary:
            return text
        
        # Sort by length (longest first) to avoid partial replacements
        sorted_terms = sorted(self.glossary.keys(), key=len, reverse=True)
        
        for english_term in sorted_terms:
            farsi_term = self.glossary[english_term]
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(english_term) + r'\b'
            text = re.sub(pattern, farsi_term, text, flags=re.IGNORECASE)
        
        return text
    
    def _rate_limit(self):
        """Implement rate limiting for API requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens for a text."""
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            # Fallback estimation: roughly 4 characters per token
            return len(text) // 4
    
    def estimate_cost(self, total_tokens: int) -> float:
        """Estimate the cost based on token count."""
        # GPT-4o pricing (as of 2024): $5.00 per 1M input tokens, $15.00 per 1M output tokens
        # Assume roughly equal input/output for translation
        input_cost = (total_tokens / 1_000_000) * 5.00
        output_cost = (total_tokens / 1_000_000) * 15.00
        return input_cost + output_cost
    
    def translate_text(self, text: str) -> str:
        """Translate a single text string."""
        if not text or not text.strip():
            return text
        
        # Check cache first
        cached_translation = self.cache.get_translation(text)
        if cached_translation:
            self.logger.debug(f"Using cached translation for: {text[:50]}...")
            return cached_translation
        
        # For single text, use batch processing with size 1
        results = self._translate_batch_internal([text])
        return results[0] if results else text
    
    def _translate_batch_internal(self, texts: List[str]) -> List[str]:
        """Internal method to translate multiple texts in a single API call."""
        if not texts:
            return []
        
        # Separate texts that need translation from cached ones
        texts_to_translate = []
        results: List[str] = [""] * len(texts)
        
        for i, text in enumerate(texts):
            if not text or not text.strip():
                results[i] = text
                continue
                
            cached_translation = self.cache.get_translation(text)
            if cached_translation:
                results[i] = cached_translation
                self.logger.debug(f"Using cached translation for: {text[:30]}...")
            else:
                texts_to_translate.append((i, text))
        
        # If no texts need translation, return cached results
        if not texts_to_translate:
            return results
        
        # Prepare batch translation
        batch_items = []
        placeholder_maps = {}
        
        for idx, text in texts_to_translate:
            # Extract placeholders and apply glossary
            text_with_tokens, placeholder_map = self._replace_placeholders_with_tokens(text)
            text_with_glossary = self._apply_glossary(text_with_tokens)
            
            batch_items.append(f"[{len(batch_items) + 1}] {text_with_glossary}")
            placeholder_maps[len(batch_items) - 1] = placeholder_map
        
        # Retry logic for rate limits and transient errors
        max_retries = self.config.max_retries
        response = None
        
        for attempt in range(max_retries + 1):
            try:
                # Rate limiting
                self._rate_limit()
                
                # Prepare batch translation prompt
                system_prompt = (
                    "You are a professional translator specializing in video game localization. "
                    "Translate the following numbered English texts to Farsi (Persian) while maintaining "
                    "the tone, style, and context appropriate for a fantasy RPG game. "
                    "Preserve any placeholder tokens exactly as they appear. "
                    "Do not translate proper nouns unless they have established Farsi equivalents. "
                    "Maintain the emotional tone and formality level of the original text. "
                    "Return the translations with the same numbers in the format: [1] translation1\\n[2] translation2\\n etc."
                )
                
                batch_text = "\n".join(batch_items)
                user_prompt = f"Translate these texts to Farsi:\n{batch_text}"
                
                # Make API request
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=4000,  # Moderate size for reliability
                    temperature=0.3
                )
                
                # If successful, break out of retry loop
                break
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if "rate limit" in error_msg or "too many requests" in error_msg or "429" in error_msg:
                    if attempt < max_retries:
                        wait_time = (2 ** attempt) * self.config.retry_delay  # Exponential backoff
                        self.logger.warning(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        self.logger.error(f"Rate limit exceeded after {max_retries} retries")
                        raise
                
                # Check for other retryable errors
                elif any(err in error_msg for err in ["timeout", "connection", "server error", "503", "502", "500"]):
                    if attempt < max_retries:
                        wait_time = self.config.retry_delay * (attempt + 1)
                        self.logger.warning(f"Transient error: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        self.logger.error(f"Request failed after {max_retries} retries: {e}")
                        raise
                
                # Non-retryable error
                else:
                    raise
        
        # Process the successful response
        if response:
            try:
                batch_response = response.choices[0].message.content
                if not batch_response:
                    raise Exception("Empty response from API")
                
                # Parse batch response
                translated_texts = self._parse_batch_response(batch_response, len(texts_to_translate))
                
                # Process translated texts and cache them
                for i, (original_idx, original_text) in enumerate(texts_to_translate):
                    if i < len(translated_texts):
                        translated_text = translated_texts[i]
                        # Restore placeholders
                        translated_text = self._restore_placeholders(translated_text, placeholder_maps[i])
                        # Cache the translation
                        self.cache.store_translation(original_text, translated_text)
                        results[original_idx] = translated_text
                        self.logger.debug(f"Translated: {original_text[:30]}... -> {translated_text[:30]}...")
                    else:
                        # Fallback to original text if parsing failed
                        results[original_idx] = original_text
                        self.logger.warning(f"Failed to parse translation for: {original_text[:30]}...")
                
            except Exception as e:
                self.logger.error(f"Error processing response: {e}")
                # Fallback: use original texts for untranslated items
                for original_idx, original_text in texts_to_translate:
                    if not results[original_idx]:
                        results[original_idx] = original_text
        else:
            # No successful response after all retries
            self.logger.error("No successful response received after all retries")
            for original_idx, original_text in texts_to_translate:
                results[original_idx] = original_text
        
        return results
    
    def _parse_batch_response(self, response: str, expected_count: int) -> List[str]:
        """Parse the batch translation response into individual translations."""
        translations = []
        lines = response.strip().split('\n')
        
        current_translation = ""
        for line in lines:
            line = line.strip()
            if re.match(r'\[\d+\]', line):  # New numbered item
                if current_translation:
                    # Remove the number prefix and clean up
                    clean_translation = re.sub(r'^\[\d+\]\s*', '', current_translation).strip()
                    translations.append(clean_translation)
                current_translation = line
            else:
                # Continuation of current translation
                if current_translation:
                    current_translation += " " + line
                else:
                    current_translation = line
        
        # Add the last translation
        if current_translation:
            clean_translation = re.sub(r'^\[\d+\]\s*', '', current_translation).strip()
            translations.append(clean_translation)
        
        # Ensure we have the expected number of translations
        while len(translations) < expected_count:
            translations.append("")
        
        return translations[:expected_count]
    
    def translate_batch(self, texts: List[str], batch_size: int = 20) -> List[str]:
        """Translate a batch of texts with configurable batch size."""
        if not texts:
            return []
        
        all_results = []
        
        # Process in chunks
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            self.logger.info(f"Processing batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size} ({len(batch)} items)")
            
            batch_results = self._translate_batch_internal(batch)
            all_results.extend(batch_results)
        
        return all_results
