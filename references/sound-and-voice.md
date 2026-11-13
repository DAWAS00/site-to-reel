# Sound and voice

## Choosing the voice (ask the user)

1. **The user records it (preferred).** Retime the timeline to the measured take. Their own voice is the only one that may speak as them in the first person.
2. **A generated narrator (TTS).** Allowed only when the user asks for it, and only with disclosure:
   - The voice speaks about the creator in the **third person**: "جمعها محمد دوّاس", never "أنا محمد".
   - On-screen first-person lines are changed to match.
   - The voiceover script file, `vo/*.json`, the timeline `meta.audio` field and the report all say "AI-generated voice, not <creator>".
   - Tell the user to use Instagram's AI label or to add a line in the caption.
   - Never clone or imitate a real person's voice.
3. **Music and captions only.** This is fine for muted autoplay.

**TTS engine.** Use `edge-tts`, Microsoft's neural voices. It's free, but it needs `pip install edge-tts` and an internet connection, and it sends only the script text to Microsoft. Check what's installed first: on Windows, SAPI and OneCore voices often have no Arabic. Ask before installing, and let the user pick the voice. For Jordanian/Levantine scripts the options are `ar-JO-TaimNeural` (male) and `ar-JO-SanaNeural` (female). `--list-voices` shows the rest.

## Fitting VO to an approved picture (`tools/make_vo.py`)

- **Measured timings.** `WordBoundary` events give real word timings. Place each line by its **first word**, not by the start of the file, because clips have about 0.1 s of silence before the first word.
- **Line placement.** `vo-lines.json` holds `[earliest_start, text, latest_end]` for each line. A line starts at its earliest time or 0.15 s after the previous line, whichever is later. Lines never overlap.
- **Lines that run OVER.** In order of preference, fix them by:
  1. shortening the words
  2. starting earlier, in a gap
  3. a small rate change (we used +8%)

  TTS runs slow, about 2 words/s with pauses at commas. The first fit of the example script ran **46 s of speech for a 45 s film**, so plan about 25% fewer words than you'd write for a human.
- **A line may cross a cut**, but:
  - it shouldn't name something that isn't on screen yet, or isn't any more
  - its caption must move with it
- **Lines and captions match.** The VO hook uses the same words as the on-screen hook. VO lines and captions say the same thing, though the caption may be shorter.
- **The hero sits in a pause.** The line before it ends **≥ 0.4 s before** the hero (in the example, the reel's VO ended at 23.49 for a click at 24.15). The next line starts about 0.5 s after it. Don't split a sentence around the hero in a way that leaves a fragment like "على My shelf…". Re-voice it as a full sentence instead.
- **English words inside Arabic**, such as "My shelf", "Learning" or "AI", are unverified by ear. If one comes out mangled, respell it phonetically ("ماي شِلف").
- **The CTA line needs room.** Leave the URL chime its own space rather than landing it on the CTA's first word.

## Timeline fields for sound

```json
"vo": [{"text", "start", "file", "words": [{"w", "t", "end"}]}],
"silences": [{"from": 23.6, "to": 24.12, "why": "pause before the save click"}],
"sfx": [{"t": 20.05, "kind": "tick"}, {"t": 24.15, "kind": "hit"}, {"t": 41.3, "kind": "chime"}]
```

`meta.clock` becomes `"voice"` once VO exists.

## Score and SFX (`tools/make_audio.py`, all synthesized with numpy)

- **Score:** a pad with one chord per scene (Dmaj7, Bm7, Gmaj7, Asus4 cycled), detuned sines with slow breathing, plus a soft pluck on every other scene start.
- **Ducking:** the bed sits about 14 dB under the voice by RMS and ducks another ~11 dB while speech is present.
- **Silences:** the bed drops out entirely for each planned silence and stays out until ~0.35 s after it. Otherwise the smoothed gate creeps back into the silence and qa_video fails it (we hit this: −24.7 dBFS against the −30 needed).
- **SFX:** about half the cuts are silent.
  - `tick`: real UI state changes such as Copied and the count.
  - `hit`: the hero, a thump plus a bell plus a click. It is the loudest non-voice sound.
  - `chime`: the URL lands.
- **Master:** gain to −16 LUFS integrated, then `alimiter` at −1.6 dB, giving a true peak of about −1.1 dBTP. Measured with ffmpeg `ebur128`. Stems go to `out/audio/`.

## Subtitles (`tools/make_srt.py`)

One SRT cue per VO line, timed from the first word's time to the last word's end + 0.25 s, clipped before the next line, saved as UTF-8 with BOM. Instagram Reels doesn't take SRT uploads (it has auto-captions), so ship the SRT as a sidecar and never burn a second text layer over the captions.

## Encode the finals

Add `-i out/audio/<film>-mix.wav -map 0:v -map 1:a -c:a aac -b:a 192k -ar 48000 -t <dur>` to the video encode. Verify with ffprobe:
- Video: h264, yuv420p, SAR 1:1, the exact frame count.
- Audio: aac at 48 kHz.
- Duration: exact.

## QA expectations (qa_video with `--lufs -16 --tp -1`)

- Loudness passes: −16 ±1 LUFS, true peak ≤ −1 dBTP.
- The planned silence passes (below −30 dBFS).
- There is a silence before the peak.
- The loudest 100 ms falls on the hero hit. With a voice clock this is reported as INFO, so confirm it yourself.
