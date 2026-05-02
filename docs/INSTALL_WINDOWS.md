# Install and run on Windows

This guide is written for beginners.

## 1. Install Python

1. Go to the official Python website.
2. Download Python 3.10, 3.11, or 3.12.
3. Run the installer.
4. Tick **Add Python to PATH**.
5. Click **Install Now**.

## 2. Open the project folder

Open PowerShell in the project folder.

A simple way:

1. Open the project folder in File Explorer.
2. Click the address bar.
3. Type `powershell`.
4. Press Enter.

## 3. Create a virtual environment

```powershell
python -m venv .venv
```

## 4. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activation again.

## 5. Install requirements

```powershell
pip install -r requirements.txt
```

## 6. Run the GUI

```powershell
python src/desktop_gui.py
```

## 7. Test the webcam

In the GUI:

1. Open **Webcam Stream**.
2. Keep webcam index `0`.
3. Set segment length to `1` minute for testing.
4. Click **Start Webcam Stream**.
5. Close the preview window or press `q` to stop.

## 8. Test a video file

In the GUI:

1. Open **MOT17 / Video File**.
2. Click **Choose video**.
3. Select an MP4 file.
4. Click **Run File Demo**.
