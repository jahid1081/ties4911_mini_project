# Preview window size fix

This patch updates the OpenCV preview windows used by the GUI and command-line demo.

## What changed

- The file-demo preview window is now created as a resizable OpenCV window.
- The preview window is resized based on the selected video's actual frame resolution.
- Large videos are scaled down to fit a laptop-friendly maximum of 1280 x 720 while preserving aspect ratio.
- Small videos are shown at their original size.
- Closing the file-demo preview window now stops the file demo cleanly.
- The same preview behavior is also applied to the webcam stream window.

## Updated file

```text
src/visiontrack/tracking_engine.py
```

## How to apply

Copy the updated file into your project, replacing the existing file at the same path.

Then run:

```powershell
python src/desktop_gui.py
```
