async page => {
  // Fix round: My shelf at 4x (2160x3840 for 540x960 css) so the camera can hold the
  // "1 resource on your shelf" count at z 3.6 without upscaling. Same route and scroll as capture3x.
  // Creates one demo bookmark in this clean in-memory session and removes it afterwards.
  const BASE = 'http://127.0.0.1:4321';
  const OUT = 'E:/New Video ai/dawas-shlef-reel-production/capture3x';
  await page.goto(BASE + '/resources/phosphor-icons/', { waitUntil: 'networkidle' });
  const before = await page.evaluate(() => Object.keys(localStorage));
  await page.getByRole('button', { name: 'Save Phosphor Icons' }).click();
  await page.waitForTimeout(800);
  await page.goto(BASE + '/resources/?saved=1', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => window.scrollTo(0, 562));
  await page.waitForTimeout(900);
  const sy = await page.evaluate(() => scrollY);
  await page.screenshot({ path: `${OUT}/shelf-saved-4x.png` });
  const count = await page.evaluate(() => {
    const e = [...document.querySelectorAll('p, span, div')].filter((x) => /resource on your shelf/i.test(x.innerText || ''))
      .sort((a, b) => a.getBoundingClientRect().width - b.getBoundingClientRect().width)[0];
    const r = e.getBoundingClientRect();
    return { x: r.x, y: r.y, w: r.width, h: r.height, text: e.innerText.trim(), fontSize: getComputedStyle(e).fontSize };
  });
  await page.evaluate(() => localStorage.removeItem('ai-shelf:saved:v1'));
  const after = await page.evaluate(() => Object.keys(localStorage));
  return JSON.stringify({ scrollY: sy, count, storageBefore: before, storageAfter: after });
}
