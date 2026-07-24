#!/usr/bin/env python3
"""Replace the header <nav> block in every built HTML page with the one from navdata.py.
Run from the _source folder: python3 patch_nav.py
Safe to re-run any time (idempotent)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from navdata import render_nav

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE = {"financial-freedom": "ff", "productivity": "prod", "life": "life", "tools": "tools"}
NAV_RE = re.compile(r"<nav>.*?</nav>", re.S)


def main():
    patched = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "_")) and d != "images"]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            relpath = os.path.relpath(path, ROOT)
            parts = relpath.split(os.sep)
            if fn == "404.html":
                rel, active = "/", ""   # 404 is served at any depth -> absolute links
            else:
                rel = "../" * (len(parts) - 1)
                active = ACTIVE.get(parts[0], "")
            with open(path, encoding="utf-8") as f:
                html = f.read()
            new_html, n = NAV_RE.subn(render_nav(rel, active), html, count=1)
            if n and new_html != html:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_html)
                patched += 1
    print(f"patched {patched} pages")


if __name__ == "__main__":
    main()
