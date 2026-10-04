"""M0 checks: the CLI reports, never guesses, and never leaks a token."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from arena import __version__, cli


def test_version_prints_release_string(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.run(["version"]) == 0
    out = capsys.readouterr().out.strip()
    assert re.fullmatch(r"arena \d+\.\d+\.\d+.*", out), out
    assert __version__ in out


def test_version_flag_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.run(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_args_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.run([]) == 0
    assert "usage: arena" in capsys.readouterr().out


def test_unknown_command_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.run(["frobnicate"])
    assert exc.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_doctor_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.run(["doctor"]) == 0
    assert "arena doctor" in capsys.readouterr().out


def test_doctor_never_prints_token_contents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake = tmp_path / "gh_token"
    fake.write_text("github_pat_FAKEVALUE1234567890", encoding="utf-8")
    monkeypatch.setenv("ARENA_GITHUB_TOKEN_FILE", str(fake))
    assert cli.run(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "github_pat_" not in out
    assert "FAKEVALUE" not in out
    assert "present" in out


def test_doctor_reports_missing_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ARENA_GITHUB_TOKEN_FILE", str(tmp_path / "nope"))
    assert cli.run(["doctor"]) == 0
    assert "missing" in capsys.readouterr().out


def test_skills_empty_dir_says_so(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.run(["skills", "--skills-dir", str(tmp_path)]) == 0
    assert "no skills installed yet" in capsys.readouterr().out


def test_skills_lists_bundles(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    for name in ("anti-slop", "web-replica"):
        d = tmp_path / name
        d.mkdir()
        (d / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
    (tmp_path / "not-a-skill").mkdir()
    assert cli.run(["skills", "--skills-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out.split()
    assert out == ["anti-slop", "web-replica"]
