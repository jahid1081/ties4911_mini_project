from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Any, Callable, Iterable

import cv2
import numpy as np
from ultralytics import YOLO

from .utils import TrackState, box_center, color_for_id, ensure_dir, open_video_source, timestamp_for_filename


StatusCallback = Callable[[dict], None]


@dataclass
class TrackingConfig:
    model: str = "yolov8n.pt"
    tracker: str = "botsort.yaml"
    conf: float = 0.50
    iou: float = 0.50
    imgsz: int = 640
    min_box_height_ratio: float = 0.035
    min_box_area_ratio: float = 0.00025
    min_box_aspect: float = 0.12
    max_box_aspect: float = 1.45
    min_confirmed_frames: int = 3
    hide_trails: bool = False


def box_geometry(box: Iterable[float], frame_shape: tuple[int, int, int]) -> dict[str, float]:
    x1, y1, x2, y2 = [float(v) for v in box]
    frame_h, frame_w = frame_shape[:2]
    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)
    area = width * height
    frame_area = max(1.0, float(frame_w * frame_h))

    return {
        "width": width,
        "height": height,
        "area": area,
        "height_ratio": height / max(1.0, float(frame_h)),
        "area_ratio": area / frame_area,
        "aspect": width / max(1.0, height),
    }


def passes_person_box_filter(
    box: Iterable[float],
    frame_shape: tuple[int, int, int],
    config: TrackingConfig,
) -> tuple[bool, str, dict[str, float]]:
    geometry = box_geometry(box, frame_shape)

    if config.min_box_height_ratio > 0 and geometry["height_ratio"] < config.min_box_height_ratio:
        return False, "too_short", geometry

    if config.min_box_area_ratio > 0 and geometry["area_ratio"] < config.min_box_area_ratio:
        return False, "too_small", geometry

    if config.min_box_aspect > 0 and geometry["aspect"] < config.min_box_aspect:
        return False, "too_narrow", geometry

    if config.max_box_aspect > 0 and geometry["aspect"] > config.max_box_aspect:
        return False, "too_wide", geometry

    return True, "accepted", geometry


def extract_tracks(result: Any) -> list[dict]:
    tracks: list[dict] = []
    boxes = getattr(result, "boxes", None)

    if boxes is None or len(boxes) == 0:
        return tracks

    xyxy = boxes.xyxy.cpu().numpy()
    confs = boxes.conf.cpu().numpy() if boxes.conf is not None else np.zeros(len(xyxy))
    ids = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else None

    for index, box in enumerate(xyxy):
        track_id = int(ids[index]) if ids is not None else index + 1
        tracks.append(
            {
                "track_id": track_id,
                "box": box,
                "confidence": float(confs[index]),
            }
        )

    return tracks


def draw_annotated_frame(
    frame: np.ndarray,
    tracks: list[dict],
    frame_index: int,
    fps: float,
    config: TrackingConfig,
    raw_track_count: int,
    rejected_count: int,
    segment_index: int | None = None,
) -> np.ndarray:
    annotated = frame.copy()
    height, width = annotated.shape[:2]

    for track in tracks:
        track_id = int(track["track_id"])
        x1, y1, x2, y2 = [int(v) for v in track["box"]]
        color = color_for_id(track_id)

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        center = box_center(track["box"])
        cv2.circle(annotated, center, 4, color, -1)

        if not config.hide_trails:
            trail = track.get("trail", [])
            for i in range(1, len(trail)):
                cv2.line(annotated, trail[i - 1], trail[i], color, 2)

        label = (
            f"ID {track_id} | {track.get('direction', 'unknown')} | "
            f"{track.get('visible_frames', 0)}f | conf {track.get('confidence', 0.0):.2f}"
        )

        cv2.putText(
            annotated,
            label,
            (x1, max(24, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA,
        )

    segment_text = f" | Segment {segment_index}" if segment_index is not None else ""
    header = (
        f"Frame {frame_index}{segment_text} | FPS {fps:.1f} | "
        f"People {len(tracks)} | Raw {raw_track_count} | Rejected {rejected_count}"
    )
    cv2.rectangle(annotated, (0, 0), (width, 34), (0, 0, 0), -1)
    cv2.putText(
        annotated,
        header,
        (10, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return annotated




def preview_size_for_frame(
    frame_shape: tuple[int, int, int],
    max_width: int = 1280,
    max_height: int = 720,
) -> tuple[int, int]:
    """Return a preview size that keeps the video aspect ratio.

    The preview uses the real frame size when it fits inside the maximum preview
    bounds. Larger videos are scaled down so the OpenCV window stays usable on a
    laptop screen.
    """
    height, width = frame_shape[:2]

    if width <= 0 or height <= 0:
        return max_width, max_height

    scale = min(max_width / width, max_height / height, 1.0)
    preview_width = max(1, int(width * scale))
    preview_height = max(1, int(height * scale))

    return preview_width, preview_height


def configure_preview_window(
    window_name: str,
    frame_shape: tuple[int, int, int],
    max_width: int = 1280,
    max_height: int = 720,
) -> tuple[int, int]:
    """Create a resizable OpenCV window and size it to the video aspect ratio."""
    preview_width, preview_height = preview_size_for_frame(
        frame_shape=frame_shape,
        max_width=max_width,
        max_height=max_height,
    )

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, preview_width, preview_height)

    return preview_width, preview_height


def process_frame(
    model: YOLO,
    frame,
    frame_index: int,
    track_states: dict[int, TrackState],
    unique_ids: set[int],
    raw_unique_ids: set[int],
    direction_counts: dict[str, int],
    rejection_counts: dict[str, int],
    config: TrackingConfig,
) -> tuple[list[dict], int, int]:
    results = model.track(
        frame,
        persist=True,
        tracker=config.tracker,
        classes=[0],
        conf=config.conf,
        iou=config.iou,
        imgsz=config.imgsz,
        verbose=False,
    )

    raw_tracks = extract_tracks(results[0]) if results else []
    enriched_tracks: list[dict] = []
    rejected_this_frame = 0

    for track in raw_tracks:
        track_id = int(track["track_id"])
        raw_unique_ids.add(track_id)
        center = box_center(track["box"])

        state = track_states.setdefault(track_id, TrackState(track_id=track_id))
        direction = state.update(center, frame_index)

        accepted_shape, reason, geometry = passes_person_box_filter(
            box=track["box"],
            frame_shape=frame.shape,
            config=config,
        )

        if not accepted_shape:
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
            rejected_this_frame += 1
            continue

        if state.visible_frames < max(1, config.min_confirmed_frames):
            rejection_counts["not_confirmed"] = rejection_counts.get("not_confirmed", 0) + 1
            rejected_this_frame += 1
            continue

        direction_counts[direction] = direction_counts.get(direction, 0) + 1

        track["direction"] = direction
        track["visible_frames"] = state.visible_frames
        track["trail"] = list(state.centers)
        track["geometry"] = geometry
        enriched_tracks.append(track)
        unique_ids.add(track_id)

    return enriched_tracks, len(raw_tracks), rejected_this_frame


def _write_track_rows(writer_csv, tracks: list[dict], frame_index: int, time_s: float) -> None:
    for track in tracks:
        x1, y1, x2, y2 = [int(v) for v in track["box"]]
        cx, cy = box_center(track["box"])
        geometry = track["geometry"]
        writer_csv.writerow(
            {
                "frame": frame_index,
                "time_s": f"{time_s:.3f}",
                "track_id": track["track_id"],
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "center_x": cx,
                "center_y": cy,
                "confidence": f"{track['confidence']:.4f}",
                "direction": track.get("direction", "unknown"),
                "visible_frames": track.get("visible_frames", 0),
                "box_height_ratio": f"{geometry['height_ratio']:.6f}",
                "box_area_ratio": f"{geometry['area_ratio']:.8f}",
                "box_aspect": f"{geometry['aspect']:.4f}",
            }
        )


TRACKING_CSV_FIELDS = [
    "frame",
    "time_s",
    "track_id",
    "x1",
    "y1",
    "x2",
    "y2",
    "center_x",
    "center_y",
    "confidence",
    "direction",
    "visible_frames",
    "box_height_ratio",
    "box_area_ratio",
    "box_aspect",
]


def run_video_file(
    source: str,
    output_name: str,
    output_dir: str = "outputs",
    config: TrackingConfig | None = None,
    display: bool = False,
    max_frames: int = 0,
    status_callback: StatusCallback | None = None,
) -> dict:
    config = config or TrackingConfig()

    output_dir_path = Path(output_dir)
    video_dir = output_dir_path / "videos"
    log_dir = output_dir_path / "logs"
    ensure_dir(video_dir)
    ensure_dir(log_dir)

    csv_path = log_dir / f"{output_name}_tracking_log.csv"
    summary_path = log_dir / f"{output_name}_summary.json"
    video_path = video_dir / f"{output_name}_annotated.mp4"

    cap, source_fps, source_kind = open_video_source(source)
    model = YOLO(config.model)

    writer = None
    track_states: dict[int, TrackState] = {}
    unique_ids: set[int] = set()
    raw_unique_ids: set[int] = set()

    direction_counts: dict[str, int] = {"stationary": 0, "left": 0, "right": 0, "up": 0, "down": 0, "unknown": 0}
    rejection_counts: dict[str, int] = {"too_short": 0, "too_small": 0, "too_narrow": 0, "too_wide": 0, "not_confirmed": 0}

    frame_index = 0
    raw_observations = 0
    accepted_observations = 0
    start_time = time.perf_counter()
    preview_window_name = "VisionTrack file demo"
    preview_window_configured = False

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer_csv = csv.DictWriter(csv_file, fieldnames=TRACKING_CSV_FIELDS)
        writer_csv.writeheader()

        while True:
            if max_frames and frame_index >= max_frames:
                break

            ok, frame = cap.read()
            if not ok or frame is None:
                break

            frame_index += 1

            tracks, raw_count, rejected_count = process_frame(
                model=model,
                frame=frame,
                frame_index=frame_index,
                track_states=track_states,
                unique_ids=unique_ids,
                raw_unique_ids=raw_unique_ids,
                direction_counts=direction_counts,
                rejection_counts=rejection_counts,
                config=config,
            )

            raw_observations += raw_count
            accepted_observations += len(tracks)

            elapsed = time.perf_counter() - start_time
            current_fps = frame_index / elapsed if elapsed > 0 else 0.0

            annotated = draw_annotated_frame(
                frame=frame,
                tracks=tracks,
                frame_index=frame_index,
                fps=current_fps,
                config=config,
                raw_track_count=raw_count,
                rejected_count=rejected_count,
            )

            if writer is None:
                h, w = annotated.shape[:2]
                writer = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"mp4v"), source_fps, (w, h))

            writer.write(annotated)
            time_s = frame_index / source_fps if source_fps > 0 else 0.0
            _write_track_rows(writer_csv, tracks, frame_index, time_s)

            if status_callback and frame_index % 10 == 0:
                status_callback(
                    {
                        "mode": "file",
                        "frame": frame_index,
                        "people": len(tracks),
                        "fps": current_fps,
                        "output_video": str(video_path),
                    }
                )

            if display:
                if not preview_window_configured:
                    configure_preview_window(preview_window_name, annotated.shape)
                    preview_window_configured = True

                cv2.imshow(preview_window_name, annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                # Stop cleanly if the user closes the preview window.
                if cv2.getWindowProperty(preview_window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break

    cap.release()
    if writer is not None:
        writer.release()
    if display:
        cv2.destroyAllWindows()

    elapsed = time.perf_counter() - start_time
    summary = {
        "source": source,
        "source_kind": source_kind,
        "model": config.model,
        "tracker": config.tracker,
        "conf": config.conf,
        "frames_processed": frame_index,
        "raw_unique_track_count": len(raw_unique_ids),
        "accepted_unique_track_count": len(unique_ids),
        "accepted_unique_track_ids": sorted(unique_ids),
        "raw_observations": raw_observations,
        "accepted_observations": accepted_observations,
        "average_fps": frame_index / elapsed if elapsed > 0 else 0.0,
        "direction_counts": direction_counts,
        "rejection_counts": rejection_counts,
        "csv_log": str(csv_path),
        "annotated_video": str(video_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


class WebcamSegmentWriter:
    def __init__(self, session_dir: Path, source_fps: float, frame_shape: tuple[int, int, int]):
        self.session_dir = session_dir
        self.source_fps = source_fps
        self.frame_shape = frame_shape
        self.segment_index = 0
        self.segment_start: datetime | None = None
        self.video_writer = None
        self.csv_file = None
        self.csv_writer = None
        self.current_video_tmp: Path | None = None
        self.current_csv_tmp: Path | None = None
        self.saved_segments: list[dict] = []

    def start_segment(self) -> None:
        self.segment_index += 1
        self.segment_start = datetime.now()
        start_stamp = timestamp_for_filename(self.segment_start)

        self.current_video_tmp = self.session_dir / f"segment_{self.segment_index:03d}_{start_stamp}_recording.mp4"
        self.current_csv_tmp = self.session_dir / f"segment_{self.segment_index:03d}_{start_stamp}_tracking_log_recording.csv"

        height, width = self.frame_shape[:2]
        self.video_writer = cv2.VideoWriter(
            str(self.current_video_tmp),
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.source_fps,
            (width, height),
        )

        self.csv_file = open(self.current_csv_tmp, "w", newline="", encoding="utf-8")
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=TRACKING_CSV_FIELDS)
        self.csv_writer.writeheader()

    def write(self, annotated_frame, tracks: list[dict], global_frame: int, time_s: float) -> None:
        if self.video_writer is None or self.csv_writer is None:
            self.start_segment()

        self.video_writer.write(annotated_frame)
        _write_track_rows(self.csv_writer, tracks, global_frame, time_s)

    def close_segment(self) -> dict | None:
        if self.video_writer is None:
            return None

        end_dt = datetime.now()
        end_stamp = timestamp_for_filename(end_dt)
        start_stamp = timestamp_for_filename(self.segment_start) if self.segment_start else "unknown_start"

        self.video_writer.release()
        self.video_writer = None

        if self.csv_file is not None:
            self.csv_file.close()
            self.csv_file = None

        final_video = self.session_dir / f"webcam_{start_stamp}_to_{end_stamp}_annotated.mp4"
        final_csv = self.session_dir / f"webcam_{start_stamp}_to_{end_stamp}_tracking_log.csv"

        if self.current_video_tmp and self.current_video_tmp.exists():
            self.current_video_tmp.rename(final_video)
        if self.current_csv_tmp and self.current_csv_tmp.exists():
            self.current_csv_tmp.rename(final_csv)

        info = {
            "segment_index": self.segment_index,
            "start": start_stamp,
            "end": end_stamp,
            "video": str(final_video),
            "csv": str(final_csv),
        }
        self.saved_segments.append(info)
        return info

    def close(self) -> list[dict]:
        self.close_segment()
        return self.saved_segments


def run_webcam_continuous(
    webcam_index: int = 0,
    output_root: str = "outputs/webcam_sessions",
    segment_minutes: float = 10.0,
    config: TrackingConfig | None = None,
    stop_event: Event | None = None,
    status_callback: StatusCallback | None = None,
) -> dict:
    config = config or TrackingConfig()
    stop_event = stop_event or Event()

    session_start = datetime.now()
    session_dir = Path(output_root) / f"session_{timestamp_for_filename(session_start)}"
    ensure_dir(session_dir)

    cap, source_fps, _ = open_video_source(str(webcam_index))
    model = YOLO(config.model)

    track_states: dict[int, TrackState] = {}
    unique_ids: set[int] = set()
    raw_unique_ids: set[int] = set()
    direction_counts: dict[str, int] = {"stationary": 0, "left": 0, "right": 0, "up": 0, "down": 0, "unknown": 0}
    rejection_counts: dict[str, int] = {"too_short": 0, "too_small": 0, "too_narrow": 0, "too_wide": 0, "not_confirmed": 0}

    frame_index = 0
    raw_observations = 0
    accepted_observations = 0
    start_time = time.perf_counter()
    segment_start_time = time.perf_counter()
    segment_seconds = max(1.0, segment_minutes * 60.0)
    segment_writer: WebcamSegmentWriter | None = None
    preview_window_name = "VisionTrack webcam stream - close window or press q to stop"
    preview_window_configured = False

    try:
        while not stop_event.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                break

            frame_index += 1
            if segment_writer is None:
                segment_writer = WebcamSegmentWriter(session_dir, source_fps, frame.shape)
                segment_writer.start_segment()

            tracks, raw_count, rejected_count = process_frame(
                model=model,
                frame=frame,
                frame_index=frame_index,
                track_states=track_states,
                unique_ids=unique_ids,
                raw_unique_ids=raw_unique_ids,
                direction_counts=direction_counts,
                rejection_counts=rejection_counts,
                config=config,
            )

            raw_observations += raw_count
            accepted_observations += len(tracks)

            elapsed = time.perf_counter() - start_time
            current_fps = frame_index / elapsed if elapsed > 0 else 0.0

            annotated = draw_annotated_frame(
                frame=frame,
                tracks=tracks,
                frame_index=frame_index,
                fps=current_fps,
                config=config,
                raw_track_count=raw_count,
                rejected_count=rejected_count,
                segment_index=segment_writer.segment_index if segment_writer else None,
            )

            time_s = frame_index / source_fps if source_fps > 0 else 0.0
            segment_writer.write(annotated, tracks, frame_index, time_s)

            if not preview_window_configured:
                configure_preview_window(preview_window_name, annotated.shape)
                preview_window_configured = True

            cv2.imshow(preview_window_name, annotated)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                stop_event.set()

            # Stop if user manually closes the OpenCV stream window.
            if cv2.getWindowProperty(preview_window_name, cv2.WND_PROP_VISIBLE) < 1:
                stop_event.set()

            if time.perf_counter() - segment_start_time >= segment_seconds:
                segment_info = segment_writer.close_segment()
                segment_writer.start_segment()
                segment_start_time = time.perf_counter()
                if status_callback:
                    status_callback({"mode": "webcam", "event": "segment_saved", "segment": segment_info})

            if status_callback and frame_index % 10 == 0:
                status_callback(
                    {
                        "mode": "webcam",
                        "frame": frame_index,
                        "people": len(tracks),
                        "fps": current_fps,
                        "session_dir": str(session_dir),
                        "segments": len(segment_writer.saved_segments) if segment_writer else 0,
                    }
                )
    finally:
        cap.release()
        cv2.destroyAllWindows()
        saved_segments = segment_writer.close() if segment_writer is not None else []

    elapsed = time.perf_counter() - start_time
    summary = {
        "mode": "webcam_continuous",
        "webcam_index": webcam_index,
        "session_dir": str(session_dir),
        "segment_minutes": segment_minutes,
        "model": config.model,
        "tracker": config.tracker,
        "conf": config.conf,
        "frames_processed": frame_index,
        "raw_unique_track_count": len(raw_unique_ids),
        "accepted_unique_track_count": len(unique_ids),
        "accepted_unique_track_ids": sorted(unique_ids),
        "raw_observations": raw_observations,
        "accepted_observations": accepted_observations,
        "average_fps": frame_index / elapsed if elapsed > 0 else 0.0,
        "direction_counts": direction_counts,
        "rejection_counts": rejection_counts,
        "saved_segments": saved_segments,
    }
    (session_dir / "session_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
