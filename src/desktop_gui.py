from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from threading import Event

from visiontrack.tracking_engine import TrackingConfig, run_video_file, run_webcam_continuous


class VisionTrackApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("VisionTrack - Modern Multi-Person Human Tracking")
        self.geometry("920x680")
        self.minsize(860, 620)

        self.stop_event: Event | None = None
        self.worker: threading.Thread | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.home_tab = ttk.Frame(notebook)
        self.webcam_tab = ttk.Frame(notebook)
        self.file_tab = ttk.Frame(notebook)
        self.help_tab = ttk.Frame(notebook)

        notebook.add(self.home_tab, text="Home")
        notebook.add(self.webcam_tab, text="Webcam Stream")
        notebook.add(self.file_tab, text="MOT17 / Video File")
        notebook.add(self.help_tab, text="Help")

        self._build_home_tab()
        self._build_webcam_tab()
        self._build_file_tab()
        self._build_help_tab()

    def _build_home_tab(self) -> None:
        title = ttk.Label(
            self.home_tab,
            text="VisionTrack",
            font=("Segoe UI", 24, "bold"),
        )
        title.pack(anchor="w", padx=18, pady=(18, 8))

        subtitle = ttk.Label(
            self.home_tab,
            text="A beginner-friendly demo for YOLO-based multi-person human detection and tracking.",
            font=("Segoe UI", 12),
        )
        subtitle.pack(anchor="w", padx=18, pady=(0, 18))

        text = (
            "What this app does:\n"
            "1. Tracks people from a live webcam stream.\n"
            "2. Saves webcam results into timestamped video/log segments.\n"
            "3. Runs tracking on a selected MOT17/video file.\n"
            "4. Saves annotated videos, CSV logs, and JSON summaries.\n\n"
            "Important:\n"
            "- This app tracks people as people. It does not need to detect walking sticks separately.\n"
            "- Use real continuous video when claiming tracking results.\n"
            "- MOT17 is used as the public continuous-video tracking dataset."
        )

        box = tk.Text(self.home_tab, wrap="word", height=16, font=("Segoe UI", 11))
        box.insert("1.0", text)
        box.configure(state="disabled")
        box.pack(fill="both", expand=True, padx=18, pady=8)

    def _common_settings_frame(self, parent: ttk.Frame) -> dict[str, tk.StringVar]:
        frame = ttk.LabelFrame(parent, text="Tracking settings")
        frame.pack(fill="x", padx=18, pady=10)

        values = {
            "model": tk.StringVar(value="yolov8n.pt"),
            "conf": tk.StringVar(value="0.50"),
            "tracker": tk.StringVar(value="botsort.yaml"),
            "confirmed": tk.StringVar(value="3"),
        }

        ttk.Label(frame, text="YOLO model").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=values["model"], width=24).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frame, text="Confidence").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=values["conf"], width=10).grid(row=0, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(frame, text="Tracker").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Combobox(frame, textvariable=values["tracker"], values=["botsort.yaml", "bytetrack.yaml"], width=21).grid(
            row=1, column=1, sticky="w", padx=8, pady=6
        )

        ttk.Label(frame, text="Confirmed frames").grid(row=1, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=values["confirmed"], width=10).grid(row=1, column=3, sticky="w", padx=8, pady=6)

        return values

    def _config_from_values(self, values: dict[str, tk.StringVar]) -> TrackingConfig:
        try:
            conf = float(values["conf"].get())
            confirmed = int(values["confirmed"].get())
        except ValueError as exc:
            raise ValueError("Confidence must be a number and confirmed frames must be an integer.") from exc

        return TrackingConfig(
            model=values["model"].get().strip() or "yolov8n.pt",
            tracker=values["tracker"].get().strip() or "botsort.yaml",
            conf=conf,
            min_confirmed_frames=confirmed,
        )

    def _build_webcam_tab(self) -> None:
        header = ttk.Label(self.webcam_tab, text="Continuous Webcam Stream", font=("Segoe UI", 18, "bold"))
        header.pack(anchor="w", padx=18, pady=(18, 8))

        self.webcam_settings = self._common_settings_frame(self.webcam_tab)

        frame = ttk.LabelFrame(self.webcam_tab, text="Webcam stream")
        frame.pack(fill="x", padx=18, pady=10)

        self.webcam_index = tk.StringVar(value="0")
        self.segment_minutes = tk.StringVar(value="10")
        self.webcam_output_root = tk.StringVar(value="outputs/webcam_sessions")

        ttk.Label(frame, text="Webcam index").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=self.webcam_index, width=10).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frame, text="Segment length in minutes").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=self.segment_minutes, width=10).grid(row=0, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(frame, text="Output folder").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=self.webcam_output_root, width=55).grid(row=1, column=1, columnspan=3, sticky="w", padx=8, pady=6)
        ttk.Button(frame, text="Choose", command=self._choose_webcam_output).grid(row=1, column=4, padx=8, pady=6)

        buttons = ttk.Frame(self.webcam_tab)
        buttons.pack(fill="x", padx=18, pady=8)

        ttk.Button(buttons, text="Start Webcam Stream", command=self._start_webcam).pack(side="left", padx=4)
        ttk.Button(buttons, text="Stop Webcam Stream", command=self._stop_webcam).pack(side="left", padx=4)

        self.webcam_status = tk.Text(self.webcam_tab, height=14, wrap="word", font=("Consolas", 10))
        self.webcam_status.pack(fill="both", expand=True, padx=18, pady=8)
        self._append_webcam_status("Ready. Use a short segment like 1 minute for testing, 10 minutes for the real demo.")

    def _build_file_tab(self) -> None:
        header = ttk.Label(self.file_tab, text="MOT17 / Video File Demo", font=("Segoe UI", 18, "bold"))
        header.pack(anchor="w", padx=18, pady=(18, 8))

        self.file_settings = self._common_settings_frame(self.file_tab)

        frame = ttk.LabelFrame(self.file_tab, text="Input and output")
        frame.pack(fill="x", padx=18, pady=10)

        self.selected_video = tk.StringVar(value="")
        self.file_output_name = tk.StringVar(value="gui_file_demo")
        self.file_output_dir = tk.StringVar(value="outputs")
        self.max_frames = tk.StringVar(value="300")

        ttk.Label(frame, text="Video file").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=self.selected_video, width=62).grid(row=0, column=1, columnspan=3, sticky="w", padx=8, pady=6)
        ttk.Button(frame, text="Choose video", command=self._choose_video).grid(row=0, column=4, padx=8, pady=6)

        ttk.Label(frame, text="Output name").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=self.file_output_name, width=24).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frame, text="Max frames").grid(row=1, column=2, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=self.max_frames, width=10).grid(row=1, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(frame, text="Output folder").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frame, textvariable=self.file_output_dir, width=62).grid(row=2, column=1, columnspan=3, sticky="w", padx=8, pady=6)
        ttk.Button(frame, text="Choose", command=self._choose_file_output).grid(row=2, column=4, padx=8, pady=6)

        buttons = ttk.Frame(self.file_tab)
        buttons.pack(fill="x", padx=18, pady=8)

        ttk.Button(buttons, text="Run File Demo", command=self._run_file_demo).pack(side="left", padx=4)

        self.file_status = tk.Text(self.file_tab, height=14, wrap="word", font=("Consolas", 10))
        self.file_status.pack(fill="both", expand=True, padx=18, pady=8)
        self._append_file_status("Ready. Choose an MP4 file such as data/sample_videos/MOT17-02-DPM_300frames.mp4.")

    def _build_help_tab(self) -> None:
        header = ttk.Label(self.help_tab, text="Beginner Help", font=("Segoe UI", 18, "bold"))
        header.pack(anchor="w", padx=18, pady=(18, 8))

        text = (
            "Quick start:\n"
            "1. Install Python 3.10, 3.11, or 3.12.\n"
            "2. Open a terminal in the project folder.\n"
            "3. Create and activate a virtual environment.\n"
            "4. Install requirements with pip install -r requirements.txt.\n"
            "5. Run python src/desktop_gui.py.\n\n"
            "Webcam stream:\n"
            "- Use webcam index 0 for the default webcam.\n"
            "- Use 1 minute segments for testing.\n"
            "- Use 10 minute segments for the full demo.\n"
            "- Close the live stream window or press q to stop.\n\n"
            "MOT17/file demo:\n"
            "- Convert a MOT17 sequence to MP4 first, or choose an existing MP4.\n"
            "- Run the file demo and check the outputs folder.\n\n"
            "Common problems:\n"
            "- If the webcam does not open, try another index such as 1.\n"
            "- If YOLO downloads a model on first run, that is normal.\n"
            "- If the app is slow, keep yolov8n.pt and confidence 0.50.\n"
        )

        box = tk.Text(self.help_tab, wrap="word", font=("Segoe UI", 11))
        box.insert("1.0", text)
        box.configure(state="disabled")
        box.pack(fill="both", expand=True, padx=18, pady=8)

    def _choose_webcam_output(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.webcam_output_root.set(folder)

    def _choose_file_output(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.file_output_dir.set(folder)

    def _choose_video(self) -> None:
        filename = filedialog.askopenfilename(
            title="Choose video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")],
        )
        if filename:
            self.selected_video.set(filename)

    def _append_webcam_status(self, message: str) -> None:
        self.webcam_status.insert("end", message + "\n")
        self.webcam_status.see("end")

    def _append_file_status(self, message: str) -> None:
        self.file_status.insert("end", message + "\n")
        self.file_status.see("end")

    def _start_webcam(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Already running", "The webcam stream is already running.")
            return

        try:
            webcam_index = int(self.webcam_index.get())
            segment_minutes = float(self.segment_minutes.get())
            config = self._config_from_values(self.webcam_settings)
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        self.stop_event = Event()

        def status_callback(info: dict) -> None:
            self.after(0, lambda: self._append_webcam_status(json.dumps(info)))

        def worker() -> None:
            try:
                summary = run_webcam_continuous(
                    webcam_index=webcam_index,
                    output_root=self.webcam_output_root.get(),
                    segment_minutes=segment_minutes,
                    config=config,
                    stop_event=self.stop_event,
                    status_callback=status_callback,
                )
                self.after(0, lambda: self._append_webcam_status("Finished:\n" + json.dumps(summary, indent=2)))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Webcam error", str(exc)))
                self.after(0, lambda: self._append_webcam_status(f"Error: {exc}"))

        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()
        self._append_webcam_status("Started webcam stream. Close the stream window or press q to stop.")

    def _stop_webcam(self) -> None:
        if self.stop_event:
            self.stop_event.set()
            self._append_webcam_status("Stop requested. The current segment will be finalized.")

    def _run_file_demo(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Busy", "Another job is already running.")
            return

        source = self.selected_video.get().strip()
        if not source:
            messagebox.showerror("Missing input", "Please choose a video file first.")
            return

        try:
            max_frames = int(self.max_frames.get())
            config = self._config_from_values(self.file_settings)
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        def status_callback(info: dict) -> None:
            self.after(0, lambda: self._append_file_status(json.dumps(info)))

        def worker() -> None:
            try:
                summary = run_video_file(
                    source=source,
                    output_name=self.file_output_name.get().strip() or "gui_file_demo",
                    output_dir=self.file_output_dir.get().strip() or "outputs",
                    config=config,
                    display=True,
                    max_frames=max_frames,
                    status_callback=status_callback,
                )
                self.after(0, lambda: self._append_file_status("Finished:\n" + json.dumps(summary, indent=2)))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("File demo error", str(exc)))
                self.after(0, lambda: self._append_file_status(f"Error: {exc}"))

        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()
        self._append_file_status("Started file demo. The tracking preview window will open.")


if __name__ == "__main__":
    app = VisionTrackApp()
    app.mainloop()
