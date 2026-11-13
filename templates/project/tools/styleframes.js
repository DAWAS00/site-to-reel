async page => {
  // Look-proof stills from the real renderer: one per chosen time, plus the end card on its own.
  // Page URL: reel.html?tl=timeline.json&out=<abs dir>&times=1.2,6.8   (pick the most DIFFERENT beats)
  const q = new URL(page.url()).searchParams;
  const out = q.get('out');
  const times = (q.get('times') || '1.2').split(',').map(Number);
  await page.evaluate(() => window.READY);
  for (const [i, t] of times.entries()) {
    await page.evaluate((x) => window.seek(x), t);
    await page.screenshot({ path: `${out}/styleframe-${String(i + 1).padStart(2, '0')}-t${t.toFixed(2)}.png` });
  }
  const u = new URL(page.url());
  u.searchParams.set('scene', 'cta');
  await page.goto(u.toString());
  await page.evaluate(() => window.READY);
  await page.evaluate(() => window.seek(0));
  await page.screenshot({ path: `${out}/styleframe-cta.png` });
  return `${times.length + 1} styleframes written`;
}
