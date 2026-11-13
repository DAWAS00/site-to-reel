"""Dawas Shlef worked example: builds timeline.json (45 s reel) and timeline-ad15.json (15 s cutdown).
Brand values come from brand.json; captures from capture3x/ (not shipped in the skill: re-capture them).

One source for picture, captions and checks. Frame ranges are derived from seconds
(start inclusive, end exclusive), so they always cover F0..F(n-1) with no gaps.
Run:  python tools/build_timelines.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30

ASSETS = {
    "home": "capture3x/home-top.png",
    "library": "capture3x/library-search.png",
    "libraryPhosphor": "capture3x/library-phosphor.png",
    "detail": "capture3x/detail-top.png",
    "detailSource": "capture3x/detail-source.png",
    "detailSaved": "capture3x/detail-saved.png",
    "shelf": "capture3x/shelf-saved-4x.png",
    "prompt": "capture3x/prompt-copy.png",
    "promptCopied": "capture3x/prompt-copied.png",
    "skill": "capture3x/skill-copy.png",
    "learning": "capture3x/learning-top.png",
    "chapters": "capture3x/learning-chapters.png",
    "about": "capture3x/about-contact.png",
    "cardPhosphor": "assets/previews/phosphor-icons.png",
    "cardLucide": "assets/previews/lucide-icons.png",
    "cardShadcn": "assets/previews/shadcn-design.png",
    "iconBook": "assets/icons/book-open.svg",
}

BRAND = json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
PALETTE = BRAND["palette"]
CARDS = [  # real site preview images on native paper cards (scatter scenes)
    {"img": "cardPhosphor", "title": "Phosphor Icons", "tag": "WEBSITE", "seed": 11},
    {"img": "cardLucide", "title": "Lucide Icons", "tag": "WEBSITE", "seed": 23},
    {"img": "cardShadcn", "title": "shadcn.io Design", "tag": "WEBSITE", "seed": 37},
]
TABS = [  # abstract browser tabs (no real history)
    {"label": "Tools", "x": 270, "y": 545, "rot": -3.5, "seed": 51},
    {"label": "Prompts", "x": 800, "y": 660, "rot": 3.0, "seed": 52},
    {"label": "Saved links", "x": 760, "y": 1330, "rot": -2.0, "seed": 53},
]

FULL = {"cx": 270, "cy": 480, "z": 2.0}          # page fills the frame, 1:1.5 of the 3x capture
CTA = {
    "creator": BRAND["creator"]["credit"],
    "line": "اختار أول مورد يفيد مشروعك",
    "overlay": "اكتشف. افهم. احفظ.",
    "url": BRAND["publicUrl"],
}


def cam(t, cx, cy, z, fx=540, fy=960):
    return {"t": t, "cx": cx, "cy": cy, "z": z, "fx": fx, "fy": fy}


def full(t):
    return cam(t, **FULL)


def finish(scenes, dur):
    for i, s in enumerate(scenes):
        s["end"] = scenes[i + 1]["start"] if i + 1 < len(scenes) else dur
        s["frames"] = [round(s["start"] * FPS), round(s["end"] * FPS) - 1]
    return scenes


def caption(cid, text, a, b):
    return {"id": cid, "text": text, "from": a, "to": b, "px": 54, "y": 1462}


def meta(title, version, dur, note):
    return {
        "title": title, "version": version, "w": 1080, "h": 1920, "fps": FPS, "dur": dur,
        "frames": round(dur * FPS), "frameRange": f"F0-F{round(dur * FPS) - 1} inclusive",
        "clock": "voice", "register": "editorial / clean UI, 30 fps, no motion blur",
        "audio": "AI-generated narrator (ar-JO-TaimNeural, edge-tts) + synthesized score and SFX (tools/make_audio.py)",
        "vo": {"status": "MEASURED - TTS WordBoundary timings (tools/make_vo.py); AI-generated voice, not Mohammad Dawas"},
        "boxesFile": "capture3x/boxes.json",
        "captureScale": 3,
        "silenceNote": "VO lines were fitted to the approved picture; the save click sits in a planned pause.",
        "note": note,
    }


def vo_lines(film):
    # measured VO lines from tools/make_vo.py, in the shape check_timeline.py reads
    d = json.loads((ROOT / "vo" / f"{film}.json").read_text(encoding="utf-8"))
    return [{"text": s["text"], "start": s["start"], "file": s["file"], "words": s["words"]} for s in d["segments"]]


# ---------------------------------------------------------------- 45 s reel
def reel():
    dur = 45.0
    sc = [
        {"id": "s01-scatter", "start": 0.0, "kind": "scatter", "variant": "tabs", "cards": CARDS, "tabs": TABS,
         "source": "Native paper tabs (abstract) + real site preview images",
         "action": "Hook over scattered tabs (Tools / Prompts / Saved links) and three resource cards; everything gathers to the centre at 2.0 s",
         "gatherAt": 2.0,
         "beats": {"settled": 0.75, "gather": 2.0},
         "transitionOut": {"type": "emerge", "dur": 0.6, "why": "the scattered finds collapse into the one place they now live: the real homepage"}},
        {"id": "s02-home", "start": 2.6, "kind": "ui", "img": "home",
         "source": "capture3x/home-top.png (live local site, 540x960 @3x)",
         "action": "Homepage card; camera moves to the real wordmark, then to Good tools. Clearer thinking.",
         "cam": [cam(2.6, 270, 480, 1.45, 540, 1080), cam(4.1, 270, 480, 1.45, 540, 1080),
                 cam(4.8, 180, 42, 3.0, 540, 620), cam(5.9, 180, 42, 3.0, 540, 620),
                 cam(6.6, 270, 330, 2.0, 540, 860)],
         "beats": {"wordmark": 4.8, "proposition": 6.6},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "Explore the library: one step into the collection"}},
        {"id": "s03-library", "start": 9.0, "kind": "ui", "img": "library",
         "source": "capture3x/library-search.png",
         "action": "Real Design search; underline on the query, slow push, circle on Websites 16",
         "cam": [full(9.0), full(9.9), cam(12.0, 270, 470, 2.12)],
         "callouts": [
             {"type": "underline", "rect": {"x": 64, "y": 40, "w": 43, "h": 30}, "t": 9.7, "dur": 0.3, "color": "celadon"},
             {"type": "ring", "box": "library-search.websites", "t": 12.2, "dur": 0.35, "color": "celadon"}],
         "beats": {"query": 9.7, "filter": 12.2},
         "transitionOut": {"type": "push-up", "dur": 0.45, "why": "scrolling the same results down to Phosphor Icons"}},
        {"id": "s03b-result", "start": 13.4, "kind": "ui", "img": "libraryPhosphor",
         "source": "capture3x/library-phosphor.png (same search, scrolled to the third result)",
         "action": "The Phosphor Icons result card; push in and underline the title that the next shot opens",
         "cam": [full(13.4), full(13.9), cam(14.5, 220, 470, 2.5)],
         "callouts": [{"type": "underline", "box": "library-phosphor.title", "t": 14.7, "dur": 0.3, "color": "celadon"}],
         "beats": {"result": 14.7},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "opening Phosphor Icons goes one level deeper"}},
        {"id": "s04-detail", "start": 16.0, "kind": "ui", "img": "detail",
         "source": "capture3x/detail-top.png",
         "action": "Phosphor Icons detail: title and purpose",
         "cam": [full(16.0)],
         "callouts": [{"type": "underline", "rect": {"x": 20, "y": 235.5, "w": 276, "h": 51.8}, "t": 16.6, "dur": 0.3, "color": "celadon"}],
         "beats": {"title": 16.6},
         "transitionOut": {"type": "push-up", "dur": 0.45, "why": "scrolling the same page down to its source credit"}},
        {"id": "s05-source", "start": 17.5, "kind": "ui", "img": "detailSource",
         "source": "capture3x/detail-source.png",
         "action": "Source credit (Helena Zhang and Tobias Fried) and the real Visit website link",
         "cam": [cam(17.5, 270, 436, 2.2)],
         "callouts": [
             {"type": "underline", "rect": {"x": 46, "y": 231, "w": 179, "h": 13}, "t": 18.0, "dur": 0.3, "color": "celadon"},
             {"type": "ring", "box": "detail-source.visit", "t": 18.35, "dur": 0.35, "color": "celadon"}],
         "beats": {"credit": 18.0, "visit": 18.35},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "the next kind of resource: a prompt"}},
        {"id": "s06-prompt", "start": 19.0, "kind": "ui", "img": "prompt",
         "source": "capture3x/prompt-copy.png -> capture3x/prompt-copied.png (real click, real Copied feedback)",
         "action": "Copy prompt ring, then the site's own Copied state and toast",
         "cam": [full(19.0)],
         "swaps": [{"t": 20.05, "img": "promptCopied"}],
         "callouts": [{"type": "ring", "box": "prompt-copy.copy", "t": 19.7, "dur": 0.35, "color": "cinnabar", "pulseAt": 20.05}],
         "beats": {"ring": 19.7, "copied": 20.05},
         "transitionOut": {"type": "push-up", "dur": 0.45, "why": "the same copy control on a skill"}},
        {"id": "s07-skill", "start": 21.3, "kind": "ui", "img": "skill",
         "source": "capture3x/skill-copy.png",
         "action": "Copy SKILL.md control and the full skill text (no click shown, no fake feedback)",
         "cam": [full(21.3)],
         "callouts": [{"type": "ring", "box": "skill-copy.copy", "t": 21.9, "dur": 0.35, "color": "cinnabar"}],
         "beats": {"ring": 21.9},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "back to a resource to keep it"}},
        {"id": "s08-save", "start": 23.0, "kind": "ui", "img": "detail",
         "source": "capture3x/detail-top.png -> capture3x/detail-saved.png (real click)",
         "action": "Close on Save, real state swap to Saved to my shelf, pull out to the header count and toast",
         "cam": [cam(23.0, 190, 370, 2.3), cam(24.9, 190, 370, 2.3), full(25.5)],
         "swaps": [{"t": 24.15, "img": "detailSaved"}],
         "callouts": [
             {"type": "ring", "box": "detail-top.save", "t": 23.75, "dur": 0.35, "color": "cinnabar", "pulseAt": 24.15, "until": 24.75},
             {"type": "underline", "box": "detail-saved.myshelf", "t": 25.6, "dur": 0.3, "color": "celadon"}],
         "beats": {"ring": 23.75, "saved": 24.15, "pullOut": 24.9},
         "transitionOut": {"type": "push-up", "dur": 0.45, "why": "where the saved item goes: My shelf"}},
        {"id": "s09-shelf", "start": 26.0, "kind": "ui", "img": "shelf",
         "source": "capture3x/shelf-saved-4x.png (4x, so the count holds at z 4 without upscaling)",
         "action": "My shelf: 1 resource on your shelf, Saved only filter",
         "cam": [full(26.0), full(26.3), cam(26.8, 128, 183, 4.0, 540, 700), cam(28.9, 128, 192, 4.0, 540, 700)],
         "callouts": [{"type": "underline", "box": "shelf-saved.count", "t": 26.95, "dur": 0.3, "color": "celadon"}],
         "beats": {"count": 26.95},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "from keeping to learning"}},
        {"id": "s10-learning", "start": 29.0, "kind": "ui", "img": "learning",
         "source": "capture3x/learning-top.png",
         "action": "Learning guide title, then the table of contents and the Original tutorial link",
         "cam": [full(29.0), full(29.9), cam(31.9, 270, 440, 2.12), cam(32.5, 150, 840, 3.0)],
         "callouts": [
             {"type": "underline", "rect": {"x": 280, "y": 97, "w": 52, "h": 16}, "t": 29.7, "dur": 0.3, "color": "celadon"},
             {"type": "ring", "box": "learning-top.original", "t": 32.8, "dur": 0.35, "color": "celadon"}],
         "beats": {"section": 29.7, "toc": 32.5, "original": 32.8},
         "transitionOut": {"type": "push-up", "dur": 0.45, "why": "scrolling the same guide to its chapter map"}},
        {"id": "s11-chapters", "start": 33.4, "kind": "ui", "img": "chapters",
         "source": "capture3x/learning-chapters.png",
         "action": "A map of the nine chapters",
         "cam": [cam(33.4, 179, 330, 2.4)],
         "callouts": [{"type": "underline", "rect": {"x": 20, "y": 57.1, "w": 318, "h": 33.5}, "t": 33.9, "dur": 0.3, "color": "celadon"}],
         "beats": {"map": 33.9},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "who made the shelf"}},
        {"id": "s12-about", "start": 35.0, "kind": "ui", "img": "about",
         "source": "capture3x/about-contact.png",
         "action": "The real profile area and @dawas_tech (photo is static, never animated)",
         "cam": [cam(35.0, 200, 400, 2.4), cam(37.9, 200, 410, 2.5)],
         "callouts": [{"type": "ring", "box": "about-contact.insta", "t": 35.8, "dur": 0.35, "color": "celadon"}],
         "beats": {"insta": 35.8},
         "transitionOut": {"type": "fade", "dur": 0.5, "why": "from the real profile to the curator's own line"}},
        {"id": "s13-creator", "start": 38.0, "kind": "creator", "creator": BRAND["creator"],
         "source": "Native paper surface",
         "action": "Identity line محمد دوّاس / Mohammad Dawas",
         "beats": {"name": 38.15},
         "transitionOut": {"type": "rise", "dur": 0.6, "why": "the purpose line resolves into the one action"}},
        {"id": "s14-cta", "start": 40.0, "kind": "cta", "cta": CTA,
         "source": "Native end card",
         "action": "Wordmark, creator, one CTA, public URL; stable hold from 43 s",
         "beats": {"wordmark": 40.0, "line": 40.6, "url": 41.2, "hold": 43.0}},
    ]
    texts = [
        {"id": "hook", "role": "hook", "type": "arabic", "text": "مصادر كثيرة… وين البداية؟",
         "from": 0.0, "to": 3.9, "px": 88, "weight": 700, "y": 330, "box": [90, 245, 900, 120]},
        {"id": "url-early", "role": "cta", "type": "tag", "text": BRAND["publicUrl"],
         "from": 0.5, "to": 2.6, "px": 48, "y": 1450, "box": [290, 1405, 500, 90]},
        {"id": "wordmark-capture", "role": "brand", "draw": False, "text": "Dawas Shlef.", "from": 4.8, "to": 6.6,
         "note": "the real wordmark inside the home capture"},
        {"id": "cta-wordmark", "role": "brand", "draw": False, "text": "Dawas Shlef.", "from": 40.0, "to": 45.0, "px": 150},
        {"id": "cta-url", "role": "cta", "draw": False, "text": BRAND["publicUrl"], "from": 41.2, "to": 45.0, "px": 66, "box": [190, 1228, 700, 120]},
        {"id": "cta-line", "role": "line", "draw": False, "text": CTA["line"], "from": 40.6, "to": 45.0, "px": 80},
    ]
    caps = [
        caption("c-brand", "مكتبة مصادر بتساعدك\nتبلّش بالذكاء الاصطناعي", 6.8, 8.9),
        caption("c-lib", "مواقع، مهارات،\nبرومبتات، وخطوات شغل", 9.6, 13.3),
        caption("c-search", "ابحث • فلتر • اكتشف", 13.5, 15.8),
        caption("c-detail", "افهم شو بفيدك، وشوف مصدره", 16.4, 18.9),
        caption("c-copy", "النص جاهز تنسخه وتعدّله", 19.4, 21.65),
        caption("c-save", "واللي بعجبك، احفظه في My shelf", 21.85, 25.9),
        caption("c-shelf", "محفوظ على نفس المتصفح", 26.4, 28.9),
        caption("c-learn", "وبقسم Learning،\nدليل عملي لهندسة الأوامر", 29.4, 32.0),
        caption("c-sources", "مع روابط للدروس الأصلية", 32.3, 34.9),
        caption("c-about", "جمعها محمد دوّاس، والفكرة بسيطة", 35.1, 37.75),
        caption("c-purpose", "تشتّت أقل، وفائدة أوضح", 37.95, 40.2),
    ]
    brief = [
        ("0.00-2.00", "F0-F59", "s01-scatter"), ("2.00-4.00", "F60-F119", "s01-scatter / s02-home"),
        ("4.00-6.00", "F120-F179", "s02-home (wordmark)"), ("6.00-9.00", "F180-F269", "s02-home (proposition)"),
        ("9.00-12.00", "F270-F359", "s03-library (search)"), ("12.00-16.00", "F360-F479", "s03-library (filter) / s03b-result"),
        ("16.00-19.00", "F480-F569", "s04-detail / s05-source"), ("19.00-23.00", "F570-F689", "s06-prompt / s07-skill"),
        ("23.00-26.00", "F690-F779", "s08-save"), ("26.00-29.00", "F780-F869", "s09-shelf"),
        ("29.00-32.00", "F870-F959", "s10-learning"), ("32.00-35.00", "F960-F1049", "s10-learning (toc) / s11-chapters"),
        ("35.00-38.00", "F1050-F1139", "s12-about"), ("38.00-40.00", "F1140-F1199", "s13-creator"),
        ("40.00-43.00", "F1200-F1289", "s14-cta"), ("43.00-45.00", "F1290-F1349", "s14-cta (stable hold)"),
    ]
    return {
        "meta": meta("Dawas Shlef - 45 s reel", "reel-final-v1", dur,
                     "Approved animatic picture; VO and sound fitted to it."),
        "palette": PALETTE, "brand": BRAND, "assets": ASSETS, "scenes": finish(sc, dur),
        "hero": {"t": 24.15, "what": "Save becomes Saved to my shelf (real captured state)"},
        "reads": [
            {"what": "hook over scattered tabs", "from": 0.0, "to": 2.0},
            {"what": "real wordmark", "from": 4.8, "to": 5.9},
            {"what": "Good tools. Clearer thinking.", "from": 6.6, "to": 9.0},
            {"what": "Design search + Websites filter", "from": 9.7, "to": 12.9},
            {"what": "Noiced result", "from": 13.6, "to": 16.0},
            {"what": "source credit + Visit website", "from": 18.0, "to": 19.0},
            {"what": "Copied feedback", "from": 20.05, "to": 21.3},
            {"what": "Saved to my shelf", "from": 24.15, "to": 24.9},
            {"what": "1 resource on your shelf", "from": 26.95, "to": 29.0},
            {"what": "A map of the nine chapters", "from": 33.9, "to": 35.0},
            {"what": "@dawas_tech", "from": 35.8, "to": 38.0},
            {"what": "public URL", "from": 41.5, "to": 45.0},
        ],
        "texts": texts, "captions": caps, "terms": ["Dawas Shlef"],
        "vo": vo_lines("reel"),
        "silences": [{"from": 23.6, "to": 24.12, "why": "pause before the save click"}],
        "sfx": [
            {"t": 20.05, "kind": "tick", "why": "real Copied state"},
            {"t": 24.15, "kind": "hit", "why": "hero: Saved to my shelf"},
            {"t": 26.95, "kind": "tick", "why": "shelf count"},
            {"t": 41.3, "kind": "chime", "why": "public URL lands"},
        ],
        "cuts": [],
        "briefSchedule": [{"seconds": a, "frames": b, "scenes": c} for a, b, c in brief],
    }


# ---------------------------------------------------------------- 15 s ad
def ad():
    dur = 15.0
    sc = [
        {"id": "a01-cards", "start": 0.0, "kind": "scatter", "variant": "cards", "cards": CARDS, "alignAt": 1.9,
         "source": "Real site preview images on native paper cards (approved opening test)",
         "action": "Hook over three resource cards; cards align at 2.0 s with the wordmark and public URL",
         "beats": {"settled": 0.75, "align": 1.9, "wordmark": 2.8},
         "transitionOut": {"type": "rise", "dur": 0.6, "why": "the organised column becomes the real library it stands for"}},
        {"id": "a02-search", "start": 3.9, "kind": "ui", "img": "library",
         "source": "capture3x/library-search.png",
         "action": "Real Design search and Websites filter",
         "cam": [cam(3.9, 270, 480, 1.76, 540, 1060), cam(4.25, 270, 480, 1.76, 540, 1060), full(4.75)],
         "callouts": [
             {"type": "underline", "rect": {"x": 64, "y": 40, "w": 43, "h": 30}, "t": 4.8, "dur": 0.3, "color": "celadon"},
             {"type": "ring", "box": "library-search.websites", "t": 5.25, "dur": 0.3, "color": "celadon"}],
         "beats": {"query": 4.8, "filter": 5.25},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "open a prompt from the library"}},
        {"id": "a03-prompt", "start": 5.9, "kind": "ui", "img": "prompt",
         "source": "capture3x/prompt-copy.png -> capture3x/prompt-copied.png (real click)",
         "action": "Copy prompt ring, then the real Copied state",
         "cam": [full(5.9)],
         "swaps": [{"t": 6.75, "img": "promptCopied"}],
         "callouts": [{"type": "ring", "box": "prompt-copy.copy", "t": 6.4, "dur": 0.35, "color": "cinnabar", "pulseAt": 6.75}],
         "beats": {"ring": 6.4, "copied": 6.75},
         "transitionOut": {"type": "push-left", "dur": 0.5, "why": "keep a resource for later"}},
        {"id": "a04-save", "start": 8.0, "kind": "ui", "img": "detail",
         "source": "capture3x/detail-top.png -> capture3x/detail-saved.png (real click)",
         "action": "Save close-up, real Saved state, pull out to the header count",
         "cam": [cam(8.0, 190, 370, 2.3), cam(9.6, 190, 370, 2.3), full(10.1)],
         "swaps": [{"t": 8.85, "img": "detailSaved"}],
         "callouts": [
             {"type": "ring", "box": "detail-top.save", "t": 8.5, "dur": 0.35, "color": "cinnabar", "pulseAt": 8.85, "until": 9.45},
             {"type": "underline", "box": "detail-saved.myshelf", "t": 10.15, "dur": 0.3, "color": "celadon"}],
         "beats": {"ring": 8.5, "saved": 8.85},
         "transitionOut": {"type": "push-up", "dur": 0.45, "why": "where the saved item goes: My shelf"}},
        {"id": "a05-shelf", "start": 10.4, "kind": "ui", "img": "shelf",
         "source": "capture3x/shelf-saved-4x.png (4x, so the count holds at z 4 without upscaling)",
         "action": "1 resource on your shelf",
         "cam": [full(10.4), cam(10.85, 128, 183, 4.0, 540, 700), cam(12.0, 128, 188, 4.0, 540, 700)],
         "callouts": [{"type": "underline", "box": "shelf-saved.count", "t": 11.0, "dur": 0.3, "color": "celadon"}],
         "beats": {"count": 11.0},
         "transitionOut": {"type": "fade", "dur": 0.5, "why": "from the shelf to the one place to start: the URL"}},
        {"id": "a06-cta", "start": 12.0, "kind": "cta",
         "cta": {**CTA, "line": "زور الموقع وجرّبه"},
         "source": "Native end card",
         "action": "Wordmark, creator, CTA line, overlay, public URL",
         "beats": {"wordmark": 12.0, "url": 13.2}},
    ]
    texts = [
        {"id": "hook", "role": "hook", "type": "arabic", "text": "ضايع بين أدوات AI؟",
         "from": 0.0, "to": 2.5, "px": 92, "weight": 700, "y": 360, "box": [90, 270, 900, 125]},
        # each "from" is fully legible; the 0.3 s entrance runs before it, after the hook has cleared
        {"id": "wordmark", "role": "brand", "type": "wordmark", "text": "Dawas Shlef.",
         "from": 2.8, "to": 4.4, "px": 118, "y": 322},
        {"id": "url-early", "role": "cta", "type": "tag", "text": BRAND["publicUrl"],
         "from": 2.9, "to": 4.4, "px": 48, "y": 455, "box": [290, 410, 500, 90]},
        {"id": "cta-wordmark", "role": "brand", "draw": False, "text": "Dawas Shlef.", "from": 12.0, "to": 15.0, "px": 150},
        {"id": "cta-url", "role": "cta", "draw": False, "text": BRAND["publicUrl"], "from": 13.2, "to": 15.0, "px": 66, "box": [190, 1228, 700, 120]},
    ]
    caps = [
        caption("c-what", "مواقع، مهارات، وبرومبتات بمكان واحد", 4.5, 7.9),
        caption("c-keep", "اكتشف اللي بناسبك،\nواحفظه لوقت تحتاجه", 8.3, 11.9),
    ]
    return {
        "meta": meta("Dawas Shlef - 15 s ad", "ad-final-v1", dur,
                     "Composed separately from the 45 s reel; not a speed-up."),
        "palette": PALETTE, "brand": BRAND, "assets": ASSETS, "scenes": finish(sc, dur),
        "hero": {"t": 8.85, "what": "Save becomes Saved to my shelf"},
        "reads": [
            {"what": "hook + cards", "from": 0.0, "to": 2.0},
            {"what": "wordmark + URL", "from": 2.8, "to": 4.4},
            {"what": "Design search", "from": 4.8, "to": 5.9},
            {"what": "Copied", "from": 6.75, "to": 8.0},
            {"what": "Saved to my shelf", "from": 8.85, "to": 9.6},
            {"what": "1 resource on your shelf", "from": 11.0, "to": 12.0},
            {"what": "public URL", "from": 13.2, "to": 15.0},
        ],
        "texts": texts, "captions": caps, "terms": ["Dawas Shlef"],
        "vo": vo_lines("ad15"),
        "silences": [{"from": 8.1, "to": 8.82, "why": "pause before the save click"}],
        "sfx": [
            {"t": 6.75, "kind": "tick", "why": "real Copied state"},
            {"t": 8.85, "kind": "hit", "why": "hero: Saved to my shelf"},
            {"t": 11.0, "kind": "tick", "why": "shelf count"},
            {"t": 13.2, "kind": "chime", "why": "public URL lands"},
        ],
        "cuts": [],
    }


for name, tl in (("timeline.json", reel()), ("timeline-ad15.json", ad())):
    (ROOT / name).write_text(json.dumps(tl, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", name, tl["meta"]["frames"], "frames,", len(tl["scenes"]), "scenes")
