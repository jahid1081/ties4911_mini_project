# Install and run on macOS

## 1. Install Python

Install Python 3.10, 3.11, or 3.12.

You can use the official Python installer or Homebrew.

With Homebrew:

```bash
brew install python
```

## 2. Open Terminal in the project folder

```bash
cd path/to/visiontrack-modern-human-tracking
```

## 3. Create a virtual environment

```bash
python3 -m venv .venv
```

## 4. Activate the virtual environment

```bash
source .venv/bin/activate
```

## 5. Install requirements

```bash
pip install -r requirements.txt
```

## 6. Run the GUI

```bash
python src/desktop_gui.py
```

## 7. Allow camera access

macOS may ask for camera permission. Allow access for Terminal or the Python app.

If the webcam does not open, close other apps that may be using the camera.
