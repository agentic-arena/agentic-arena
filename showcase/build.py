#!/usr/bin/env python3
"""Build the showcase page: subset the fonts, embed them, write index.html.

Fonts are fetched from Google Fonts (see SOURCES.md for the exact URLs and licenses),
subset to the glyphs this page actually uses, then base64 embedded so the page makes
zero network requests. Rebuild with:

  python3 build.py --fonts-dir ./fonts --set-contrast 12.1 --set-kb 88 --set-requests 0
"""
from __future__ import annotations

import argparse
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
def subset(src: Path, text_file: Path, out: Path) -> None:
    cmd = [
        sys.executable, "-m", "fontTools.subset", str(src),
        f"--text-file={text_file}",
        "--flavor=woff2",
        "--layout-features=*",
        "--drop-tables+=DSIG",
        f"--output-file={out}",
    ]
    # needs: pip install fonttools brotli
    subprocess.run(cmd, check=True)


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=str(HERE / "index.template.html"))
    ap.add_argument("--fonts-dir", default=str(HERE / "fonts"))
    ap.add_argument("--out", default=str(HERE.parent / "docs" / "index.html"))
    ap.add_argument("--set-contrast", default="")
    ap.add_argument("--set-kb", default="")
    ap.add_argument("--set-requests", default="0")
    args = ap.parse_args()

    template = Path(args.template).read_text(encoding="utf-8")
    fonts = Path(args.fonts_dir)

    with tempfile.TemporaryDirectory() as td:
        glyphs = Path(td) / "glyphs.txt"
        glyphs.write_text(template, encoding="utf-8")
        sizes = {}
        blobs = {}
        for name in ("inter", "serif", "serif-italic", "mono"):
            src = fonts / f"{name}.woff2"
            out = Path(td) / f"{name}.subset.woff2"
            subset(src, glyphs, out)
            sizes[name] = out.stat().st_size
            blobs[name] = b64(out)

    html = template
    for key, name in (("FONT_INTER", "inter"), ("FONT_SERIF", "serif"),
                      ("FONT_SERIF_ITALIC", "serif-italic"), ("FONT_MONO", "mono")):
        html = html.replace(f"{{{{{key}}}}}", blobs[name])
    if args.set_contrast:
        html = html.replace("{{CONTRAST}}", args.set_contrast)
    if args.set_kb:
        html = html.replace("{{PAGE_KB}}", args.set_kb)
    html = html.replace("{{REQUESTS}}", args.set_requests)

    out_path = Path(args.out)
    out_path.write_text(html, encoding="utf-8")
    for name, size in sizes.items():
        print(f"  {name}.subset.woff2: {size:>6} bytes")
    print(f"  total font bytes: {sum(sizes.values())}")
    print(f"  wrote {out_path} ({out_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
