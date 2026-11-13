async page => {
  // Captures every UI state the film needs from the LOCAL site, in a clean in-memory session.
  // Run with tools/cli3x.config.json: viewport 540x960 css px at 3x = 1620x2880 PNG, so the camera can
  // hold up to z 3 without upscaling (use cli4x for one tiny detail you need to hold at z 4).
  // Boxes are css px relative to each capture's scroll position and feed callouts ("box": "shot.name").
  // Rules: real states only (click the real button and capture the real result, never draw a fake one);
  // create only demo data you then remove; record storage before and after; submit no forms.
  // EDIT: BASE, OUT, and the shots at the bottom.
  const BASE = 'http://127.0.0.1:4321';
  const OUT = 'ABSOLUTE/PATH/TO/PROJECT/capture3x';
  const caps = {};

  async function settle() {
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(900);
  }
  // first visible element matching a selector and a text regexp (topmost, then smallest)
  function find(spec) {
    return page.evaluate(({ sel, re }) => {
      const rx = new RegExp(re, 'i');
      const text = (e) => e.tagName === 'IMG' ? (e.getAttribute('src') || '') + ' ' + (e.alt || '')
        : e.tagName === 'INPUT' ? (e.value || '') : (e.innerText || '').trim();
      const els = [...document.querySelectorAll(sel)].filter((e) => {
        const r = e.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && rx.test(text(e));
      });
      els.sort((a, b) => {
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        return ra.top - rb.top || ra.width * ra.height - rb.width * rb.height;
      });
      const e = els[0];
      if (!e) return null;
      const r = e.getBoundingClientRect();
      return { x: r.x, y: r.y + scrollY, w: r.width, h: r.height, text: text(e).slice(0, 60) };
    }, spec);
  }
  async function shot(name, scrollTo, targets) {
    await page.evaluate((y) => window.scrollTo(0, y), Math.max(0, scrollTo));
    await page.waitForTimeout(600);
    const sy = await page.evaluate(() => scrollY);
    await page.screenshot({ path: `${OUT}/${name}.png` });
    const boxes = {};
    for (const [k, spec] of Object.entries(targets)) {
      const b = await find(spec);
      boxes[k] = b && { x: +b.x.toFixed(1), y: +(b.y - sy).toFixed(1), w: +b.w.toFixed(1), h: +b.h.toFixed(1), text: b.text };
    }
    caps[name] = { url: page.url().replace(BASE, ''), scrollY: sy, boxes };
  }
  async function go(path) {
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    await settle();
  }

  const storageBefore = await (async () => { await go('/'); return page.evaluate(() => ({ ...localStorage })); })();

  // ---- EDIT: one shot() per state. Example: --------------------------------
  await shot('home-top', 0, {
    logo: { sel: 'header a', re: 'BRAND' },
    hero: { sel: 'h1', re: '.' },
  });
  // A real state change: capture before, click the real control, capture after.
  // await go('/item/');
  // await shot('item-top', 0, { save: { sel: 'main button', re: 'save' } });
  // await page.getByRole('button', { name: 'Save' }).click();
  // await page.waitForTimeout(800);
  // await shot('item-saved', 0, { save: { sel: 'main button', re: 'saved' } });

  // ---- restore: put back exactly what was there before this session -------
  const storageAfterDemo = await page.evaluate(() => ({ ...localStorage }));
  await page.evaluate((before) => {
    for (const k of Object.keys(localStorage)) if (!(k in before)) localStorage.removeItem(k);
    for (const [k, v] of Object.entries(before)) localStorage.setItem(k, v);
  }, storageBefore);
  const storageAfter = await page.evaluate(() => ({ ...localStorage }));
  return JSON.stringify({ caps, storageBefore, storageAfterDemo, storageAfter }, null, 1);
}
