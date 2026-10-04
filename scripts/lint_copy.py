#!/usr/bin/env python3
"""lint_copy.py: catch AI slop in prose.

Checks three things:
  1. em dashes, en dashes, figure dashes, horizontal bars, and minus signs used as dashes
  2. a swap list of hype words and phrases, with a plainer replacement for each
  3. sentence shapes that read like generated filler

Stdlib only. Skips fenced code blocks unless you pass --include-code.
Two pragmas are honoured:
  slop-lint:ignore-file    anywhere in the file, skips the whole file
  slop-lint:ignore         on a line, skips that line

Usage:
  python3 lint_copy.py FILE_OR_DIR [FILE_OR_DIR ...]
  python3 lint_copy.py --format json docs/ README.md
  python3 lint_copy.py --self-test

Exit codes: 0 clean or warnings only, 1 errors found, 2 usage or read error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

DASH_CHARS = {
    "\u2014": "em dash",
    "\u2013": "en dash",
    "\u2012": "figure dash",
    "\u2015": "horizontal bar",
    "\u2212": "minus sign used as a dash",
}

DASH_FIX = "use a comma, a colon, or a full stop; hyphens are fine"

# (phrase, severity, suggested replacement)
SWAPS: list[tuple[str, str, str]] = [
    # errors: clear hype or vague filler
    ("leverage", "error", "use"),
    ("leveraging", "error", "using"),
    ("utilize", "error", "use"),
    ("utilizes", "error", "uses"),
    ("utilization", "error", "use"),
    ("seamless", "error", "say what works without friction"),
    ("seamlessly", "error", "say how it works"),
    ("robust", "error", "say what holds up, and where"),
    ("comprehensive", "error", "complete, full, or say what it covers"),
    ("elevate", "error", "raise, improve"),
    ("elevating", "error", "raising, improving"),
    ("unlock", "error", "start, open, get"),
    ("unleash", "error", "release, start"),
    ("empower", "error", "let, help, give"),
    ("empowering", "error", "helping, letting"),
    ("delve", "error", "look at, read, dig into"),
    ("delving", "error", "looking at"),
    ("realm", "error", "area, field"),
    ("tapestry", "error", "mix, range"),
    ("pivotal", "error", "important, key, or say why"),
    ("meticulous", "error", "careful"),
    ("meticulously", "error", "carefully"),
    ("foster", "error", "build, encourage"),
    ("fostering", "error", "building, encouraging"),
    ("streamline", "error", "simplify, cut steps from"),
    ("streamlined", "error", "simplified"),
    ("cutting-edge", "error", "new, current, or name the technique"),
    ("state-of-the-art", "error", "best available, or name the technique"),
    ("best-in-class", "error", "say the number or name the benchmark"),
    ("world-class", "error", "name the benchmark"),
    ("game-changer", "error", "say what changed, with numbers"),
    ("game changer", "error", "say what changed, with numbers"),
    ("paradigm", "error", "model, approach"),
    ("synergy", "error", "say what the two things do together"),
    ("holistic", "error", "whole-system, or say what is included"),
    ("commence", "error", "start"),
    ("endeavor", "error", "try"),
    ("embark", "error", "start"),
    ("nestled", "error", "sitting, located"),
    ("boasts", "error", "has"),
    ("testament", "error", "proof, evidence"),
    ("underscores", "error", "shows"),
    ("revolutionize", "error", "change, replace"),
    ("revolutionary", "error", "new, different, or say what changed"),
    ("transformative", "error", "say what changed and how much"),
    ("unparalleled", "error", "say the comparison"),
    ("supercharge", "error", "speed up, improve"),
    ("turbocharge", "error", "speed up"),
    ("plethora", "error", "many"),
    ("myriad", "error", "many"),
    ("multitude", "error", "many"),
    ("ever-evolving", "error", "changing"),
    ("ever-changing", "error", "changing"),
    ("harness the power", "error", "use"),
    ("the power of", "error", "say what it does"),
    ("next level", "error", "better, more"),
    ("look no further", "error", "cut it, say what you built"),
    ("in today's fast-paced world", "error", "cut it"),
    ("in today's digital world", "error", "cut it"),
    ("when it comes to", "error", "for, about"),
    ("at the end of the day", "error", "cut it"),
    ("in conclusion", "error", "cut it"),
    ("furthermore", "error", "also, and"),
    ("moreover", "error", "also"),
    ("it is important to note", "error", "say the thing"),
    ("it's important to note", "error", "say the thing"),
    ("it is worth noting", "error", "say the thing"),
    ("dive into", "error", "start, read"),
    ("dive deep", "error", "look closely"),
    ("let's dive", "error", "start with, begin with"),
    ("unpack", "error", "explain"),
    ("curated", "error", "chosen, picked"),
    ("bespoke", "error", "custom"),
    ("crafted", "error", "made, built"),
    ("battle-tested", "error", "say where it ran"),
    ("future-proof", "error", "say what it survives"),
    ("paving the way", "error", "say what enabled it"),
    ("plays a vital role", "error", "say what it does"),
    ("plays a crucial role", "error", "say what it does"),
    ("got you covered", "error", "cut it"),
    ("great question", "error", "answer the question"),
    ("as an ai", "error", "cut it, just answer"),
    ("i hope this helps", "error", "cut it"),
    ("hope this helps", "error", "cut it"),
    ("feel free to reach out", "error", "cut it, offer the specific next step"),
    ("happy to help", "error", "cut it"),
    ("let me know if you need", "error", "cut it, or ask one specific question"),
    # warnings: softer tells
    ("thoughtful", "warn", "say what the thinking was"),
    ("thoughtfully", "warn", "say what the thinking was"),
    ("must-have", "warn", "say why"),
    ("a must", "warn", "say why"),
    ("unpack that", "warn", "explain it"),
    ("is a must", "warn", "say why"),
    ("we're excited to", "warn", "just announce it"),
    ("thrilled to", "warn", "just announce it"),
    ("imagine if you", "warn", "cut it"),
    ("stands as", "warn", "is"),
    ("serves as", "warn", "is"),
    ("a testament to", "warn", "evidence of"),
    ("navigate the complexities", "warn", "handle the hard parts"),
    ("in a world where", "warn", "cut it"),
    ("whether you're", "warn", "name one reader"),
    ("not only", "warn", "write two sentences"),
]

PATTERNS: list[tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"\bit'?s not just\b[^.!?\n]{0,60}\bit'?s\b", re.IGNORECASE), "error",
     "it's not just X, it's Y", "pick one, state it plainly"),
    (re.compile(r"\bwe'?re (excited|thrilled|proud|delighted)\b", re.IGNORECASE), "error",
     "enthusiasm announcement", "just announce it"),
    (re.compile(r"\b(imagine|picture) (a world|a future|if you)\b", re.IGNORECASE), "error",
     "imagine a world opener", "cut it"),
    (re.compile(r"[\U0001F680\U0001F525\U0001F4A1\U0001F31F\u2728]", re.UNICODE), "warn",
     "emoji used as hype", "cut it"),
]

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
             ".mypy_cache", ".ruff_cache", ".pytest_cache", "site-packages", ".egg-info"}
DEFAULT_EXTS = (".md", ".markdown", ".txt", ".rst", ".html", ".htm")


def is_ignored_file(text: str) -> bool:
    return "slop-lint:ignore-file" in text[:2000]


def scan_text(path: str, text: str, include_code: bool = False) -> list[dict]:
    """Return a list of violations: line, col, severity, kind, found, fix."""
    out: list[dict] = []
    in_code = False
    lines = text.splitlines()
    for lineno, raw in enumerate(lines, start=1):
        line = raw
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code and not include_code:
            continue
        if "slop-lint:ignore" in line:
            continue
        # normalise curly apostrophes for matching only; positions stay identical
        norm = line.replace("\u2019", "'")

        for ch, name in DASH_CHARS.items():
            idx = line.find(ch)
            while idx != -1:
                out.append({"line": lineno, "col": idx + 1, "severity": "error", "kind": "dash",
                            "found": f"{name} {ch!r}", "fix": DASH_FIX})
                idx = line.find(ch, idx + 1)

        for phrase, severity, fix in SWAPS:
            bounded = r"(?<![A-Za-z0-9-])" + re.escape(phrase) + r"(?![A-Za-z0-9-])"
            pat = re.compile(bounded, re.IGNORECASE)
            for m in pat.finditer(norm):
                out.append({"line": lineno, "col": m.start() + 1, "severity": severity,
                            "kind": "word", "found": m.group(0), "fix": fix})

        for pat, severity, kind, fix in PATTERNS:
            for m in pat.finditer(norm):
                out.append({"line": lineno, "col": m.start() + 1, "severity": severity,
                            "kind": kind, "found": m.group(0).strip()[:60], "fix": fix})
    return out


def iter_files(paths: list[str], exts: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith(".egg-info")]
                for f in sorted(files):
                    if f.lower().endswith(exts):
                        found.append(os.path.join(root, f))
        else:
            found.append(p)
    return found


def run(paths: list[str], fmt: str, include_code: bool, exts: tuple[str, ...]) -> int:
    files = iter_files(paths, exts)
    report, errors, warnings, skipped = [], 0, 0, []
    for path in files:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"cannot read {path}: {exc}", file=sys.stderr)
            return 2
        if is_ignored_file(text):
            skipped.append(path)
            continue
        v = scan_text(path, text, include_code)
        if v:
            report.append({"path": path, "violations": v})
            errors += sum(1 for x in v if x["severity"] == "error")
            warnings += sum(1 for x in v if x["severity"] == "warn")
    totals = {"files_scanned": len(files) - len(skipped), "files_skipped": len(skipped),
              "errors": errors, "warnings": warnings}
    if fmt == "json":
        print(json.dumps({"files": report, "skipped": skipped, "totals": totals}, indent=2))
    else:
        for entry in report:
            for v in entry["violations"]:
                print(f"{entry['path']}:{v['line']}:{v['col']}: {v['severity']}: {v['kind']}: "
                      f"{v['found']!r} | fix: {v['fix']}")
        for s in skipped:
            print(f"{s}: skipped (slop-lint:ignore-file)")
        print(f"\n{totals['errors']} errors, {totals['warnings']} warnings, "
              f"{totals['files_scanned']} files scanned, {totals['files_skipped']} skipped")
    return 1 if errors else 0


SELF_TEST_CASES = [
    ("clean", "I built the thing. It runs in 40 ms. Tests pass.\n", 0, 0),
    ("em dash", "It works \u2014 most of the time.\n", 1, 0),
    ("en dash", "Pages 3\u20135 are missing.\n", 1, 0),
    ("hyphen ok", "Pages 3-5 are fine, and --flag is fine.\n", 0, 0),
    ("swap", "We leverage a seamless pipeline.\n", 2, 0),
    ("shape", "It's not just a tool, it's a platform.\n", 1, 0),
    ("ignore line ok", "We leverage this. slop-lint:ignore\n", 0, 0),
    ("fence skipped", "```\nwe leverage a seamless thing\n```\n", 0, 0),
]


def self_test() -> int:
    failures = 0
    for name, text, want_err, want_warn in SELF_TEST_CASES:
        v = scan_text("<self-test>", text)
        got_err = sum(1 for x in v if x["severity"] == "error")
        got_warn = sum(1 for x in v if x["severity"] == "warn")
        ok = (got_err, got_warn) == (want_err, want_warn)
        print(f"{'ok  ' if ok else 'FAIL'} {name}: errors={got_err} warnings={got_warn} "
              f"(want {want_err}/{want_warn})")
        failures += 0 if ok else 1
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("<!-- slop-lint:ignore-file -->\nWe leverage everything \u2014 seamlessly.\n")
        with open(p, encoding="utf-8") as fh:
            ignored = is_ignored_file(fh.read())
        print(f"{'ok  ' if ignored else 'FAIL'} ignore-file pragma detected")
        failures += 0 if ignored else 1
    print(f"\nself-test: {'passed' if failures == 0 else str(failures) + ' failed'}")
    return 0 if failures == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Catch AI slop in prose.")
    ap.add_argument("paths", nargs="*", help="files or directories to scan")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--include-code", action="store_true", help="also scan fenced code blocks")
    ap.add_argument("--ext", default=",".join(e.lstrip(".") for e in DEFAULT_EXTS),
                    help="comma separated extensions for directory scans")
    ap.add_argument("--self-test", action="store_true", help="run internal checks and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.paths:
        ap.print_usage(sys.stderr)
        return 2
    exts = tuple("." + e.strip().lstrip(".").lower() for e in args.ext.split(",") if e.strip())
    return run(args.paths, args.format, args.include_code, exts)


if __name__ == "__main__":
    sys.exit(main())
