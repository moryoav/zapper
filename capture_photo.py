#!/usr/bin/env python3
"""
Capture a single JPEG image from the first detected USB webcam.

Usage:
    python capture_photo.py                  # Saves <timestamp>.jpg in current dir
    python capture_photo.py --out img.jpg    # Saves as img.jpg
"""

import cv2
import argparse
from datetime import datetime
from pathlib import Path
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Take a photo with a USB camera")
    parser.add_argument(
        "--device",
        type=int,
        default=0,
        help="Video device index (default 0). If you have multiple cameras, use 1, 2, …",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output filename. Default: <YYYYMMDD_HHMMSS>.jpg in current folder",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1280,
        help="Frame width in pixels (default 1280)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=720,
        help="Frame height in pixels (default 720)",
    )
    return parser.parse_args()

def main():
    args = parse_args()

    # 1. Open the video capture
    cap = cv2.VideoCapture(args.device, cv2.CAP_V4L2)  # V4L2 backend is reliable on Pi
    if not cap.isOpened():
        sys.exit(f"❌  Could not open /dev/video{args.device}")

    # 2. Optionally set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    # 3. Grab a frame
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        sys.exit("❌  Failed to capture image")

    # 4. Choose output filename
    outfile = (
        Path(args.out)
        if args.out
        else Path(f"{datetime.now():%Y%m%d_%H%M%S}.jpg")
    )

    # 5. Write JPEG
    if not cv2.imwrite(str(outfile), frame):
        sys.exit("❌  Failed to save image")

    print(f"✅  Saved photo to {outfile.resolve()}")

if __name__ == "__main__":
    main()

