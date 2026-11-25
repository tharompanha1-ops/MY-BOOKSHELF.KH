#!/usr/bin/env python3
"""Snapshot every <a href> value in the repo. Used to verify the rebuild
preserves 100% of original link destinations (preservation rule)."""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def hrefs_of(path: str):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    return re.findall(r'<a\b[^>]*\bhref\s*=\s*"([^"]*)"', html, re.IGNORECASE)


manifest = {}
for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    rel = os.path.relpath(f, ROOT)
    manifest[rel] = hrefs_of(f)

out = os.path.join(ROOT, "tools", "link_manifest.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=2)

total = sum(len(v) for v in manifest.values())
print(f"Wrote {out}: {len(manifest)} files, {total} <a href> links")
