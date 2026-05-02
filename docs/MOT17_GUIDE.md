# MOT17 guide

MOT17 is used as the main public continuous-video dataset for this project.

## Why MOT17?

MOT17 contains real video sequences for multi-person pedestrian tracking. This makes it suitable for testing whether the system can track multiple people over time.

## Download MOT17

Download the MOT17 train set from the official MOTChallenge website.

Place it under:

```text
data/MOT17/
```

Expected folder example:

```text
data/MOT17/train/MOT17-02-DPM/img1/
data/MOT17/train/MOT17-02-DPM/seqinfo.ini
```

## Convert MOT17 sequence to MP4

```bash
python scripts/mot17_sequence_to_video.py --sequence-dir data/MOT17/train/MOT17-02-DPM --output data/sample_videos/MOT17-02-DPM_300frames.mp4 --max-frames 300
```

## Run tracking

```bash
python src/track_people.py --source data/sample_videos/MOT17-02-DPM_300frames.mp4 --display --output-name mot17_demo --max-frames 300
```

## Generate charts

```bash
python scripts/summarize_tracking_log.py --csv outputs/logs/mot17_demo_tracking_log.csv --output-dir outputs/logs
```
