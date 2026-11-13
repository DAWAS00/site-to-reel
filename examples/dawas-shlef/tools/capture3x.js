async page => {
  // Captures every reel state from the local site (read-only, clean in-memory session).
  // Viewport 540x960 css px at 3x = 1620x2880 PNG, so the reel camera can frame up to
  // 1.5x a full-frame view without upscaling. Boxes are css px relative to each capture.
  const BASE = 'http://127.0.0.1:4321';
  const OUT = 'E:/New Video ai/dawas-shlef-reel-production/capture3x';
  const caps = {};

  async function settle() {
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(900);
  }
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

  await go('/');
  await shot('home-top', 0, {
    logo: { sel: 'header a', re: 'Dawas Shlef' },
    hero: { sel: 'h1', re: 'Good tools' },
    explore: { sel: 'a', re: 'Explore the library' },
  });

  await go('/resources/?type=website&q=Design&sort=newest');
  const input = await find({ sel: 'input', re: 'Design' });
  await shot('library-search', input.y - 40, {
    search: { sel: 'input', re: 'Design' },
    websites: { sel: 'button, a', re: '^Websites' },
    skills: { sel: 'button, a', re: '^AI skills' },
    count: { sel: 'p, span, div', re: 'resources to explore' },
    card: { sel: 'h2, h3', re: '^Noiced$' },
    cardDesc: { sel: 'p', re: 'curated gallery' },
  });

  await go('/resources/phosphor-icons/');
  await shot('detail-top', 0, {
    title: { sel: 'h1', re: '^Phosphor Icons$' },
    purpose: { sel: 'p', re: '^A flexible icon' },
    save: { sel: 'main button', re: 'shelf' },
    myshelf: { sel: 'header a', re: 'My shelf' },
  });
  await shot('detail-source', 1500, {
    closer: { sel: 'h2', re: 'A closer look' },
    tags: { sel: 'a', re: '^Design$' },
    visit: { sel: 'a', re: 'Visit website' },
  });
  // real save: the button state and the header count come from the site itself
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.getByRole('button', { name: 'Save Phosphor Icons' }).click();
  await page.waitForTimeout(800);
  await shot('detail-saved', 0, {
    save: { sel: 'main button', re: 'shelf' },
    myshelf: { sel: 'header a', re: 'My shelf' },
  });

  await go('/resources/?saved=1');
  const count = await find({ sel: 'p, span, div', re: 'resource on your shelf' });
  await shot('shelf-saved', count.y - 170, {
    count: { sel: 'p, span, div', re: 'resource on your shelf' },
    savedOnly: { sel: 'button, label', re: 'Saved only' },
    card: { sel: 'h2, h3', re: '^Phosphor Icons$' },
  });

  await go('/resources/creative-brief/');
  await shot('prompt-copy', 820, {
    heading: { sel: 'h2', re: 'Your starting point' },
    copy: { sel: 'button', re: 'Copy prompt' },
  });
  await page.context().grantPermissions(['clipboard-read', 'clipboard-write'], { origin: BASE });
  await page.getByRole('button', { name: /copy prompt/i }).first().click();
  await page.waitForTimeout(500);
  await shot('prompt-copied', 820, {
    copy: { sel: 'button', re: 'cop' },
  });

  await go('/resources/research-companion/');
  await shot('skill-copy', 1190, {
    heading: { sel: 'h2', re: 'The complete skill' },
    copy: { sel: 'button', re: 'Copy SKILL.md' },
  });

  await go('/learning/anthropic-prompt-engineering/');
  await shot('learning-top', 0, {
    title: { sel: 'h1', re: 'Better prompts' },
    tocMap: { sel: 'a', re: 'A map of the nine chapters' },
    original: { sel: 'a', re: 'Original tutorial' },
  });
  await shot('learning-chapters', 2560, {
    map: { sel: 'h2', re: 'A map of the nine chapters' },
    first: { sel: 'a', re: '^Prompt structure$' },
    last: { sel: 'a', re: '^Complex prompts$' },
  });

  await go('/about/');
  await shot('about-contact', 940, {
    touch: { sel: 'h2', re: 'Get in touch' },
    photo: { sel: 'img', re: 'portrait' },
    name: { sel: 'h3', re: '^Dawas$' },
    insta: { sel: 'a', re: 'dawas_tech' },
  });

  // restore: remove only the bookmark this session created
  const before = await page.evaluate(() => Object.keys(localStorage));
  await page.evaluate(() => localStorage.removeItem('ai-shelf:saved:v1'));
  const after = await page.evaluate(() => Object.keys(localStorage));
  return JSON.stringify({ caps, storageBefore: before, storageAfter: after }, null, 1);
}
