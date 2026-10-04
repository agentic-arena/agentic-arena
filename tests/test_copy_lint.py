"""The prose rules are enforced, not promised.

If someone writes an em dash into a doc, or drops "leverage" into the README, CI goes red.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINT = REPO / "scripts" / "lint_copy.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(LINT), *args],
        cwd=REPO,
        capture_output=True,
        text=True,
    )


def test_linter_self_test_passes() -> None:
    result = run("--self-test")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "self-test: passed" in result.stdout


def test_linter_fails_on_em_dash(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("This works \u2014 honest.\n", encoding="utf-8")
    result = run(str(bad))
    assert result.returncode == 1
    assert "em dash" in result.stdout


def test_linter_clean_on_repo_prose() -> None:
    targets = ["docs", "README.md", "CONTRIBUTING.md"]
    existing = [t for t in targets if (REPO / t).exists()]
    result = run(*existing)
    assert result.returncode == 0, result.stdout
    assert "0 errors" in result.stdout
