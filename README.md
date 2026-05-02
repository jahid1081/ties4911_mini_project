# VisionTrack - Modern Multi-Person Human Tracking

VisionTrack is a laptop-friendly Python application for detecting and tracking people in video. It uses YOLO for person detection, OpenCV for video processing, and BoT-SORT or ByteTrack for multi-person tracking.

The project was built as a modern continuation of earlier human detection and tracking work. Instead of classical computer vision methods, this version uses a modern YOLO-based pipeline that can run on a normal laptop with a webcam or a video file.

## What this project does

- Tracks multiple people in a video stream.
- Works with a normal webcam.
- Works with MP4 video files, including converted MOT17 sequences.
- Draws person bounding boxes, track IDs, movement trails, and movement directions.
- Saves annotated video files.
- Saves CSV tracking logs.
- Saves JSON run summaries.
- Can generate charts from saved tracking logs.
- Includes a simple desktop GUI for non-programmers.

## Demo modes

### 1. Continuous webcam stream

Use this mode when you want the system to keep running from a webcam.

The webcam mode:

- opens a live tracking preview,
- keeps running until the preview window is closed or stopped,
- saves timestamped output segments,
- can save a new video/log file every 10 minutes,
- can use shorter segments, such as 1 minute, for testing.

Example output folder:

```text
outputs/webcam_sessions/session_YYYYMMDD_HHMMSS/
```

### 2. MOT17 or video file demo

Use this mode when you want to choose a local video file and run tracking on it.

The file demo mode:

- lets the user select an MP4 file,
- runs person detection and tracking,
- saves an annotated video,
- saves a CSV tracking log,
- saves a JSON summary.

## Important scope note

This project tracks people as people. It does not need to detect walking sticks as separate objects to track a person.

A person using one stick, two sticks, crutches, or poles should still be tracked if the person detector sees the body clearly enough.

This project does not claim perfect detection. False detections can happen, especially with posters, mannequins, reflections, or background objects that look like people. The default confidence value was increased to reduce this problem.

## Recommended settings

```text
Model: yolov8n.pt
Tracker: botsort.yaml
Confidence: 0.50
Confirmed frames: 3
```

These settings give a good balance between speed and detection quality for a laptop demo.

## Install and run - quick version

### Step 1 - Install Python

Install Python 3.10, 3.11, or 3.12.

On Windows, tick this option during installation:

```text
Add Python to PATH
```

### Step 2 - Download the project

Clone with Git:

```bash
git clone https://github.com/jahid1081/ties4911_mini_project.git
cd ties4911_mini_project
```

Or download without Git:

1. Click the green **Code** button on this GitHub page.
2. Click **Download ZIP**.
3. Unzip the folder.
4. Open a terminal or PowerShell inside the folder.

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

### Step 5 - Open the desktop GUI

```bash
python src/desktop_gui.py
```

## Detailed setup guides

Use the guide for your operating system:

- [Windows setup guide](docs/INSTALL_WINDOWS.md)
- [macOS setup guide](docs/INSTALL_MACOS.md)
- [Linux setup guide](docs/INSTALL_LINUX.md)

Other useful guides:

- [User guide](docs/USER_GUIDE.md)
- [MOT17 guide](docs/MOT17_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Project scope](docs/PROJECT_SCOPE.md)

## How to use the GUI

Run:

```bash
python src/desktop_gui.py
```

The GUI has four tabs:

```text
Home
Webcam Stream
MOT17 / Video File
Help
```

### Webcam stream tab

1. Set webcam index to `0`.
2. Set segment length to `1` minute for a quick test.
3. Use `10` minutes for the full demo.
4. Click **Start Webcam Stream**.
5. Press `q`, close the preview window, or click **Stop Webcam Stream** to stop.

### MOT17 / video file tab

1. Click **Choose video**.
2. Select an MP4 file.
3. Set an output name.
4. Click **Run File Demo**.

## Command-line examples

You can also run the project without the GUI.

### Webcam smoke test

```bash
python src/track_people.py --source 0 --display --output-name webcam_smoke --max-frames 200
```

### MOT17 or MP4 file test

```bash
python src/track_people.py --source data/sample_videos/MOT17-02-DPM_300frames.mp4 --display --output-name mot17_demo --max-frames 300
```

### Generate charts from a tracking log

```bash
python scripts/summarize_tracking_log.py --csv outputs/logs/mot17_demo_tracking_log.csv --output-dir outputs/logs
```

## MOT17 dataset note

The MOT17 dataset is not included in this repository because datasets and videos can be large.

To use MOT17:

1. Download MOT17 from the official MOTChallenge website.
2. Place it under `data/MOT17/`.
3. Convert one sequence to MP4 with the provided script.

Example:

```bash
python scripts/mot17_sequence_to_video.py --sequence-dir data/MOT17/train/MOT17-02-DPM --output data/sample_videos/MOT17-02-DPM_300frames.mp4 --max-frames 300
```

## Output files

VisionTrack saves outputs under:

```text
outputs/videos/
outputs/logs/
outputs/webcam_sessions/
```

These folders are ignored by Git so that large generated files are not uploaded by mistake.

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
  GITHUB_UPLOAD_GUIDE.md
  AI_USAGE_STATEMENT.md

examples/
  example_commands.md
```

## Privacy and responsible use

The webcam mode records video and tracking logs locally. Use it only in appropriate settings and respect privacy rules, consent requirements, and local laws.

## Known limitations

- Pretrained YOLO models can produce false person detections.
- Small, far-away, or heavily occluded people may be missed.
- Tracking IDs can change when people are occluded or leave and re-enter the scene.
- The app is designed for educational and demo use, not production surveillance.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
