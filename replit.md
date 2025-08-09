# Overview

The Pillars of Eternity Farsi Translation Tool is a Python CLI application that translates game text files from English to Farsi using OpenAI's GPT-4o model. The tool is specifically designed to handle Pillars of Eternity .stringtable XML files while preserving game-specific formatting, placeholders, and structure. It features smart caching to avoid redundant translations, glossary support for consistent terminology, and multiple operation modes for cost estimation, translation, and quality verification.

## Project Status: TOOL STABILITY IMPROVED ✅
- Tool completely fixed and consolidated (Aug 9, 2025)
- All completed work properly organized in output structure
- Import issues resolved (GameTextTranslator → TranslationService)
- XML function signatures corrected
- Dependencies properly installed (OpenAI, tiktoken)
- **Accurate Progress**: 542/1,116 files completed (48.6% done)
- **Remaining Work**: 574 files to translate (51.4%)
- **STABILITY FIXES APPLIED** (Aug 9, 2025):
  - Reduced API timeout from infinite to 60 seconds
  - Capped retry wait times (10s max for rate limits, 5s for others)
  - Reduced request interval from 2s to 0.5s
  - Changed error handling to continue rather than crash
  - Added progress tracking to prevent infinite loops
  - Smaller batch sizes (15 instead of 20) for reliability
- **CRITICAL FILE SKIPPING ISSUE** (Aug 9, 2025):
  - Tool was re-processing already completed files instead of skipping them
  - Fixed file-checking logic to properly skip existing completed files
  - Tool should now only process the remaining 574 unprocessed files

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architecture Pattern
The application follows a modular CLI architecture with clear separation of concerns:

- **CLI Layer** (`cli.py`): Handles command-line arguments, logging setup, and orchestrates the translation workflow
- **Translation Service** (`translator.py`): Core business logic for AI-powered translation with caching and glossary integration
- **XML Processing** (`xml_utils.py`): Specialized parsing and writing of game-specific .stringtable XML files
- **Caching System** (`cache.py`): SQLite-based persistent storage for translation results
- **Configuration Management** (`config.py`): Centralized configuration validation and management

## Data Flow Design
1. Input XML files are parsed to extract translatable text entries
2. Text is processed through placeholder extraction to preserve game formatting
3. Translation requests are checked against cache before API calls
4. AI translation incorporates glossary terms for consistency
5. Translated text has placeholders restored and is written back to XML format

## AI Integration Strategy
- Uses OpenAI GPT-4o model for high-quality contextual translation
- Implements rate limiting and retry logic for API reliability
- Token counting and cost estimation for budget management
- Batch processing for efficiency while respecting API limits

## Data Storage Architecture
- **SQLite Cache**: Persistent storage for translated strings with hash-based lookup
- **CSV Glossary**: Human-readable terminology mapping for consistent translations
- **XML Preservation**: Maintains original game file structure and formatting

## Error Handling and Reliability
- Comprehensive logging with both console and file output
- Retry mechanisms for transient API failures
- Input validation for all configuration parameters
- Graceful handling of malformed XML files

# External Dependencies

## AI/ML Services
- **OpenAI API**: GPT-4o model for neural machine translation
- **tiktoken**: Token counting for cost estimation and API compliance

## Core Libraries
- **lxml**: Advanced XML parsing and manipulation
- **sqlite3**: Built-in database for translation caching (Python standard library)

## Development Tools
- **unittest**: Testing framework for core functionality
- **pathlib**: Modern file path handling (Python standard library)
- **argparse**: Command-line interface construction (Python standard library)

## File Format Support
- **XML**: Pillars of Eternity .stringtable file format
- **CSV**: Glossary file format for terminology management
- **JSON**: Structured data exchange with OpenAI API

The architecture is designed to be maintainable and extensible, with clear interfaces between components and comprehensive error handling throughout the translation pipeline.