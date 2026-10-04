# agentic-arena, Integrated Build Plan v0.3 (anti-slop first)

**Supersedes:** design doc §6 milestone table (v0.2) · **Status:** awaiting your go · **Companion:** `docs/anti-slop.md`

## 1. What changed and why

Your steer, "first skill/feature is Anti UI slop", reorders the plan: the design skill becomes the **flagship
and the proof** that the harness works, instead of a generic website generator. The harness work (M0 to M4) is
unchanged; the *skill* work (M5 and M6) is now anti-slop, and the replica demo becomes the evidence that it works.

Two engineering facts from today's feasibility work reshape provisioning:
- **The agent can have eyes.** Headless Chromium renders here (275 MB after pruning to headless shell; deps installed via `playwright install-deps`).
- **`playwright-cli` is not the v1 engine.** It wants system Google Chrome, which we won't install by default. We drive `playwright-core` ourselves; the CLI stays an optional skill.

## 2. Repo layout (single repo, one project)

```
agentic-arena/
├── src/arena/            # harness: cli · providers · tools · agent loop · skills engine
├── skills/
│   ├── anti-slop/        # flagship skill (SKILL.md + arena.yml + references + scripts + assets)
│   ├── project-init/     # PRODUCT.md / DESIGN.md intake interview
│   └── web-replica/      # replica workflow: extract tokens from a reference → build → diff
├── tests/                # unit + end-to-end with mock provider; golden files for skill outputs
├── docs/                 # skill-authoring guide, rubric reference, demo walkthrough
├── .github/workflows/    # CI: 3.11/3.12/3.13 × pytest + ruff; browser job for render tests
└── scripts/provision.sh  # toolchains + browsers under /tmp or /var/tmp; never the home folder
```
Skills live in-repo in v1 so we can iterate with the harness; the loader takes any path (or a future
URL/git install), so skills can graduate to their own repos without code changes.

## 3. Revised milestones

| # | Milestone | Acceptance checks (written first; shown with real output) |
|---|---|---|
| **M0** | Skeleton + CI (0.5d) | `pytest` output shown · `arena version` runs · CI green on 3.11/3.12/3.13 · LICENSE, README, CONTRIBUTING · PR open · `docs/voice.md` + `scripts/lint_copy.py` in CI, with 0 errors on the repo's own prose |
| **M1** | Provider layer (1d) | Mock determinism; adapters vs local fake HTTP server (request-shape asserted); redactor test; `arena doctor` redacted output |
| **M2** | Tools + safety + **browser policy** (1d) | Negative tests: traversal, symlink escape, non-allowlisted command, timeout, output cap · browser tool is opt-in per skill · `provision.sh` installs browsers outside home, verified idempotent |
| **M3** | Agent loop + traces (1d) | End-to-end with mock provider in temp workspace; JSONL trace asserts step order + budget cutoff; `--dry-run` writes nothing |
| **M4** | Skills engine + linter (1d) | Spec conformance table (bad name/length/mismatch → useful errors); progressive disclosure asserted; `arena skill-lint` passes on our own three skills |
| **M5** | **anti-slop skill: grounding + rules + static validator** (1d) | `validate_ui.py` on a deliberately sloppy fixture fails with specific codes; on a clean fixture passes; every rubric row in the design doc maps to a named test; fully offline |
| **M6** | **render audit + replica demo** (1d) | `audit_render.py` reports measured contrast/tap targets/overflow/hero-fit at 390·768·1440 · replica diff numbers (Δ colour/type/spacing) · screenshots attached to the PR · demo page served in-sandbox → you click it |
| **M7** | Release + docs (0.5d) | README audited claim-by-claim vs code · skill-authoring guide · demo walkthrough with the real transcript · tag `v0.1.0` · PR open, not merged |

Every milestone still runs the five roles (Planner → Builder → Tester → Reviewer → Release) with raw output.

## 4. Risks added by this scope

| # | Risk | Mitigation |
|---|---|---|
| **R9** | Browser footprint vs 993 MB `/tmp` tmpfs | Headless-shell only (275 MB verified); browsers default to `/var/tmp` (root fs, 20 GB free); `arena doctor` warns before installing; CI installs fresh |
| **R10** | Render checks unavailable ⇒ false green | `UNVERIFIED` is a distinct verdict; CI runs the browser job so the gate stays honest |
| **R11** | Copying reference sites | Substitute assets only; layout/typography study, never their binaries/fonts; sources recorded in `DESIGN.md` |
| **R12** | Third-party skill content and licenses | Attribution table (verified: MIT ×3, Apache-2.0 ×2); we adapt with our own text; no vendored third-party files in v1 |
| **R13** | Rubric becomes an unmaintainable checklist | Each check is a named test with a code; advisory rules clearly separated from hard gates |
| **R14** | The voice rules drift as the repo grows | The linter runs in CI, in the commit hook, and inside the anti-slop skill, so new prose and generated copy get checked the same way |

## 5. Decisions I need from you (also in the decisions register)

1. **Browser dependency in v1**, accept a ~275 MB browser + 12 apt packages so the agent has eyes? (My recommendation: **yes**; it is what makes "no slop" verifiable.)
2. **`playwright-cli` as an agent-facing tool**, skip in v1 (needs ~200 MB+ system Chrome), or install Chrome so the CLI works as designed? (My recommendation: **skip in v1**, drive `playwright-core` ourselves; add it in v2 as an optional debug skill.)
3. **Third-party content**, adapt ideas with attribution (my recommendation), or vendor MIT/Apache files verbatim where allowed?
4. **Mockup-first image path**, the "generate a reference image, then build toward it" workflow needs a paid image API. Defer to v2 and ship code-led only? (My recommendation: **defer**.)
5. **Skills in-repo for v1**, confirm, with graduation to standalone repos later.
