async page => {
  // Review stills at chosen times, rendered by the same seek(t) used for the film.
  // Page URL: reel.html?tl=<timeline>&out=<abs dir>&times=0,1.2,...
  const q = new URL(page.url()).searchParams;
  const out = q.get('out');
  const times = q.get('times').split(',').map(Number);
  await page.evaluate(() => window.READY);
  for (const t of times) {
    await page.evaluate((x) => window.seek(x), t);
    await page.screenshot({ path: `${out}/t${t.toFixed(2)}.png` });
  }
  return JSON.stringify(await page.evaluate(() => window.MEASURE()));
}
