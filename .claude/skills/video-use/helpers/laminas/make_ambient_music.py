#!/usr/bin/env python3
"""Very soft ambient background pad (gentle, low-register drone) for when the
user asks for quiet background music and no licensed track is available.
Not a substitute for real music — use it only when explicitly asked for
"algo de fondo" / "muy suave" and no source track is provided.
"""
import argparse
import numpy as np
import soundfile as sf


def build(out_path: str, dur: float, sr: int = 48000):
    n = int(sr * dur)
    t = np.arange(n) / sr

    freqs = [110.0, 130.81, 164.81, 220.0]  # A2, C3, E3, A3 (Am-ish, ambiguous/soft)
    rng = np.random.default_rng(11)

    sig = np.zeros(n)
    for f in freqs:
        detune = f * (1 + rng.uniform(-0.003, 0.003))
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.03, 0.07) * t + rng.uniform(0, 6.28))
        tone = np.sin(2 * np.pi * detune * t) * (0.4 + 0.6 * lfo)
        sig += tone / len(freqs)

    kernel = np.ones(9) / 9
    sig = np.convolve(sig, kernel, mode="same")

    fade_len = int(sr * 3.0)
    env = np.ones(n)
    env[:fade_len] = np.linspace(0, 1, fade_len)
    env[-fade_len:] = np.linspace(1, 0, fade_len)
    sig *= env

    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.5
    sf.write(out_path, sig.astype(np.float32), sr)
    print(f"wrote {out_path} ({dur}s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="music.wav")
    ap.add_argument("--dur", type=float, required=True,
                     help="Make this a few seconds LONGER than the final video "
                          "so atrim never runs dry near the end.")
    args = ap.parse_args()
    build(args.output, args.dur)
