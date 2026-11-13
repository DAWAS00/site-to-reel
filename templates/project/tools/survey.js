async page => {
  // READ-ONLY survey: headings, links, buttons and images with page-y positions for each route.
  // Use the output to pick capture scroll positions and callout targets. Clicks nothing, saves nothing.
  // EDIT: the local site (never the public one for captures) and the routes to survey.
  const BASE = 'http://127.0.0.1:4321';
  const routes = ['/', '/about/'];
  const out = {};
  for (const r of routes) {
    await page.goto(BASE + r, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    out[r] = await page.evaluate(() => {
      const items = [...document.querySelectorAll('header a, main h1, main h2, main h3, main a, main button, main input, main img')]
        .map((e) => {
          const b = e.getBoundingClientRect();
          const t = (e.tagName === 'IMG' ? 'img:' + (e.getAttribute('src') || '') : (e.innerText || e.value || '').trim().replace(/\s+/g, ' ')).slice(0, 70);
          return `${Math.round(b.y + scrollY)} ${e.tagName} ${t}`;
        })
        .filter((s) => !/ $/.test(s));
      return { height: document.documentElement.scrollHeight, storageKeys: Object.keys(localStorage), items: items.slice(0, 90) };
    });
  }
  return JSON.stringify(out, null, 1);
}
