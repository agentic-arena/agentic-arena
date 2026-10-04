# agentic-arena, Starting Decisions (discussion register)

**Status tags:** `LOCKED` = you already decided · `DEFAULT` = my proposal, say nothing and it's what we build · `OPEN` = genuinely needs your call · `DEFERRED` = agreed out of v1

Reply with row numbers, or just add rows of your own. Nothing gets built until this list is settled.

---

## A. Product & scope

1. **v1 atomic demo (what "it works" looks like)**, `DEFAULT`: one command → `arena run --skill web-replica --goal "<award-winning style landing page>" --out ./site` → a served page you can click. Nothing else claimed.
2. **Primary audience**, `OPEN`: portfolio reviewers (hiring), open-source contributors, or mainly your own tooling? Changes README tone and how much docs we invest in. My default: **portfolio-first, contributor-second**.
3. **CLI name `arena`**, `DEFAULT`. Alternative: `agentic-arena` (longer to type, same as repo, less confusing for newcomers).
4. **License MIT**, `LOCKED` (repo was created with MIT).
5. **Branding (logo/banner/favicon for docs)**, `OPEN`. Default: skip in v1; a plain, well-written README beats a hobby logo.

## B. Architecture

6. **Python floor**, `DEFAULT`: 3.11 (CI matrix 3.11/3.12/3.13). Higher floor = fewer compat bugs, smaller audience.
7. **Providers in v1**, `DEFAULT`: `mock` (default, offline), OpenAI-compatible, Anthropic. The two real adapters get **request-shape tests only**; README will say "not live-API tested" until you hand me a key.
8. **Skill metadata placement**, `DEFAULT`: `SKILL.md` stays 100% spec-clean (portable to the 40+ clients); arena-specific fields (toolchains, budgets, validators) live in a sidecar `arena.yml`. This is the "universal" mechanism.
9. **How a skill gets chosen**, `OPEN`: v1 default is explicit `--skill <name>` plus `arena skills list`. Auto-selection from the goal text (matching against `description` fields) is more magical but needs a real model to be honest about it. My default: **explicit first, auto-select at M4 if tests can prove it**.
10. **Tool surface for the agent**, `DEFAULT`: `fs` (read/write/list, workspace-rooted), `shell` (allowlist + timeout + output cap), `run_tests`, and `git` limited to `status`/`diff`/`add`/`commit` inside the *target* dir, never to our own repo, never to `main`.
11. **Shell allowlist contents**, `OPEN`. Default: `python3, pip, pytest, node, npm, npx, git, ls, cat, grep, find, mkdir, cp, mv, sed, awk, sort, wc`. **Network tools denied by default** (`curl`, `wget`); opt-in per skill via `arena.yml`. This is the single most security-sensitive list, your input welcome.
12. **Human-in-the-loop**, `OPEN`: (a) fully unattended with `--dry-run` available, or (b) confirm-by-default before shell/git, `--yes` to skip. My default: **(b)**, least surprising for a tool an agent runs on your machine.
13. **Agent loop budget**, `DEFAULT`: step budget (default 25 steps), JSONL trace per run, `--dry-run` guarantees zero writes.
14. **Offline-capable skills**, `DEFAULT`: skills must work with no network. No wallet keys, ever, anywhere. Blockchain skills deferred (see §D).

## C. Repo & process

15. **Branch + PR granularity**, `DEFAULT`: one branch + PR **per milestone** (`arena/m0-bootstrap`, …), small commits inside. Alternative: a PR per task (noisier, more overhead).
16. **Commit convention & identity**, `DEFAULT`: Conventional Commits; commits authored by a neutral identity so no personal email lands in public history.
17. **Lint/format**, `OPEN`: `ruff` (dev-only dependency, not runtime) vs nothing. My default: **ruff in CI**, catches real bugs cheaply.
18. **Coverage**, `DEFAULT`: no coverage gate in v1. I'll report a real number if you ask; I won't claim coverage we never measured.
19. **CI**, `DEFAULT`: GitHub Actions, matrix 3.11/3.12/3.13, `pytest` + ruff. "Require status checks" gets ticked by you **after** our first CI run (GitHub only offers it then).
20. **Secrets**, `LOCKED`: GitHub token at `~/.secrets/gh_token` (600), redacted from all output, never committed; LLM key later at `~/.secrets/llm_key`. **You revoke both when we're done**, the PAT is already in our chat transcript.
21. **Milestone order M0 to M6**, `DEFAULT` (see design doc §6). Change it if you want the demo earlier and polish later.
22. **Cadence**, `OPEN`: gate after **every** milestone (you review + merge, I continue), or let me run M0→M2 straight and review three at once? My default: **gate every milestone** while the process is young.

## E. Anti-slop skill (added 2026-10-04 after source review)

23. **Browser dependency in v1**, `OPEN`. ~275 MB headless Chromium + 12 apt packages, so the agent can measure real rendered output (verified working here). Recommendation: **yes**.
24. **`playwright-cli` as the agent's browser tool**, `OPEN`. It defaults to system Google Chrome (~200 MB more) and its daemon exits without it. Recommendation: **skip in v1**, drive `playwright-core` with our own scripts; revisit as an optional debug skill.
25. **Third-party content**, `OPEN`. Adapt concepts with attribution (recommended) vs vendoring MIT/Apache-2.0 files verbatim. Licenses verified: taste-skill MIT · Vercel guidelines MIT · awesome-design-md MIT · impeccable Apache-2.0 · playwright-cli Apache-2.0.
26. **Mockup-first image generation**, `OPEN`. Needs a paid image API key. Recommendation: **defer to v2**, ship code-led only and say so.
27. **Skills in-repo for v1**, `DEFAULT`: yes, in `skills/`, with the loader accepting any path so they can graduate to standalone repos later.
28. **Replica asset policy**, `DEFAULT`: study layout/typography/spacing/interaction; substitute assets; never ship the reference site's images, fonts, or binaries; record sources in `DESIGN.md`.

29. **Merge policy**, `LOCKED` (revised 2026-10-05 by you). The agent opens a pull request for each
milestone and merges it itself once CI is green. You do not review pull requests. `main` stays protected:
no direct pushes to it, no force pushes, and every change arrives through a pull request. Say the word if
you want direct commits to `main` instead.

30. **Working directory**, `LOCKED` (2026-10-05). Repo work happens in a temp directory under `/tmp`.
The workspace keeps only the token file and files you asked to see. Nothing of value lives only in the
sandbox; it gets pushed.

31. **Voice rules**, `LOCKED`. Everything the agent writes follows `docs/voice.md`: chat replies, docs, README, commit messages, PR bodies, and the copy inside generated sites. No em or en dashes, no hype words, no filler openers. Enforced by `scripts/lint_copy.py` in CI, in the commit hook, and in the agent prompt. Hyphens stay allowed.

## D. Explicitly out of v1 (deferred, not deleted)

Blockchain/wallet skills · multi-agent orchestration · MCP server · hosted service / public deployment · auto-skill-writing ("self-improving") claims · Windows support · package distribution (Homebrew/apt) · web-browsing tool.
