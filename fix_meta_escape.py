#!/usr/bin/env python3
"""Fix og:image / twitter:image meta tags that have literal backslash-quotes
instead of real quotes — broken HTML caused by template generation.

Pattern: <meta property=\"og:image\" content=\"https://...">
Fix to:  <meta property="og:image" content="https://...">
"""
import glob
import re

PATTERNS = [
    (r'<meta property=\\"og:image\\" content=\\"([^"]*)"', r'<meta property="og:image" content="\1"'),
    (r'<meta name=\\"twitter:image\\" content=\\"([^"]*)"', r'<meta name="twitter:image" content="\1"'),
]


def fix_file(path: str) -> int:
    html = open(path, encoding="utf-8").read()
    fixes = 0
    for src, dst in PATTERNS:
        html, n = re.subn(src, dst, html)
        fixes += n
    if fixes:
        open(path, "w", encoding="utf-8").write(html)
    return fixes


def main() -> None:
    paths = (
        glob.glob("porta-potty-rental-*-*/index.html")
        + glob.glob("services/*.html")
        + glob.glob("blog/*.html")
        + ["index.html", "locations.html"]
    )
    total_files = 0
    total_fixes = 0
    for path in sorted(paths):
        try:
            n = fix_file(path)
        except FileNotFoundError:
            continue
        if n:
            total_files += 1
            total_fixes += n
    print(f"Fixed {total_fixes} occurrences in {total_files} files.")


if __name__ == "__main__":
    main()
