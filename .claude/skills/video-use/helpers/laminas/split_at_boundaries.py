#!/usr/bin/env python3
"""Split a video at a list of boundary timestamps into separate clips, each
with a 30ms audio fade in/out at its new edges (Hard Rule 3: no pops at cuts).

Usage:
    python split_at_boundaries.py source.mp4 out_dir/ 0 17.083 20.083 23.083 ...

Writes out_dir/seg00.mp4, seg01.mp4, ... and prints each one's role guess
(you still have to confirm which are cards vs. talking-head by eye — see
the card-boundary-detection note in ../../../LAMINAS_LESSONS.md).
"""
import subprocess
import sys
from pathlib import Path


def main():
    src = sys.argv[1]
    out_dir = Path(sys.argv[2])
    bounds = [float(x) for x in sys.argv[3:]]
    out_dir.mkdir(parents=True, exist_ok=True)

    for i in range(len(bounds) - 1):
        start = bounds[i]
        end = bounds[i + 1]
        d = end - start
        fade_out_st = max(0.0, d - 0.03)
        out = out_dir / f"seg{i:02d}.mp4"
        cmd = [
            "ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", src, "-t", f"{d:.3f}",
            "-af", f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out_st:.3f}:d=0.03",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "24",
            "-c:a", "aac", "-b:a", "192k",
            str(out),
        ]
        print(f"seg{i:02d}: {start:.3f}-{end:.3f} ({d:.3f}s)")
        subprocess.run(cmd, check=True)
    print("done")


if __name__ == "__main__":
    main()
