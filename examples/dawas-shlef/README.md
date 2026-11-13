# Worked example: Dawas Shlef

This is the project the skill was distilled from: a 45 s Instagram Reel and a 15 s ad cut for Dawas Shlef, a browser-based library of AI resources curated by Mohammad Dawas (public URL dawas-shelf.vercel.app). The narrator is an AI-generated voice (`ar-JO-TaimNeural`) speaking about Mohammad in the third person. It is not his voice.

| File | What |
|---|---|
| `brand.json` | Brand tokens, fonts, allowed claims, things never to say, voice and safe area |
| `tools/build_timelines.py` | The real timeline builder for both films, using every feature: scatter tabs and cards, 12 UI scenes, swaps, callouts, creator, CTA, VO, silences and SFX |
| `timeline.json`, `timeline-ad15.json` | Its output, including the measured VO word timings |
| `vo-lines.json` | The voice lines as fitted to the approved picture |
| `tools/capture3x.js` and friends | The capture scripts (real Save and Copy clicks, a 4x detail, the demo bookmark created and removed) |
| `boxes.json` | Callout boxes from the captures |
| `review-notes.md` | The stage 2 and stage 3 report: checks, the critic round, decisions and commands |
| `voiceover-script-ar.txt` | The script as voiced, with its disclosure |

**Not included:**
- The captures (screenshots of the site) and the font files. To rebuild, re-capture against the running site with `tools/capture3x.js`, and put the fonts in `assets/fonts/`.
- The rendered MP4s.

Use this as a reference for the level of detail. Don't copy the scene list onto a different product.
