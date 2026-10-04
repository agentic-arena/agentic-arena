# anti-slop, Skill Design v0.1 (first flagship skill)

**Status:** design for your review · **Nothing built yet.** · **Evidence:** every "verified" line below was measured in this sandbox on 2026-10-04.

## 1. What this skill is for

> "This skill pushes the agent to work from the actual product, existing components, tokens, and real UI
> patterns, instead of inventing another generic SaaS interface.", your brief, verbatim, and it is now the skill's contract.

It does **not** try to teach taste and then claim taste. It does three things, each with evidence:
1. **Ground** the agent in product truth before a line of markup exists.
2. **Constrain** output with explicit, written anti-pattern rules (the "ban list"), not vibes.
3. **Audit** the result with a deterministic rubric, including real rendered measurements, and report
   numbers, never adjectives.

## 2. Design: three layers

### Layer 1, GROUND (product truth before pixels)

The failure mode we are killing: the agent invents a hero, three equal feature cards, a purple gradient, and
a headline about "unlocking potential". That happens because it has no product facts, so it fills the vacuum
with SaaS boilerplate.

So the skill **refuses to design before it has facts**:

| Artifact | Written where | Contents | Rule |
|---|---|---|---|
| `PRODUCT.md` | target project | audience, primary task, real constraints, real copy that exists | Every claim must trace to the brief or a real source. "Do not invent availability" is a hard rule. |
| `DESIGN.md` | target project | tokens (color/type/spacing/radius), component inventory, do/don't | If the project has an existing system, **use it**. If it has components, **reuse them**. |
| `DESIGN.exceptions.md` | target project | every deliberate deviation from a rule, with a reason | Silences the "rule-breaking is normal" ambiguity, an unrecorded exception is a bug. |

**Replica mode** (our demo): the reference page *is* the product truth. The agent:
1. Renders the reference (Playwright) and harvests **real** computed values: palette (background/text/accent),
   font families + sizes + weights + line-heights, spacing rhythm, radius scale, container widths, section order.
2. Writes those into `DESIGN.md` and a `tokens.css` draft.
3. Rebuilds **from the extracted tokens**, not from imagination.
4. Diffs extraction vs build (Δ colour, Δ type scale, Δ spacing), see Layer 3.

**Honesty rule for replicas (also a legal rule):** we replicate *layout, typography, spacing, and interaction
patterns*, with **substitute assets**, never the original site's images, fonts, or binaries. This goes in the
skill, in the README, and in every demo README. Licensing/attribution for the reference is recorded in
`DESIGN.md` sources.

### Layer 2, RULES (the anti-slop playbook)

A credited synthesis of the five sources (see §4), written by us, as `references/`:
- `banned-patterns.md`, the machine-checkable subset is enforced; the rest is advisory.
- `locks.md`, one accent, one radius system, one theme per page.
- `hero-discipline.md`, headline ≤2 lines desktop, subtext ≤20 words, primary CTA visible without scroll, nav ≤80px.
- `motion.md`, CSS > WAAPI > JS; `transform`/`opacity` only; `prefers-reduced-motion` honoured; interruptible.
- `grounding.md`, the layer-1 workflow in step form.
- `sources.md`, attribution table (§4). **We do not paste third-party files into our repo.**

### Layer 3, AUDIT (numbers, not adjectives)

**`scripts/validate_ui.py`, offline, no browser, stdlib-only. Hard checks (fail = non-zero exit):**

| # | Check | Threshold |
|---|---|---|
| 1 | HTML parses, no unclosed tags, one `<h1>` |, |
| 2 | Heading order has no skipped levels |, |
| 3 | Every `<img>` has `alt` (or explicit `alt=""` + `role="presentation"`) |, |
| 4 | `:focus-visible` styles exist for interactive elements |, |
| 5 | `prefers-reduced-motion` block exists if any animation declared |, |
| 6 | Declared colour pairs meet contrast | **AA 4.5:1** body · **3:1** large text · **3:1** UI borders |
| 7 | Single accent colour across all CTA/primary surfaces | exactly 1 |
| 8 | Radius values drawn from ≤1 declared scale | ≤1 system, or recorded exception |
| 9 | Font families used | ≤2 (+1 mono) |
| 10 | Every asset reference is local (self-contained) | 0 external requests |
| 11 | Banned strings in copy: em/en dashes, "Scroll to explore", "V1.0 / BETA", "Lisbon 14:23"-style strips | 0 |
| 12 | Banned structures: 3-equal-card feature row as the only evidence section, div-built fake product UI, pills overlaid on photos | 0 |
| 13 | Page weight budget | ≤ 300 KB total, no single asset > 150 KB |

**`scripts/audit_render.py`, needs the browser (verified working here). Measured, not parsed:**
- **Real** computed contrast on the rendered DOM (verified: measured `11.8:1` on a test page this session).
- Hero fits inside the first viewport at 1440×900 and 390×844 (verified viewport control + DPR-2 screenshots work).
- Tap targets ≥ 24 px (44 px on mobile viewports) measured from bounding boxes.
- No horizontal overflow at 390 px.
- Replica delta: reference vs build, colour ΔE, type-scale Δ, spacing Δ, section-order match.
- Screenshots at 390 / 768 / 1440 for human eyes; the numbers are the gate, the screenshots are the evidence.

**Report format:** JSON + a human summary. `PASS` · `FAIL` · **`UNVERIFIED`**, and `UNVERIFIED` is never
silently upgraded to `PASS`. If the browser is unavailable, render checks report `UNVERIFIED`, not green.

Copy checks share the same word list as the repo voice rules (`docs/voice.md`), so a page the agent ships reads the same way the agent talks.

## 3. Skill bundle anatomy

```
skills/anti-slop/
├── SKILL.md              # spec-clean (portable to every Skills client). name/description only + body <5k tokens
├── arena.yml             # OUR sidecar: requires.playwright, validator scripts, budgets, rubric thresholds
├── references/           # banned-patterns · locks · hero-discipline · motion · grounding · sources
├── scripts/
│   ├── validate_ui.py    # offline hard checks, stdlib only
│   ├── extract_tokens.py # replica mode: reference → tokens.json (playwright-core)
│   └── audit_render.py   # eyes: measurements + screenshots (playwright-core)
└── assets/
    ├── tokens.template.css
    └── reset.css
```
`SKILL.md` stays portable; everything arena-specific lives in `arena.yml` so other clients can still use the skill.

## 4. Sources, licenses, and exactly how we use each

| Source | License (verified) | How we use it |
|---|---|---|
| [taste-skill](https://www.tasteskill.dev/), `Leonxlnx/taste-skill`, 92.5k★ | **MIT** | **Adapt ideas with attribution**: ban-list concepts, 3 locks, hero discipline, brief-inference, pre-flight checklist. We write our own text. |
| [Vercel Web Interface Guidelines](https://vercel.com/design/guidelines), `vercel-labs/web-interface-guidelines` | **MIT** | **Reference + machine-check subset**: keyboard/focus, tap targets, reduced-motion, `transition: all`, loading states. Link as authority; checks are ours. |
| [awesome-design-md](https://github.com/VoltAgent/awesome-design-md), 119.5k★, 74 DESIGN.md files | **MIT** | **Format adoption**: `DESIGN.md` (Google Stitch format) as our Layer-1 artifact. We do **not** ship their files; users may drop one in themselves. |
| [Impeccable](https://impeccable.style/), npm `impeccable` v4.1.0 | **Apache-2.0** | **Adapt the workflow ideas**: PRODUCT.md, evidence-based claims ("do not invent availability"), critique→polish→harden loop, mockup-first vs code-led. Their plugin is Claude/Codex-shaped; our runtime is our own loop. |
| [playwright-cli](https://github.com/microsoft/playwright-cli), 13.8k★ | **Apache-2.0** | **Optional skill later**, not the v1 engine, see §5. |

Attribution lives in `references/sources.md` and the README. Nothing is claimed as original that isn't.

## 5. Verified feasibility (measured here today)

| Claim | Receipt |
|---|---|
| Headless Chromium renders in this sandbox | `RENDER OK … contrast 11.8` from live computed styles; screenshots 780×1688 @2× DPR |
| Disk cost is manageable after pruning | Full chromium 399 MB + headless shell 270 MB → **kept headless shell only: 275 MB total**; `/tmp` at 30% used |
| System deps installable | `playwright install-deps chromium` under passwordless `sudo` → **missing libs: 0** (12 packages) |
| `playwright-cli` v0.1.22 installs | ✅, but its `open` defaults to **system Google Chrome** (`/opt/google/chrome/chrome`) and its daemon exits without it; `--browser` accepts `chrome, firefox, webkit, msedge`, **not our bundled chromium** |
| Therefore | v1 engine = **`playwright-core` driven by our own scripts** (works now, headless-shell only). `playwright-cli` becomes an optional debug skill if we accept a ~200 MB+ system-Chrome install. |

## 6. Non-goals

- ❌ No "this looks premium" claim without a passing rubric + screenshots to show.
- ❌ No shipping third-party assets, fonts, or images from a reference site.
- ❌ No image-generation mockup path in v1 (needs a paid API key), code-led path only, and the docs will say so.
- ❌ No subjective score ("design quality: 8/10"). Numbers we can defend, or `UNVERIFIED`.
- ❌ No claiming third-party work as ours; attribution is mandatory in `references/sources.md`.
