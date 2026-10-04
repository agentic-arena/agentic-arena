#!/usr/bin/env python3
"""Turn on GitHub Pages for a repository, using a config file.

No owner, repo, or account name lives in this script. Point it at whichever
account and repository you like:

  python3 scripts/publish.py status    --owner agentic-arena --repo agentic-arena
  python3 scripts/publish.py enable    --owner agentic-arena --repo agentic-arena --yes
  python3 scripts/publish.py check

The token comes from --token-file, ARENA_GITHUB_TOKEN_FILE, or ~/.secrets/gh_token.
It is never printed, and errors are redacted before they reach the terminal.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REDACT = re.compile(r"(github_pat_|gh[pousr]_)[A-Za-z0-9_]+")
CONFIG = Path(__file__).resolve().parent.parent / "publish" / "pages.json"


def redact(text: str) -> str:
    return REDACT.sub("[REDACTED]", str(text))


def token_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    env = os.environ.get("ARENA_GITHUB_TOKEN_FILE")
    return Path(env) if env else Path.home() / ".secrets" / "gh_token"


def token(explicit: str | None) -> str:
    path = token_path(explicit)
    if not path.is_file():
        sys.exit(f"no token file at {path}. pass --token-file or set ARENA_GITHUB_TOKEN_FILE.")
    return path.read_text(encoding="utf-8").strip()


def api(method: str, url: str, tok: str, payload: dict | None = None) -> tuple[int, object]:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + tok,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "arena-publish",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode() or "null"
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode() or "null")
        except Exception:
            body = {"message": "unparseable error body"}
        return exc.code, body
    except OSError as exc:
        return -1, {"message": redact(exc)}


def load_config() -> dict:
    if not CONFIG.is_file():
        sys.exit(f"missing config: {CONFIG}")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def cmd_check(args: argparse.Namespace) -> int:
    cfg = load_config()
    site = Path(__file__).resolve().parent.parent / cfg["site_dir"] / cfg["index"]
    problems = []
    if not site.is_file():
        problems.append(f"{site} is missing. run showcase/build.py first.")
    else:
        text = site.read_text(encoding="utf-8")
        # only things the browser loads count. outbound links are navigation, not requests.
        loaded = [
            r'<(?:img|script|iframe|source|video|audio)[^>]*\ssrc="(https?://[^"]+)"',
            r'<link[^>]*rel="stylesheet"[^>]*href="(https?://[^"]+)"',
            r'url\((https?://[^)]+)\)',
        ]
        external: list[str] = []
        for pattern in loaded:
            external += re.findall(pattern, text)
        if external:
            problems.append(f"{len(external)} external asset references: {external[:3]}")
        if "{{" in text and "}}" in text:
            problems.append("template placeholders left unfilled")
    print(f"site: {site}")
    print(f"size: {site.stat().st_size if site.is_file() else 0} bytes")
    for p in problems:
        print(f"problem: {p}")
    print("check: ok" if not problems else "check: failed")
    return 1 if problems else 0


def _print_pages_state(owner: str, repo: str, tok: str) -> int:
    status, body = api("GET", f"https://api.github.com/repos/{owner}/{repo}/pages", tok)
    if status == 404:
        print(f"{owner}/{repo}: pages is off")
        return 1
    if status != 200:
        print(f"{owner}/{repo}: could not read pages state [{status}]: "
              f"{redact(body.get('message') if isinstance(body, dict) else body)}")
        return 2
    if isinstance(body, dict):
        print(f"{owner}/{repo}: pages on, url {body.get('html_url')}, "
              f"source {(body.get('source') or {}).get('branch')}"
              f"{(body.get('source') or {}).get('path')}, status {body.get('status')}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    tok = token(args.token_file)
    rc = _print_pages_state(args.owner, args.repo, tok)
    build_url = f"https://api.github.com/repos/{args.owner}/{args.repo}/pages/builds/latest"
    status, builds = api("GET", build_url, tok)
    if status == 200 and isinstance(builds, dict):
        print(f"last build: {builds.get('status')}"
              f" ({builds.get('error') or 'no error'}) at {builds.get('updated_at')}")
    return rc


def cmd_enable(args: argparse.Namespace) -> int:
    cfg = load_config()
    pages = cfg["pages"]
    if not args.yes:
        print("this turns on github pages for "
              f"{args.owner}/{args.repo} from {pages['branch']}{pages['folder']}.")
        print("re-run with --yes to do it.")
        return 0
    tok = token(args.token_file)
    status, body = api("POST", f"https://api.github.com/repos/{args.owner}/{args.repo}/pages", tok,
                       {"source": {"branch": pages["branch"], "path": pages["folder"]}})
    if status in (201, 204):
        print(f"pages enabled for {args.owner}/{args.repo} "
              f"from {pages['branch']}{pages['folder']}")
        print("url: " + pages["url_template"].format(owner=args.owner, repo=args.repo))
        return 0
    if status == 409:
        print("pages is already enabled; nothing to do")
        return _print_pages_state(args.owner, args.repo, tok)
    print(f"failed [{status}]: {redact(body.get('message') if isinstance(body, dict) else body)}")
    return 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="GitHub Pages control, config driven.")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check", help="verify the built site before publishing")
    p.set_defaults(func=cmd_check)

    for name, func in (("status", cmd_status), ("enable", cmd_enable)):
        sp = sub.add_parser(name, help=f"{name} pages for a repository")
        sp.add_argument("--owner", required=True)
        sp.add_argument("--repo", required=True)
        sp.add_argument("--token-file", default=None)
        if name == "enable":
            sp.add_argument("--yes", action="store_true", help="actually make the change")
        sp.set_defaults(func=func)

    args = ap.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
