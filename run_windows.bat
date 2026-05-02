@echo off
setlocal

echo VisionTrack - Windows launcher
echo.

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Make sure Python 3.10, 3.11, or 3.12 is installed.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat

echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo Starting VisionTrack GUI...
python src\desktop_gui.py
pause
