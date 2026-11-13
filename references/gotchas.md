# Gotchas we hit (and the fix)

**Tooling**
- **The user didn't want custom Node Playwright scripts.** Every browser step uses playwright-cli: `open --config`, `run-code --filename` with a single `async page => {}`, and parameters passed in the page URL query.
- **One playwright-cli session is shared across scripts.** A script that changes the viewport (the storyboard's 1800 px full-page shot) left later renders distorted. The fix was to restore 1080×1920 at the end of the script.
- **Literal `\n` became real newlines.** `sed` and unquoted heredocs turned `"\n"` in Python strings into real line breaks, which broke the code. Use Edit, or a quoted heredoc (`<<'EOF'`).
- **Windows needs UTF-8 for Python.** Without `python -X utf8` and `PYTHONIOENCODING=utf-8`, Arabic output crashes or turns to mojibake.
- **`ffmpeg -ss` missed the last frame.** Pull exact frames with `-vf "select=eq(n\,N)" -fps_mode passthrough -frames:v 1`.
- **Mixed renderer versions.** A render was running while fixes landed. Stop the in-progress render (TaskStop), apply all the fixes, then re-render.
- **The skill's script path.** check_timeline and qa_video live in `~/.claude/skills/video-director/scripts/`.

**Picture**
- **Hook and caption overflow.** Text was wider than 900 px, so the hook became 88 px, captions 54 px, and long captions are split onto two lines. `MEASURE()` checks the widths.
- **Captions over page text were unreadable.** The fix was a paper scrim behind a hairline pill.
- **Transitions ghosted text.** `rise` showed the old type over the new, and `fade` made a double exposure. Now the outgoing shot clears first and fade dips to paper.
- **qa_video failed CTA contrast (2.4:1).** It measured mid-entrance. The fix: "from" now means fully legible, with the entrance before it, and the URL tag became ink because deep accent was only ~5:1.
- **A callout box was missing because a `sed` pattern silently didn't match.** Grep after every scripted edit.
- **Ring outside the safe area at the hero.** The fix was to reframe and fade the ring out (`until`) before the pull-out.
- **The camera showed one item and opened another.** We recaptured the same search scrolled to the real item.
- **A 10 px count was unreadable.** The fix was a 4x capture held at z 4.
- **Frozen holds.** Slow pushes and caption moves fixed them. The longest hold mid-film is now about 1.9 s.
- **Dubai drops the tatweel** ("الـ AI", "بـ My shelf"), so reword.
- **Ad CTA said "link in the description".** Reels have none, so it became "visit the site".

**Sound**
- **No Arabic voice was installed locally**, only English SAPI voices. We asked, installed edge-tts and let the user choose Taim.
- **First TTS fit was 46 s of speech for a 45 s film.** Fixes: shorter lines, rate +8%, placing the first word instead of the file start, and sequential placement with 0.15 s gaps.
- **The planned silence failed at −24.7 dBFS.** The smoothed music gate crept in, so the gate now stays closed until 0.35 s after the silence ends.
- **The critic found the VO saying "save it" while the copy caption was still up.** The fix was to retime the captions to the voice.
- **The VO said "بدون حساب" (no account), which the brief doesn't support.** We cut it. Check every spoken line against `claims`.
- **The URL chime was buried under the CTA's first word.** We moved the chime and delayed the line.
- **A generated voice said "أنا محمد دوّاس".** Never do that. It became "جمعها محمد دوّاس", and the caption was changed too.

**Process**
- **Never report from memory.** ffprobe, QA numbers and stills come from the encoded files every time.
- **Temporary servers.** The static server on 4380 is started for rendering and stopped afterwards, with the user's site on 4321 left running. Check both with curl at the end.
- **The critic is model output.** Its notes aren't user approval, and it gets one fix round, not endless loops.
