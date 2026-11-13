async page => {
  // Extra callout boxes (css px relative to the matching capture's scroll position). Read-only.
  const BASE = 'http://127.0.0.1:4321';
  async function box(path, scroll, sel, re) {
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate((y) => window.scrollTo(0, y), scroll);
    await page.waitForTimeout(300);
    return page.evaluate(({ sel, re }) => {
      const rx = new RegExp(re, 'i');
      const e = [...document.querySelectorAll(sel)].filter((x) => rx.test((x.innerText || '').trim()))
        .sort((a, b) => a.getBoundingClientRect().width - b.getBoundingClientRect().width)[0];
      if (!e) return null;
      const r = e.getBoundingClientRect();
      return { x: +r.x.toFixed(1), y: +r.y.toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1), text: e.innerText.trim().slice(0, 50) };
    }, { sel, re });
  }
  return JSON.stringify({
    'detail-source.author': await box('/resources/phosphor-icons/', 1500, 'main p, main dd, main span, main div', 'Helena Zhang'),
    'learning-top.navLearning': await box('/learning/anthropic-prompt-engineering/', 0, 'header a', '^Learning$'),
  });
}
