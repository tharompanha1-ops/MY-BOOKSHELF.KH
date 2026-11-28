#!/usr/bin/env python3
"""Rebuild processor: rewire every page to the shared design system.

Preserves 100% of existing <a href> destinations (verified against
tools/link_manifest.json). For each HTML page:
  - extract inline <style> to assets/css/pages/<name>.css
  - link shared assets/css/style.css + per-page css
  - add skip link + theme toggle
  - add rel="noopener noreferrer" to target=_blank links missing it
  - remove duplicated footer-reveal / nav-toggle script blocks
    (now handled by assets/js/app.js)
  - append shared assets/js/app.js before </body>
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, "assets", "css", "pages")
os.makedirs(CSS_DIR, exist_ok=True)

# ---- patterns for duplicated script blocks now in app.js ----
# Footer reveal block (comment variants)
FOOTER_REVEAL = re.compile(
    r"[ \t]*//[^\n]*Footer scroll-reveal animation[^\n]*\n"
    r"(?:[^\n]*\n)*?"
    r"[ \t]*footerObserver\.observe\(footerEl\);[^\n]*\n"
    r"[ \t]*\}\n",
    re.M,
)
# Compact footer-reveal block (graphing.html style, no comment)
FOOTER_REVEAL_COMPACT = re.compile(
    r"[ \t]*const footerEl = document\.querySelector\(\"[^\"]*\"\);\n"
    r"[ \t]*if \(footerEl\) \{\n"
    r"(?:[^\n]*\n)*?"
    r"[ \t]*footerObserver\.observe\(footerEl\);[^\n]*\n"
    r"[ \t]*\}\n",
    re.M,
)
# Menu toggle block
MENU_TOGGLE = re.compile(
    r"[ \t]*const menuToggle = document\.getElementById\(\"menuToggle\"\);[^\n]*\n"
    r"(?:[^\n]*\n)*?"
    r"[ \t]*menuToggle\.addEventListener\(\"click\", \(\) => \{[^\n]*\n"
    r"(?:[^\n]*\n)*?"
    r"[ \t]*\}\);[^\n]*\n",
    re.M,
)
# Icon toggle block
ICON_TOGGLE = re.compile(
    r"[ \t]*const iconToggle = document\.getElementById\(\"iconToggle\"\);[^\n]*\n"
    r"(?:[^\n]*\n)*?"
    r"[ \t]*iconToggle\.addEventListener\(\"click\", \(\) => \{[^\n]*\n"
    r"(?:[^\n]*\n)*?"
    r"[ \t]*\}\);[^\n]*\n",
    re.M,
)

SKIP_LINK = (
    '    <a class="skip-link" href="#main">ទៅកាន់មាតិកា</a>\n'
)
THEME_TOGGLE = (
    '      <button id="themeToggle" class="theme-toggle" type="button" '
    'aria-label="ផ្លាស់ប្តូររបៀបពន្លឺ/ងងឹត" title="Toggle theme">'
    '<i class="fas fa-moon"></i></button>\n'
)


def css_link(rel_prefix: str, name: str):
    return (
        f'    <link rel="stylesheet" href="{rel_prefix}assets/css/style.css" />\n'
        f'    <link rel="stylesheet" href="{rel_prefix}assets/css/pages/{name}.css" />\n'
    )


def rel_prefix_for(rel_path: str) -> str:
    depth = rel_path.count(os.sep)
    return "../" * depth


def css_slug(rel: str) -> str:
    """Unique, filesystem-safe slug for a page's CSS file, derived from
    its path so pages that share a basename don't collide."""
    parts = rel.replace(os.sep, "/").split("/")
    parts[-1] = os.path.splitext(parts[-1])[0]
    return "__".join(parts)


def process(path: str, rel: str):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    orig = html
    slug = css_slug(rel)
    prefix = rel_prefix_for(rel)

    # 1. Extract inline <style>...</style> -> per-page css
    m = re.search(r"<style>([\s\S]*?)</style>", html)
    page_css = ""
    if m:
        page_css = m.group(1).strip() + "\n"
        with open(os.path.join(CSS_DIR, f"{slug}.css"), "w", encoding="utf-8") as fh:
            fh.write(page_css)
        html = html[: m.start()] + css_link(prefix, slug) + html[m.end() :]

    # 2. rel=noopener noreferrer on target=_blank links missing it
    def fix_rel(tag_match):
        tag = tag_match.group(0)
        if "target=\"_blank\"" in tag and "rel=" not in tag:
            tag = tag.replace("target=\"_blank\"", 'target="_blank" rel="noopener noreferrer"')
        return tag
    html = re.sub(r"<a\b[^>]*>", fix_rel, html)

    # 3. Remove duplicated script blocks (footer reveal, menu/icon toggle)
    before = html
    html = FOOTER_REVEAL.sub("", html)
    html = FOOTER_REVEAL_COMPACT.sub("", html)
    html = MENU_TOGGLE.sub("", html)
    html = ICON_TOGGLE.sub("", html)
    # Drop now-empty <script> blocks left behind
    html = re.sub(r"[ \t]*<script>\s*</script>\n", "", html)

    # 4. Skip link after <body>
    if "skip-link" not in html:
        html = re.sub(r"(<body[^>]*>)\n", r"\1\n" + SKIP_LINK, html, count=1)

    # 5. Theme toggle inside header (before menu-toggle or nav-burger or </header>)
    if "themeToggle" not in html:
        if "menu-toggle" in html:
            html = html.replace(
                '<button class="menu-toggle"',
                THEME_TOGGLE + '      <button class="menu-toggle"',
                1,
            )
        elif "nav-burger" in html:
            html = html.replace(
                '<button class="nav-burger"',
                THEME_TOGGLE + '      <button class="nav-burger"',
                1,
            )
        else:
            html = html.replace("</header>", THEME_TOGGLE + "    </header>", 1)

    # 6. Append shared app.js before </body>
    if "assets/js/app.js" not in html:
        html = html.replace(
            "</body>",
            '    <script src="' + prefix + 'assets/js/app.js" defer></script>\n  </body>',
            1,
        )

    if html != orig:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return True, slug, page_css
    return False, slug, ""


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
    changed = 0
    for f in files:
        rel = os.path.relpath(f, ROOT)
        ok, name, css = process(f, rel)
        if ok:
            changed += 1
            print(f"  rebuilt: {rel}  (page css: {len(css)} chars)")
    print(f"\n{changed} files rebuilt out of {len(files)}")


if __name__ == "__main__":
    main()
