#!/usr/bin/env python3
"""Broken internal link checker for MY BOOKSHELF.

Scans every HTML page, resolves each internal href/src against the file
tree, and reports links whose target does not exist.

Report-only: this tool never modifies, removes, or rewrites any link.
It exits non-zero when broken links are found, so it can gate CI.
"""
import glob
import os
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
    broken = []
    checked = 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            html = fh.read()
        for m in re.finditer(r'(?:href|src)\s*=\s*"([^"]+)"', html):
            u = m.group(1)
            if not u or u.startswith(("#", "tel:", "mailto:", "javascript:", "data:")):
                continue
            p = urlparse(u)
            if p.scheme in ("http", "https"):
                continue
            rel = unquote(p.path)
            if rel.startswith("/"):
                target = os.path.join(ROOT, rel.lstrip("/"))
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(f), rel))
            checked += 1
            if not os.path.exists(target):
                broken.append((os.path.relpath(f, ROOT), u))

    if broken:
        print(f"❌ {len(broken)} broken internal link(s) found (of {checked} checked):")
        for f, u in broken:
            print(f"  {f}  ->  {u}")
        return 1
    print(f"✅ No broken internal links. ({checked} internal links checked across {len(files)} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
