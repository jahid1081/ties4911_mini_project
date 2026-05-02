# VisionTrack - Modern Multi-Person Human Tracking

VisionTrack is a beginner-friendly Python application for real-time human detection and tracking. It uses YOLO-based person detection with OpenCV video processing and can run on a normal laptop.

This project modernizes earlier classical computer vision work on human detection and tracking. The current implementation focuses on practical multi-person tracking from a webcam or a public continuous video dataset such as MOT17.

## What the app can do

- Run a continuous webcam tracking stream.
- Save webcam recordings into timestamped segments, for example every 10 minutes.
- Run tracking on a selected MOT17 or MP4 video file.
- Draw bounding boxes, track IDs, movement trails, and direction labels.
- Save annotated videos, CSV tracking logs, and JSON summaries.
- Generate simple charts from the tracking logs.

## What this project does not claim

- It does not claim perfect detection.
- It does not classify walking sticks as separate objects.
- It tracks people as people. A person using one stick or two sticks should still be tracked if the person detector sees the body.
- It does not use filtered unrelated image subsets as tracking evidence.

## Quick start for beginners

### Step 1 - Install Python

Install Python 3.10, 3.11, or 3.12 from the official Python website.

During installation on Windows, tick:

```text
Add Python to PATH
```

### Step 2 - Download this project

If you use GitHub:

```bash
git clone https://github.com/YOUR_USERNAME/visiontrack-modern-human-tracking.git
cd visiontrack-modern-human-tracking
```

If you do not use GitHub, click the green **Code** button on GitHub, choose **Download ZIP**, unzip it, and open the folder.

### Step 3 - Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4 - Install requirements

```bash
pip install -r requirements.txt
```

### Step 5 - Open the GUI

```bash
python src/desktop_gui.py
```

## Demo mode 1 - Continuous webcam stream

In the GUI:

1. Open the **Webcam Stream** tab.
2. Use webcam index `0`.
3. Use segment length `1` minute for testing.
4. Use segment length `10` minutes for the real demo.
5. Click **Start Webcam Stream**.
6. Close the tracking preview window or press `q` to stop.

Outputs are saved in:

```text
outputs/webcam_sessions/
```

Each session has timestamped segment files.

## Demo mode 2 - MOT17 or MP4 file

In the GUI:

1. Open the **MOT17 / Video File** tab.
2. Choose an MP4 video file.
3. Set output name.
4. Click **Run File Demo**.

Outputs are saved in:

```text
outputs/videos/
outputs/logs/
```

## Command-line examples

Webcam smoke test:

```bash
python src/track_people.py --source 0 --display --output-name webcam_smoke --max-frames 200
```

MOT17 video test:

```bash
python src/track_people.py --source data/sample_videos/MOT17-02-DPM_300frames.mp4 --display --output-name mot17_demo --max-frames 300
```

Generate charts:

```bash
python scripts/summarize_tracking_log.py --csv outputs/logs/mot17_demo_tracking_log.csv --output-dir outputs/logs
```

## Recommended default settings

```text
Model: yolov8n.pt
Tracker: botsort.yaml
Confidence: 0.50
Confirmed frames: 3
```

These settings are chosen because a lower confidence value produced persistent false person tracks in MOT17 testing.

## Folder structure

```text
src/
  desktop_gui.py
  track_people.py
  visiontrack/
    tracking_engine.py
    utils.py

scripts/
  mot17_sequence_to_video.py
  summarize_tracking_log.py
  make_video_slow.py

docs/
  INSTALL_WINDOWS.md
  INSTALL_MACOS.md
  INSTALL_LINUX.md
  USER_GUIDE.md
  MOT17_GUIDE.md
  TROUBLESHOOTING.md
  PROJECT_SCOPE.md

outputs/
  videos/
  logs/
  webcam_sessions/
```

## License

MIT License.
