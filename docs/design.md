# agentic-arena, Design Document v0.2

**Date:** 2026-10-04 · **Author:** lead engineer (agent) · **Status:** awaiting your "go"
**Repo (planned):** `agentic-arena` (public, one repo per project) · **Setup guide:** `docs/repo-setup.md`

> v0.2 changes: (1) harness is **no longer Go-only**, the runtime language is a tool, universality lives
> in skills; (2) added **portability requirements** so any of your accounts can operate the repo;
> (3) stack-per-project is now declared by each skill. Sources for spec claims are cited inline; every
> environmental claim was measured in this sandbox on 2026-10-04.

**Decisions locked (2026-10-04, you):**
- **Identity:** single-purpose **GitHub Organization** owns the repo; personal accounts join as Owners. → procedure in `docs/repo-setup.md`.
- **Harness language: Python 3.11+**, stdlib-first + PyYAML. Tools/provisioning under `/tmp`.
- **Repo name:** `agentic-arena`. **License:** MIT (default, tell me if you want another).
- **Provider:** mock-first; real keys optional and additive.
- **Voice:** human writing everywhere, no em or en dashes, no hype words. Enforced by `scripts/lint_copy.py` in CI. Canonical file: `docs/voice.md`.

---

## 1. What we're building

A **stack-agnostic agent harness** that loads portable **Agent Skills** (`SKILL.md` folders), runs a
plan → act → observe → verify loop against a pluggable LLM provider, and produces real, verifiable
projects, starting with a static website replica. New capability = new skill folder, never a core change.

**For:** you, as a portfolio project, and other agent builders, skills stay portable to every client
that reads the open Agent Skills format (40+ clients as of Sep 2026;
[1](https://atlan.com/know/ai-agent/ai-agent-skills/what-are-agent-skills/)).

**Why this shape:** the format is a folder with a required `SKILL.md` (YAML frontmatter: `name` ≤64 chars
kebab-case, `description` ≤1024 chars stating *what + when*; body <5k tokens) plus optional `references/`,
`scripts/`, `assets/` loaded on demand (progressive disclosure). **No conformance test suite exists yet**, 
that's our open-source contribution angle ([1](https://ylanglabs.com/blogs/agent-skills),
[2](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)).

## 2. Stack philosophy (v0.2)

**The harness is one small program. The universality is the skills.**

- **Harness:** Python 3.11+, **stdlib-first with a single runtime dependency (PyYAML)** for frontmatter.
  Rationale: already present here (3.13.14, pytest installed, measured), fastest iteration to a working
  demo, zero-install for contributors, and the CLI contract stays small enough to port later if we ever
  need single-binary distribution. Runner-up: TypeScript (Node 20.20.2 also present).
- **What the agent builds:** anything. Each skill declares its own toolchain in an `arena.yml` sidecar
  (kept out of `SKILL.md` frontmatter so other clients still parse the skill cleanly):
  ```yaml
  # skills/<name>/arena.yml
  requires: { toolchains: ["node>=20", "python>=3.11"] }
  ```
  `arena doctor --provision` installs missing toolchains under `/tmp` (never your home folder).
- **Consequence:** Go, Rust, TS, Python, plain HTML targets are all first-class, they're a skill
  authoring detail, not an architecture decision.

## 3. Goals

- **G1, Capability = skill folder.** No core code change to add a stack or a workflow.
- **G2, Honest verification.** Deterministic validators with shown output. "Award-winning" is measured
  by checkable proxies (contrast ≥4.5:1, heading order, spacing scale, reduced-motion, self-contained
  assets, byte budget), never by taste claims.
- **G3, Zero-key usability.** Tests, CI and the demo run on a deterministic `mock` provider.
- **G4, Contribution-ready.** `arena skill-lint` (spec conformance) + skill-authoring guide.
- **G5, Provable in sandbox.** Demo ends in a served, clickable page.
- **G6, Account-portable (new in v0.2).** Nothing about the owner, remote, or token path is baked into
  the code; any of your accounts can operate the same repo.
- **G7, Voice (new in v0.3).** Everything the agent writes, including the copy inside sites it generates, passes the copy linter. Rules live in `docs/voice.md`, renamed to `docs/voice.md` in the repo.

## 4. Non-goals (v0.1)

- ❌ No hosted SaaS, no multi-tenant service. Local CLI + static demo server.
- ❌ No auto-merge, no pushes to `main`, no writes to repos other than a target you name.
- ❌ **No nested projects:** `agentic-arena` never absorbs another project's files. Targets live in their
  own repos/dirs (your one-repo-per-project rule, enforced by design).
- ❌ No blockchain/wallet/private-key code in v0.1 (deferred to a skill later, see R2 for the real constraint).
- ❌ No paid services, no signups, no key required. No "self-improving" claims, skills land via human PR.
- ❌ No MCP server, no browsing tool, no multi-agent orchestration.
- ❌ No Windows claim (Linux/macOS only, stated in README). No Homebrew/apt distribution.

## 5. Architecture

```
agentic-arena (Python 3.11+ CLI, stdlib + PyYAML)
├── src/arena/
│   ├── cli.py            run | skills | skill-lint | doctor | serve | version
│   ├── providers/        base.py · mock.py (deterministic, fixture-driven) · openai.py · anthropic.py · redact.py
│   ├── tools/            fs.py (workspace-rooted) · shell.py (allowlist+timeout) · git.py · run_tests.py
│   ├── agent/            loop.py (plan→act→observe→verify) · trace.py (JSONL) · budget.py
│   └── skills/           loader.py · validate.py (spec linter) · disclose.py (progressive disclosure)
├── skills/web-replica/   SKILL.md · arena.yml · references/ · scripts/validate_site.py · assets/
├── tests/
└── .github/workflows/ci.yml
```

**Safety posture (enforced, tested):** fs tools rooted at a workspace dir, traversal/symlink escapes
rejected; shell allowlist + timeouts + output caps; all traces/logs through the redactor; keys read from
env or `~/.secrets/`, never written by the tool.

**Portability (G6), enforced in code review:** `--remote`, `--token-file`, env `ARENA_REMOTE` /
`ARENA_GITHUB_TOKEN_FILE`; no hardcoded owner/repo/URLs anywhere in `src/` or `skills/`; commits authored
as a neutral identity by default (no personal email in public history).

## 6. Milestones (each ≤ 1 day)

| # | Milestone | Acceptance checks (written first; verified by shown output) |
|---|---|---|
| **M0** | Skeleton + CI (0.5d) | `python -m pytest` output shown; `arena version` prints; CI matrix 3.11/3.12/3.13 green on the PR; MIT LICENSE; README with zero unbacked claims |
| **M1** | Provider layer (1d) | Mock determinism tests; adapter tests against a **local fake HTTP server** asserting exact request shape; redactor test proves a fake key never appears in output; `arena doctor` prints redacted config |
| **M2** | Tools + safety (1d) | **Negative tests:** `../` traversal rejected, symlink escape rejected, non-allowlisted command rejected, timeout kills, output truncated. Happy paths covered too |
| **M3** | Loop + traces (1d) | End-to-end with mock provider in a temp workspace produces expected files; JSONL trace asserts step order + budget cutoff; `--dry-run` writes nothing |
| **M4** | Skills engine + linter (1d) | Conformance table test (bad name, >64 chars, missing field, >1024-char description, dir/name mismatch → useful errors); progressive disclosure asserted; `arena skill-lint` passes on our own bundles |
| **M5** | First skill: `web-replica` + demo (1d) | `arena run --skill web-replica --goal "…" --out ./site` reproducible; `validate_site.py` output shown (contrast, heading order, self-containment, byte budget); page served in-sandbox → clickable preview |
| **M6** | Release + docs (0.5d) | README audited claim-by-claim against code; CONTRIBUTING + skill-authoring guide; tag `v0.1.0`; PR open, **not merged** |

Each milestone runs the five roles, Planner (checks first) → Builder (small commits) → Tester (raw
output) → Reviewer (skeptic pass) → Release (docs + PR + summary).

## 7. Risks

| # | Risk | Measured reality (2026-10-04) | Mitigation |
|---|---|---|---|
| **R1** | Org/repo/token not set up → blocks M0 push | `~/.secrets` absent; `gh` absent; `api.github.com` reachable (200) | `docs/repo-setup.md`, 10-min checklist, entirely on your side |
| **R2** | **/tmp is a 993 MB tmpfs**, heavy toolchains won't fit there | `df`: 993M `/tmp`, 20G `/` | Provision toolchains per skill; if a target needs more (Go/Rust dep trees), relocate caches to `/var/tmp` (root fs). Blockchain targets stay deferred until this is proven |
| **R3** | Harness-language bet (Python) | Python 3.13.14 + pytest present; Node 20.20.2 present | Single runtime dep, documented CLI contract; if you veto, TS rework costs ~2 days **now** (only M0 exists) and more later |
| **R4** | "Award-winning" is unfalsifiable |, | Reduced to the proxy checks in G2; README states exactly what is and isn't claimed |
| **R5** | Adapters unverifiable against live APIs without a key | No key present | Tested against local fakes only; README labels them "request-shape tested, not live-API tested" |
| **R6** | Scope creep ("builds anything") |, | §4 non-goals; new capability = queued skill, never incidental |
| **R7** | Sandbox resets / tmpfs wipes | Stated in your brief | Small commits, push every task, branch pushed at each milestone |
| **R8** | Community skills commonly carry security flaws (36% figure reported in research) |, | Our skills: no network calls, stdlib-only scripts; `skill-lint` flags injection smells; Reviewer reads skills as code |

## 8. Definition of Done (per milestone)

Tests pass with **output shown** · README matches reality · branch pushed · PR open (never merged by me) ·
short summary with the PR link and run commands.
