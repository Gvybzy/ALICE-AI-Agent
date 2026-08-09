# ALICE

A voice-and-text desktop agent for Windows. Type or speak a command and ALICE opens apps and websites, launches "modes" (bundles of apps/sites for study, coding, gaming, etc.), reads you the news and weather, and can lock/sleep/shut down your PC.

## Requirements

- Windows 10/11
- Python 3.9+
- No third-party pip packages — everything is standard library
- Text-to-speech and voice input use Windows' built-in `System.Speech` via PowerShell

## Setup

1. Clone or download this repo anywhere — the scripts find their own folder automatically
2. Run: `python agent.py`
3. If `python` isn't on your PATH, use: `py agent.py`

To create a one-click launcher, create a `.bat` file:
```batch
@echo off
python "C:\path\to\ALICE\agent.py"
pause