"""Builds out/storyboard-<film>.html from a timeline and frames pulled from the encoded MP4.
Each panel: the frame at the scene's key beat, scene id, seconds and frames, the VO spoken over the scene
(from timeline "vo" if present), the on-screen caption, the motion and the transition out (with its reason).
Screenshot it to out/storyboard-explained.png with tools/shot-storyboard.js (see SKILL.md).
Key frame per scene: scene["key"] if set, else its last beat + 0.35 s, else its midpoint.
Run:  python tools/storyboard.py out/reel-final.mp4 timeline.json reel
"""
import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
video, tl_path, film = sys.argv[1], sys.argv[2], sys.argv[3]
TL = json.loads((ROOT / tl_path).read_text(encoding="utf-8"))
FPS = TL["meta"]["fps"]
BR = TL.get("brand", {})


def key_time(s):
    if "key" in s:
        return s["key"]
    beats = sorted((s.get("beats") or {}).values())
    if beats:
        return min(beats[-1] + 0.35, s["end"] - 0.05)
    return (s["start"] + s["end"]) / 2


def grab(t, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / video),
                    "-vf", f"select=eq(n\\,{round(t * FPS)})", "-fps_mode", "passthrough",
                    "-frames:v", "1", str(path)], check=True)


def spoken_in(s):
    return " ".join(l["text"] for l in TL.get("vo") or [] if isinstance(l, dict) and "words" in l
                    and l["words"] and s["start"] <= l["words"][0]["t"] < s["end"])


def captions_in(s):
    return [c["text"].replace("\n", " ") for c in TL["captions"] if c["from"] < s["end"] and c["to"] > s["start"]]


panels = []
for i, s in enumerate(TL["scenes"]):
    tr = s.get("transitionOut")
    trtxt = f"{tr['type']} {tr['dur']} s: {tr['why']}" if tr else "end: stable hold"
    caps = " / ".join(captions_in(s)) or "(none)"
    grab(key_time(s), ROOT / "out" / "review" / f"storyboard-{film}" / f"{s['id']}.png")
    panels.append(f"""
<div class="p">
  <img src="review/storyboard-{film}/{s['id']}.png">
  <div class="m">
    <div class="h"><b>{i + 1:02d} {s['id']}</b><span>{s['start']:.1f}-{s['end']:.1f} s · F{s['frames'][0]}-F{s['frames'][1]}</span></div>
    <div class="k">Frame at {key_time(s):.2f} s</div>
    <div class="l">VO</div><div class="sc">{html.escape(spoken_in(s) or '(none)')}</div>
    <div class="l">On-screen caption</div><div class="sc cap">{html.escape(caps)}</div>
    <div class="t"><i>Motion:</i> {html.escape(s.get('action', ''))}</div>
    <div class="t"><i>Out:</i> {html.escape(trtxt)}</div>
  </div>
</div>""")

fonts = BR.get("fonts", {})
sf, lf = fonts.get("script", {}), fonts.get("latin", {})
face = lambda fam, alias: (f"@font-face {{ font-family: {alias}; src: url(../{fam['files'][0]['url']}); }}" if fam.get("files") else "")
direction = BR.get("direction", "rtl")
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{face(sf, 'Script')}
{face(lf, 'Latin')}
body {{ margin: 0; background: {TL['palette'].get('paper', '#f5f1e7')}; color: {TL['palette'].get('ink', '#23282a')}; font: 15px/1.35 Georgia, serif; width: 1800px; }}
header {{ padding: 28px 36px 8px; }}
h1 {{ font: 600 44px Latin, serif; margin: 0; }}
header p {{ margin: 4px 0 0; opacity: .8; }}
.g {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 16px; padding: 20px 36px 36px; }}
.p {{ background: #fbf9f3; border: 1px solid #ddd6c6; }}
.p img {{ width: 100%; display: block; }}
.m {{ padding: 8px 10px 12px; }}
.h {{ display: flex; justify-content: space-between; font-size: 14px; }}
.h span, .k {{ opacity: .75; font-size: 12px; }}
.sc {{ font-family: Script, sans-serif; direction: {direction}; text-align: {'right' if direction == 'rtl' else 'left'}; margin-top: 1px; font-size: 15px; }}
.cap {{ opacity: .8; font-size: 13px; }}
.l {{ font-size: 11px; opacity: .75; margin-top: 7px; text-transform: uppercase; letter-spacing: .06em; }}
.t {{ font-size: 12px; margin-top: 5px; }}
</style></head><body>
<header><h1>{html.escape(TL['meta']['title'])}: storyboard</h1>
<p>{html.escape(TL['meta']['frameRange'])} · {TL['meta']['w']}×{TL['meta']['h']} · {FPS} fps · hero {TL.get('hero', {}).get('t', '?')} s: {html.escape(TL.get('hero', {}).get('what', ''))} ·
frames are taken from {html.escape(video)}</p></header>
<div class="g">{''.join(panels)}</div></body></html>"""
(ROOT / "out" / f"storyboard-{film}.html").write_text(page, encoding="utf-8")
print("key times:", ",".join(f"{key_time(s):.2f}" for s in TL["scenes"]))
