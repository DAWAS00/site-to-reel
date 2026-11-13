# Dawas Shlef reel: review notes

Status: **stage 3 is done, and `out/reel-final.mp4` and `out/ad-final-15s.mp4` now exist.** The narrator is an **AI-generated voice**, not Mohammad. The stage 3 section at the end covers it. The stage 2 notes below describe the approved silent animatics and still apply to the picture.

Output folder: `E:\New Video ai\dawas-shlef-reel-production`

## Deliverables

| File | What it is |
|---|---|
| `out/reel-animatic-silent.mp4` | 45 s vertical animatic, 1080×1920, 30 fps, F0–F1349 (1350 frames), H.264 yuv420p, SAR 1:1, faststart, no audio |
| `out/ad-animatic-silent-15s.mp4` | 15 s ad cutdown, composed separately (not a speed-up), F0–F449 (450 frames), same encode |
| `out/storyboard-explained.png` | One panel per scene: frame from the encoded reel, seconds and frames, draft VO phrase, on-screen caption, motion, transition and why |
| `out/contact-sheet-rendered.jpg` | Reel every 2 s plus the last frame, pulled from the encoded MP4 |
| `out/contact-sheet-rendered-ad15.jpg` | Ad every 1 s plus the last frame |
| `out/review/reel/` and `out/review/ad15/` | `transitions/` (before / mid / after every seam), `details/` (search, filter, result, detail, source, copy, save, saved, My shelf, Learning, chapters, About, creator, CTA), and a sheet for each |
| `out/qa-reel/`, `out/qa-ad15/` | qa_video.py report plus beats, phone (360 px) and hook sheets, made from the MP4s |
| `timeline.json`, `timeline-ad15.json` | The single source per film: scenes with inclusive frame ranges, cameras, callouts, real state swaps, texts, captions, reads, the brief's 16-row schedule |
| `voiceover-script-ar.txt` | Draft Jordanian Arabic script, labelled unrecorded |
| `reel.html`, `reel.js` | Deterministic data-driven canvas renderer: `?tl=` selects the timeline, `seek(t)` draws any frame, seeded PRNG, no clocks |
| `tools/` | playwright-cli configs and run-code scripts (capture, render, stills, storyboard), the timeline builder, review-frame and storyboard scripts |
| Stage 1 (unchanged) | `out/opening-test-8s-silent.mp4`, three styleframes, `reel-opening-test.*`, `timeline-opening-test.json` |

## Metadata (ffprobe on the encoded files, `-count_frames`)

- Reel: `h264 1080x1920 yuv420p r_frame_rate 30/1 SAR 1:1 nb_read_frames 1350 duration 45.000000 nb_streams 1`
- Ad: `h264 1080x1920 yuv420p r_frame_rate 30/1 SAR 1:1 nb_read_frames 450 duration 15.000000 nb_streams 1`

Both frame counts match duration × 30. Each file has one stream (video) and no audio.

## Structure

**Reel, 15 scenes:**
- Hook over abstract tabs and three real resource cards.
- Real homepage, wordmark, then "Good tools. Clearer thinking."
- Design search with the Websites filter.
- Scroll to the Phosphor Icons result, then open it.
- Purpose, then source credit and Visit website.
- Copy prompt shows the real "Copied" state. The skill shows its Copy SKILL.md control, not clicked.
- Save shows the real "Saved to my shelf" state. **This is the hero, at 24.15 s.**
- My shelf shows "1 resource on your shelf".
- Learning guide, then Original tutorial, then the chapter map.
- About with @dawas_tech.
- محمد دوّاس / Mohammad Dawas.
- End card: wordmark, "Collected by Mohammad Dawas", the CTA, the public URL. Stable hold from 43 s.

**Ad, 6 scenes:**
- Hook over cards.
- Cards align under the wordmark and URL by 2.9 s.
- Search, then copy, then save (the hero, at 8.85 s), then shelf.
- End card.

**Every UI frame is a real capture** of the local site, taken with playwright-cli in a clean in-memory session at 3× (My shelf at 4×). The camera never goes past 1:1 of a capture, so nothing is upscaled.

The demo bookmark was created twice, once in the 3× pass and once in the 4× shelf pass. Both times it was removed, and storage was verified `[]` before and after. Your own browser profile was never touched, and the site server on 4321 was never stopped or changed.

## Checks

**check_timeline:** both films have 0 errors and 1 warning. The warning is "no planned silence before the hero", which is expected in a silent animatic. Sound is designed once narration exists.

**qa_video on the reel MP4:**
- PASS: frame 0.
- PASS: hook at 105.6 px, contrast 12.6:1.
- PASS: early URL at 0.6 s and end URL at 41.3 s, both ≥ 48 px and 12.7:1 or better.
- PASS: no single-frame flashes.
- WARN: one pop at 20.07 s. This is the real Copied swap.
- WARN: frozen stretches. After the fix round these are read holds of 1.0–1.9 s plus the 4 s end hold. Before the fix round there were six holds of 2.2–2.5 s.
- WARN: near-blank frames at about 38.3 s and 40.3 s. These are the designed dip-to-paper (fade) and the clear-before-enter (rise). Each lasts 1–2 frames.
- "Detected cuts" are the whole-frame pushes, not hard cuts.

**qa_video on the ad MP4:**
- PASS: frame 0.
- PASS: hook at 141.7 px, 12.5:1.
- PASS: URL at 3.0 s and 13.3 s, both 12.7:1 or better.
- PASS: no flashes.
- WARN: pop at 6.77 s. This is the real Copied swap.
- WARN: frozen read holds of 1.1–1.4 s, and the final 2 s hold.
- WARN: blank dip at 12.23 s, which is the fade.

**Arabic widths**, measured in the renderer (`MEASURE()`), are all 900 px or less including the caption pill. Two captions in the reel and one in the ad are set on two lines (the brief allows at most 2). Arabic is always drawn as a whole shaped RTL phrase, never letter by letter.

## Independent review and the one fix round

A clean-context critic reviewed only the MP4-derived sheets, the QA reports, the timelines and the brief. Its ranked notes and what I changed:

| # | Critic note | Fix |
|---|---|---|
| 1 must | Save hero breaks the safe area (ring at x≈0) | Close-up reframed (cx 190, z 2.3): ring now inside x 90–990. The ring fades out before the pull-out to the full page |
| 2 must | Push into "Noiced", then land on Phosphor Icons | New capture `library-phosphor.png` (same search, scrolled to the real Phosphor Icons result). New scene s03b underlines that title and opens it |
| 3 must | Caption over the half-drawn "Clearer thinking" at 4.3–6.5 s | Brand caption moved onto the settled hero hold (6.8–8.9 s). The wordmark close-up has no caption |
| 4 should | Tatweel joins ("الـ AI", "بـ My shelf") render detached in Dubai | Reworded: ad hook "ضايع بين أدوات AI؟", caption "…تبلّش بالذكاء الاصطناعي", "احفظه في My shelf" |
| 5 should | "1 resource on your shelf" unreadable on a phone | My shelf recaptured at 4×. Camera holds the count at z 4, about 40 px on the canvas, with no upscaling |
| 6 should | Learning and chapters are walls of small text | Slow push on the guide title, 1:1 close-up on "Original tutorial", chapter map framed at z 2.4 on the heading and first rows |
| 7 should | Ad CTA "من الرابط بالوصف" points to a description link that a reel doesn't have | Ad CTA line is now "افتح الرابط وجرّبه", matching the URL on screen |
| 8 should | Too many frozen holds | Slow pushes added to the library, shelf, Learning and About holds, and the brand caption now fills the hero hold. I didn't shorten anything: holds sized for narration stay until a real take sets the pace |
| 9 nit | About text cropped at x≈0 | Reframed (cx 200): text now starts inside x 90, with a slow push |
| 10 nit | "Contribute" visible in the nav; loud preview colours | Not changed. Contribute is the real nav label and is never shown as a flow. The previews are the real site's images |

Every finding was a picture or timing fix, not a change of facts. No claim, brand spelling or URL was flagged.

## Other decisions I made (each is one reply to reverse)

- **URL tag colour:** The URL tag is ink #23282a with a celadon dot. The approved styleframe used deep celadon, but paper on deep celadon measured about 5:1, below the 7:1 CTA floor. Paper on ink measured 12.7–12.9:1.
- **Text timing:** A text's "from" time now means the moment it's fully legible. Its 0.3 s entrance runs just before that, so the QA reads full-opacity text at the cue.
- **Ad retiming:** The ad's opening was retimed so the wordmark never double-exposes over the hook. The hook clears at 2.5 s, the wordmark is fully in at 2.8 s and the URL at 2.9 s. The prompt scene lost 0.3 s to make room.
- **Transitions:** Fade is a dip to paper and rise clears before it enters. Neither double-exposes type.
- **Caption legibility:** Captions get a soft paper scrim and a hairline pill, so page text behind them never competes.

## Limitations, stated plainly

- **Not watched in real time.** I checked stills, sheets and measurements. Motion feel needs your playback. **No audio exists**, and none was generated, cloned or implied.
- **Captions are draft phrase cues, not subtitles.** They follow the unrecorded script and aren't aligned to any voice. Once a narration is recorded, measure it, re-time the timeline to the take and write `subtitles.srt`. Only then make the `*-final` files.
- **Opening cards:** The 0–2.6 s cards and tabs are a composed layer (real preview images on drawn paper). They aren't the site's card component.
- **Edge-of-frame elements:** At full-page framing the real UI runs edge to edge, so nav items and the left margin sit outside x 90–990. Close-ups keep marks inside the safe area.
- **16:9 version:** Not made. It's optional and comes after the vertical is approved.

## Exact commands

```bash
# 1. capture (read-only, clean in-memory session; local site already running on 4321)
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=cap open --config=tools/cli3x.config.json "about:blank"
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=cap --raw run-code --filename=tools/capture3x.js
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=cap --raw run-code --filename=tools/capture-library-phosphor.js
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=cap close
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=cap4 open --config=tools/cli4x.config.json "about:blank"
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=cap4 --raw run-code --filename=tools/capture-shelf4x.js
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=cap4 close

# 2. timelines (+ gate)
python -X utf8 tools/build_timelines.py
python -X utf8 C:/Users/dawas/.claude/skills/video-director/scripts/check_timeline.py timeline.json
python -X utf8 C:/Users/dawas/.claude/skills/video-director/scripts/check_timeline.py timeline-ad15.json

# 3. render (temporary static server, stopped afterwards); out= is any empty folder
python -m http.server 4380 --bind 127.0.0.1
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=render open --config=tools/render.config.json "http://127.0.0.1:4380/reel.html?tl=timeline.json&out=<frames-reel>&from=0&to=1349"
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=render --raw run-code --filename=tools/render-frames.js
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=render goto "http://127.0.0.1:4380/reel.html?tl=timeline-ad15.json&out=<frames-ad>"
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=render --raw run-code --filename=tools/render-frames.js
#    review stills at chosen times: reel.html?tl=...&out=...&times=0,1.2,... then run-code --filename=tools/stills.js

# 4. encode
ffmpeg -framerate 30 -start_number 0 -i <frames-reel>/frame_%04d.png -frames:v 1350 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -vf setsar=1 -movflags +faststart out/reel-animatic-silent.mp4
ffmpeg -framerate 30 -start_number 0 -i <frames-ad>/frame_%04d.png -frames:v 450 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -vf setsar=1 -movflags +faststart out/ad-animatic-silent-15s.mp4

# 5. verify and review (all from the encoded MP4s)
ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,sample_aspect_ratio,nb_read_frames:format=duration,nb_streams out/reel-animatic-silent.mp4
python -X utf8 C:/Users/dawas/.claude/skills/video-director/scripts/qa_video.py out/reel-animatic-silent.mp4 --out out/qa-reel --beats timeline.json
python -X utf8 C:/Users/dawas/.claude/skills/video-director/scripts/qa_video.py out/ad-animatic-silent-15s.mp4 --out out/qa-ad15 --beats timeline-ad15.json
python -X utf8 tools/review_frames.py out/reel-animatic-silent.mp4 timeline.json reel
python -X utf8 tools/review_frames.py out/ad-animatic-silent-15s.mp4 timeline-ad15.json ad15
python -X utf8 tools/storyboard.py
node "E:/New Video ai/argo/node_modules/playwright/cli.js" cli -s=render --raw run-code --filename=tools/shot-storyboard.js
```

## Decisions for you

1. Approve the vertical animatics' pacing and framing, or send timecoded notes. **(Approved.)**
2. Record the narration (your own voice or a voice actor you choose; nothing is cloned). **(You chose a generated narrator. See stage 3.)**
3. Do you want the 16:9 version? **(No. The target is Instagram Reels, 9:16.)**

## Stage 3: finals for Instagram Reels (AI narrator, score, SFX, mix)

| File | ffprobe |
|---|---|
| out/reel-final.mp4 | h264 1080x1920 yuv420p 30/1 SAR 1:1, 1350 frames, 45.000 s; aac 48 kHz stereo 192k |
| out/ad-final-15s.mp4 | h264 1080x1920 yuv420p 30/1 SAR 1:1, 450 frames, 15.000 s; aac 48 kHz stereo 192k |
| out/subtitles-reel.srt, out/subtitles-ad15.srt | sidecar subtitles, the VO's exact words |
| out/audio/ | the masters `*-mix.wav` and the stems `*-stem-{vo,music,sfx}.wav` |
| out/cover/reel-cover.jpg | Reels cover (end card), plus a 3:4 grid preview |
| vo/ | the TTS clips and the measured word timings |

**Voice.** The narrator is Microsoft neural TTS `ar-JO-TaimNeural`, produced with edge-tts at rate +8%; only the script text was sent to the service. It is AI-generated and is not Mohammad. It speaks about him only in the third person ("جمعها محمد دوّاس"), and the on-screen About caption was changed to match. Word timings come from the TTS WordBoundary events, so they are measured, not estimated.

**Picture.** The picture is unchanged from the approved animatic, apart from these fixes:
- the About caption wording
- caption timings retimed to the voice
- the early URL tag raised 25 px, clear of the Reels UI
- the ad end line changed to "زور الموقع وجرّبه", because a link in an organic Reel isn't tappable

Lines were fitted to the approved shots, and none overlap.

**Sound.** All of it is generated by `tools/make_audio.py`, placed from the timeline:
- a D-major pad with one chord per scene and a pluck on alternate scene starts
- the pad ducks about 11 dB under the voice
- ticks on the real Copied and shelf-count states
- a chime when the URL lands

The save hit sits in a planned pause: reel 23.6–24.12 measures −97 dBFS, ad 8.1–8.82 measures −120 dBFS. It is the loudest moment in both films (reel 24.2 s, ad 8.9 s).

**QA (qa_video, on the encoded finals).**
- Loudness: −16.1 LUFS, true peak −1.1 dBTP, for both films.
- Hook and URL text pass for size (≥ 84 / 48 px) and contrast (about 12.5–12.9:1).
- No flashes.
- The remaining WARNs are the same as in stage 2: the Copied-swap pop, read holds of 1–1.9 s, dip-to-paper frames, and the final hold.
- check_timeline reports 0 errors. Its one WARN, "Dawas Shlef shown but never said", is expected because it's spoken in Arabic as "دوّاس شِلف".

**Critic round: what was fixed.**
1. "احفظه" was spoken under the copy caption; the captions now follow the voice.
2. "بدون حساب" was cut, because nothing supports that claim.
3. The URL chime moved off the CTA line.
4. The VO hook now matches the on-screen hook.
5. The shelf line was re-voiced as a full sentence ("بينحفظ على My shelf").
6. The purpose line was tightened and its caption extended.
7. "وخطوات شغل" was added to the VO.
8. "ابحث، فلتر، واكتشف" now matches its caption.
9. The URL tag was raised.
10. "تشتّت أقل" replaced "مصادر أقل تشتّت".
11. The ad CTA is now "زور الموقع".

**Not verified.**
- Nobody has listened to the audio. TTS pronunciation of "دوّاس شِلف", "My shelf", "Learning" and "AI" is unchecked by ear. If any is mangled, respell it in `tools/make_vo.py`, for example "ماي شِلف", and re-run.
- Real-time playback on a phone hasn't been checked.

**Posting (yours to do; nothing was uploaded).** Instagram asks you to label realistic AI-generated audio, so mark the post as containing an AI voice, or say so in the caption (for example "التعليق الصوتي مولّد بالذكاء الاصطناعي").

```bash
python -X utf8 tools/make_vo.py          # TTS clips + word timings (needs: pip install edge-tts; online)
python -X utf8 tools/build_timelines.py  # timelines with vo / silences / sfx
python -X utf8 tools/make_audio.py       # score, SFX, mix, -16 LUFS master
python -X utf8 tools/make_srt.py         # subtitles
# re-render frames as in step 3 above, then:
ffmpeg -framerate 30 -start_number 0 -i <frames-reel>/frame_%04d.png -i out/audio/reel-mix.wav -frames:v 1350 -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -vf setsar=1 -c:a aac -b:a 192k -ar 48000 -t 45 -movflags +faststart out/reel-final.mp4
ffmpeg -framerate 30 -start_number 0 -i <frames-ad>/frame_%04d.png -i out/audio/ad15-mix.wav -frames:v 450 -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -vf setsar=1 -c:a aac -b:a 192k -ar 48000 -t 15 -movflags +faststart out/ad-final-15s.mp4
python ~/.claude/skills/video-director/scripts/qa_video.py out/reel-final.mp4 --beats timeline.json --lufs -16 --tp -1 --out out/qa-reel-final
```
