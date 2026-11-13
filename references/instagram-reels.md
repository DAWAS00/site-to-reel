# Instagram Reels

- **Format:** 1080×1920 (9:16), 30 fps, H.264 yuv420p, SAR 1:1, faststart, AAC 48 kHz.
- **Length:** a 45 s main reel plus a 15 s ad cut that is cut separately, not sped up. Reels allow far longer, but shorter holds attention.
- **16:9:** only if asked. It's a recomposition, not a crop.
- **Safe area:** keep text and key UI inside x 90–990 and y 200–1500.
  - **Top:** Reels header.
  - **Right:** the like, comment and share column, which grows over x > 990 near the bottom.
  - **Bottom:** below about y 1500 the caption, username and audio line cover the frame.
  - Captions sit at y 1300–1500.
  - The early URL tag's bottom edge goes at y ≤ 1495. The critic caught it at about 1520.
- **Muted autoplay:** the hook text and the public URL are legible by 3 s with sound off. Check `hook_sheet.jpg` from qa_video: from those tiles alone you should be able to say what the film is and what to do.
- **CTA wording:**
  - Links in organic Reels aren't tappable, and Reels have no description.
  - Say "visit the site" ("زور الموقع وجرّبه") and show the URL. Don't say "link in the description".
  - "Open the link" fits only a paid ad with a button.
- **Cover** (`out/cover/`):
  - Instagram shows a 3:4 centre crop (1080×1440, y 240–1680) on the profile grid.
  - Pull candidate frames from the encoded MP4 and crop each to 3:4 to check it.
  - The end card usually survives the crop. The opening hook often gets clipped at the top.
  - Export `reel-cover.jpg` (q 2) plus `reel-cover-grid-preview-3x4.png`.
  - The user picks it with "Edit cover → Add from camera roll".

  ```bash
  ffmpeg -i out/reel-final.mp4 -vf "select=eq(n\,1349)" -fps_mode passthrough -frames:v 1 out/cover/reel-cover.png
  ffmpeg -i out/cover/reel-cover.png -vf "crop=1080:1440:0:240" out/cover/reel-cover-grid-preview-3x4.png
  ffmpeg -i out/cover/reel-cover.png -q:v 2 out/cover/reel-cover.jpg
  ```
- **AI label:** if the narrator is TTS, tell the user to mark the post as containing AI-generated audio, or to add a caption line such as "التعليق الصوتي مولّد بالذكاء الاصطناعي".
- **Posting:** always the user's job. Never upload or schedule for them.
