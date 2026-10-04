"""Command line entry point.

Small on purpose. M0 only reports what it can see: which Python, whether git is
there, whether a token file exists (never its contents), and what skills are on
disk. Nothing here talks to a network or writes files.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__

DEFAULT_TOKEN_FILE = Path.home() / ".secrets" / "gh_token"
DEFAULT_LLM_KEY_FILE = Path.home() / ".secrets" / "llm_key"


def repo_root() -> Path:
    """Repo root for a src layout checkout: src/arena/cli.py -> parents[2]."""
    return Path(__file__).resolve().parents[2]


def token_file_path() -> Path:
    override = os.environ.get("ARENA_GITHUB_TOKEN_FILE")
    return Path(override) if override else DEFAULT_TOKEN_FILE


def _git_version() -> str:
    if not shutil.which("git"):
        return "missing"
    try:
        out = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, timeout=10, check=False
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _disk(path: str) -> str:
    try:
        usage = shutil.disk_usage(path)
        free_mb = usage.free // (1024 * 1024)
        return f"{free_mb} MB free"
    except OSError:
        return "unavailable"


def cmd_version(_args: argparse.Namespace) -> int:
    print(f"arena {__version__}")
    return 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    """Print what the environment looks like. Paths only, never file contents."""
    tok = token_file_path()
    llm = DEFAULT_LLM_KEY_FILE
    browsers = os.environ.get(
        "PLAYWRIGHT_BROWSERS_PATH", str(Path.home() / ".cache" / "ms-playwright")
    )
    print("arena doctor")
    print(f"  python          {sys.version.split()[0]}")
    print(f"  executable      {sys.executable}")
    print(f"  git             {_git_version()}")
    print(f"  repo root       {repo_root()}")
    print(f"  token file      {tok} ({'present' if tok.is_file() else 'missing'})")
    print(f"  llm key file    {llm} ({'present' if llm.is_file() else 'missing'})")
    print(f"  browsers        {browsers} ({'present' if Path(browsers).exists() else 'missing'})")
    print(f"  tmp             {_disk('/tmp')}")
    print(f"  workspace       {_disk(str(repo_root()))}")
    return 0


def cmd_skills(args: argparse.Namespace) -> int:
    skills_dir = Path(args.skills_dir) if args.skills_dir else repo_root() / "skills"
    if not skills_dir.is_dir():
        print("no skills installed yet")
        return 0
    names = sorted(
        child.name for child in skills_dir.iterdir() if (child / "SKILL.md").is_file()
    )
    if not names:
        print("no skills installed yet")
        return 0
    for name in names:
        print(name)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arena",
        description="Run portable Agent Skills against real projects.",
    )
    parser.add_argument("--version", action="version", version=f"arena {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="command")

    p_version = sub.add_parser("version", help="print the version and exit")
    p_version.set_defaults(func=cmd_version)

    p_doctor = sub.add_parser("doctor", help="report what the environment looks like")
    p_doctor.set_defaults(func=cmd_doctor)

    p_skills = sub.add_parser("skills", help="list installed skills")
    p_skills.add_argument(
        "--skills-dir", default=None, help="directory to scan (default: <repo>/skills)"
    )
    p_skills.set_defaults(func=cmd_skills)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return int(args.func(args))


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
