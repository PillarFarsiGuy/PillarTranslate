"""
Command-line interface for the stringtable translation tool.
"""
import logging
from pathlib import Path
from typing import Optional
import argparse

from src.translator import TranslationService
from src.config import Config
import os
from src.xml_utils import XMLProcessor

logger = logging.getLogger(__name__)

def build_command(input_dir: str, output_dir: str = "out") -> None:
    """Build translated stringtable files."""
    
    input_path = Path(input_dir).expanduser()
    output_path = Path(output_dir)
    
    if not input_path.exists():
        raise ValueError(f"Input directory does not exist: {input_path}")
    
    logger.info(f"Starting translation build from: {input_path}")
    logger.info(f"Output directory: {output_path}")
    
    # Initialize components
    xml_processor = XMLProcessor()
    
    # Create config for translator
    config = Config(
        input_dir=input_path,
        output_dir=output_path,
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        target_language="Farsi",
        batch_size=20
    )
    translator = TranslationService(config)
    
    # Find all stringtable files
    stringtable_files = list(input_path.rglob("*.stringtable"))
    total_files = len(stringtable_files)
    processed_files = 0
    
    logger.info(f"Found {total_files} stringtable files to process")
    
    for file_path in stringtable_files:
        # Calculate relative path and output path
        try:
            relative_path = file_path.relative_to(input_path)
        except ValueError:
            logger.warning(f"Skipping file outside input directory: {file_path}")
            continue
        
        # Map to Italian language slot in output
        output_file_path = output_path / "localized" / "it" / "text" / relative_path
        
        # CHECK OUTPUT FILE INSTEAD OF CACHE
        if output_file_path.exists():
            logger.info(f"Skipping existing file ({processed_files + 1}/{total_files}): {relative_path}")
            processed_files += 1
            continue
        
        logger.info(f"Processing ({processed_files + 1}/{total_files}): {relative_path}")
        
        try:
            # Parse the XML file
            entries = xml_processor.parse_stringtable(file_path)
            
            if not entries:
                # Create empty output file for consistency
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                xml_processor.write_stringtable(output_file_path, entries)
                logger.info(f"Created empty file: {output_file_path}")
                processed_files += 1
                continue
            
            # Extract texts for translation
            texts_to_translate = [entry["text"] for entry in entries if entry["text"].strip()]
            
            if not texts_to_translate:
                # No texts to translate, just copy structure
                translated_entries = entries
            else:
                # Translate texts
                translated_texts = translator.translate_batch(texts_to_translate, batch_size=config.batch_size)
                
                # Update entries with translations
                translated_entries = []
                text_index = 0
                for entry in entries:
                    new_entry = entry.copy()
                    if entry["text"].strip():
                        if text_index < len(translated_texts):
                            new_entry["text"] = translated_texts[text_index]
                            text_index += 1
                    translated_entries.append(new_entry)
            
            # Ensure output directory exists
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the translated file
            xml_processor.write_stringtable(output_file_path, translated_entries)
            
            logger.info(f"Completed: {output_file_path}")
            processed_files += 1
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            continue
    
    logger.info(f"Translation build complete! Processed {processed_files}/{total_files} files")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Translate Pillars of Eternity stringtable files to Farsi"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build translated files")
    build_parser.add_argument("input_dir", help="Input directory containing English stringtable files")
    build_parser.add_argument("--output", default="out", help="Output directory (default: out)")
    
    # Dry run command
    dry_run_parser = subparsers.add_parser("dry-run", help="Show what would be translated")
    dry_run_parser.add_argument("input_dir", help="Input directory containing English stringtable files")
    dry_run_parser.add_argument("--output", default="out", help="Output directory (default: out)")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify existing translations")
    verify_parser.add_argument("output_dir", help="Directory containing translated files")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "build":
            build_command(args.input_dir, args.output)
        elif args.command == "dry-run":
            # For dry-run, just count files that would be processed
            input_path = Path(args.input_dir).expanduser()
            output_path = Path(args.output)
            
            stringtable_files = list(input_path.rglob("*.stringtable"))
            existing_count = 0
            
            for file_path in stringtable_files:
                relative_path = file_path.relative_to(input_path)
                output_file_path = output_path / "localized" / "it" / "text" / relative_path
                if output_file_path.exists():
                    existing_count += 1
            
            to_process = len(stringtable_files) - existing_count
            print(f"Found {len(stringtable_files)} total files")
            print(f"Already completed: {existing_count}")
            print(f"Would process: {to_process} files")
        
        elif args.command == "verify":
            # Simple verification - check if files exist and are valid XML
            output_path = Path(args.output_dir)
            if not output_path.exists():
                print(f"Output directory does not exist: {output_path}")
                return
            
            translated_files = list(output_path.rglob("*.stringtable"))
            print(f"Found {len(translated_files)} translated files")
            
            # Could add XML validation here
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1

if __name__ == "__main__":
    main()
