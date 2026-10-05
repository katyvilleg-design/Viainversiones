#!/usr/bin/env python3
"""Procedural background music: soft informative pad + restrained rhythmic
pulse + sparse plucked arpeggio. Free/local synthesis, no AI credits.
Mood target: calm-informative fintech content, NOT flat/silent — gentle
forward motion under the voice. Based on helpers/laminas/make_ambient_music.py
but adds a quarter-note pulse and an off-beat pluck layer for "algo de ritmo".
"""
import argparse
import numpy as np
import soundfile as sf

# C major-ish, warm/trustworthy, gentle motion: Cmaj9 - Am7 - Fmaj7 - G(add9)
CHORDS = [
    [130.81, 164.81, 196.00, 246.94],  # C3 E3 G3 B3  (Cmaj9, no 9th for simplicity)
    [110.00, 130.81, 164.81, 220.00],  # A2 C3 E3 A3  (Am7-ish)
    [87.31, 130.81, 174.61, 220.00],   # F2 C3 F3 A3  (Fmaj7-ish)
    [98.00, 146.83, 196.00, 246.94],   # G2 D3 G3 B3  (G)
]
BPM = 96.0
BEAT = 60.0 / BPM  # 0.625s
BAR = BEAT * 4      # one chord per bar, 2.5s... keep chords 4s for calmer harmonic rhythm
CHORD_DUR = 4.0


def ease_pluck_env(n, sr, decay=0.35):
    t = np.arange(n) / sr
    env = np.exp(-t / decay)
    attack = min(int(sr * 0.004), n)
    if attack > 1:
        env[:attack] *= np.linspace(0, 1, attack)
    return env


def build(out_path: str, dur: float, sr: int = 48000, seed: int = 7):
    n = int(sr * dur)
    t_full = np.arange(n) / sr
    rng = np.random.default_rng(seed)

    # ---- pad layer (soft, shimmering, chord changes every CHORD_DUR) ----
    pad = np.zeros(n)
    n_chords = int(np.ceil(dur / CHORD_DUR))
    for ci in range(n_chords):
        chord = CHORDS[ci % len(CHORDS)]
        c_start = int(ci * CHORD_DUR * sr)
        c_end = min(n, int((ci + 1) * CHORD_DUR * sr))
        if c_start >= n:
            break
        seg_n = c_end - c_start
        t = np.arange(seg_n) / sr
        seg = np.zeros(seg_n)
        for f in chord:
            detune = f * (1 + rng.uniform(-0.002, 0.002))
            lfo = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.05, 0.09) * t + rng.uniform(0, 6.28))
            seg += np.sin(2 * np.pi * detune * t) * lfo / len(chord)
        # soft crossfade at chord boundary
        xf = min(int(sr * 0.6), seg_n // 2)
        if xf > 1:
            seg[:xf] *= np.linspace(0, 1, xf)
            seg[-xf:] *= np.linspace(1, 0, xf)
        pad[c_start:c_end] += seg
    kernel = np.ones(7) / 7
    pad = np.convolve(pad, kernel, mode="same")
    pad = pad / (np.max(np.abs(pad)) + 1e-9) * 0.42

    # ---- pulse layer: soft low thump on every beat (restrained percussion) ----
    pulse = np.zeros(n)
    n_beats = int(dur / BEAT) + 1
    for bi in range(n_beats):
        start_s = bi * BEAT
        start_i = int(start_s * sr)
        if start_i >= n:
            break
        chord = CHORDS[int(start_s // CHORD_DUR) % len(CHORDS)]
        root = chord[0] / 2  # one octave down, soft felt-like low thump
        env_len = min(int(sr * 0.5), n - start_i)
        env = ease_pluck_env(env_len, sr, decay=0.22)
        tt = np.arange(env_len) / sr
        tone = np.sin(2 * np.pi * root * tt) * env
        # slight amplitude variation so it doesn't feel robotic
        tone *= 0.85 + 0.15 * rng.uniform()
        pulse[start_i:start_i + env_len] += tone
    pulse = pulse / (np.max(np.abs(pulse)) + 1e-9) * 0.16

    # ---- sparse pluck arpeggio on off-beats (every other beat, upper chord tone) ----
    pluck = np.zeros(n)
    for bi in range(n_beats):
        if bi % 2 == 0:
            continue  # only off-beats -> sparse, not busy
        if rng.uniform() < 0.35:
            continue  # randomly skip some for human feel
        start_s = bi * BEAT
        start_i = int(start_s * sr)
        if start_i >= n:
            break
        chord = CHORDS[int(start_s // CHORD_DUR) % len(CHORDS)]
        note = chord[rng.integers(2, 4)] * 2  # upper octave tone
        env_len = min(int(sr * 0.4), n - start_i)
        env = ease_pluck_env(env_len, sr, decay=0.18)
        tt = np.arange(env_len) / sr
        # triangle-ish via odd harmonics for a soft plucked-piano color
        tone = (np.sin(2 * np.pi * note * tt)
                + 0.3 * np.sin(2 * np.pi * note * 3 * tt)
                + 0.12 * np.sin(2 * np.pi * note * 5 * tt))
        tone *= env
        pluck[start_i:start_i + env_len] += tone
    pluck = pluck / (np.max(np.abs(pluck)) + 1e-9) * 0.10

    sig = pad + pulse + pluck

    fade_len = int(sr * 1.5)
    env = np.ones(n)
    env[:fade_len] = np.linspace(0, 1, fade_len)
    env[-fade_len:] = np.linspace(1, 0, fade_len)
    sig *= env

    peak = np.max(np.abs(sig)) + 1e-9
    sig = sig / peak * 0.6
    stereo = np.stack([sig, sig], axis=1).astype(np.float32)
    sf.write(out_path, stereo, sr)
    print(f"wrote {out_path} ({dur}s, {sr}Hz, peak={np.max(np.abs(sig)):.3f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="bgm.wav")
    ap.add_argument("--dur", type=float, required=True)
    args = ap.parse_args()
    build(args.output, args.dur)
