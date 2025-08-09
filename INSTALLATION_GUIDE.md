# Pillars of Eternity Farsi Language Mod - Installation Guide

## What This Tool Creates

This tool generates a complete Farsi language mod for Pillars of Eternity that:

1. **Safely integrates** into the game's existing language system
2. **Preserves game integrity** by using the Italian language slot
3. **Maintains all formatting** and game-specific placeholders
4. **Creates professional-quality** translations using AI

## Output Structure

The tool creates this exact folder structure that mirrors the game's language system:

```
out/
└── localized/
    └── it/              # Italian language slot (replaced with Farsi)
        └── text/
            ├── conversations/
            ├── game/
            └── quests/
```

## How to Install the Farsi Mod in Pillars of Eternity

### Step 1: Locate Your Game Installation
Find your Pillars of Eternity installation directory:
- **Steam**: `Steam/steamapps/common/Pillars of Eternity/`
- **GOG**: Usually in `Program Files (x86)/GOG Galaxy/Games/Pillars of Eternity/`

### Step 2: Navigate to Game Data
Go to: `PillarsOfEternity_Data/data/localized/`

### Step 3: Backup Original Italian Files (Optional)
1. Rename the existing `it` folder to `it_backup`
2. This preserves the original Italian translation

### Step 4: Install Farsi Translation
1. Copy the entire `it` folder from the tool's `out/localized/` directory
2. Paste it into the game's `localized/` directory
3. The path should be: `PillarsOfEternity_Data/data/localized/it/`

### Step 5: Switch to Farsi in Game
1. Launch Pillars of Eternity
2. Go to Options → Language
3. Select "Italiano" (this will now show Farsi text)
4. Restart the game

## Switching Back to English
1. In-game Options → Language → Select "English"
2. Restart the game

## Why Use the Italian Slot?
- **Safe**: Doesn't modify core English files
- **Reversible**: Easy to switch back to English
- **Clean**: Follows game's language system exactly
- **Stable**: No risk of breaking the game

## Verification
After installation, you should see:
- Main menus in Farsi
- All dialogue in Farsi
- Quest text in Farsi
- Game interface elements in Farsi

The translation preserves all game mechanics, formatting, and special codes.