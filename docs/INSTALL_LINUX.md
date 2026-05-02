# Install and run on Linux

## 1. Install Python and Tkinter

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
```

## 2. Open a terminal in the project folder

```bash
cd path/to/visiontrack-modern-human-tracking
```

## 3. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install requirements

```bash
pip install -r requirements.txt
```

## 5. Run the GUI

```bash
python src/desktop_gui.py
```

## 6. Webcam permission

Make sure your user has access to the webcam.

Check video devices:

```bash
ls /dev/video*
```

If webcam index `0` does not work, try another index.
