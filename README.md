# Borderless Focus Timer

A desktop focus timer built with Python and Tkinter, featuring a borderless user interface, floating window capabilities, and minimal background footprints.

## Features

- **Borderless Interface**: Utilizes system window override settings (`overrideredirect`) to remove standard OS title bars, delivering a clean and non-intrusive UI widget.
- **Floating Mini Mode**: Supports collapsing the main window into a lightweight floating icon in the lower-right corner for background operation without cluttering the workspace.
- **Dynamic Animation & Alerts**: Features visual text zooming and background color pulse alerts during the final 10 seconds of a countdown in mini mode.
- **Smart Pause on Lock/Sleep**: Integrates native Windows system event listeners (`pywin32`) to automatically pause the timer when your PC locks or enters sleep mode.
- **Drag-and-Drop Navigation**: Allows both the main window and mini window to be freely moved across the desktop.
- **Accurate Event Handling**: Distinguishes between click and drag actions to prevent accidental UI toggles.
- **Pomodoro Workflow Cycle**: Includes a 60-minute focus session followed by a 5-minute break.
- **Customizable Themes & Opacity**: Supports Catppuccin, Dark Gold, and Pastel Pink themes with adjustable opacity.
- **Autostart Compatibility**: Can be packaged as a standalone executable and launched automatically when Windows starts.

---

## Architecture & Technology Stack

- **GUI Framework:** Python `tkinter`
- **System Integration:** `pywin32`
- **Threading & Event Loop:** Tkinter `after()`
- **Compilation Tool:** PyInstaller

---

## Prerequisites

- Python 3.8 or higher
- Windows OS

---

## Installation & Setup

## Download

You can download the latest Windows executable from:

Releases:
https://github.com/SeniorBugEngineer/mini-focus-timer/releases

No Python installation required.

### 1. Clone the Repository

```bash
git clone https://github.com/SeniorBugEngineer/mini-focus-timer.git
cd mini-focus-timer
```

### 2. Install Required Dependencies

Install **pywin32** for Windows lock/sleep event integration.

```bash
pip install pywin32
```

---

## Build Executable (.exe)

Install **PyInstaller**:

```bash
pip install pyinstaller
```

Build the executable:

```bash
python -m PyInstaller --noconsole --onefile timer.py
```

After the build completes, the executable will be generated in:

```text
dist/
└── timer.exe
```

---

## Launch Automatically When Windows Starts

To automatically launch the application whenever Windows starts:

1. Press **Win + R**.
2. Type:

```text
shell:startup
```

3. Press **Enter**.
4. Copy **timer.exe** into the Startup folder.

The application will automatically launch each time you sign in to Windows.
