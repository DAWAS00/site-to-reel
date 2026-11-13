"""Builds timeline.json (main reel) and timeline-ad15.json (separate short cut, not a speed-up).

One source for picture, captions, VO, sound and checks. Frame ranges come from seconds (start
inclusive, end exclusive), so they always cover F0..F(n-1) with no gaps. Brand values come from
brand.json. VO lines (if vo/<film>.json exists) are copied in with their measured word timings.
Gate:  python ~/.claude/skills/video-director/scripts/check_timeline.py timeline.json   (0 errors)
Run:   python tools/build_timelines.py
Worked example with every feature in use: <skill>/examples/dawas-shlef/tools/build_timelines.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30
BRAND = json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
PALETTE = BRAND["palette"]

# key -> file. Captures (3x) from tools/capture.js; card previews and the wordmark icon (svg, currentColor).
ASSETS = {
    "home": "capture3x/home-top.png",
    "iconBrand": "assets/icons/brand.svg",
    # "cardA": "assets/previews/a.png", "cardB": ..., "cardC": ...   (scatter scenes need 3)
}

FULL = {"cx": 270, "cy": 480, "z": 2.0}  # a 540x960 css capture fills the 1080x1920 frame
SAFE = BRAND.get("safeArea", {"x": [90, 990], "y": [200, 1500], "captionBand": [1300, 1500]})
CTA = {
    "creator": BRAND["creator"]["credit"],
    "line": "ONE ACTION LINE",           # the single thing to do; no "link in description" on Reels
    "overlay": "THREE. WORD. RHYTHM.",
    "url": BRAND["publicUrl"],            # always the public domain, never localhost
}


def cam(t, cx, cy, z, fx=540, fy=960):
    # place capture point (cx, cy) css px at frame point (fx, fy); z frame px per css px (<= capture scale)
    return {"t": t, "cx": cx, "cy": cy, "z": z, "fx": fx, "fy": fy}


def full(t):
    return cam(t, **FULL)


def finish(scenes, dur):
    for i, s in enumerate(scenes):
        s["end"] = scenes[i + 1]["start"] if i + 1 < len(scenes) else dur
        s["frames"] = [round(s["start"] * FPS), round(s["end"] * FPS) - 1]
    return scenes


def caption(cid, text, a, b):
    # at most 2 lines (split with \n); sits in the caption band, clear of the platform UI
    return {"id": cid, "text": text, "from": a, "to": b, "px": 54, "y": 1462}


def vo_lines(film):
    p = ROOT / "vo" / f"{film}.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return [{"text": s["text"], "start": s["start"], "file": s["file"], "words": s["words"]} for s in d["segments"]]


def meta(title, version, dur, film, note):
    vo = vo_lines(film)
    return {
        "title": title, "version": version, "w": 1080, "h": 1920, "fps": FPS, "dur": dur,
        "frames": round(dur * FPS), "frameRange": f"F0-F{round(dur * FPS) - 1} inclusive",
        # "reads" for a silent animatic; "voice" once measured VO exists
        "clock": "voice" if vo else "reads",
        "register": "editorial / clean UI, 30 fps, no motion blur",
        "audio": BRAND["voice"]["disclosure"] + " + synthesized score and SFX" if vo else "silent animatic",
        "vo": {"status": "MEASURED - word timings from tools/make_vo.py" if vo else "NONE - silent animatic"},
        "boxesFile": "capture3x/boxes.json",
        "captureScale": 3,
        "note": note,
    }


def film(title, version, film_id, dur, scenes, texts, caps, hero, reads, silences=(), sfx=(), note=""):
    return {
        "meta": meta(title, version, dur, film_id, note),
        "palette": PALETTE, "brand": BRAND, "assets": ASSETS, "scenes": finish(scenes, dur),
        "hero": hero, "reads": reads, "texts": texts, "captions": caps, "terms": [BRAND["name"]],
        "vo": vo_lines(film_id), "silences": list(silences), "sfx": list(sfx), "cuts": [],
    }


# ---------------------------------------------------------------- main reel (EDIT)
def reel():
    dur = 45.0
    sc = [
        # A scatter opening needs 3 preview cards (and optional tabs):
        # {"id": "s01-scatter", "start": 0.0, "kind": "scatter", "variant": "cards", "cards": [
        #     {"img": "cardA", "title": "Card A", "tag": "WEBSITE", "seed": 11}, ...], "alignAt": 1.9,
        #  "beats": {"align": 1.9}, "transitionOut": {"type": "rise", "dur": 0.6, "why": "..."}},
        {"id": "s01-home", "start": 0.0, "kind": "ui", "img": "home",
         "source": "capture3x/home-top.png",
         "action": "Homepage under the hook; push to the wordmark",
         "cam": [full(0.0), full(1.2), cam(3.0, 180, 42, 3.0, 540, 620)],
         "callouts": [{"type": "underline", "box": "home-top.logo", "t": 3.1, "dur": 0.3, "color": "accent"}],
         "beats": {"wordmark": 3.1},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "say aloud why this cut happens"}},
        # ... one ui scene per feature; real before/after via "swaps": [{"t": ..., "img": "..."}]
        {"id": "s02-creator", "start": 38.0, "kind": "creator", "creator": BRAND["creator"],
         "action": "Identity line", "beats": {"name": 38.15},
         "transitionOut": {"type": "rise", "dur": 0.6, "why": "the identity resolves into the one action"}},
        {"id": "s03-cta", "start": 40.0, "kind": "cta", "cta": CTA,
         "action": "Wordmark, creator, one CTA, public URL; stable hold",
         "beats": {"wordmark": 40.0, "line": 40.6, "url": 41.2, "hold": 43.0}},
    ]
    texts = [
        # hook: legible from frame 0, >= 84 px, >= 7:1, inside x 90-990; box = [x, y, w, h] for qa_video
        {"id": "hook", "role": "hook", "type": "script", "text": "HOOK IN THE CAPTION LANGUAGE",
         "from": 0.0, "to": 2.6, "px": 88, "weight": 700, "y": 330, "box": [90, 245, 900, 120]},
        # the public URL early too (by 3 s), not only at the end
        {"id": "url-early", "role": "cta", "type": "tag", "text": BRAND["publicUrl"],
         "from": 0.5, "to": 2.6, "px": 48, "y": 1450, "box": [290, 1405, 500, 90]},
        {"id": "cta-wordmark", "role": "brand", "draw": False, "text": BRAND["wordmark"], "from": 40.0, "to": dur, "px": 150},
        {"id": "cta-url", "role": "cta", "draw": False, "text": BRAND["publicUrl"], "from": 41.2, "to": dur, "px": 66, "box": [190, 1228, 700, 120]},
    ]
    caps = [
        caption("c-01", "CAPTION LINE ONE", 6.8, 8.9),
    ]
    return film(f"{BRAND['name']} - 45 s reel", "reel-v1", "reel", dur, sc, texts, caps,
                hero={"t": 24.15, "what": "THE ONE REAL STATE CHANGE THE FILM BUILDS TO"},
                reads=[{"what": "hook", "from": 0.0, "to": 2.0}, {"what": "public URL", "from": 41.5, "to": dur}],
                # once VO exists: a planned pause before the hero, and SFX on real state changes
                silences=[], sfx=[], note="EDIT")


# ---------------------------------------------------------------- 15 s cut (EDIT)
def ad():
    dur = 15.0
    sc = [
        {"id": "a01-home", "start": 0.0, "kind": "ui", "img": "home", "action": "Hook over the homepage",
         "cam": [full(0.0)], "beats": {"hook": 0.0},
         "transitionOut": {"type": "fade", "dur": 0.5, "why": "straight to the action"}},
        {"id": "a02-cta", "start": 12.0, "kind": "cta", "cta": CTA, "action": "End card",
         "beats": {"wordmark": 12.0, "url": 13.2}},
    ]
    texts = [
        {"id": "hook", "role": "hook", "type": "script", "text": "SHORT HOOK", "from": 0.0, "to": 2.5,
         "px": 92, "weight": 700, "y": 360, "box": [90, 270, 900, 125]},
        {"id": "cta-url", "role": "cta", "draw": False, "text": BRAND["publicUrl"], "from": 13.2, "to": dur, "px": 66, "box": [190, 1228, 700, 120]},
    ]
    return film(f"{BRAND['name']} - 15 s ad", "ad-v1", "ad15", dur, sc, texts, [],
                hero={"t": 8.85, "what": "EDIT"}, reads=[{"what": "public URL", "from": 13.2, "to": dur}], note="EDIT")


for name, tl in (("timeline.json", reel()), ("timeline-ad15.json", ad())):
    (ROOT / name).write_text(json.dumps(tl, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", name, tl["meta"]["frames"], "frames,", len(tl["scenes"]), "scenes")
