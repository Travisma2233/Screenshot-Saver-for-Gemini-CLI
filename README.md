# Screenshot Saver for Gemini CLI

**A clipboard screenshot auto-save tool designed specifically for Gemini CLI users**

> 🎯 **Project Background**: Since Gemini CLI cannot directly paste images into the terminal, this tool helps you quickly save screenshots and get file paths, making it convenient to have image-related conversations with Gemini.

## Why do you need this tool?

When using Gemini CLI, you might encounter the following situations:
- 🔍 Need to analyze screenshot content, but cannot paste images directly
- 📊 Want to discuss charts or data visualizations, but terminal doesn't support image input
- 🎨 Need to analyze design mockups or interface screenshots, but can only reference via file paths

**Solution**: Use hotkey to save screenshot → Copy file path → Reference image file in Gemini CLI

## Features

- 🖼️ Automatically monitor screenshots in clipboard
- ⌨️ Support custom hotkeys (default: Ctrl+Alt+P)
- 🔄 Smart deduplication to avoid saving duplicate screenshots
- 📁 Automatically create timestamped filenames
- 📋 Automatically copy file path to clipboard (convenient for pasting into Gemini CLI)
- ⚙️ Configurable save path and hotkeys
- 🚀 One-click packaging into EXE file

## Working with Gemini CLI

### Workflow
1. **Screenshot**: Use any screenshot tool (WeChat, QQ, Snipping Tool, etc.)
2. **Save**: Press `Ctrl+Alt+P` to save the screenshot
3. **Copy Path**: Program automatically copies file path to clipboard
4. **Paste to Gemini**: Paste file path in Gemini CLI for discussion

### Usage Example
```bash
# In Gemini CLI
gemini> Please analyze the content in this screenshot: C:\Users\username\screenshots\screenshot_20241201_143022.png
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Program

### Method 1: GUI Mode (Recommended)
The program will pop up a folder selection dialog when started, and automatically hide the console after selecting the screenshot save location.

```bash
# Run GUI version (will pop up folder selection dialog)
python clipboard_screenshot_saver_gui.py

# Or use batch file (recommended)
run_gui.bat

# Completely silent mode
run_silent.bat
```

### Method 2: Command Line Mode
```bash
python clipboard_screenshot_saver.py
```

### Method 3: Run Packaged EXE File
1. First build the EXE file:
   ```bash
   # Method 1: Use batch file (recommended)
   build.bat
   
   # Method 2: Use Python script
   python build.py
   
   # Method 3: Manual PyInstaller
   pyinstaller --clean screenshot_app.spec
   ```

2. Run the generated EXE file:
   ```
   dist\ScreenshotSaver.exe
   ```

## Usage Instructions

1. **Start the Program**:
   - **GUI Mode**: Double-click `run_silent.bat` or run `python clipboard_screenshot_saver_gui.py`
   - First run will pop up a folder selection dialog, choose the folder where you want to save screenshots
   - Program will show startup notification, then automatically hide to background

2. **Save Screenshots**:
   - Use any screenshot tool (WeChat, QQ, Snipping Tool, etc.) to take a screenshot
   - Screenshot will automatically copy to clipboard
   - Press hotkey `Ctrl+Alt+P` to save the screenshot
   - **Program automatically copies file path to clipboard**, convenient for pasting into Gemini CLI

3. **Use in Gemini CLI**:
   - After screenshot is saved, file path is already copied to clipboard
   - Paste path directly in Gemini CLI to reference the image
   - Example: `Please analyze this screenshot: C:\Users\username\screenshots\screenshot_20241201_143022.png`

4. **Exit Program**: Press `Ctrl+C` or close console window

## Configuration File

The program will automatically create `screenshot_config.json` configuration file:

```json
{
  "save_path": "screenshots",
  "hotkey": "ctrl+alt+p",
  "total_screenshots": 0,
  "auto_copy_path": true
}
```

- `save_path`: Screenshot save directory
- `hotkey`: Hotkey for saving screenshots
- `total_screenshots`: Total number of saved screenshots
- `auto_copy_path`: Whether to automatically copy file path to clipboard

## Hotkey Format

Supported hotkey formats:
- `ctrl+alt+p` (default)
- `ctrl+shift+s`
- `alt+f1`
- `ctrl+alt+shift+s`

## Build Instructions

### Build File Description

- `requirements.txt`: Python dependency package list
- `screenshot_app.spec`: PyInstaller configuration file
- `build.py`: Automated build script
- `build.bat`: Windows batch build script
- `create_icon.py`: Icon generation script

### Build Options

1. **Console Version**: Set `console=True` in `screenshot_app.spec`
2. **Windowless Version**: Set `console=False` in `screenshot_app.spec`

## System Requirements

- Windows 10/11
- Python 3.7+
- Supported screenshot tools (built-in system tools, WeChat, QQ, etc.)
- Gemini CLI (for image analysis)

## Notes

- Program needs to run on Windows system
- First run will automatically create screenshots directory
- Supports common image formats like PNG, JPEG, BMP
- Program automatically filters duplicate screenshots (based on image content hash)
- **File path automatically copies to clipboard**, convenient for use in Gemini CLI

## Troubleshooting

### Common Issues

1. **Hotkey not working**
   - Check if hotkey is occupied by other programs
   - Try modifying hotkey in configuration file

2. **Screenshot save failed**
   - Ensure clipboard contains an image
   - Check write permissions for save directory

3. **Program cannot start**
   - Check if all dependency packages are installed
   - Ensure Python version compatibility

4. **File path not copied to clipboard**
   - Check `auto_copy_path` setting in configuration file
   - Ensure program has clipboard access permissions

### Build Issues

1. **PyInstaller build failed**
   - Ensure latest version of PyInstaller is installed
   - Check if dependency packages are correctly installed

2. **EXE file too large**
   - This is normal as it includes Python runtime environment
   - Can consider using UPX compression (already enabled in spec file)


- **Optimized for Gemini CLI users**
