#!/usr/bin/env python3
"""Concatenate N clips with a fadeblack xfade + impact-hit sound at every
junction. This is the "transicion contundente" recipe: works whether every
cut is a card boundary or a mix of card/interview cuts.

Usage:
    python assemble_with_transitions.py clip_order.json hit.wav -o final.mp4

CRITICAL GOTCHA (cost hours to find): ffmpeg's `amix` filter defaults to
normalize=1, which divides the summed signal by the NUMBER OF INPUTS. With
one dialogue/music track plus N short hit-sound tracks, that is N+1 inputs,
so amix silently crushes the dialogue by up to -20dB even though the hit
tracks are individually quiet. ALWAYS pass normalize=0 on any amix call that
mixes more than 2 streams, and control loudness yourself via `volume=`.
This applies to the final music-mix step too, not just the hit-sound mix.
"""
import json
import subprocess
import sys


def dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "default=noprint_wrappers=1:nokey=1", p], capture_output=True, text=True)
    return float(out.stdout.strip())


def main():
    clips = json.loads(open(sys.argv[1]).read())
    hit = sys.argv[2]
    out_path = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else sys.argv[3]
    xf = 0.25

    d = [dur(c) for c in clips]
    n = len(clips)
    print("durations:", d)

    inputs = []
    for c in clips:
        inputs += ["-i", c]
    inputs += ["-i", hit]
    hit_idx = n

    filt = []
    for i in range(n):
        filt.append(f"[{i}:v]format=yuv420p,setsar=1[v{i}n]")
        filt.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo[a{i}n]")

    cur_v, cur_a = "v0n", "a0n"
    cum = d[0]
    hit_delays = []
    for i in range(1, n):
        offset = cum - xf
        hit_delays.append(max(0.0, offset - 0.08))
        out_v, out_a = f"vx{i}", f"ax{i}"
        filt.append(f"[{cur_v}][v{i}n]xfade=transition=fadeblack:duration={xf}:offset={offset:.3f}[{out_v}]")
        filt.append(f"[{cur_a}][a{i}n]acrossfade=d={xf}[{out_a}]")
        cur_v, cur_a = out_v, out_a
        cum = cum + d[i] - xf

    total = cum
    print("total duration:", total)

    hit_labels = []
    for i, delay in enumerate(hit_delays):
        ms = int(delay * 1000)
        lbl = f"hit{i}"
        filt.append(f"[{hit_idx}:a]adelay={ms}|{ms},volume=0.9[{lbl}]")
        hit_labels.append(f"[{lbl}]")

    mix_inputs = f"[{cur_a}]" + "".join(hit_labels)
    # normalize=0 is mandatory here — see module docstring.
    filt.append(f"{mix_inputs}amix=inputs={len(hit_labels)+1}:duration=first:dropout_transition=0:normalize=0[aout]")

    filt_complex = ";".join(filt)
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filt_complex,
        "-map", f"[{cur_v}]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        out_path,
    ]
    subprocess.run(cmd, check=True)
    print("done:", out_path)


if __name__ == "__main__":
    main()
