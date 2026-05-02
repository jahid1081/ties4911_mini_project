from __future__ import annotations

import argparse
from pathlib import Path

import cv2


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a slower copy of a video for visual inspection.")
    parser.add_argument("--input", required=True, help="Input video path.")
    parser.add_argument("--output", required=True, help="Output video path.")
    parser.add_argument("--fps", type=float, default=2.0, help="Output FPS.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open input video: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create output video: {output_path}")

    frames = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(frame)
        frames += 1

    cap.release()
    writer.release()

    print({"input": str(input_path), "output": str(output_path), "frames": frames, "fps": args.fps})


if __name__ == "__main__":
    main()
