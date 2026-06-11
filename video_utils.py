"""
Video Frame Extraction Utility

Author: Mohammed Faris Sait

This module handles:
- Extracting frames from a given video at a fixed interval (default: 1 frame per second)
- Saving the extracted frames as JPEG images in a specified output directory
- Designed to work with OpenCV for video processing
"""



import cv2
import os

def extract_frames(video_path, output_dir, interval=1):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)

    count = 0
    saved_frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{count}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_frames.append(frame_path)
        count += 1
    cap.release()
    return saved_frames
