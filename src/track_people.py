from __future__ import annotations

import argparse
import json

from visiontrack.tracking_engine import TrackingConfig, run_video_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VisionTrack on a webcam or video file.")
    parser.add_argument("--source", required=True, help="Webcam index such as 0, or path to a video file.")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--tracker", default="botsort.yaml", choices=["botsort.yaml", "bytetrack.yaml"])
    parser.add_argument("--conf", type=float, default=0.50)
    parser.add_argument("--iou", type=float, default=0.50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--min-confirmed-frames", type=int, default=3)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--output-name", default="run")
    parser.add_argument("--display", action="store_true")
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--hide-trails", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = TrackingConfig(
        model=args.model,
        tracker=args.tracker,
        conf=args.conf,
        iou=args.iou,
        imgsz=args.imgsz,
        min_confirmed_frames=args.min_confirmed_frames,
        hide_trails=args.hide_trails,
    )

    summary = run_video_file(
        source=args.source,
        output_name=args.output_name,
        output_dir=args.output_dir,
        config=config,
        display=args.display,
        max_frames=args.max_frames,
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
