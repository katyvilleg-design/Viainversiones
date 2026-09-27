#!/usr/bin/env python3
"""Turn a still image into a silent MP4 held for a given duration.

This is the proven, flicker-free way to put a static card/lamina into a
video timeline. Do NOT hold a card by decoding+extending a live source clip
(via tpad/apad or concat) — if the source clip has ANY compression artifact
near its last frames (very common with phone/CapCut exports), that artifact
gets held/looped and reads as a visible flicker. Always render the card as
ONE still image for its FULL on-screen duration instead.

Usage:
    python make_still_card_clip.py card.png 6.0 -o card.mp4
"""
import argparse
import subprocess


def build(image_path: str, duration: float, out_path: str, fps: int = 24, crf: int = 12):
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", f"{duration:.3f}",
        "-af", f"afade=t=in:st=0:d=0.03,afade=t=out:st={max(0.0, duration - 0.03):.3f}:d=0.03",
        "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "192k",
        out_path,
    ], check=True, capture_output=True)
    print(f"{out_path}: {duration:.2f}s still card")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("duration", type=float)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--crf", type=int, default=12)
    args = ap.parse_args()
    build(args.image, args.duration, args.output, args.fps, args.crf)
