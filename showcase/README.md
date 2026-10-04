# showcase

The page that lives at `docs/index.html`. One hand built page, used as two things: something to click,
and the golden example the anti-slop rubric is written against.

## What this is, and is not

It is a hand written page. The agent that will generate pages does not exist yet. Pretending otherwise
would poison the example, because the rubric cannot be built against output the harness never produced.

It exists so the design rules stop being prose. Every rule we wrote is checked against something real:
one accent, one radius system, two fonts plus mono, a hero that fits the first screen, contrast measured
on the rendered page, zero network requests.

## Files

| File | What it is |
| --- | --- |
| `index.template.html` | the page, with font placeholders and three measured values left blank |
| `build.py` | subsets the fonts, embeds them, fills in the placeholders, writes `docs/index.html` |
| `audit_render.mjs` | renders the page in headless chromium and measures it |
| `fonts/` | the four woff2 files pulled from Google Fonts, before subsetting |
| `sources.md` | font licenses and the exact download URLs |

## Rebuild

```bash
pip install fonttools brotli
python3 showcase/build.py \
  --fonts-dir showcase/fonts \
  --set-contrast 5.2 --set-kb 88 --set-requests 0
```

Those three flags put the measured numbers into the footer. Take them from a fresh audit run, not from
memory, or the footer lies.

## Audit

```bash
npm install --prefix /tmp/tools playwright-core
npx --prefix /tmp/tools playwright-core install chromium

PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers \
  node showcase/audit_render.mjs docs/index.html --out audit.json --shots shots
```

It launches a real headless chromium at 1440, 768 and 390 wide, measures the rendered page, writes
screenshots, and exits non-zero when a check fails. Verdicts are pass, fail, or warn. Nothing reports
green when it could not be measured.

## Measured on 2026-10-05

Thirteen checks, all passing. The numbers that matter:

| What | Result |
| --- | --- |
| worst small text contrast | 5.2:1 (needs 4.5:1) |
| hero headline contrast | 17.13:1 |
| chromatic colors on the page | one, rgb(255, 106, 61) |
| external requests | 0 |
| horizontal overflow at 390, 768, 1440 | 0px |
| hero call to action bottom | 717px at 900 tall, 672px at 844 tall |
| mobile controls under 44px tall | none |
| page weight | 106 KB, fonts included |
| under reduced motion | 0 elements left hidden |

The first audit run failed twice. `no-horizontal-overflow` failed at 253px because the footer grid stayed
three columns on a phone. `mobile-controls-44px` failed because a css specificity mistake left the nav
link at 34px tall. Both are fixed, and the audit is what found them.
