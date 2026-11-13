"""Pulls review frames from an ENCODED MP4 (never from the PNG frames) and builds sheets.
  out/review/<film>/contact/      every 2 s (1 s for short films), plus out/contact-sheet-<film>.jpg
  out/review/<film>/transitions/  before / mid / after each seam, plus transitions-sheet.jpg
  out/review/<film>/details/      every scene beat + 0.35 s (the settled read), plus details-sheet.jpg
Run:  python tools/review_frames.py out/reel-final.mp4 timeline.json reel
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
video, tl_path, film = sys.argv[1], sys.argv[2], sys.argv[3]
TL = json.loads((ROOT / tl_path).read_text(encoding="utf-8"))
OUT = ROOT / "out" / "review" / film
FPS = TL["meta"]["fps"]


def grab(t, path):
    # the select filter decodes to the exact frame (-ss can miss the last frame); index = round(t * fps)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = round(t * FPS)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / video), "-vf", f"select=eq(n\\,{n})",
                    "-fps_mode", "passthrough", "-frames:v", "1", str(path)], check=True)
    return n / FPS


def sheet(items, dst, cols, tw=270):
    th = tw * 16 // 9
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (cols * tw, rows * (th + 24)), "white")
    d = ImageDraw.Draw(im)
    for i, (label, p) in enumerate(items):
        x, y = (i % cols) * tw, (i // cols) * (th + 24)
        im.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + 24))
        d.text((x + 4, y + 6), label, fill="black")
    im.save(dst, quality=90)


dur = TL["meta"]["dur"]
last = (dur * FPS - 1) / FPS
step = 2.0 if dur > 20 else 1.0
contact = []
t = 0.0
while t < dur:
    p = OUT / "contact" / f"t{t:05.2f}.png"
    contact.append((f"{grab(t, p):.2f}s F{round(t * FPS)}", p))
    t += step
p = OUT / "contact" / f"t{last:05.2f}.png"
contact.append((f"{grab(last, p):.2f}s F{round(last * FPS)} (last)", p))
sheet(contact, ROOT / "out" / f"contact-sheet-{film}.jpg", 6 if dur > 20 else 4)

trans = []
for prev, s in zip(TL["scenes"], TL["scenes"][1:]):
    tr = prev.get("transitionOut")
    if not tr:
        continue
    for tag, tt in (("before", s["start"] - 0.2), ("mid", s["start"] + tr["dur"] / 2), ("after", s["start"] + tr["dur"] + 0.1)):
        p = OUT / "transitions" / f"{prev['id']}__{s['id']}__{tag}.png"
        trans.append((f"{tag} {grab(tt, p):.2f}s {tr['type']}", p))
if trans:
    sheet(trans, OUT / "transitions-sheet.jpg", 6)

det = []
for s in TL["scenes"]:
    for k, bt in (s.get("beats") or {}).items():
        tt = min(bt + 0.35, s["end"] - 1 / FPS, last)
        p = OUT / "details" / f"{s['id']}__{k}.png"
        det.append((f"{s['id']} {k} {grab(tt, p):.2f}s", p))
p = OUT / "details" / "last.png"
det.append((f"last {grab(last, p):.2f}s", p))
sheet(det, OUT / "details-sheet.jpg", 6)

print("review frames written to", OUT)
