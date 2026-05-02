# Troubleshooting

## Problem: webcam does not open

Try:

```text
- Close Zoom, Teams, OBS, browser camera tabs, or other camera apps.
- Use webcam index 1 instead of 0.
- Restart the app.
```

## Problem: PowerShell blocks virtual environment activation

Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

## Problem: YOLO model downloads on first run

That is normal. The first run may download `yolov8n.pt`.

## Problem: detections are wrong or too many objects are boxed as people

Try increasing confidence:

```text
0.50 -> 0.55 -> 0.60
```

Higher confidence reduces false detections but may miss small or far-away people.

## Problem: app is slow

Use:

```text
Model: yolov8n.pt
Image size: 640
Confidence: 0.50
```

Close other heavy apps.

## Problem: output files are too large

Use shorter demo runs or delete old outputs from:

```text
outputs/
```

Do not commit large output videos to GitHub unless you use Git LFS.
