#!/usr/bin/env python3
"""Strip fabricated aggregateRating from city pages.

Removes the JSON-LD aggregateRating block (4 lines) wherever the page's
LocalBusiness schema claims more reviews than it carries Review objects.

Default behavior: strip aggregateRating completely. We don't know the real
number of reviews per city, and Google penalises fabricated review counts
more harshly than absent ones. The visible 4.9★ display in HTML is left in
place — only the structured-data claim is removed.

Run: python3 strip_fake_ratings.py
"""
from __future__ import annotations
import glob
import re

CITY_GLOB = "porta-potty-rental-*-*/index.html"

# Match an aggregateRating block of the form:
#   "aggregateRating": {
#     "@type": "AggregateRating",
#     "ratingValue": "...",
#     "reviewCount": "..."
#   },
AGG_BLOCK = re.compile(
    r'\s*"aggregateRating"\s*:\s*\{[^{}]*?"@type"\s*:\s*"AggregateRating"[^{}]*?\}\s*,?\s*\n',
    re.DOTALL,
)


def real_review_count(html: str) -> int:
    return len(re.findall(r'"@type"\s*:\s*"Review"', html))


def strip(path: str) -> tuple[bool, int, int]:
    html = open(path, encoding="utf-8").read()
    m = re.search(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    if not m:
        return False, 0, 0
    claimed = int(m.group(1))
    actual = real_review_count(html)
    new_html, n = AGG_BLOCK.subn("\n", html)
    if n:
        open(path, "w", encoding="utf-8").write(new_html)
    return n > 0, claimed, actual


def main() -> None:
    paths = (
        sorted(glob.glob(CITY_GLOB))
        + sorted(glob.glob("services/*.html"))
        + ["index.html", "locations.html"]
    )
    stripped = 0
    skipped = 0
    for path in paths:
        try:
            ok, claimed, actual = strip(path)
        except FileNotFoundError:
            continue
        if ok:
            stripped += 1
            if claimed and claimed > actual * 2:
                print(f"  {path}  (claimed {claimed}, actual {actual})")
        else:
            skipped += 1
    print(f"\nStripped aggregateRating from {stripped} pages; {skipped} had none.")


if __name__ == "__main__":
    main()
