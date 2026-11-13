// site-to-reel: deterministic, data-driven canvas renderer for vertical (1080x1920) promos.
// Every frame is a pure function of t (seconds). No Date.now(), no timers, no carried state;
// randomness (grain, torn edges) comes from a seeded PRNG and is built once at load.
// Everything brand-specific comes from the timeline (built from brand.json by tools/build_timelines.py):
//   TL.palette  colours            TL.brand  wordmark, fonts, text direction
//   TL.scenes   scenes, cameras, callouts, swaps, transitions
//   TL.texts / TL.captions   on-screen type
// Page contract: window.READY, DUR, FPS, seek(t), MEASURE().
// URL: reel.html?tl=timeline.json   (&scene=cta renders only the end card, for styleframes)
(() => {
  const W = 1080, H = 1920;
  const cv = document.getElementById('c');
  const ctx = cv.getContext('2d');
  const params = new URLSearchParams(location.search);
  const TL_FILE = params.get('tl') || 'timeline.json';
  const ONLY = params.get('scene');

  // ---- easing -------------------------------------------------------------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const prog = (t, a, b) => clamp((t - a) / (b - a));
  const outCubic = (x) => 1 - Math.pow(1 - x, 3);
  const inCubic = (x) => x * x * x;
  const inOut = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const lerp = (a, b, k) => a + (b - a) * k;

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // colour helpers: tokens are hex; rgba() strings are derived, never typed by hand
  const rgb = (hex) => { const n = parseInt(hex.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const rgba = (hex, a) => `rgba(${rgb(hex).join(',')},${a})`;

  let TL, BOXES, B, C, F;
  const IMG = {};
  const EDGES = {};
  let GRAIN;

  async function loadImage(src) {
    const im = new Image();
    im.src = src;
    await im.decode();
    return im;
  }

  async function loadSvgTinted(src, color) {
    const txt = await (await fetch(src)).text();
    const svg = txt.replace(/currentColor/g, color);
    return loadImage(URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' })));
  }

  async function init() {
    TL = await (await fetch(TL_FILE)).json();
    BOXES = TL.meta.boxesFile ? (await (await fetch(TL.meta.boxesFile)).json()).caps : {};
    B = TL.brand;
    const p = TL.palette;
    // accent = "look here" (underlines, dots); action = a user action (rings on Copy / Save)
    C = { paper: p.paper, ink: p.ink, accent: p.accent, deep: p.accentDeep, action: p.action, card: p.card || '#fbf9f3' };
    F = { script: B.fonts.script.family, latin: B.fonts.latin.family, dir: B.direction || 'rtl' };
    for (const fam of [B.fonts.script, B.fonts.latin]) {
      for (const f of fam.files) {
        const face = new FontFace(fam.family, `url(${f.url})`, { weight: String(f.weight) });
        await face.load();
        document.fonts.add(face);
      }
    }
    await document.fonts.ready;
    for (const [k, src] of Object.entries(TL.assets)) {
      if (!src.endsWith('.svg')) IMG[k] = await loadImage(src);
    }
    if (B.wordmarkIcon) IMG.wordmarkIcon = await loadSvgTinted(TL.assets[B.wordmarkIcon], C.deep);
    GRAIN = makeGrain();
    window.DUR = TL.meta.dur;
    window.FPS = TL.meta.fps;
  }

  // ---- paper surface ------------------------------------------------------
  function makeGrain() {
    const g = document.createElement('canvas');
    g.width = W; g.height = H;
    const gx = g.getContext('2d');
    const id = gx.createImageData(W, H);
    const r = mulberry32(7);
    for (let i = 0; i < id.data.length; i += 4) {
      const v = r() < 0.5 ? 35 : 255;
      id.data[i] = id.data[i + 1] = id.data[i + 2] = v;
      id.data[i + 3] = Math.floor(r() * 12);
    }
    gx.putImageData(id, 0, 0);
    return g;
  }

  function fog(x, y, r, col) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, col);
    g.addColorStop(1, rgba(C.paper, 0));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  function background(t) {
    ctx.fillStyle = C.paper;
    ctx.fillRect(0, 0, W, H);
    // ambient fog drifts linearly and slowly; it stays behind all readable content
    fog(220 + 40 * Math.sin(t * 0.35), 380, 640, rgba(C.accent, '0.10'));
    fog(880 - 30 * Math.sin(t * 0.28), 1520, 740, rgba(C.deep, '0.08'));
    ctx.drawImage(GRAIN, 0, 0);
  }

  // torn-paper outline in local units, cached per size and seed
  function tornPath(w, h, seed, amp = 2.4, step = 16) {
    const key = `${w}|${h}|${seed}|${amp}|${step}`;
    if (EDGES[key]) return EDGES[key];
    const r = mulberry32(seed);
    const j = () => (r() - 0.5) * 2 * amp;
    const pts = [];
    for (let x = 0; x < w; x += step) pts.push([x, j()]);
    for (let y = 0; y < h; y += step) pts.push([w + j(), y]);
    for (let x = w; x > 0; x -= step) pts.push([x, h + j()]);
    for (let y = h; y > 0; y -= step) pts.push([j(), y]);
    const p = new Path2D();
    pts.forEach(([a, b], i) => (i ? p.lineTo(a, b) : p.moveTo(a, b)));
    p.closePath();
    EDGES[key] = p;
    return p;
  }

  // ---- type ---------------------------------------------------------------
  function drawWordmark(cx, baseline, size, alpha = 1) {
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.direction = 'ltr';
    ctx.textAlign = 'left';
    ctx.font = `500 ${size}px "${F.latin}"`;
    const tw = ctx.measureText(B.wordmark).width;
    const ic = IMG.wordmarkIcon ? size * 0.56 : 0, gap = IMG.wordmarkIcon ? size * 0.2 : 0;
    const x0 = cx - (ic + gap + tw) / 2;
    if (IMG.wordmarkIcon) ctx.drawImage(IMG.wordmarkIcon, x0, baseline - size * 0.6, ic, ic);
    ctx.fillStyle = C.ink;
    ctx.fillText(B.wordmark, x0 + ic + gap, baseline);
    ctx.restore();
  }

  // caption-language text (Arabic by default) is drawn as a whole shaped phrase, never per character
  function script(text, x, y, px, weight, color, alpha = 1) {
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.direction = F.dir;
    ctx.textAlign = 'center';
    ctx.font = `${weight} ${px}px "${F.script}"`;
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
    ctx.restore();
  }

  function latin(text, x, y, px, weight, color, alpha = 1) {
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.direction = 'ltr';
    ctx.textAlign = 'center';
    ctx.font = `${weight} ${px}px "${F.latin}"`;
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
    ctx.restore();
  }

  // public URL on a torn ink tag (paper on ink clears 7:1; a mid-tone accent fill usually does not)
  function urlTag(text, cy, px, alpha = 1, scale = 1) {
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.font = `600 ${px}px "${F.latin}"`;
    const tw = ctx.measureText(text).width;
    const bw = Math.round(tw + px * 1.8), bh = Math.round(px * 1.88);
    ctx.translate(W / 2, cy);
    ctx.scale(scale, scale);
    ctx.translate(-bw / 2, -bh / 2);
    ctx.shadowColor = rgba(C.ink, 0.20);
    ctx.shadowBlur = 26;
    ctx.shadowOffsetY = 10;
    ctx.fillStyle = C.ink;
    ctx.fill(tornPath(bw, bh, 41, 2.6, 14));
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = C.accent; // one accent dot ties the tag to the brand
    ctx.beginPath();
    ctx.arc(px * 0.5, bh / 2, px * 0.12, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = C.paper;
    ctx.direction = 'ltr';
    ctx.textAlign = 'center';
    ctx.fillText(text, bw / 2, bh / 2 + px * 0.33);
    ctx.restore();
  }

  function captionBand(text, y, px, alpha, rise) {
    if (alpha <= 0) return;
    // up to two lines (split on \n); the last line's baseline sits at y
    const lines = text.split('\n');
    const lh = px * 1.38;
    ctx.save();
    ctx.font = `500 ${px}px "${F.script}"`;
    ctx.direction = F.dir;
    const tw = Math.max(...lines.map((l) => ctx.measureText(l).width));
    const bw = tw + 104, bh = px * 1.7 + (lines.length - 1) * lh;
    const x = (W - bw) / 2, top = y - (lines.length - 1) * lh - px * 1.09 + rise;
    // soft paper scrim so page text behind the band never competes with the caption
    const s0 = top - 90, s1 = top + bh + 70;
    const g = ctx.createLinearGradient(0, s0, 0, s1);
    g.addColorStop(0, rgba(C.paper, 0));
    g.addColorStop(0.3, rgba(C.paper, 0.82));
    g.addColorStop(0.75, rgba(C.paper, 0.82));
    g.addColorStop(1, rgba(C.paper, 0));
    ctx.globalAlpha = alpha;
    ctx.fillStyle = g;
    ctx.fillRect(0, s0, W, s1 - s0);
    ctx.shadowColor = rgba(C.ink, 0.14);
    ctx.shadowBlur = 24;
    ctx.shadowOffsetY = 8;
    ctx.fillStyle = rgba(C.paper, 0.97);
    ctx.beginPath();
    ctx.roundRect(x, top, bw, bh, Math.min(bh / 2, px * 0.85));
    ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.strokeStyle = rgba(C.ink, 0.14);
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
    lines.forEach((l, i) => script(l, W / 2, y - (lines.length - 1 - i) * lh + rise, px, 500, C.ink, alpha));
  }

  // ---- scatter scene: preview cards and abstract tabs -----------------------
  // scene.cards: [{img, title, tag, seed}] (3 cards); scene.tabs: [{label, x, y, rot, seed}] (variant "tabs")
  const CARD = { BW: 470 };
  CARD.IH = Math.round((CARD.BW - 24) / 1.7767);
  CARD.BH = 12 + CARD.IH + 96;
  const LAYOUT = {
    cards: { // three cards; the middle one is drawn last so no title is covered
      pos: [[330, 760, -3.0, 470], [770, 975, 2.4, 470], [320, 1300, 1.2, 470]],
      stack: [653, 973, 1293], order: [0, 2, 1],
    },
    tabs: {
      pos: [[330, 790, -3.0, 430], [760, 1000, 2.4, 430], [330, 1230, 1.2, 430]],
      order: [0, 2, 1],
    },
  };

  function drawCard(card, cx, cy, w, rot) {
    const { BW, IH, BH } = CARD;
    const s = w / BW;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate((rot * Math.PI) / 180);
    ctx.scale(s, s);
    ctx.translate(-BW / 2, -BH / 2);
    const path = tornPath(BW, BH, card.seed);
    ctx.save();
    ctx.shadowColor = rgba(C.ink, 0.18);
    ctx.shadowBlur = 36;
    ctx.shadowOffsetY = 16;
    ctx.fillStyle = C.card;
    ctx.fill(path);
    ctx.restore();
    ctx.drawImage(IMG[card.img], 12, 12, BW - 24, IH);
    ctx.direction = 'ltr';
    ctx.textAlign = 'left';
    ctx.fillStyle = C.deep;
    ctx.font = `500 21px "${F.latin}"`;
    ctx.letterSpacing = '3px';
    ctx.fillText(card.tag, 26, 12 + IH + 34);
    ctx.letterSpacing = '0px';
    ctx.fillStyle = C.ink;
    ctx.font = `600 42px "${F.latin}"`;
    ctx.fillText(card.title, 26, 12 + IH + 78);
    ctx.restore();
  }

  // abstract browser tab: a paper slip with a rounded top, a dot and a label (no real history)
  function drawTab(tab, cx, cy, rot, s = 1) {
    const w = 300, h = 84;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate((rot * Math.PI) / 180);
    ctx.scale(s, s);
    ctx.translate(-w / 2, -h / 2);
    ctx.shadowColor = rgba(C.ink, 0.16);
    ctx.shadowBlur = 26;
    ctx.shadowOffsetY = 10;
    ctx.fillStyle = C.card;
    ctx.beginPath();
    ctx.moveTo(0, h);
    ctx.lineTo(14, 18);
    ctx.quadraticCurveTo(18, 0, 38, 0);
    ctx.lineTo(w - 38, 0);
    ctx.quadraticCurveTo(w - 18, 0, w - 14, 18);
    ctx.lineTo(w, h);
    ctx.closePath();
    ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = C.accent;
    ctx.beginPath();
    ctx.arc(52, 46, 9, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = C.ink;
    ctx.font = `600 36px "${F.latin}"`;
    ctx.direction = 'ltr';
    ctx.textAlign = 'left';
    ctx.fillText(tab.label, 76, 58);
    ctx.strokeStyle = rgba(C.ink, 0.35);
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(w - 56, 36); ctx.lineTo(w - 40, 52);
    ctx.moveTo(w - 40, 36); ctx.lineTo(w - 56, 52);
    ctx.stroke();
    ctx.restore();
  }

  function drawScatter(s, t) {
    const L = LAYOUT[s.variant];
    const tabs = s.variant === 'tabs' ? s.tabs || [] : [];
    const gather = s.gatherAt != null ? inOut(prog(t, s.gatherAt, s.gatherAt + 0.6)) : 0;
    const align = s.alignAt != null ? (i) => inOut(prog(t, s.alignAt + i * 0.075, s.alignAt + 0.8 + i * 0.075)) : () => 0;
    const toCentre = (x, y) => [lerp(x, 540, gather), lerp(y, 1000, gather)];
    const shrink = lerp(1, 0.55, gather);

    tabs.forEach((tab, i) => {
      const enter = outCubic(prog(t, 0.08 + i * 0.075, 0.68 + i * 0.075));
      const [x, y] = toCentre(tab.x, tab.y + (1 - enter) * 60);
      drawTab(tab, x, y, tab.rot * (1 - gather), shrink);
    });
    L.order.forEach((i) => {
      const [sx, sy, sr, sw] = L.pos[i];
      const enter = outCubic(prog(t, i * 0.075, 0.6 + i * 0.075));
      const a = align(i);
      const ey = (1 - enter) * 70;
      const er = (1 - enter) * 2 * (i % 2 ? -1 : 1);
      let cx = lerp(sx, 540, a), cy = sy + ey, w = lerp(sw, 400, a), rot = lerp(sr + er, 0, a);
      if (L.stack) cy = lerp(cy, L.stack[i], a);
      [cx, cy] = toCentre(cx, cy);
      drawCard(s.cards[i], cx, cy, w * shrink, rot * (1 - gather));
    });
  }

  // ---- UI scenes: real captures, camera, callouts, real state swaps --------
  // Camera: (cx, cy) is the capture point (css px) placed at frame point (fx, fy);
  // z = frame px per css px. A 3x capture never upscales while z <= 3 (4x capture: z <= 4).
  function camAt(keys, t) {
    if (t <= keys[0].t) return keys[0];
    for (let i = 0; i < keys.length - 1; i++) {
      const a = keys[i], b = keys[i + 1];
      if (t < b.t) {
        const k = inOut(prog(t, a.t, b.t));
        return { cx: lerp(a.cx, b.cx, k), cy: lerp(a.cy, b.cy, k), z: lerp(a.z, b.z, k), fx: lerp(a.fx, b.fx, k), fy: lerp(a.fy, b.fy, k) };
      }
    }
    return keys[keys.length - 1];
  }

  function drawPage(img, cam) {
    const x0 = cam.fx - cam.cx * cam.z, y0 = cam.fy - cam.cy * cam.z;
    ctx.save();
    ctx.translate(x0, y0);
    ctx.scale(cam.z, cam.z);
    ctx.shadowColor = rgba(C.ink, 0.20);
    ctx.shadowBlur = 48;
    ctx.shadowOffsetY = 20;
    ctx.fillStyle = C.card;
    ctx.translate(-7, -7);
    ctx.fill(tornPath(554, 974, 5, 1.1, 9));
    ctx.restore();
    ctx.drawImage(img, x0, y0, 540 * cam.z, 960 * cam.z);
  }

  const toFrame = (cam, x, y) => [cam.fx + (x - cam.cx) * cam.z, cam.fy + (y - cam.cy) * cam.z];

  function calloutRect(c) {
    if (c.rect) return c.rect;
    const [cap, name] = c.box.split('.');
    return BOXES[cap].boxes[name];
  }

  function drawCallout(c, cam, t) {
    const p = outCubic(prog(t, c.t, c.t + c.dur));
    if (p <= 0) return;
    const r = calloutRect(c);
    const color = c.color === 'action' || c.color === 'cinnabar' ? C.action : C.accent;
    const lw = Math.max(3, 2.6 * cam.z);
    ctx.save();
    if (c.until != null) ctx.globalAlpha *= 1 - prog(t, c.until, c.until + 0.2); // mark leaves before the camera moves on
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';
    ctx.lineWidth = lw;
    if (c.type === 'underline') {
      const [a, b] = toFrame(cam, r.x - 2, r.y + r.h + 4);
      const [e] = toFrame(cam, r.x + r.w + 2, r.y + r.h + 4);
      const x1 = lerp(a, e, p);
      ctx.beginPath();
      ctx.moveTo(a, b);
      ctx.quadraticCurveTo((a + x1) / 2, b + 2.5 * cam.z, x1, b - cam.z);
      ctx.stroke();
    } else {
      const pulse = c.pulseAt != null ? 1 + 0.06 * Math.sin(Math.PI * prog(t, c.pulseAt, c.pulseAt + 0.25)) : 1;
      const [x, y] = toFrame(cam, r.x + r.w / 2, r.y + r.h / 2);
      const rx = (r.w / 2 + 14) * cam.z * pulse, ry = (r.h / 2 + 9) * cam.z * pulse;
      const start = -Math.PI * 0.62, sweep = Math.PI * 2.12 * p;
      ctx.beginPath();
      for (let i = 0; i <= 64; i++) {
        const a = start + (sweep * i) / 64;
        const wob = 1 + 0.025 * Math.sin(a * 3 + 1.3);
        const px = x + Math.cos(a) * rx * wob;
        const py = y + Math.sin(a) * ry * wob + (a - start) * 0.55 * cam.z;
        i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
      }
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawUIScene(s, t) {
    let img = IMG[s.img];
    for (const sw of s.swaps || []) if (t >= sw.t) img = IMG[sw.img]; // real before/after captures
    const cam = camAt(s.cam, t);
    drawPage(img, cam);
    for (const c of s.callouts || []) drawCallout(c, cam, t);
  }

  // ---- creator and end card ------------------------------------------------
  // scene.creator: {primary (caption language), secondary (latin)}
  function drawCreator(s, t) {
    const a = outCubic(prog(t, s.start + 0.1, s.start + 0.6));
    const b = outCubic(prog(t, s.start + 0.25, s.start + 0.75));
    script(s.creator.primary, W / 2, 860 + (1 - a) * 24, 132, 700, C.ink, a);
    latin(s.creator.secondary, W / 2, 968 + (1 - b) * 20, 60, 500, C.deep, b);
    const p = outCubic(prog(t, s.start + 0.5, s.start + 0.9));
    if (p > 0) {
      ctx.save();
      ctx.strokeStyle = C.accent;
      ctx.lineWidth = 4;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(430, 1012);
      ctx.quadraticCurveTo(540, 1022, lerp(430, 650, p), 1008);
      ctx.stroke();
      ctx.restore();
    }
  }

  // scene.cta: {creator, line, overlay, url}
  function drawCTA(s, t) {
    const cta = s.cta;
    const k = (d, len = 0.55) => outCubic(prog(t, s.start + d, s.start + d + len));
    // the line is fully in by +0.6 s and the URL by +1.2 s (the timeline's line and url beats)
    const a = k(0, 0.45), b = k(0.1, 0.45), c = k(0.2, 0.4), d = k(0.5, 0.4), e = k(0.75, 0.45);
    drawWordmark(W / 2, 640 + (1 - a) * 26, 150, a);
    latin(cta.creator, W / 2, 740 + (1 - b) * 18, 46, 500, C.deep, b);
    if (b > 0) {
      ctx.save();
      ctx.globalAlpha = b;
      ctx.strokeStyle = C.accent;
      ctx.lineWidth = 4;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(440, 782);
      ctx.quadraticCurveTo(540, 790, 640, 778);
      ctx.stroke();
      ctx.restore();
    }
    script(cta.line, W / 2, 1000 + (1 - c) * 18, 80, 700, C.ink, c);
    script(cta.overlay, W / 2, 1112 + (1 - d) * 16, 58, 500, C.deep, d);
    if (e > 0) urlTag(cta.url, 1288, 66, e, lerp(0.96, 1, e));
  }

  // ---- shots and transitions ------------------------------------------------
  function drawShot(s, t, xf) {
    ctx.save();
    ctx.globalAlpha = xf.alpha;
    ctx.translate(540 + xf.dx, 960 + xf.dy);
    ctx.scale(xf.scale, xf.scale);
    ctx.translate(-540, -960);
    if (s.kind === 'scatter') drawScatter(s, t);
    else if (s.kind === 'ui') drawUIScene(s, t);
    else if (s.kind === 'creator') drawCreator(s, t);
    else if (s.kind === 'cta') drawCTA(s, t);
    ctx.restore();
  }

  const ID = { dx: 0, dy: 0, alpha: 1, scale: 1 };

  function transition(type, e) {
    switch (type) {
      case 'push-left': return [{ ...ID, dx: -1150 * e }, { ...ID, dx: 1150 * (1 - e) }];
      case 'push-up': return [{ ...ID, dy: -1920 * e }, { ...ID, dy: 1920 * (1 - e) }];
      // the outgoing shot clears before the incoming one is visible, so type never ghosts over type
      case 'rise': return [{ ...ID, dy: -500 * e, alpha: clamp(1 - e * 2.2) }, { ...ID, dy: 900 * (1 - outCubic(e)), alpha: clamp((e - 0.35) * 2.5) }];
      case 'emerge': return [{ ...ID, scale: 1 - 0.25 * e, alpha: 1 - e }, { ...ID, scale: 0.86 + 0.14 * outCubic(e), alpha: clamp(e * 2) }];
      default: return [{ ...ID, alpha: clamp(1 - e * 2) }, { ...ID, alpha: clamp(e * 2 - 1) }]; // fade: dip to paper, never a double exposure
    }
  }

  function drawTexts(t) {
    for (const x of TL.texts) {
      // "from" is the time the text is fully legible, so the 0.3 s entrance runs just before it
      const f0 = Math.max(0, x.from - 0.3);
      if (x.draw === false || t < f0 || t > x.to) continue;
      const enter = x.from === 0 ? 1 : outCubic(prog(t, f0, x.from));
      const a = enter * (1 - inCubic(prog(t, x.to - 0.17, x.to)));
      const rise = (1 - enter) * 18;
      if (x.type === 'script' || x.type === 'arabic') script(x.text, W / 2, x.y + rise, x.px, x.weight || 700, C.ink, a);
      else if (x.type === 'wordmark') drawWordmark(W / 2, x.y + rise, x.px, a);
      else if (x.type === 'tag') urlTag(x.text, x.y + rise, x.px, a);
    }
  }

  function drawCaptions(t) {
    for (const c of TL.captions) {
      if (t < c.from || t > c.to) continue;
      const enter = outCubic(prog(t, c.from, c.from + 0.3));
      const exit = c.to >= TL.meta.dur ? 0 : inCubic(prog(t, c.to - 0.15, c.to));
      captionBand(c.text, c.y, c.px, enter * (1 - exit), (1 - enter) * 14);
    }
  }

  function render(t) {
    background(t);
    const S = TL.scenes;
    if (ONLY) {
      const s = S.find((x) => x.kind === ONLY);
      drawShot(s, s.end - 0.01, ID);
      return;
    }
    let i = S.findIndex((s) => t >= s.start && t < s.end);
    if (i < 0) i = S.length - 1;
    const s = S[i], prev = S[i - 1];
    const tr = prev && prev.transitionOut;
    if (tr && t < s.start + tr.dur) {
      const [out, inn] = transition(tr.type, inOut(prog(t, s.start, s.start + tr.dur)));
      drawShot(prev, t, out);
      drawShot(s, t, inn);
    } else {
      drawShot(s, t, ID);
    }
    drawTexts(t);
    drawCaptions(t);
  }

  window.READY = init();
  window.seek = (t) => render(t);
  // rendered widths of every caption-language line, for the x 90-990 layout check
  window.MEASURE = () => {
    const out = [];
    const m = (text, px, weight, pad = 0) => {
      ctx.save();
      ctx.font = `${weight} ${px}px "${F.script}"`;
      ctx.direction = F.dir;
      for (const l of text.split('\n')) out.push({ text: l, w: Math.round(ctx.measureText(l).width + pad) });
      ctx.restore();
    };
    for (const x of TL.texts) if (x.type === 'script' || x.type === 'arabic') m(x.text, x.px, x.weight || 700);
    for (const c of TL.captions) m(c.text, c.px, 500, 104);
    for (const s of TL.scenes) if (s.cta) { m(s.cta.line, 80, 700); m(s.cta.overlay, 58, 500); }
    return out;
  };
})();
