#!/usr/bin/env bash
set -e

echo "VisionTrack - macOS/Linux launcher"
echo

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Python was not found."
    echo "Please install Python 3.10, 3.11, or 3.12 and try again."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON_CMD" -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting VisionTrack GUI..."
python src/desktop_gui.py
