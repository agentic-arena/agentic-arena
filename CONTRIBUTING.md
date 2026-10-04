# Contributing

Small repo, small rules.

## Branches and commits

- Branch off `main`. Name branches `arena/<short-topic>`, for example `arena/m0-bootstrap`.
- Never commit to `main`. Open a pull request and let CI run.
- Commit messages: a short subject line, then a blank line, then why the change exists. No em dashes.
- Keep commits small. One idea per commit.

## Before you push

```bash
pytest -q
ruff check .
python scripts/lint_copy.py docs README.md CONTRIBUTING.md
```

CI runs the same three commands on Python 3.11, 3.12, and 3.13. If they pass locally, CI should agree.

## Prose

Everything written in this repo follows [docs/voice.md](docs/voice.md): no em or en dashes, no hype
vocabulary, no filler sentence shapes. The linter checks docs, the README, and this file. Quoted material
from another source keeps its original punctuation and carries a `slop-lint:ignore` marker with a citation.

## Skills

Skills live in `skills/` and follow the portable `SKILL.md` format. Arena specific settings go in a
sidecar `arena.yml`, so other tools can still read the skill. A skill that needs a network call or a
credential is not accepted in v1.

## Attribution

If a contribution adapts work from another project, credit it in the file and in the sources list for
that skill. Adapt ideas with attribution. Do not copy files from other projects into this repo.
