# Gemini Code Assistant Context

## Project Overview

This project is a desktop utility application built with Python and the PySide6 GUI framework. Its primary purpose is to generate QR codes and their corresponding JSON data structure based on user-provided device manufacturing information.

The application is designed to be simple and extensible. All source code is contained within a single file, `main.py`. It uses a `MainWindow` class to define the UI and connect user actions (like button clicks) to the core logic for JSON and QR code generation.

**Key Technologies:**
- **Language:** Python
- **GUI Framework:** PySide6
- **QR Code Generation:** `qrcode` library (with `Pillow` for image handling)
- **Packaging:** `pyinstaller` for creating standalone executables

## Building and Running

The project uses a standard Python virtual environment (`venv`) to manage dependencies.

### 1. Environment Setup

To set up the development environment, run the following commands from the project root:

```bash
# Create the virtual environment
python3 -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Application

With the virtual environment activated, run the following command to start the application:

```bash
python main.py
```

### 3. Packaging for Distribution

To create a standalone executable for Windows (.exe) or macOS (.app), use `pyinstaller`:

```bash
pyinstaller --name SRE-QR-Generator --onefile --windowed main.py
```
The distributable file will be located in the `dist/` directory.

## Development Conventions

- **Code Structure:** The application is contained in a single file (`main.py`) and organized within the `MainWindow` class.
- **UI and Logic:** UI elements and business logic are kept within the `MainWindow` class. UI widgets are managed in a dictionary (`self.inputs`) to allow for easy extension with new fields.
- **Dependencies:** All Python dependencies are listed in `requirements.txt`.
- **Styling:** UI styling is handled via a global stylesheet applied to the main window, as seen with the `QPushButton` styles.
- **Testing:** There is currently no test suite for this project.
