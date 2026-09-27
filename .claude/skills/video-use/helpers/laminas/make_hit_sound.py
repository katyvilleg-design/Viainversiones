#!/usr/bin/env python3
"""Synthesize a short dramatic 'hit' sound for a hard news-style transition:
a fast descending pitch sweep + sub thump + brief noise crack. No external
SFX library needed. Reused across every "transición contundente" request.
"""
import argparse
import numpy as np
import soundfile as sf


def build(out_path: str, dur: float = 0.55, sr: int = 48000):
    n = int(sr * dur)
    t = np.arange(n) / sr

    f0, f1 = 900, 60
    freq = f0 * (f1 / f0) ** (t / dur)
    phase = 2 * np.pi * np.cumsum(freq) / sr
    sweep = np.sin(phase) * np.exp(-t / 0.35)

    thump = np.sin(2 * np.pi * 55 * t) * np.exp(-t / 0.12)

    crack_n = int(sr * 0.03)
    crack = np.zeros(n)
    crack[:crack_n] = np.random.default_rng(3).standard_normal(crack_n) * np.exp(-np.arange(crack_n) / (sr * 0.006))

    sig = 0.55 * sweep + 0.55 * thump + 0.5 * crack
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.9
    sf.write(out_path, sig.astype(np.float32), sr)
    print(f"wrote {out_path} ({dur}s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="hit.wav")
    ap.add_argument("--dur", type=float, default=0.55)
    args = ap.parse_args()
    build(args.output, args.dur)
