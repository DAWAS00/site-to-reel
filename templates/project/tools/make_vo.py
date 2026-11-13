"""Narration from vo-lines.json: an AI-generated TTS voice (edge-tts) or a real recording.

TTS mode (default): one clip per line, voice/rate from brand.json "voice". Word timings come from the
TTS WordBoundary events (measured, not estimated). The text goes to Microsoft's online speech service.
A generated voice is never the creator: lines refer to the creator in the third person only.

vo-lines.json:
  { "reel": { "lines": [[earliest_start_s, "line", latest_end_s], ...] },
    "ad15": { "lines": [...] } }
A line starts at its earliest time or GAP after the previous line, whichever is later (its first WORD is
placed there, not the file start). It may cross a cut but must end by latest_end_s: OVER lines need
shortening, an earlier start, or a slightly faster rate. End lines >= 0.4 s before a hard beat (the hero).

Run:  python tools/make_vo.py   -> vo/<film>/NN.mp3 and vo/<film>.json   (pip install edge-tts)
"""
import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
BRAND = json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
VOICE = BRAND["voice"]["voice"]
RATE = BRAND["voice"].get("rate", "+0%")
GAP = 0.15  # minimum silence between lines
LINES = json.loads((ROOT / "vo-lines.json").read_text(encoding="utf-8"))


async def synth(text, path):
    words = []
    com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    with open(path, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    return words


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


async def main():
    for film, spec in LINES.items():
        if film.startswith("_"):
            continue
        d = ROOT / "vo" / film
        d.mkdir(parents=True, exist_ok=True)
        segs = []
        prev_end = -GAP
        for i, (earliest, text, until) in enumerate(spec["lines"]):
            p = d / f"{i:02d}.mp3"
            words = await synth(text, p)
            # the clip has lead-in silence before the first word: place the first word, not the file start
            lead = words[0]["t"] if words else 0.0
            start = round(max(earliest, prev_end + GAP) - lead, 3)
            last = words[-1]["t"] + words[-1]["d"] if words else dur(p)
            prev_end = start + last
            seg = {"i": i, "start": start, "text": text, "file": str(p.relative_to(ROOT)).replace("\\", "/"),
                   "fileDur": round(dur(p), 3), "speechEnd": round(start + last, 3), "until": until,
                   "words": [{"w": w["w"], "t": round(start + w["t"], 3), "end": round(start + w["t"] + w["d"], 3)} for w in words]}
            seg["fits"] = seg["speechEnd"] <= until + 0.02
            segs.append(seg)
            print(film, i, f"{start:.2f}->{seg['speechEnd']:.2f} (limit {until})", "OK" if seg["fits"] else "OVER", text)
        (ROOT / "vo" / f"{film}.json").write_text(json.dumps({"voice": VOICE, "engine": "edge-tts (Microsoft neural TTS)",
            "disclosure": BRAND["voice"]["disclosure"], "segments": segs}, ensure_ascii=False, indent=1), encoding="utf-8")


asyncio.run(main())
