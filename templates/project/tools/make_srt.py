"""Sidecar subtitles from the measured VO lines (the AI narrator's words, exactly as spoken).
Run:  python tools/make_srt.py  -> out/subtitles-reel.srt, out/subtitles-ad15.srt
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


for film, tl in (("reel", "timeline.json"), ("ad15", "timeline-ad15.json")):
    lines = json.loads((ROOT / tl).read_text(encoding="utf-8"))["vo"]
    out = []
    for i, l in enumerate(lines, 1):
        a = l["words"][0]["t"]
        b = l["words"][-1]["end"] + 0.25  # short tail so the line doesn't vanish on the last syllable
        if i < len(lines):
            b = min(b, lines[i]["words"][0]["t"] - 0.05)
        out.append(f"{i}\n{ts(a)} --> {ts(b)}\n{l['text']}\n")
    (ROOT / "out" / f"subtitles-{film}.srt").write_text("\n".join(out), encoding="utf-8-sig")
    print(film, len(out), "cues")
