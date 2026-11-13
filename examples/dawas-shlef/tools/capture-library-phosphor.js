async page => {
  // Fix round: the library scrolled to the Phosphor Icons result, so the push into the
  // Phosphor detail page follows from the card the viewer actually sees. Read-only.
  const BASE = 'http://127.0.0.1:4321';
  const OUT = 'E:/New Video ai/dawas-shlef-reel-production/capture3x';
  await page.goto(BASE + '/resources/?type=website&q=Design&sort=newest', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const titleY = await page.evaluate(() => {
    const h = [...document.querySelectorAll('h2, h3')].find((e) => e.innerText.trim() === 'Phosphor Icons');
    return h.getBoundingClientRect().y + scrollY;
  });
  await page.evaluate((y) => window.scrollTo(0, y), Math.round(titleY - 560));
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${OUT}/library-phosphor.png` });
  return JSON.stringify(await page.evaluate(() => {
    const box = (e) => { const r = e.getBoundingClientRect(); return { x: +r.x.toFixed(1), y: +r.y.toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1), text: (e.innerText || '').trim().slice(0, 60) }; };
    const h = [...document.querySelectorAll('h2, h3')].find((e) => e.innerText.trim() === 'Phosphor Icons');
    const card = h.closest('article, li, a') || h.parentElement;
    return { scrollY, title: box(h), card: box(card) };
  }));
}
