#!/usr/bin/env python3
"""
prepare_dataset_files.py
------------------------

1. Download a public mosquito-cropped dataset from Kaggle (≈ 400 JPGs).
2. Clear / recreate the ./frames directory.
3. Extract negative patches from cam_bg.mp4:
      - one frame every 0.5 s
      - five 96×96 random crops per frame
4. Final layout:

dataset/
├── mosquito/        (positives, 96×96)
└── background/      (negatives, 96×96)
"""

import os, shutil, subprocess, random, zipfile, sys
from pathlib import Path
import cv2
import numpy as np
from tqdm import tqdm

# ---------- CONFIG ----------------------------------------------------------
KAGGLE_DATASET = "kashnitsky/mosquito-detection"   # public cropped set
VIDEO_FILE     = Path("cam_bg.mp4")                # 2-minute clip @30 fps
FRAME_DIR      = Path("frames")
DATA_ROOT      = Path("dataset")
POS_DIR        = DATA_ROOT / "mosquito"
NEG_DIR        = DATA_ROOT / "background"
CROPS_PER_FRAME = 5
PATCH_SIZE      = 96
FPS_SAMPLING    = 2                                # frames/sec (= 0.5 s step)
# ---------------------------------------------------------------------------

def run(cmd: list[str], check: bool = True):
    subprocess.run(cmd, shell=False, check=check)

def ensure_dirs():
    for p in (POS_DIR, NEG_DIR):
        p.mkdir(parents=True, exist_ok=True)

def download_kaggle():
    """Grab cropped mosquito positives if POS_DIR is still empty."""
    if any(POS_DIR.iterdir()):
        print("✓ Positive crops already present.")
        return
    print("⬇  Downloading mosquito crops from Kaggle …")
    # kaggle API needs $HOME/.kaggle/kaggle.json
    run(["kaggle", "datasets", "download", "-d", KAGGLE_DATASET])

    zfile = next(Path(".").glob(f"{KAGGLE_DATASET.split('/')[-1]}*.zip"))
    with zipfile.ZipFile(zfile) as z:
        for name in z.namelist():
            if name.lower().endswith((".jpg", ".png")):
                with z.open(name) as src:
                    tgt = POS_DIR / Path(name).name
                    tgt.write_bytes(src.read())
    zfile.unlink()
    print("✓ Crops downloaded and extracted.")

def clear_frame_dir():
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir()
    print("✓ frames/ ready.")

def extract_frames():
    """ffmpeg pulls N frames/sec into ./frames/frame_%04d.jpg"""
    if not VIDEO_FILE.exists():
        sys.exit(f"ERROR: {VIDEO_FILE} not found.")
    cmd = [
        "ffmpeg", "-y", "-i", str(VIDEO_FILE),
        "-vf", f"fps={FPS_SAMPLING}",
        str(FRAME_DIR / "frame_%04d.jpg")
    ]
    run(cmd)
    total = len(list(FRAME_DIR.glob("*.jpg")))
    print(f"✓ Extracted {total} still frames.")

def random_crops():
    random.seed(0)
    for jpg in tqdm(list(FRAME_DIR.glob("*.jpg")), desc="Crops"):
        img = cv2.imread(str(jpg))
        h, w = img.shape[:2]
        for i in range(CROPS_PER_FRAME):
            x = random.randint(0, w - PATCH_SIZE)
            y = random.randint(0, h - PATCH_SIZE)
            crop = img[y : y + PATCH_SIZE, x : x + PATCH_SIZE]
            out = NEG_DIR / f"{jpg.stem}_{i}.jpg"
            cv2.imwrite(str(out), crop)

def main():
    ensure_dirs()
    download_kaggle()
    clear_frame_dir()
    extract_frames()
    random_crops()
    print("\nDataset ready:", DATA_ROOT.resolve())

if __name__ == "__main__":
    main()
