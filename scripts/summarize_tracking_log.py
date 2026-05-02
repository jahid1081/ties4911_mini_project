from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Create simple charts from a tracking CSV log.")
    parser.add_argument("--csv", required=True, help="Path to tracking CSV.")
    parser.add_argument("--output-dir", required=True, help="Directory where charts and summary JSON are saved.")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError(f"CSV file is empty: {csv_path}")

    base_name = csv_path.stem

    people_per_frame = df.groupby("frame")["track_id"].nunique()
    track_lengths = df.groupby("track_id")["frame"].nunique().sort_values(ascending=False)
    direction_counts = df["direction"].value_counts()

    plt.figure(figsize=(12, 4))
    people_per_frame.plot()
    plt.title("Tracked people per frame")
    plt.xlabel("Frame")
    plt.ylabel("Tracked people")
    plt.tight_layout()
    people_chart = output_dir / f"{base_name}_people_per_frame.png"
    plt.savefig(people_chart, dpi=150)
    plt.close()

    plt.figure(figsize=(12, 4))
    track_lengths.head(30).plot(kind="bar")
    plt.title("Track duration by ID")
    plt.xlabel("Track ID")
    plt.ylabel("Visible frames")
    plt.tight_layout()
    track_chart = output_dir / f"{base_name}_track_lengths.png"
    plt.savefig(track_chart, dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4))
    direction_counts.plot(kind="bar")
    plt.title("Movement direction observations")
    plt.xlabel("Direction")
    plt.ylabel("Observations")
    plt.tight_layout()
    direction_chart = output_dir / f"{base_name}_direction_counts.png"
    plt.savefig(direction_chart, dpi=150)
    plt.close()

    summary = {
        "csv": str(csv_path),
        "rows": int(len(df)),
        "frames": int(df["frame"].nunique()),
        "unique_track_count": int(df["track_id"].nunique()),
        "people_per_frame_min": int(people_per_frame.min()),
        "people_per_frame_max": int(people_per_frame.max()),
        "people_per_frame_mean": float(people_per_frame.mean()),
        "longest_tracks": {str(k): int(v) for k, v in track_lengths.head(10).items()},
        "direction_counts": {str(k): int(v) for k, v in direction_counts.items()},
        "charts": {
            "people_per_frame": str(people_chart),
            "track_lengths": str(track_chart),
            "direction_counts": str(direction_chart),
        },
    }

    summary_path = output_dir / f"{base_name}_analysis_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
