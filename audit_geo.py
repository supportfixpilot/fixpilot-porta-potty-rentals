#!/usr/bin/env python3
"""Audit city pages for geo/schema/content mismatches.

Flags pages where the URL state code disagrees with:
  - <meta name="geo.region" content="US-XX">
  - schema "addressRegion"
  - schema "geo.latitude/longitude" (cross-checked against expected state bbox)

Also flags:
  - aggregateRating reviewCount > number of <Review> entries (fabricated rating)
  - Backslash-escape bug in og:image / twitter:image attributes
  - "Anaheim Ana" / similar broken templating artifacts
  - Hard-coded Atlanta neighborhoods in non-Atlanta pages

Run: python3 audit_geo.py
Outputs: audit_report.md
"""
from __future__ import annotations
import glob
import json
import os
import re
from collections import defaultdict

CITY_GLOB = "porta-potty-rental-*-*/index.html"

# Coarse state-bbox lookup (lat min/max, lon min/max). Generous boundaries.
STATE_BBOX = {
    "AL": (30.1, 35.1, -88.5, -84.9), "AZ": (31.3, 37.1, -114.9, -109.0),
    "CA": (32.5, 42.1, -124.5, -114.0), "CO": (36.9, 41.1, -109.1, -102.0),
    "CT": (40.9, 42.1, -73.8, -71.7),  "FL": (24.4, 31.1, -87.7, -79.9),
    "GA": (30.3, 35.1, -85.7, -80.7),  "ID": (41.9, 49.1, -117.3, -111.0),
    "IL": (36.9, 42.6, -91.6, -87.4),  "IN": (37.7, 41.8, -88.1, -84.7),
    "KS": (36.9, 40.1, -102.1, -94.5), "KY": (36.4, 39.2, -89.7, -81.9),
    "LA": (28.8, 33.1, -94.1, -88.7),  "MA": (41.1, 43.0, -73.6, -69.8),
    "MD": (37.8, 39.8, -79.6, -75.0),  "MI": (41.6, 48.4, -90.5, -82.3),
    "MN": (43.4, 49.5, -97.3, -89.4),  "MO": (35.9, 40.7, -95.9, -89.0),
    "NC": (33.7, 36.7, -84.4, -75.4),  "NJ": (38.8, 41.4, -75.6, -73.8),
    "NV": (35.0, 42.1, -120.1, -113.9), "NY": (40.4, 45.1, -79.9, -71.7),
    "OH": (38.3, 42.0, -84.9, -80.4),  "OK": (33.5, 37.1, -103.1, -94.3),
    "PA": (39.6, 42.4, -80.6, -74.6),  "SC": (32.0, 35.3, -83.4, -78.4),
    "TN": (34.9, 36.7, -90.4, -81.6),  "TX": (25.8, 36.6, -106.7, -93.4),
    "VA": (36.5, 39.5, -83.7, -75.2),  "WA": (45.5, 49.1, -124.8, -116.8),
    "WI": (42.4, 47.1, -92.9, -86.7),
}

ATLANTA_NEIGHBORHOODS = {
    "Virginia-Highland", "Inman Park", "Old Fourth Ward", "Poncey-Highland",
    "Ansley Park", "Piedmont Park", "Candler Park", "Morningside",
    "Grant Park", "Buckhead", "Midtown Atlanta", "Cabbagetown",
}


def slug_state(path: str) -> str | None:
    m = re.search(r"-([a-z]{2})/index\.html$", path)
    return m.group(1).upper() if m else None


def parse_geo_region(html: str) -> str | None:
    m = re.search(r'name="geo\.region"\s+content="US-([A-Z]{2})"', html)
    return m.group(1) if m else None


def parse_geo_position(html: str) -> tuple[float, float] | None:
    m = re.search(r'name="geo\.position"\s+content="([0-9.\-]+);([0-9.\-]+)"', html)
    if not m:
        return None
    try:
        return float(m.group(1)), float(m.group(2))
    except ValueError:
        return None


def parse_address_region(html: str) -> str | None:
    m = re.search(r'"addressRegion"\s*:\s*"([A-Z]{2})"', html)
    return m.group(1) if m else None


def parse_aggregate_rating(html: str) -> tuple[int, int] | None:
    """Return (claimed_count, actual_review_count) when aggregateRating exists."""
    rc = re.search(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    if not rc:
        return None
    claimed = int(rc.group(1))
    actual = len(re.findall(r'"@type"\s*:\s*"Review"', html))
    return claimed, actual


def has_escape_bug(html: str) -> bool:
    return bool(re.search(r'<meta property=\\"og:image\\"', html) or
                re.search(r'<meta name=\\"twitter:image\\"', html))


def list_atlanta_neighborhoods(html: str) -> list[str]:
    found = []
    for name in ATLANTA_NEIGHBORHOODS:
        if re.search(rf'"name"\s*:\s*"{re.escape(name)}"', html):
            found.append(name)
    return found


def has_broken_template(html: str) -> list[str]:
    """Return list of broken-template artifacts found."""
    issues = []
    for pat, label in [
        (r"\bAnaheim Ana\b", "Anaheim Ana"),
        (r"\b\w+ \w+ porta potty rental\b", None),  # noisy; skipped
        (r"\{\{\s*\w+\s*\}\}", "unrendered template variable"),
        # Use (?-i) negative lookahead style: match TODO but NOT Spanish "todo el/la/los/las"
        (r"\bTODO\b(?!\s+el\b|\s+la\b|\s+los\b|\s+las\b|\s+lo\b|\s+un\b)", "TODO marker"),
        # Only flag real developer placeholder text, not CSS pseudo-element ::placeholder
        (r"placeholder(?![-\w]|::|\s*\{|\s*,|,\s*textarea)", "placeholder text"),
    ]:
        if label and re.search(pat, html):
            issues.append(label)
    return issues


def main() -> None:
    rows = []
    summary = defaultdict(int)

    for path in sorted(glob.glob(CITY_GLOB)):
        state = slug_state(path)
        if not state:
            continue

        html = open(path, encoding="utf-8", errors="replace").read()

        issues: list[str] = []

        # Geo region mismatch
        geo_state = parse_geo_region(html)
        if geo_state and geo_state != state:
            issues.append(f"geo.region=US-{geo_state} but URL state={state}")
            summary["geo_region_mismatch"] += 1

        # Geo position mismatch
        coords = parse_geo_position(html)
        if coords and state in STATE_BBOX:
            lat, lon = coords
            la_lo, la_hi, lo_lo, lo_hi = STATE_BBOX[state]
            if not (la_lo <= lat <= la_hi and lo_lo <= lon <= lo_hi):
                issues.append(f"geo.position=({lat},{lon}) outside {state} bbox")
                summary["geo_position_mismatch"] += 1

        # Schema addressRegion mismatch
        addr_region = parse_address_region(html)
        if addr_region and addr_region != state:
            issues.append(f"addressRegion={addr_region} but URL state={state}")
            summary["address_region_mismatch"] += 1

        # Fabricated aggregateRating
        rating = parse_aggregate_rating(html)
        if rating:
            claimed, actual = rating
            if claimed > max(actual, 1) * 3:  # heuristic: >3x discrepancy
                issues.append(f"aggregateRating reviewCount={claimed} but only {actual} Review objects")
                summary["fabricated_rating"] += 1

        # og:image escape bug
        if has_escape_bug(html):
            issues.append("og:image / twitter:image has \\\" escape bug")
            summary["escape_bug"] += 1

        # Atlanta neighborhoods on non-Atlanta page
        if state != "GA" or "atlanta" not in path:
            atl = list_atlanta_neighborhoods(html)
            if atl:
                issues.append(f"Atlanta neighborhoods on non-Atlanta page: {', '.join(atl[:5])}")
                summary["atlanta_neighborhoods"] += 1

        # Broken template
        broken = has_broken_template(html)
        if broken:
            issues.append(f"broken template: {', '.join(broken)}")
            summary["broken_template"] += 1

        if issues:
            rows.append((path, state, issues))

    out = ["# City Page Geo/Data Audit", ""]
    out.append(f"Scanned {len(glob.glob(CITY_GLOB))} city pages.")
    out.append("")
    out.append("## Summary")
    out.append("")
    for key, count in sorted(summary.items(), key=lambda x: -x[1]):
        out.append(f"- **{key}**: {count} pages")
    out.append("")
    out.append(f"**Total flagged pages: {len(rows)}**")
    out.append("")
    out.append("## Pages with issues")
    out.append("")
    for path, state, issues in rows:
        out.append(f"### `{path}` (URL state: {state})")
        for i in issues:
            out.append(f"- {i}")
        out.append("")

    open("audit_report.md", "w").write("\n".join(out))
    print(f"Scanned {len(glob.glob(CITY_GLOB))} pages; flagged {len(rows)}; report → audit_report.md")
    for key, count in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {key:30s} {count}")


if __name__ == "__main__":
    main()
