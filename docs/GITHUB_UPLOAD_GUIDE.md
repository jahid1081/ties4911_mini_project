# Uploading this project to GitHub

## Option A - Beginner ZIP method

1. Create a new repository on GitHub.
2. Download this project as a folder on your computer.
3. Open the new GitHub repository in your browser.
4. Click **Add file**.
5. Click **Upload files**.
6. Drag the project files into the browser.
7. Do not upload large output videos or datasets.
8. Click **Commit changes**.

## Option B - Git command line

```bash
git init
git add .
git commit -m "Initial VisionTrack project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/visiontrack-modern-human-tracking.git
git push -u origin main
```

## Do not upload

```text
data/MOT17/
outputs/
runs/
*.pt
large videos
```

These are ignored by `.gitignore`.

## Recommended repository description

```text
Laptop-friendly multi-person human detection and tracking using YOLO, OpenCV, webcam streaming, and MOT17 video demos.
```
