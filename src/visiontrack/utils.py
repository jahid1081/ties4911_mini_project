from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np


def safe_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def timestamp_for_filename(dt) -> str:
    return dt.strftime("%Y%m%d_%H%M%S")


def box_center(box: Iterable[float]) -> tuple[int, int]:
    x1, y1, x2, y2 = [float(v) for v in box]
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def color_for_id(track_id: int) -> tuple[int, int, int]:
    rng = np.random.default_rng(track_id)
    color = rng.integers(80, 255, size=3)
    return int(color[0]), int(color[1]), int(color[2])


@dataclass
class TrackState:
    track_id: int
    centers: deque[tuple[int, int]] = field(default_factory=lambda: deque(maxlen=40))
    first_frame: int = 0
    last_frame: int = 0
    visible_frames: int = 0

    def update(self, center: tuple[int, int], frame_index: int, movement_threshold: int = 6) -> str:
        if self.visible_frames == 0:
            self.first_frame = frame_index

        self.last_frame = frame_index
        self.visible_frames += 1

        if self.centers:
            previous = self.centers[-1]
            dx = center[0] - previous[0]
            dy = center[1] - previous[1]
        else:
            dx = 0
            dy = 0

        self.centers.append(center)

        if abs(dx) < movement_threshold and abs(dy) < movement_threshold:
            return "stationary"

        if abs(dx) >= abs(dy):
            return "right" if dx > 0 else "left"

        return "down" if dy > 0 else "up"


def open_video_source(source: str) -> tuple[cv2.VideoCapture, float, str]:
    webcam_index = safe_int(source)

    if webcam_index is not None:
        cap = cv2.VideoCapture(webcam_index)
        source_kind = "webcam"
    else:
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        cap = cv2.VideoCapture(str(source_path))
        source_kind = "video"

    if not cap.isOpened():
        raise RuntimeError(f"Could not open source: {source}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 1:
        fps = 30.0

    return cap, float(fps), source_kind
