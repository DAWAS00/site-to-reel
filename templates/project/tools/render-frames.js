async page => {
  // Renders every frame of the loaded timeline: frame i is drawn at t = i / fps.
  // The page URL carries the output folder: reel.html?tl=<timeline>&out=<abs dir>
  // Optional &from=<i>&to=<j> renders a frame range (inclusive) so long films can run in chunks.
  // Output: zero-padded PNGs, one per frame, F0 .. F(n-1) inclusive.
  const q = new URL(page.url()).searchParams;
  const out = q.get('out');
  await page.evaluate(() => window.READY);
  const { dur, fps } = await page.evaluate(() => ({ dur: window.DUR, fps: window.FPS }));
  const n = Math.round(dur * fps);
  const from = +(q.get('from') || 0), to = Math.min(n - 1, +(q.get('to') || n - 1));
  for (let i = from; i <= to; i++) {
    await page.evaluate((t) => window.seek(t), i / fps);
    await page.screenshot({ path: `${out}/frame_${String(i).padStart(4, '0')}.png` });
  }
  return `rendered F${from}-F${to} of ${n}`;
}
