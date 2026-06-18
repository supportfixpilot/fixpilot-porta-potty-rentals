#!/usr/bin/env python3
"""Strip aggregateRating from any JSON-LD on the page.

Handles all observed shapes:
  - block form: "aggregateRating": {\n  "@type": "AggregateRating",\n  ... \n},
  - inline form: , "aggregateRating": {"@type":"AggregateRating", ...}
  - inline form embedded inside Product/Service: ..., "aggregateRating": {...}}
"""
from __future__ import annotations
import glob
import re

# Match the entire aggregateRating key + brace-balanced object,
# with an optional leading comma + whitespace, optional trailing comma.
PATTERN = re.compile(
    r',?\s*"aggregateRating"\s*:\s*\{[^{}]*?"@type"\s*:\s*"AggregateRating"[^{}]*?\}\s*,?',
    re.DOTALL,
)


def real_review_count(html: str) -> int:
    return len(re.findall(r'"@type"\s*:\s*"Review"', html))


def strip(path: str) -> tuple[bool, int, int]:
    html = open(path, encoding="utf-8").read()
    rc = re.search(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    if not rc:
        return False, 0, 0
    claimed = int(rc.group(1))
    actual = real_review_count(html)

    def replace(m: re.Match[str]) -> str:
        # Preserve a single delimiter if removal would join two fields illegally.
        text = m.group(0)
        leading_comma = text.lstrip().startswith(",") or text.startswith(",")
        trailing_comma = text.rstrip().endswith(",")
        if leading_comma and trailing_comma:
            return ","
        return ""

    new_html = PATTERN.sub(replace, html)
    if new_html == html:
        return False, claimed, actual
    open(path, "w", encoding="utf-8").write(new_html)
    return True, claimed, actual


def main() -> None:
    paths = (
        sorted(glob.glob("porta-potty-rental-*-*/index.html"))
        + sorted(glob.glob("services/*.html"))
        + sorted(glob.glob("blog/*.html"))
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
            if claimed and claimed > max(actual, 1):
                print(f"  {path}  (claimed {claimed}, actual {actual})")
        else:
            skipped += 1
    print(f"\nStripped aggregateRating from {stripped} pages; {skipped} had none.")


if __name__ == "__main__":
    main()
