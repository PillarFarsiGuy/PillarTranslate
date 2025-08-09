#!/usr/bin/env python3
"""
Progress Preservation Script
Run this to verify your completed work is properly preserved.
"""

import os
from pathlib import Path

def check_progress():
    """Check current progress status"""
    print("=== PILLARS OF ETERNITY FARSI TRANSLATION PROGRESS ===")
    
    # Check output files
    output_dir = Path("out/localized/it/text")
    if output_dir.exists():
        completed_files = list(output_dir.rglob("*.stringtable"))
        print(f"✅ Completed translations: {len(completed_files)} files")
        print(f"📁 Location: {output_dir}")
    else:
        print("❌ No completed translations found")
    
    # Check cache
    cache_file = Path("translation_cache.db")
    if cache_file.exists():
        cache_size = cache_file.stat().st_size / 1024 / 1024  # MB
        print(f"✅ Translation cache: {cache_size:.1f} MB")
        print(f"💾 Location: {cache_file}")
    else:
        print("❌ No translation cache found")
    
    # Check Input files
    input_dir = Path("Input")
    if input_dir.exists():
        input_files = list(input_dir.rglob("*.stringtable"))
        print(f"✅ Input files available: {len(input_files)} files")
        remaining = len(input_files) - len(completed_files) if output_dir.exists() else len(input_files)
        print(f"📊 Progress: {len(completed_files) if output_dir.exists() else 0}/{len(input_files)} files ({len(completed_files)/len(input_files)*100 if output_dir.exists() and input_files else 0:.1f}%)")
        print(f"⏳ Remaining: {remaining} files")
    else:
        print("❌ Input directory not found")
    
    print("\n=== NEXT STEPS ===")
    print("1. When downloading new version, copy these files:")
    print(f"   • {output_dir}/ (all your completed translations)")
    print(f"   • {cache_file} (saves API costs)")
    print("2. Set OPENAI_API_KEY environment variable")
    print("3. Run: python stringtable_fa_builder.py build")
    print("\nThe tool will skip completed files and continue from where you left off!")

if __name__ == "__main__":
    check_progress()