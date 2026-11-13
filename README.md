# site-to-reel

A Claude Code skill that turns a real website into a vertical promo reel (Instagram Reels, TikTok or Shorts). It builds the film from real captures of the live site, draws every frame with a deterministic canvas renderer, and measures the result with QA checks.

**Workflow:** intake, then treatment and styleframes, then silent animatics, then voice, sound and finals. The user approves at each step, and a fresh-context critic reviews each stage, followed by one fix round.

**Tools it uses:** `playwright-cli` (capture and render), `ffmpeg` (encode and measure), Python with numpy and Pillow (timelines, audio, sheets), optional `edge-tts` for a disclosed AI narrator, and the `video-director` skill for principles and QA scripts.

```
SKILL.md              workflow, intake questions, non-negotiables, commands
references/           motion system, capture, sound and voice, Instagram Reels, gotchas, report template
templates/project/    copy this to start a new film (renderer, brand.json, tools/)
examples/dawas-shlef/ the complete worked example the skill was distilled from
```

**Install:** copy this folder to `~/.claude/skills/site-to-reel/`.
