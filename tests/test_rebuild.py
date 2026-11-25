#!/usr/bin/env python3
"""Rebuild integrity tests for MY BOOKSHELF.

These tests enforce the project's hard preservation rule: every original
<a href> destination must survive the rebuild untouched, and the shared
design system must be wired into every page.

Run:  python3 tests/test_rebuild.py
"""
import glob
import os
import re
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILES = sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))


def hrefs_of_text(html):
    return re.findall(r'<a\b[^>]*\bhref\s*=\s*"([^"]*)"', html, re.I)


def git_head(rel):
    return subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        capture_output=True, text=True, cwd=ROOT,
    ).stdout


def test_all_original_links_preserved():
    """No original <a href> may be removed, renamed, or re-pointed."""
    failures = []
    for f in HTML_FILES:
        rel = os.path.relpath(f, ROOT)
        old = hrefs_of_text(git_head(rel))
        new = hrefs_of_text(open(f, encoding="utf-8").read())
        missing = Counter(old) - Counter(new)
        if missing:
            failures.append((rel, dict(missing)))
    assert not failures, f"Links were altered:\n{failures}"
    print(f"✅ test_all_original_links_preserved — all original hrefs intact")


def test_every_page_uses_shared_css_and_js():
    """Each page must link the shared stylesheet and behaviour script."""
    for f in HTML_FILES:
        html = open(f, encoding="utf-8").read()
        assert "assets/css/style.css" in html, f"{f} missing shared CSS"
        assert "assets/js/app.js" in html, f"{f} missing shared JS"
    print(f"✅ test_every_page_uses_shared_css_and_js — {len(HTML_FILES)} pages wired")


def test_every_page_has_skip_link_and_theme_toggle():
    for f in HTML_FILES:
        html = open(f, encoding="utf-8").read()
        assert "skip-link" in html, f"{f} missing skip link"
        assert "themeToggle" in html, f"{f} missing theme toggle"
    print(f"✅ test_every_page_has_skip_link_and_theme_toggle — {len(HTML_FILES)} pages")


def test_no_duplicated_script_blocks_remain():
    """The shared app.js replaces the inline footer/nav toggle blocks."""
    for f in HTML_FILES:
        html = open(f, encoding="utf-8").read()
        assert "footerObserver" not in html, f"{f} still has duplicated footer reveal"
        assert "menuToggle.addEventListener" not in html, f"{f} still has duplicated menu toggle"
        assert "iconToggle.addEventListener" not in html, f"{f} still has duplicated icon toggle"
    print("✅ test_no_duplicated_script_blocks_remain — no duplication left")


def test_no_credentials_in_client_code():
    """The Telegram bot token must never appear in shipped client code."""
    for f in HTML_FILES:
        html = open(f, encoding="utf-8").read()
        assert "9075440568" not in html, f"{f} exposes Telegram bot token"
        assert "AAE6zporO" not in html, f"{f} exposes Telegram bot token"
    print("✅ test_no_credentials_in_client_code — no token in client code")


def test_contact_form_uses_secure_api():
    html = open(os.path.join(ROOT, "contactpage.html"), encoding="utf-8").read()
    assert "CONTACT_API_URL" in html, "contact form not rewired to API"
    assert "api/contact" in html, "contact form not pointing at /api/contact"
    print("✅ test_contact_form_uses_secure_api")


def test_page_css_files_exist():
    """Every page's extracted CSS file must exist on disk."""
    for f in HTML_FILES:
        rel = os.path.relpath(f, ROOT)
        slug = rel.replace(os.sep, "__").rsplit(".", 1)[0]
        css = os.path.join(ROOT, "assets", "css", "pages", f"{slug}.css")
        assert os.path.exists(css), f"missing page CSS: {css}"
    print(f"✅ test_page_css_files_exist — {len(HTML_FILES)} page CSS files present")


def test_no_inline_style_blocks_left():
    """Inline <style> blocks were extracted to per-page CSS files."""
    for f in HTML_FILES:
        html = open(f, encoding="utf-8").read()
        assert "<style>" not in html, f"{f} still has an inline <style> block"
    print("✅ test_no_inline_style_blocks_left — all CSS extracted")


def main():
    tests = [
        test_all_original_links_preserved,
        test_every_page_uses_shared_css_and_js,
        test_every_page_has_skip_link_and_theme_toggle,
        test_no_duplicated_script_blocks_remain,
        test_no_credentials_in_client_code,
        test_contact_form_uses_secure_api,
        test_page_css_files_exist,
        test_no_inline_style_blocks_left,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"❌ {t.__name__}: {e}")
            failed += 1
    print()
    if failed:
        print(f"{failed} test(s) FAILED")
        sys.exit(1)
    print(f"🎉 All {len(tests)} tests passed")


if __name__ == "__main__":
    main()
