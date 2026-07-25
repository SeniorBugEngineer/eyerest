# Borderless Focus Timer

A desktop focus timer built with Python and Tkinter, featuring a borderless user interface, floating window capabilities, and minimal background footprints.

## Features

- **Borderless Interface**: Utilizes system window override settings (`overrideredirect`) to remove standard OS title bars, delivering a clean and non-intrusive UI widget.
- **Floating Mini Mode**: Supports collapsing the main window into a lightweight floating icon in the lower-right corner for background operation without cluttering the workspace.
- **Drag-and-Drop Navigation**: Custom mouse event handlers mapped to window coordinates allow unrestricted dragging across the desktop for both the primary UI and the mini icon.
- **Accurate Event Handling**: Implements click-drag motion thresholding to differentiate between mouse drag actions and restore click events, preventing accidental UI toggles.
- **Pomodoro Workflow Cycle**: Pre-configured work/break intervals (60-minute focus session followed by a 5-minute break) with background state tracking and modal alerts on interval completion.
- **Autostart Compatibility**: Configured for standalone binary compilation via PyInstaller, allowing seamless integration into the Windows Startup sequence.

## Architecture & Technology Stack

- **GUI Framework**: Python `tkinter`
- **Threading & Event Loop**: Asynchronous UI updates driven by Tkinter `after()` scheduler
- **Color Palette**: Dark theme based on the Catppuccin Macchiato palette (`#1e1e2e`, `#89b4fa`, `#f38ba8`)
- **Compilation Tool**: PyInstaller (Bootloader/Onefile mode)

## Prerequisites

- Python 3.8 or higher
- Windows OS (recommended for native `overrideredirect` window management)

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/Ren0506/mini-focus-timer.git](https://github.com/Ren0506/mini-focus-timer.git)
   cd mini-focus-timer
