// audit_render.mjs: measure a page in a real browser instead of describing it.
// Prototype of the anti-slop skill's render audit. Drives the same headless
// chromium bundle the harness uses.
//
//   node audit_render.mjs <file-or-url> [--out audit.json] [--shots DIR]
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
// playwright-core, from node_modules or from PLAYWRIGHT_CORE if you keep it elsewhere
let pw;
try { pw = require('playwright-core'); }
catch { pw = require(process.env.PLAYWRIGHT_CORE || '/tmp/tools/node_modules/playwright-core'); }
const { chromium } = pw;
import { writeFileSync, mkdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const args = process.argv.slice(2);
const target = args[0];
if (!target) { console.error('usage: node audit_render.mjs <file-or-url>'); process.exit(2); }
const outIdx = args.indexOf('--out');
const outPath = outIdx > -1 ? args[outIdx + 1] : null;
const shotIdx = args.indexOf('--shots');
const shotDir = shotIdx > -1 ? args[shotIdx + 1] : null;
const url = target.startsWith('http') ? target : pathToFileURL(resolve(target)).href;

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 390, height: 844 },
];

const MEASURE = () => {
  const lum = (rgb) => {
    const [r, g, b] = rgb.map((v) => { const s = v / 255; return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4); });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const parse = (c) => (c.match(/\d+(\.\d+)?/g) || [0, 0, 0]).slice(0, 3).map(Number);
  const contrast = (a, b) => { const l1 = lum(parse(a)), l2 = lum(parse(b)); const hi = Math.max(l1, l2), lo = Math.min(l1, l2); return (hi + 0.05) / (lo + 0.05); };
  const bgOf = (el) => { let n = el; while (n) { const c = getComputedStyle(n).backgroundColor; const p = parse(c); if (c !== 'rgba(0, 0, 0, 0)' && !(p[0] === 0 && p[1] === 0 && p[2] === 0 && /rgba\(0, 0, 0, 0\)/.test(c))) return c; n = n.parentElement; } return 'rgb(255, 255, 255)'; };
  const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };

  const samples = [];
  const addSample = (label, el) => {
    if (!el || !visible(el)) return;
    const cs = getComputedStyle(el);
    const size = parseFloat(cs.fontSize);
    const weight = Number(cs.fontWeight) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    samples.push({ label, size: Math.round(size * 10) / 10, large, contrast: Math.round(contrast(cs.color, bgOf(el)) * 100) / 100, color: cs.color, bg: bgOf(el) });
  };
  addSample('hero headline', document.querySelector('h1'));
  addSample('hero lede', document.querySelector('.lede'));
  addSample('eyebrow', document.querySelector('.eyebrow'));
  addSample('hero foot', document.querySelector('.hero-foot'));
  addSample('nav link', document.querySelector('.nav-links a'));
  addSample('body prose', document.querySelector('.prose p'));
  addSample('row value', document.querySelector('.rows .v'));
  addSample('receipt sub', document.querySelector('.receipt .rsub'));
  addSample('section label', document.querySelector('.label'));
  addSample('primary button', document.querySelector('.btn'));
  addSample('source meta', document.querySelector('.sources .meta'));
  addSample('foot meta', document.querySelector('.foot-meta'));
  addSample('swaps from', document.querySelector('.swaps .from'));
  addSample('swaps to', document.querySelector('.swaps .to'));

  // chromatic colors: neutrals dropped, what is left should be one family
  const chroma = new Set();
  document.querySelectorAll('*').forEach((el) => {
    if (!visible(el)) return;
    const cs = getComputedStyle(el);
    const consider = (c) => {
      const m = parse(c); const mx = Math.max(...m), mn = Math.min(...m);
      if (mx - mn < 24) return;               // neutral
      if (mx < 60 || mn > 210) return;        // near-black or near-white
      chroma.add(c);
    };
    consider(cs.color); consider(cs.backgroundColor); consider(cs.borderTopColor); consider(cs.outlineColor);
  });

  // tap targets
  const targets = [];
  document.querySelectorAll('a[href], button, input, select, textarea').forEach((el) => {
    if (!visible(el)) return;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const inline = cs.display === 'inline';
    targets.push({ tag: el.tagName.toLowerCase(), text: (el.textContent || '').trim().slice(0, 32), w: Math.round(r.width), h: Math.round(r.height), inline });
  });

  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((h) => ({ level: Number(h.tagName[1]), text: h.textContent.trim().slice(0, 46) }));
  const imgs = [...document.querySelectorAll('img')].map((i) => ({ src: i.getAttribute('src'), alt: i.getAttribute('alt') }));
  const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;

  const cta = document.querySelector('.cta-row .btn');
  const lede = document.querySelector('.lede');
  const heroFit = cta ? { ctaBottom: Math.round(cta.getBoundingClientRect().bottom), ledeBottom: Math.round(lede.getBoundingClientRect().bottom), viewport: window.innerHeight } : null;
  const fonts = ['Inter', 'Instrument Serif', 'IBM Plex Mono'];
  const fontsLoaded = fonts.map((f) => ({ family: f, loaded: document.fonts ? document.fonts.check(`16px "${f}"`) : null }));
  const revealOff = [...document.querySelectorAll('.reveal')].filter((el) => parseFloat(getComputedStyle(el).opacity) === 0).length;

  return { samples, chroma: [...chroma], targets, headings, imgs, overflow, heroFit, fontsLoaded, revealHidden: revealOff, innerWidth: window.innerWidth };
};

const browser = await chromium.launch();
const results = { url, viewports: {}, requests: [], verdicts: [] };

for (const vp of VIEWPORTS) {
  const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const requested = [];
  page.on('request', (r) => requested.push(r.url()));
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(700);
  const data = await page.evaluate(MEASURE);
  data.pageBytes = null;
  results.viewports[vp.name] = { ...data, requests: [...new Set(requested)] };
  if (vp.name === 'desktop') results.requests = [...new Set(requested)];
  if (shotDir) {
    mkdirSync(shotDir, { recursive: true });
    await page.screenshot({ path: `${shotDir}/${vp.name}-hero.png` });
    await page.screenshot({ path: `${shotDir}/${vp.name}-full.png`, fullPage: true });
  }
  await ctx.close();
}

// reduced motion pass
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  const hidden = await page.evaluate(() => [...document.querySelectorAll('.reveal')].filter((el) => parseFloat(getComputedStyle(el).opacity) === 0).length);
  results.reducedMotion = { revealHidden: hidden };
  await ctx.close();
}

await browser.close();

const external = results.requests.filter((u) => !u.startsWith('file:') && !u.startsWith('data:') && !u.startsWith('blob:'));
const d = results.viewports.desktop, m = results.viewports.mobile, t = results.viewports.tablet;

const worstContrast = Object.values(results.viewports)
  .flatMap((v) => v.samples)
  .reduce((a, b) => (a.contrast <= b.contrast ? a : b));
const smallText = Object.values(results.viewports).flatMap((v) => v.samples).filter((s) => !s.large);

const controlTargets = m.targets.filter((x) => !x.inline);
const smallControls = controlTargets.filter((x) => x.h < 44);
const inlineTargets = m.targets.filter((x) => x.inline);
const inlineUnder24 = inlineTargets.filter((x) => x.h < 24);

const headings = d.headings;
let headingSkip = null;
for (let i = 1; i < headings.length; i++) if (headings[i].level - headings[i - 1].level > 1) headingSkip = `${headings[i - 1].text} -> ${headings[i].text}`;

results.verdicts = [
  { id: 'contrast-small-text', status: smallText.every((s) => s.contrast >= 4.5) ? 'pass' : 'fail', detail: `worst small-text pair ${worstContrast.label} at ${worstContrast.contrast}:1` },
  { id: 'contrast-large-text', status: Object.values(results.viewports).flatMap((v) => v.samples).filter((s) => s.large).every((s) => s.contrast >= 3) ? 'pass' : 'fail', detail: '' },
  { id: 'one-h1', status: headings.filter((h) => h.level === 1).length === 1 ? 'pass' : 'fail', detail: `${headings.filter((h) => h.level === 1).length} h1 elements` },
  { id: 'heading-order', status: headingSkip ? 'fail' : 'pass', detail: headingSkip || 'no skipped levels' },
  { id: 'single-accent-family', status: d.chroma.length <= 1 ? 'pass' : 'fail', detail: `chromatic colors: ${d.chroma.join(', ') || 'none'}` },
  { id: 'no-external-requests', status: external.length === 0 ? 'pass' : 'fail', detail: `${external.length} external` },
  { id: 'no-horizontal-overflow', status: [d, t, m].every((v) => v.overflow <= 0) ? 'pass' : 'fail', detail: `widest overflow ${Math.max(d.overflow, t.overflow, m.overflow)}px` },
  { id: 'hero-fits-first-screen', status: [d, m].every((v) => v.heroFit && v.heroFit.ctaBottom <= v.heroFit.viewport) ? 'pass' : 'fail', detail: `desktop cta bottom ${d.heroFit.ctaBottom}/${d.heroFit.viewport}, mobile ${m.heroFit.ctaBottom}/${m.heroFit.viewport}` },
  { id: 'mobile-controls-44px', status: smallControls.length === 0 ? 'pass' : 'fail', detail: smallControls.length ? smallControls.map((x) => `${x.text || x.tag} ${x.w}x${x.h}`).join('; ') : 'all controls at least 44px tall' },
  { id: 'inline-links-24px', status: inlineUnder24.length === 0 ? 'pass' : 'warn', detail: inlineUnder24.length ? `${inlineUnder24.length} inline links under 24px tall` : 'ok' },
  { id: 'images-have-alt', status: d.imgs.every((i) => i.alt !== null) ? 'pass' : 'fail', detail: `${d.imgs.length} img elements` },
  { id: 'fonts-loaded', status: d.fontsLoaded.every((f) => f.loaded) ? 'pass' : 'fail', detail: d.fontsLoaded.map((f) => `${f.family}:${f.loaded}`).join(' ') },
  { id: 'reduced-motion-honored', status: results.reducedMotion.revealHidden === 0 ? 'pass' : 'fail', detail: `${results.reducedMotion.revealHidden} elements stuck hidden under reduced motion` },
];

const fails = results.verdicts.filter((v) => v.status === 'fail');
console.log(`page: ${url}`);
console.log(`requests: ${results.requests.length} unique, ${external.length} external`);
for (const v of results.verdicts) console.log(`  [${v.status.toUpperCase().padEnd(4)}] ${v.id}${v.detail ? ' :: ' + v.detail : ''}`);
console.log('\ncontrast samples (desktop):');
for (const s of results.viewports.desktop.samples) console.log(`  ${String(s.contrast).padStart(6)}:1  ${s.large ? 'large' : 'small'}  ${s.label}  ${s.color} on ${s.bg}`);
console.log(`\nchromatic colors: ${results.viewports.desktop.chroma.join(', ') || 'none'}`);
console.log(`headings: ${results.viewports.desktop.headings.map((h) => 'h' + h.level).join(' ')}`);
console.log(`verdict: ${fails.length === 0 ? 'PASS' : 'FAIL (' + fails.map((f) => f.id).join(', ') + ')'}`);
if (outPath) { writeFileSync(outPath, JSON.stringify(results, null, 2)); console.log(`wrote ${outPath}`); }
process.exit(fails.length === 0 ? 0 : 1);
