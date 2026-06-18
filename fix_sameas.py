#!/usr/bin/env python3
"""Remove blank sameAs URLs (facebook.com/, yelp.com/) from all city page schemas."""

import glob
import re

CITY_GLOB = "porta-potty-rental-*-*/index.html"

# Patterns for the blank social URLs to remove
BLANK_URLS = [
    '"https://www.facebook.com/"',
    '"https://www.yelp.com/"',
]


def fix_sameas(html: str) -> tuple[str, bool]:
    changed = False
    for url in BLANK_URLS:
        if url not in html:
            continue
        # Remove the URL and its trailing/leading comma from the array
        # Pattern: remove line containing the URL (with optional comma)
        new_html = re.sub(
            r',?\s*\n\s*' + re.escape(url) + r'\s*,?',
            '',
            html
        )
        if new_html != html:
            html = new_html
            changed = True
    return html, changed


def main():
    paths = sorted(glob.glob(CITY_GLOB))
    fixed = 0
    for path in paths:
        with open(path, encoding='utf-8', errors='replace') as f:
            html = f.read()
        new_html, changed = fix_sameas(html)
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            fixed += 1
    print(f"Fixed sameAs in {fixed}/{len(paths)} pages")


if __name__ == '__main__':
    main()
