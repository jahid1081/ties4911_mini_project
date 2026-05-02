from __future__ import annotations

import argparse
import configparser
from pathlib import Path

import cv2


def read_seqinfo(sequence_dir: Path) -> dict:
    seqinfo_path = sequence_dir / "seqinfo.ini"

    if not seqinfo_path.exists():
        raise FileNotFoundError(f"Missing seqinfo.ini: {seqinfo_path}")

    config = configparser.ConfigParser()
    config.read(seqinfo_path)

    if "Sequence" not in config:
        raise ValueError(f"Invalid seqinfo.ini file: {seqinfo_path}")

    section = config["Sequence"]

    return {
        "name": section.get("name", sequence_dir.name),
        "im_dir": section.get("imDir", "img1"),
        "frame_rate": section.getint("frameRate", fallback=25),
        "im_ext": section.get("imExt", ".jpg"),
    }


def sequence_to_video(sequence_dir: Path, output_path: Path, max_frames: int | None = None) -> None:
    info = read_seqinfo(sequence_dir)
    image_dir = sequence_dir / info["im_dir"]

    if not image_dir.exists():
        raise FileNotFoundError(f"Missing image folder: {image_dir}")

    image_files = sorted(image_dir.glob(f"*{info['im_ext']}"))

    if not image_files:
        raise FileNotFoundError(f"No images found in: {image_dir}")

    if max_frames is not None:
        image_files = image_files[:max_frames]

    first = cv2.imread(str(image_files[0]))
    if first is None:
        raise ValueError(f"Could not read first image: {image_files[0]}")

    height, width = first.shape[:2]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        float(info["frame_rate"]),
        (width, height),
    )

    if not writer.isOpened():
        raise RuntimeError(f"Could not create output video: {output_path}")

    written = 0

    for image_path in image_files:
        frame = cv2.imread(str(image_path))
        if frame is None:
            print(f"Skipping unreadable image: {image_path}")
            continue

        if frame.shape[:2] != (height, width):
            frame = cv2.resize(frame, (width, height))

        writer.write(frame)
        written += 1

    writer.release()

    print(
        {
            "sequence": info["name"],
            "input_frames_selected": len(image_files),
            "written_frames": written,
            "fps": info["frame_rate"],
            "output_video": str(output_path),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a MOT17 image sequence to MP4.")
    parser.add_argument("--sequence-dir", required=True, help="Example: data/MOT17/train/MOT17-02-DPM")
    parser.add_argument("--output", required=True, help="Example: data/sample_videos/MOT17-02-DPM_300frames.mp4")
    parser.add_argument("--max-frames", type=int, default=None)
    args = parser.parse_args()

    sequence_to_video(
        sequence_dir=Path(args.sequence_dir),
        output_path=Path(args.output),
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    main()
