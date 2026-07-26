# Borderless Focus Timer

A desktop focus timer built with Python and Tkinter, featuring a borderless user interface, floating window capabilities, and minimal background footprints.

## Features

- **Borderless Interface**: Utilizes system window override settings (`overrideredirect`) to remove standard OS title bars, delivering a clean and non-intrusive UI widget.
- **Floating Mini Mode**: Supports collapsing the main window into a lightweight floating icon in the lower-right corner for background operation without cluttering the workspace.
- **Dynamic Animation & Alerts**: Features visual text zooming and background color pulse alerts during the final 10 seconds of a countdown in mini mode to catch your attention easily.
- **Smart Pause on Lock/Sleep**: Integrates native Windows system event listeners (via `pywin32`) to automatically pause the timer when your PC locks or enters sleep mode, and resumes gracefully.
- **Drag-and-Drop Navigation**: Custom mouse event handlers mapped to window coordinates allow unrestricted dragging across the desktop for both the primary UI and the mini icon.
- **Accurate Event Handling**: Implements click-drag motion thresholding to differentiate between mouse drag actions and restore click events, preventing accidental UI toggles.
- **Pomodoro Workflow Cycle**: Pre-configured work/break intervals (60-minute focus session followed by a 5-minute break) with background state tracking and modal alerts on interval completion.
- **Customizable Themes & Opacity**: Includes multiple color palettes (Catppuccin, Dark Gold, Pastel Pink) and adjustable opacity settings (from 40% to 100%).
- **Autostart Compatibility**: Configured for standalone binary compilation via PyInstaller, allowing seamless integration into the Windows Startup sequence.

## Architecture & Technology Stack

- **GUI Framework**: Python `tkinter`
- **System Integration**: `pywin32` (Windows API session change & power broadcast listeners)
- **Threading & Event Loop**: Asynchronous UI updates driven by Tkinter `after()` scheduler
- **Color Palette**: Dark theme based on Catppuccin Macchiato (`#1e1e2e`, `#89b4fa`, `#f38ba8`), Dark Gold, and Pastel Pink
- **Compilation Tool**: PyInstaller (Bootloader/Onefile mode)

## Prerequisites

- Python 3.8 or higher
- Windows OS (recommended for native `overrideredirect` window management & system session events)

## Installation & Setup

### Running from Source Code

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/SeniorBugEngineer/mini-focus-timer.git](https://github.com/SeniorBugEngineer/mini-focus-timer.git)
   cd mini-focus-timer

Install Required Dependencies:
Install pywin32 for Windows system lock/sleep auto-pause event integration:
```bash
pip install pywin32

Build Executable (.exe)
If you'd like to package the app into a standalone executable (.exe) for convenient everyday use or autostart setup:
Install PyInstaller:pip install pyinstaller

Build the Executable:
Run the following command to build a single executable file without opening a command prompt window:python -m PyInstaller --noconsole --onefile timer.py

Locate Your Executable:
Once compilation completes, the generated timer.exe will be saved inside the newly created dist/ directory.
