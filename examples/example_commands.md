# Example commands

## Open GUI

```bash
python src/desktop_gui.py
```

## Webcam command line smoke test

```bash
python src/track_people.py --source 0 --display --output-name webcam_smoke --max-frames 200
```

## Convert MOT17 sequence

```bash
python scripts/mot17_sequence_to_video.py --sequence-dir data/MOT17/train/MOT17-02-DPM --output data/sample_videos/MOT17-02-DPM_300frames.mp4 --max-frames 300
```

## Run MOT17

```bash
python src/track_people.py --source data/sample_videos/MOT17-02-DPM_300frames.mp4 --display --output-name mot17_demo --max-frames 300
```

## Generate charts

```bash
python scripts/summarize_tracking_log.py --csv outputs/logs/mot17_demo_tracking_log.csv --output-dir outputs/logs
```
