# Motion system

Everything here is implemented in `templates/project/reel.js`, driven by `timeline.json`. Frame size is 1080×1920 at 30 fps. The register is editorial / clean UI: no motion blur, no particles. The background is paper with grain and a slow ambient fog that never sits on readable content.

## Determinism

- **Frames are a pure function of t.** Each frame is drawn from `t = i / fps`, with no timers, `Date.now()` or carried state.
- **Randomness is seeded.** Grain and torn edges come from a seeded PRNG (`mulberry32`) and are built once at load.
- **Page contract:** `window.READY` (a promise), `DUR`, `FPS`, `seek(t)` and `MEASURE()`. `MEASURE()` returns the rendered width of each caption-language line so you can check the x 90–990 safe area.
- **Re-renders are byte-identical.** Re-rendering any frame range gives the same pixels, which is what makes scoped fixes and frame diffs possible.

## Scene kinds

| kind | Draws | Key fields |
|---|---|---|
| `scatter` | Three preview cards on torn paper, plus optional abstract browser tabs. Cards stagger in, then either align into a column (`alignAt`) or gather to the centre (`gatherAt`). | `variant: cards\|tabs`, `cards[]`, `tabs[]` |
| `ui` | A real capture on a torn-paper page, framed by the camera, with callouts and real state swaps. | `img`, `cam[]`, `callouts[]`, `swaps[]` |
| `creator` | Name in the caption language, a Latin name under it, and a drawn accent stroke. | `creator {primary, secondary}` |
| `cta` | The end card. | `cta {creator, line, overlay, url}` |

Every scene has `start`, `transitionOut {type, dur, why}` (except the last), `beats`, `action` and `source`. `end` and `frames` are derived from the next scene's start.

## Camera (ui scenes)

`cam(t, cx, cy, z, fx=540, fy=960)` places capture point `(cx, cy)`, in css px, at frame point `(fx, fy)`, with `z` frame px per css px. In frame terms: `X = fx + (px − cx)·z`.

- **Keyframes ease in and out.** Two identical keys make a hold, and moving from one key to the next is a push.
- **Never upscale.** A 3x capture allows z ≤ 3. For one tiny detail you need to hold larger (such as a 10 px count), capture that page at 4x and hold at z 4.
- **`full(t)` = `cam(t, 270, 480, 2.0)`.** A 540×960 css capture fills the frame.
- **Use slow pushes instead of frozen holds.** For example, move z from 2.4 to 2.5 over 3 s, which keeps the frame alive during a read.
- **Frame for the safe area.** The read target sits inside x 90–990 and y 200–1500, and the caption band (y 1300–1500) must not cover it. Move `fy` up when a caption is showing.

## Transitions (seams)

Every seam names its reason: "next step", "same page, scrolled down", "where the saved item goes". Don't use the same move on three seams in a row.

| type | Motion | Use |
|---|---|---|
| `push-left` | Old shot exits left, new shot enters from the right (1150 px). | The next step or a deeper level. |
| `push-up` | Vertical push of 1920 px. | Scrolling the same page or results. |
| `rise` | The old shot rises and **clears before** the new one appears (no type over type). | An idea resolving into the next one. |
| `fade` | A dip to paper: out by 50%, in after 50%. **Never a double exposure.** | A change of subject, and into the end card. |
| `emerge` | The old shot shrinks and fades as the new one scales up from 0.86. | Many things collapsing into one place. |

Durations: 0.45–0.6 s. `qa_video` reports the one or two near-blank frames inside a `fade` as "flat frames". That is expected, so note it in the report.

## Text

- **`from` means fully legible.** The 0.3 s entrance (rise 18 px, ease-out) runs *before* `from`, and the fade-out takes the last 0.17 s. QA measures text at `from + 0.1`, so mid-entrance frames never fail contrast.
- **The hook is on frame 0.** It's ≥ 84 px (we used 88–92), ≥ 7:1 contrast and at most 900 px wide. `box: [x, y, w, h]` tells qa_video where to measure.
- **The public URL is drawn as a tag:** ink fill, paper text and one accent dot. It shows early, from 0.5 to 2.6 s at y 1450, and on the end card. The URL is ink because a mid-tone accent fill gave only ~5:1 contrast, and the CTA needs ≥ 7:1.
- **Wordmark:** the icon (an SVG tinted through `currentColor`) plus the Latin wordmark.

## Captions

- **Format:** at most 2 lines, split with `\n`, at 54 px, last baseline at y 1462 (band y 1300–1500).
- **Look:** a pill at 97% paper with a 2 px ink hairline at 14% opacity. Behind it, a soft paper scrim gradient sits between the pill and the page, so page text never competes with the caption.
- **Motion:** 0.3 s entrance and 0.15 s exit.
- **Timing with a voice:** a caption follows its VO line. It appears at the line's first word and stays until the next caption. Never leave the previous line's caption up while the voice speaks the next one.
- **Rate:** ≤ 3.5 words/s (check_timeline warns above that).
- **Arabic:** keep it shaped and RTL, drawn as one phrase and never per character. Some fonts, such as Dubai, drop the tatweel ("الـ AI"), so reword instead of relying on it.

## Callouts

- **`underline`:** draws left to right over 0.3 s, a slightly curved stroke in the **accent** colour, meaning "look here".
- **`ring`:** a hand-drawn ellipse that sweeps around a control. Use **action** (rings on Copy or Save, the user's own actions) or accent.
  - `pulseAt`: a 6% pulse on the real click.
  - `until`: fades out over 0.2 s before the camera pulls away, so a ring never slides out of frame.
- **Position:** `box: "<capture>.<name>"` from boxes.json, or a literal `rect` in css px.
- **Colour has one job:** action marks an action, and accent marks attention.

## State swaps

`swaps: [{t, img}]` cuts from the before capture to the real after capture at the click time (the `pulseAt` of the ring). qa_video reports a small "pop" there, which is intended. Nothing should change between captures except the real UI.

## End card (cta), with stagger from scene start

| Element | Fully in at | y | Size |
|---|---|---|---|
| Wordmark | +0.45 s | 640 | 150 |
| Creator credit and drawn stroke | +0.55 s | 740 | |
| Action line | +0.6 s | 1000 | 80 px, bold |
| Three-word overlay | +0.9 s | 1112 | 58 px |
| URL tag | +1.2 s | 1288 | |

After that it holds stable until the end. The last 2–4 s are a stable hold (qa_video calls it "final hold").

## Pacing (what the critic checks)

- **Holds:** a read gets ~1–1.9 s, and nothing sits dead longer than that mid-film, which is why slow pushes and caption moves fill the gaps.
- **Information:** something new every 2–4 s.
- **The hero:** the one real state change (for example "Save" becoming "Saved") lands at 50–60% of the runtime. Give it a ring, a pulse, a real swap and, once there's sound, the loudest non-voice hit after a planned silence.
- **The CTA line:** one action. No "link in the description" on Reels, which have none. Use "visit the site" or show the URL.
