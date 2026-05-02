# Project scope

## In scope

- Human detection and tracking.
- Multi-person tracking in continuous video.
- Webcam stream demo.
- MOT17 video demo.
- Timestamped segmented recording for webcam mode.
- Logs, summaries, and charts.

## Out of scope

- Perfect detection.
- Face recognition.
- Person identity recognition.
- Walking-stick object classification.
- Tracking evidence from unrelated filtered images.
- Physical PTZ camera control.

## Walking sticks and two sticks

The tracker is designed to track people as people. It does not require detecting sticks separately.

The honest claim is:

```text
If a person using one stick or two sticks is visible as a person, the person detector and tracker should process them as a person.
```

A formal claim about tracking stick users requires real continuous video containing those cases.
