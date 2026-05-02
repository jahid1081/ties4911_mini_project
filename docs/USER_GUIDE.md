# User guide

## Main idea

VisionTrack tracks people in real video. It shows bounding boxes, track IDs, movement trails, and movement direction.

## Mode 1 - Webcam stream

Use this for live demonstration.

Recommended testing setup:

```text
Webcam index: 0
Segment length: 1 minute
Model: yolov8n.pt
Confidence: 0.50
Tracker: botsort.yaml
Confirmed frames: 3
```

For the real demo, set segment length to 10 minutes.

The app saves files in timestamped session folders.

## Mode 2 - Video file demo

Use this for MOT17 or any other MP4 file.

Recommended settings:

```text
Model: yolov8n.pt
Confidence: 0.50
Tracker: botsort.yaml
Confirmed frames: 3
Max frames: 300 for quick demo
```

## Output files

For each run, VisionTrack saves:

```text
annotated video
tracking CSV log
summary JSON
```

You can generate charts from the CSV log with:

```bash
python scripts/summarize_tracking_log.py --csv path/to/log.csv --output-dir outputs/logs
```

## How to stop

For webcam streaming:

- Press `q` inside the tracking preview window, or
- Close the tracking preview window, or
- Click **Stop Webcam Stream** in the GUI.

The current segment is finalized before the app stops.
