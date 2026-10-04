# agentic-arena

A small harness that runs portable Agent Skills to build and check real projects.

**Status: early.** This is the M0 skeleton. There is no agent loop and no skills engine yet, so this
repo does not generate anything today. What works: the CLI skeleton, the prose linter, and CI.
The plan and the open decisions are in [docs/plan.md](docs/plan.md) and [docs/decisions.md](docs/decisions.md).

## Why

Coding agents write interfaces that all look the same. The first skill we are building, anti-slop, pushes
an agent to work from real product facts, real tokens, and real components before it invents anything.
It then audits the result with a rubric that produces numbers, not adjectives. Design notes are in
[docs/anti-slop.md](docs/anti-slop.md).

## Install

```bash
git clone https://github.com/agentic-arena/agentic-arena.git
cd agentic-arena
python3 -m venv /tmp/arena-venv
/tmp/arena-venv/bin/pip install -e ".[dev]"
/tmp/arena-venv/bin/arena version
```

Tools and virtualenvs go under `/tmp` on purpose. Nothing lands in your home directory except the
optional secret files the CLI reads, and it never writes those.

## Use

```bash
arena version    # print the version
arena doctor     # report python, git, token file presence, disk
arena skills     # list installed skills
```

`arena doctor` prints file paths and whether they exist. It never reads a token file out loud.

## Test

```bash
pytest -q
ruff check .
python scripts/lint_copy.py docs README.md CONTRIBUTING.md
```

## Repository rules

- One repo per project. This repo never absorbs another project's files.
- Work happens on branches. `main` is protected, and pull requests are required.
- Every claim in the docs must trace to a command that ran. Test counts and measurements are real or absent.
- Prose follows [docs/voice.md](docs/voice.md) and a linter enforces it in CI.

## Docs

| File | What is in it |
| --- | --- |
| [docs/design.md](docs/design.md) | Goals, non-goals, architecture, risks |
| [docs/plan.md](docs/plan.md) | Milestones M0 to M7 and the acceptance checks for each |
| [docs/decisions.md](docs/decisions.md) | The decision register, with what is locked and what is still open |
| [docs/anti-slop.md](docs/anti-slop.md) | Design for the first skill |
| [docs/voice.md](docs/voice.md) | How the agent writes, and what is banned |
| [docs/repo-setup.md](docs/repo-setup.md) | How the repo and its access are set up |

## License

MIT. See [LICENSE](LICENSE).
