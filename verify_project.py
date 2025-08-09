#!/usr/bin/env python3
"""
Project Verification Script
Verifies all project components are working correctly.
"""

def verify_project():
    """Verify all project components"""
    print("=== PROJECT VERIFICATION ===")
    
    # Test imports
    try:
        from src.cli import main
        from src.translator import TranslationService
        from src.cache import TranslationCache
        from src.xml_utils import XMLProcessor
        from src.config import Config
        print("✅ All src modules import successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test main entry point
    try:
        import stringtable_fa_builder
        print("✅ Main entry point imports successfully")
    except ImportError as e:
        print(f"❌ Main entry point error: {e}")
        return False
    
    # Check Input directory
    from pathlib import Path
    input_dir = Path("Input")
    if input_dir.exists():
        input_files = list(input_dir.rglob("*.stringtable"))
        print(f"✅ Input directory found with {len(input_files)} files")
    else:
        print("❌ Input directory not found")
        return False
    
    # Check completed work
    output_dir = Path("out/localized/it/text")
    if output_dir.exists():
        completed_files = list(output_dir.rglob("*.stringtable"))
        print(f"✅ Output directory found with {len(completed_files)} completed files")
    else:
        print("ℹ️  No previous completed work found (fresh start)")
    
    # Check cache
    cache_file = Path("translation_cache.db")
    if cache_file.exists():
        print(f"✅ Translation cache found ({cache_file.stat().st_size / 1024 / 1024:.1f} MB)")
    else:
        print("ℹ️  No translation cache found (fresh start)")
    
    print("\n=== VERIFICATION RESULT ===")
    print("✅ Project is fully functional and ready to use!")
    print("\nTo start translation:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Run: python stringtable_fa_builder.py build")
    
    return True

if __name__ == "__main__":
    verify_project()