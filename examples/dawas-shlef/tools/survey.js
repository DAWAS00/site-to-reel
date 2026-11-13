async page => {
  // Lists headings, links and buttons with page y positions for each route (read-only).
  const BASE = 'http://127.0.0.1:4321';
  const routes = ['/resources/phosphor-icons/', '/resources/research-companion/', '/resources/creative-brief/',
    '/learning/anthropic-prompt-engineering/', '/about/'];
  const out = {};
  for (const r of routes) {
    await page.goto(BASE + r, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    out[r] = await page.evaluate(() => {
      const items = [...document.querySelectorAll('main h1, main h2, main h3, main a, main button, main img, main figcaption, main [class*=toc] a')]
        .map((e) => {
          const b = e.getBoundingClientRect();
          const t = (e.tagName === 'IMG' ? 'img:' + (e.getAttribute('src') || '') : (e.innerText || '').trim().replace(/\s+/g, ' ')).slice(0, 70);
          return `${Math.round(b.y + scrollY)} ${e.tagName} ${t}`;
        })
        .filter((s) => !/ $/.test(s));
      return { height: document.documentElement.scrollHeight, items: items.slice(0, 70) };
    });
  }
  return JSON.stringify(out, null, 1);
}
