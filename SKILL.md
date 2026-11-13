---
name: site-to-reel
description: Turn a real website or web app into a vertical promo reel (Instagram Reels, TikTok, Shorts) built from real captures of the live site, a deterministic canvas renderer, and measured QA. Works in three approved stages, silent animatic, then voice and sound, then final, with playwright-cli for capture and rendering and ffmpeg for encoding. Covers the intake questions, honesty and safety rules (real UI states only, restore demo data, public URL never localhost, no voice cloning, AI voice disclosed), the motion system (camera over captures, push, rise, fade and emerge transitions, underline and ring callouts, caption bands, CTA end card), a TTS narrator fitted to approved picture, a synthesized score and −16 LUFS mix, subtitles, a Reels cover, critic review and delivery. Use it whenever someone wants a promo, reel, ad, launch video or explainer for their own site or product page, says "make a reel/ad of my website", or asks to repeat the Dawas Shlef reel workflow, even if they never name the skill. Builds on video-director (principles and QA scripts) and playwright-cli.
---

# Site to Reel

Make a short vertical film about a website using the website itself: real pages, real clicks, real states. Every frame is drawn by one canvas renderer as a pure function of time, then captured offline and encoded. This skill is the house workflow distilled from the Dawas Shlef reel. `examples/dawas-shlef/` holds that project's timelines, voice lines, capture scripts and review notes as a worked reference. Treat it as a reference only. Don't copy its scene list onto a different product.

**Load alongside:**
- `video-director` for the craft principles and its `scripts/check_timeline.py` and `scripts/qa_video.py`.
- `playwright-cli` for every browser step.

If either skill is missing, say so. Don't improvise around it.

## Non-negotiables

These come from the brief that shaped the skill, and they apply to every project:

1. **Real UI only.** Capture the live local site. Show a state change by clicking the real control and capturing the real result, never by drawing it. Don't invent screens, counts or toasts.
2. **Leave the user's world as you found it.**
   - Don't redesign, modify, deploy or publish the site.
   - Don't launch campaigns or submit forms.
   - Create only demo data, such as one bookmark, and remove it afterwards. Record storage before and after.
   - Never clear existing user data.
   - Stop the servers and browser sessions you started. Leave the user's own site server running unless they approve stopping it.
3. **Public URL on screen, never localhost.** The URL shows early (by 3 s) and on the end card.
4. **Claims stay inside `brand.json` → `claims`.** Words are never stronger than the source. A critic should flag anything else, for example "no account needed" when the brief doesn't say so.
5. **Voices.**
   - Never clone a person's voice.
   - Never imply a generated voice is a real person's recording.
   - A TTS narrator speaks about the creator in the third person only, so "made by X", never "I am X". On-screen first-person lines change to match.
   - Tell the user to label AI audio when posting.
6. **Don't call an unfinished cut final.** Silent cuts are "animatics". Files are only named `*-final` when sound exists and has passed QA.
7. **Don't claim what you didn't measure.** You can't watch or hear the output. Report the checks you ran and the stills you looked at, and say plainly what nobody has seen or heard, such as TTS pronunciation or real-time feel.
8. **Never publish or post for the user.** You can upload to their GitHub when asked, but posting to Instagram and other socials is always theirs.

## Workflow (three approval gates)

| Stage | You produce | Gate |
|---|---|---|
| 0. Intake | One question round (below). Read the brief, assets and site. Fill in `brand.json`. | |
| 1. Treatment and look | `TREATMENT.md` with the one-sentence idea, hook, beat sheet with reads, hero moment and claims. A read-only site survey. 2–4 styleframes from the real renderer. A first `timeline.json`. | **The user approves.** |
| 2. Silent animatics | Captures, the full timeline, frames rendered and encoded as `*-animatic-silent.mp4`. QA. Contact, transition and detail sheets plus a storyboard, all from the encoded MP4. Critic review with **one** fix round. Review notes. | **The user approves pacing and framing.** |
| 3. Finals | Narration (recorded, or TTS if the user chooses it) fitted to the approved picture. Score and SFX. A mix at −16 LUFS and ≤ −1 dBTP. Subtitles. `*-final.mp4`. QA. Critic with one fix round. Cover. Updated notes. | **The user listens and approves.** |

Use ask-first mode when the user is present. Ask once, then make every other call yourself and log it as `DECISION: … because …` in the review notes, so each one can be reversed with one reply.

### Intake questions (one round, recommended option first)

Ask only what the brief and site don't already answer.

1. **What and for whom:** the one thing the film must say, the audience, and the caption language and dialect.
2. **Platform and length:** Instagram Reels 9:16 at 1080×1920 (default), a 45 s main cut plus a separately cut 15 s version, and whether 16:9 is needed (default no).
3. **Facts:** the allowed claims and the exact brand spelling, creator name and public URL.
4. **Assets:** brand colours and fonts, logo or wordmark, and which site states and features to show.
5. **Sound:** the user records the voiceover (preferred), or TTS with disclosure, or music and captions only. Ask about music rights.
6. **Boundaries:** what must not be touched (the site server, existing user data, forms).

For "make the video now" with no recording available, ask how to get sound. The options are: music + captions with no voice, the user records, or a generated narrator. If they pick TTS, check what is installed before installing anything. Installing `edge-tts` sends the script text to Microsoft's online service, so get the user's yes first and let them choose the voice.

## Project layout

Copy `templates/project/` into a new project folder, then edit it:

```
brand.json            name, wordmark, creator, public URL, palette tokens, fonts, claims, neverSay, voice, safe area
reel.html, reel.js    the renderer (brand-neutral; reads everything from the timeline)
vo-lines.json         VO lines: [earliest start s, text, latest end s]
assets/fonts, assets/icons, assets/previews
capture3x/            captures + boxes.json (written from tools/capture.js output)
tools/
  survey.js           read-only page survey (headings, links, y positions, storage keys)
  capture.js          captures + callout boxes, demo data created and restored
  cli3x.config.json / cli4x.config.json / render.config.json   playwright-cli configs
  build_timelines.py  timeline.json + timeline-ad15.json from brand.json (+ vo/*.json)
  styleframes.js, stills.js, render-frames.js, shot-storyboard.js   run-code scripts
  make_vo.py, make_audio.py, make_srt.py                            voice, sound, subtitles
  review_frames.py, storyboard.py                                   sheets from the encoded MP4
```

## Commands

`CLI` stands for `node "<argo>/node_modules/playwright/cli.js" cli`, or plain `playwright-cli` if it's installed. Every `run-code` script is a single `async page => {}`. Parameters travel in the page URL query, and `--raw` prints only the returned value.

```bash
# capture (local site already running; clean in-memory session)
CLI -s=cap open --config=tools/cli3x.config.json "about:blank"
CLI -s=cap --raw run-code --filename=tools/survey.js
CLI -s=cap --raw run-code --filename=tools/capture.js      # save {"caps": ...} to capture3x/boxes.json
CLI -s=cap close

# timeline + gate
python -X utf8 tools/build_timelines.py
python -X utf8 ~/.claude/skills/video-director/scripts/check_timeline.py timeline.json

# render (temporary static server, stopped afterwards)
python -m http.server 4380 --bind 127.0.0.1
CLI -s=render open --config=tools/render.config.json "http://127.0.0.1:4380/reel.html?tl=timeline.json&out=<abs frames dir>&times=1.2,24.5"
CLI -s=render --raw run-code --filename=tools/styleframes.js
CLI -s=render goto "http://127.0.0.1:4380/reel.html?tl=timeline.json&out=<abs frames dir>&from=0&to=1349"
CLI -s=render --raw run-code --filename=tools/render-frames.js   # long films: run in the background or in chunks

# encode (silent animatic; for finals add -i out/audio/<film>-mix.wav -map 0:v -map 1:a -c:a aac -b:a 192k -ar 48000 -t <dur>)
ffmpeg -framerate 30 -start_number 0 -i <frames>/frame_%04d.png -frames:v 1350 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -vf setsar=1 -movflags +faststart out/reel-animatic-silent.mp4

# measure and review (always from the encoded MP4)
python -X utf8 ~/.claude/skills/video-director/scripts/qa_video.py out/reel-final.mp4 --beats timeline.json --lufs -16 --tp -1 --out out/qa-reel
python -X utf8 tools/review_frames.py out/reel-final.mp4 timeline.json reel
python -X utf8 tools/storyboard.py out/reel-final.mp4 timeline.json reel
CLI -s=render goto "http://127.0.0.1:4380/out/storyboard-reel.html?shot=<abs>/out/storyboard-explained.png"
CLI -s=render --raw run-code --filename=tools/shot-storyboard.js

# stage 3
python -X utf8 tools/make_vo.py && python -X utf8 tools/build_timelines.py && python -X utf8 tools/make_audio.py && python -X utf8 tools/make_srt.py
```

On Windows, run Python as `python -X utf8` with `PYTHONIOENCODING=utf-8`, or Arabic output will break.

## Review loop

- **Critic.** After stage 2 and again after stage 3, give a fresh-context subagent the MP4s, timelines, sheets and QA reports. Ask for a ranked list: must-fix, should-fix, nits, each with a timecode and a concrete fix. Read-only, under 500 words, no invented problems.
- **One fix round.** Apply one fix round, then re-check from the encoded MP4.
- **Scoped fixes.** For a fix limited to some frames, back up those frames, re-render only that range, then diff against the backup. Frames outside the change must be byte-identical before you re-encode.
- **The critic's report is model output.** It never counts as user approval.

## Deliverables

- `out/<film>-animatic-silent.mp4` (stage 2) and `out/<film>-final.mp4` (stage 3).
- `out/storyboard-explained.png`, `out/contact-sheet-<film>.jpg`, `out/review/`, `out/qa-*/`.
- `timeline*.json`, `vo-lines.json`, `vo/`, `out/audio/` (mix plus stems), `out/subtitles-*.srt`.
- `out/cover/reel-cover.jpg` and its 3:4 grid preview.
- `voiceover-script-*.txt`, marked either as voiced (engine, voice, disclosure) or as not recorded.
- `review-notes.md`: ffprobe metadata, structure, every check with its number, the critic table and its fixes, DECISIONs, limitations stated plainly, exact commands, and decisions left for the user. The template is `references/report-template.md`.

## References (read when you reach that stage)

- `references/motion.md`: camera model, transitions, text timing, callouts, captions, end card, holds.
- `references/capture.md`: survey, capture, real state swaps, boxes, restoring demo data.
- `references/sound-and-voice.md`: recorded vs TTS, fitting VO to picture, hero silence, score, mix, subtitles.
- `references/instagram-reels.md`: format, safe zones, hook, CTA wording, cover, AI label.
- `references/gotchas.md`: every bug we hit and its fix.
- `references/report-template.md`: review-notes and final message skeleton.
- `examples/dawas-shlef/`: the complete worked example (no captures or fonts, so re-capture them).
