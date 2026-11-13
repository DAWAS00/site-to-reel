"""Score, SFX and mix for both films, all placed from the timeline (scenes, vo, silences, sfx).
- VO: the measured clips from tools/make_vo.py (recorded, or an AI-generated narrator that is never the creator).
- Score: a quiet synthesized pad (one chord per scene) plus a soft pluck on every other scene start,
  ducked under the voice and dropped out for each planned silence.
- SFX: tick (real UI state changes), hit (the save: loudest non-voice sound), chime (URL lands).
- Master: gain to -16 LUFS integrated, limited to -1.5 dBTP, measured with ffmpeg ebur128.
Run:  python tools/make_audio.py  -> out/audio/<film>-mix.wav (+ stems)
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
OUT = ROOT / "out" / "audio"
OUT.mkdir(parents=True, exist_ok=True)

# D major colour, one voicing per scene in order (cycled)
CHORDS = [[146.83, 220.0, 277.18, 369.99],   # Dmaj7
          [123.47, 185.0, 293.66, 369.99],   # Bm7
          [98.0, 196.0, 246.94, 369.99],     # Gmaj7
          [110.0, 220.0, 293.66, 329.63]]    # Asus4
rng = np.random.default_rng(7)


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def env(n, a, r):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    e[:na] = np.linspace(0, 1, na) ** 2
    e[n - nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for det in (-0.6, 0.6):
            ph = rng.uniform(0, 2 * np.pi)
            y += np.sin(2 * np.pi * (f + det) * t + ph) + 0.18 * np.sin(4 * np.pi * (f + det) * t + ph)
    y *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.23 * t)  # slow breathing
    return y / (len(freqs) * 2) * env(n, 0.6, 0.8)


def pluck(f, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * k * t) * (0.5 ** (k - 1)) for k in (1, 2, 3)) * np.exp(-t * 3.2)
    return y * env(n, 0.004, 0.2)


def tick():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * t) * 0.6 + rng.normal(0, 0.25, n)) * np.exp(-t * 140)


def hit():
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 25)) * t) * np.exp(-t * 9)
    bell = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((587.33, 0.5), (880.0, 0.35), (1174.66, 0.2))) * np.exp(-t * 3.5)
    click = rng.normal(0, 1, n) * np.exp(-t * 300) * 0.3
    return (thump * 0.9 + bell + click) * env(n, 0.002, 0.3)


def chime():
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for i, f in enumerate((587.33, 739.99, 880.0)):
        d = int(i * 0.09 * SR)
        y[d:] += np.sin(2 * np.pi * f * t[: n - d]) * np.exp(-t[: n - d] * 2.6) * 0.45
    return y * env(n, 0.003, 0.4)


def add(buf, sig, at, gain):
    i = int(round(at * SR))
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * gain


def db(x):
    return 10 ** (x / 20)


def smooth(x, sec):
    k = max(1, int(sec * SR))
    c = np.cumsum(np.insert(x, 0, 0))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.full(len(x) - len(y), y[-1] if len(y) else 0)])


def write(path, x):
    pcm = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        s = (pcm * 32767).astype("<i2")
        w.writeframes(np.column_stack([s, s]).tobytes())


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary).group(1))
    return i, tp


def build(film, tlname):
    tl = json.loads((ROOT / tlname).read_text(encoding="utf-8"))
    dur = tl["meta"]["dur"]
    n = int(dur * SR)
    vo, music, sfx = np.zeros(n), np.zeros(n), np.zeros(n)

    for line in tl["vo"]:
        add(vo, decode(ROOT / line["file"]), line["start"], 1.0)

    scenes = tl["scenes"]
    for k, s in enumerate(scenes):
        a, b = s["start"], s["end"]
        add(music, pad(CHORDS[k % len(CHORDS)], (b - a) + 0.8), max(0, a - 0.2), 1.0)
        if k % 2 == 0 and k:
            add(music, pluck(CHORDS[k % len(CHORDS)][2] * 2), a, 0.35)
    # duck the score under speech (-11 dB), and take it out entirely for planned silences
    speech = smooth(np.abs(vo), 0.05) > 0.01
    duck = np.where(smooth(speech.astype(float), 0.25) > 0.05, db(-11), 1.0)
    duck = smooth(duck, 0.12)
    gate = np.ones(n)
    for x in tl.get("silences", []):
        # the score stays out until just after the hit, so the smoothed gate can't creep into the silence
        i0, i1 = int((x["from"] - 0.25) * SR), int((x["to"] + 0.35) * SR)
        gate[i0:i1] = 0.0
    gate = smooth(gate, 0.18)
    music *= duck * gate
    music *= env(n, 0.3, 1.2)

    for c in tl.get("sfx", []):
        sig, g = {"tick": (tick(), 0.18), "hit": (hit(), 0.75), "chime": (chime(), 0.32)}[c["kind"]]
        add(sfx, sig, c["t"], g)

    vo_rms = np.sqrt(np.mean(vo[speech] ** 2)) if speech.any() else 0.1
    music *= vo_rms * db(-14) / max(1e-9, np.sqrt(np.mean(music ** 2)))  # bed ~14 dB under the voice
    mix = vo + music + sfx
    mix *= 0.5 / np.max(np.abs(mix))

    tmp = OUT / f"{film}-premaster.wav"
    write(tmp, mix)
    i, _ = loudness(tmp)
    mix *= db(-16.0 - i)
    write(tmp, mix)
    master = OUT / f"{film}-mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
                    "alimiter=limit=-1.6dB:level=false:attack=1:release=60,aresample=48000", "-c:a", "pcm_s16le", str(master)], check=True)
    tmp.unlink()
    for name, stem in (("vo", vo), ("music", music), ("sfx", sfx)):
        write(OUT / f"{film}-stem-{name}.wav", stem * 0.5 / max(1e-9, np.max(np.abs(mix))))
    i, tp = loudness(master)
    print(film, f"{i} LUFS, true peak {tp} dBTP ->", master.relative_to(ROOT))


build("reel", "timeline.json")
build("ad15", "timeline-ad15.json")
