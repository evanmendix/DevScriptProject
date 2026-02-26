# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DevScriptProject is a Windows system automation toolkit with two main components:

1. **Script Launcher GUI** (`script_launcher.py`) - A CustomTkinter-based desktop application for managing and executing scripts
2. **Screen Scheduler** (`scheduler.py`) - An automated screen control scheduler for weekday routines

The project also contains various utility scripts for Windows system management, development environment setup, and work-related automation.

## Environment Setup

### Python Environment
- **Python Version**: 3.13+
- **Package Manager**: UV (ultra-fast Python package manager)
- **Virtual Environment**: `.venv` directory

### Setup Commands
```powershell
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.ps1 | powershell

# Create and activate virtual environment
uv venv
.venv/Scripts/activate

# Install dependencies
uv pip install -e .
```

### Dependencies
- `customtkinter>=5.2.2` - Modern GUI framework based on Tkinter
- `pillow>=10.2.0` - Image processing library
- Python standard library modules: `subprocess`, `threading`, `queue`, `json`, `pathlib`

## Running the Applications

### Script Launcher GUI
```powershell
python script_launcher.py
```

### Screen Scheduler
```powershell
python scheduler.py
```
Runs as a background process scheduling screen control routines at 08:30 and 17:30 on weekdays.

## Architecture

### Script Launcher Architecture

The `script_launcher.py` follows an MVC-inspired pattern:

- **Model**: `scripts.json` configuration file containing script definitions
- **View**: CustomTkinter UI components (two-pane layout with tabbed console output)
- **Controller**: Event handlers in `ScriptLauncher` class managing script execution and UI updates

**Key architectural features**:
- **Asynchronous Execution**: All scripts run in background threads to keep UI responsive
- **Thread-Safe Logging**: Uses `queue.Queue` to safely pass output from background threads to main UI thread
- **Configuration-Driven**: All user customizations stored in `scripts.json`
- **Concurrent Background Scripts**: Supports running multiple background scripts with tabbed output for each

**Script execution types**:
- `one-time`: Executes once and terminates
- `background`: Runs continuously in background with dedicated console tab

### Screen Scheduler Architecture

The `scheduler.py` provides automated screen control:

- **Morning Routine (08:30)**: Extends displays, sets brightness to 100%
- **Evening Routine (17:30)**: Switches to internal display, dims brightness to 0%
- **Scheduling Logic**: Uses time-based triggers with a 2-minute window to avoid duplicate execution
- **Utility Module**: `windows/screen_control/screen_utils.py` contains reusable screen control functions

## Code Organization

### Root Python Files
- `script_launcher.py` - Main GUI application (single-file monolithic design)
- `scheduler.py` - Screen scheduling daemon
- `scripts.json` - Configuration for script launcher (script definitions with name, path, type)

### Utility Scripts by Category

**Windows System Management** (`windows/`):
- `screen_control/` - Display and brightness automation (Python utilities + PowerShell/Batch scripts)
- `network/` - WiFi connection monitoring and auto-run setup
- `windows_update/` - Windows Update control utilities
- `ddns/` - Cloudflare DDNS update script

**Development Setup** (`install-script/`):
- `install_all.ps1` - One-command installation of all dev tools
- `dev-tools/` - Individual installers for Git, Java 17, Node.js (via nvm), Python, UV, VS Code
- `package-managers/` - Chocolatey and Scoop installers

**Work-Specific** (`work-script/`):
- `cht/` - CHT (Chunghwa Telecom) proxy toggle utilities

**Application Tools** (`windsurf/`):
- Icon switching utility for Windsurf application

**Remote Access** (`remote-tools/`):
- Parsec remote desktop installer

### Script Formats
- `.py` - Python scripts (require virtual environment activation)
- `.bat` - Windows batch files (direct execution)
- `.ps1` - PowerShell scripts (may require ExecutionPolicy bypass)

## scripts.json Schema

Configuration file for the Script Launcher GUI:

```json
[
    {
        "name": "Display Name",
        "path": "C:/absolute/path/to/script.ext",
        "type": "one-time" | "background"
    }
]
```

## Common Development Workflows

### Adding a New Utility Script

1. Create script in appropriate category directory (e.g., `windows/new_category/`)
2. For Python scripts, import utilities from `windows/screen_control/screen_utils.py` if needed
3. Update category README.md with script description
4. Add to `scripts.json` if GUI integration is desired

### Modifying Screen Scheduler

- Adjust timing in `scheduler.py` by changing `MORNING_AT` and `EVENING_AT` constants
- Modify routines by editing `morning_routine()` and `evening_routine()` functions
- Screen control functions are in `windows/screen_control/screen_utils.py`

### Extending Script Launcher GUI

The GUI is monolithic (single file), so modifications involve:
1. UI layout changes in `ScriptLauncher.__init__()`
2. Event handlers as methods in `ScriptLauncher` class
3. Script execution logic uses threading model - maintain thread safety when adding features
4. Console output uses tabbed interface - new tabs created via `_ensure_log_tab()`

## Important Constraints

### Path Handling
- Always use absolute paths in `scripts.json`
- PowerShell scripts require `-ExecutionPolicy Bypass` flag when executed programmatically
- Batch files executed via `cmd /c`

### Threading Model
- UI must remain on main thread (Tkinter requirement)
- Script execution happens in worker threads
- Use `log_queue` for cross-thread communication
- Never block main thread with subprocess calls

### Script Types
- **one-time scripts**: Execute once, terminate on completion
- **background scripts**: Continuous processes with dedicated console tabs, can be stopped by user

## Testing Script Execution

Test scripts individually before adding to launcher:

```powershell
# Batch files
cmd /c path\to\script.bat

# PowerShell
powershell -ExecutionPolicy Bypass -File path\to\script.ps1

# Python scripts (activate venv first)
.venv\Scripts\activate
python path\to\script.py
```

## File Paths Convention

The project uses Windows-style paths with forward slashes in JSON configuration for cross-compatibility:
- `scripts.json`: Use forward slashes (`C:/path/to/file`)
- Python code: Use `pathlib.Path` for path manipulation
- Batch/PowerShell: Use backslashes as standard Windows convention
