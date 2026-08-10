# ALICE v2.0.0 🤖

A voice-and-text desktop agent for Windows. Type or speak a command and ALICE opens apps and websites, launches "modes" (bundles of apps/sites for study, coding, gaming, etc.), reads you the news and weather, and can lock/sleep/shut down your PC.

## ✨ What's New in v2

- **Remove API Key**: Type `remove api` to delete your stored API key
- **Enhanced Speech Feedback**: ALICE now speaks for all commands
- **Better Error Handling**: Clearer messages and automatic recovery
- **File Permission Fix**: No more EPERM errors when managing config files
- **Voice Overlap Fix**: Cleaner voice response handling

## Requirements

- Windows 10/11
- Python 3.9+
- No third-party pip packages — everything is standard library
- Text-to-speech and voice input use Windows' built-in `System.Speech` via PowerShell

## Setup

1. Clone or download this repo anywhere — the scripts find their own folder automatically
2. Run: `python alice.py`
3. If `python` isn't on your PATH, use: `py alice.py`

To create a one-click launcher, create a `.bat` file:
```batch
@echo off
python "C:\path\to\ALICE\alice.py"
pause
