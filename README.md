# Pillars of Eternity Farsi Translation Tool

Creates a complete Farsi language mod for Pillars of Eternity using OpenAI translation.

## 🎯 What This Creates
- **Complete Farsi language mod** for Pillars of Eternity
- **1,116 game text files** translated (conversations, quests, UI, items)
- **Safe installation** into Italian language slot
- **Easy switching** between English and Farsi in-game

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# 2. Start translation
python stringtable_fa_builder.py build
```

### Resuming Work (if you have previous version)
```bash
# 1. Copy from your old project:
#    - out/localized/it/text/ (completed translations)
#    - translation_cache.db (translation cache)

# 2. Check your progress
python preserve_progress.py

# 3. Continue translation
python stringtable_fa_builder.py build
```

## 📊 Current Status
- **542 files completed** (48.6% done)
- **574 files remaining** (51.4%)
- Tool automatically skips completed files

## 🎮 Installing the Farsi Mod

1. **Copy** `out/localized/it/` to your game's `localized/` directory
2. **In game**: Options → Language → Italiano
3. **Restart** the game
4. **Enjoy** Pillars of Eternity in Farsi!

See `INSTALLATION_GUIDE.md` for detailed instructions.

## 📁 Project Structure
```
├── stringtable_fa_builder.py  # Main CLI tool
├── src/                       # Core modules
├── Input/                     # Game text files (1,116 total)
├── out/localized/it/text/     # Completed Farsi translations
├── translation_cache.db       # Translation cache (saves API costs)
└── translation.log           # Progress logs
```

## 🛠️ Commands
```bash
# Translate files
python stringtable_fa_builder.py build

# Preview what will be translated (no API calls)
python stringtable_fa_builder.py dry-run

# Verify existing translations
python stringtable_fa_builder.py verify

# Check progress
python preserve_progress.py
```

## 🔧 Features
- **Smart caching** prevents re-translation
- **Preserves game formatting** and placeholders
- **Handles API rate limits** automatically
- **Comprehensive logging** of progress
- **Safe game integration** via Italian language slot

The tool creates a professional-quality Farsi language experience for Pillars of Eternity players!