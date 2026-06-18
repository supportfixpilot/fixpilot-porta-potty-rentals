#!/usr/bin/env python3
"""Add contextual links from blog posts to relevant service + city pages.

For each blog post:
  - Append a "Related: ..." inline block at the bottom of the article body
    (just before <footer> or </body>), with 2-3 service links + 1 city link
    chosen by topical relevance.

Blog → service mapping is hand-coded from the post slug. City link rotates by
post (uses a small set of high-traffic cities).

Idempotent: skips posts that already contain the marker comment.
"""
from __future__ import annotations
import os
import re

CITY_ROTATION = [
    ("austin-tx", "Austin, TX"),
    ("houston-tx", "Houston, TX"),
    ("phoenix-az", "Phoenix, AZ"),
    ("atlanta-ga", "Atlanta, GA"),
    ("denver-co", "Denver, CO"),
    ("nashville-tn", "Nashville, TN"),
    ("dallas-tx", "Dallas, TX"),
    ("chicago-il", "Chicago, IL"),
    ("miami-fl", "Miami, FL"),
    ("seattle-wa", "Seattle, WA"),
    ("charlotte-nc", "Charlotte, NC"),
    ("boston-ma", "Boston, MA"),
    ("philadelphia-pa", "Philadelphia, PA"),
    ("san-diego-ca", "San Diego, CA"),
]

# Per-post related links: each entry = list of (label, href) for services + 1 city.
RELATED: dict[str, list[tuple[str, str]]] = {
    "porta-potty-rental-costs-2026.html": [
        ("Standard porta potty rental", "/services/standard-porta-potty"),
        ("Deluxe porta potty rental", "/services/deluxe-porta-potty"),
        ("Luxury restroom trailer rental", "/services/luxury-restroom-trailers"),
    ],
    "porta-potty-rental-prices-2026.html": [
        ("Standard porta potty rental", "/services/standard-porta-potty"),
        ("Construction porta potty rental", "/services/construction-porta-potty-rentals"),
        ("Event restroom trailer rental", "/services/event-restroom-trailers"),
    ],
    "wedding-porta-potty-rental-guide.html": [
        ("Luxury restroom trailer rental", "/services/luxury-restroom-trailers"),
        ("VIP trailer rental", "/services/vip-trailers-rental"),
        ("ADA-compliant unit rental", "/services/ada-compliant-units"),
    ],
    "how-many-porta-potties-for-wedding.html": [
        ("Luxury restroom trailer rental", "/services/luxury-restroom-trailers"),
        ("Free porta potty calculator", "/calculator"),
        ("Hand wash station rental", "/services/hand-wash-stations"),
    ],
    "osha-requirements-construction-sites.html": [
        ("Construction porta potty rental", "/services/construction-porta-potty-rentals"),
        ("Hand wash station rental", "/services/hand-wash-stations"),
        ("ADA-compliant unit rental", "/services/ada-compliant-units"),
    ],
    "ada-compliant-porta-potties.html": [
        ("ADA-compliant unit rental", "/services/ada-compliant-units"),
        ("Handicap portable toilet rental", "/services/handicap-portable-toilets"),
        ("Hand wash station rental", "/services/hand-wash-stations"),
    ],
    "hand-wash-station-requirements.html": [
        ("Hand wash station rental", "/services/hand-wash-stations"),
        ("Construction porta potty rental", "/services/construction-porta-potty-rentals"),
        ("Standard porta potty rental", "/services/standard-porta-potty"),
    ],
    "event-sanitation-checklist.html": [
        ("Event restroom trailer rental", "/services/event-restroom-trailers"),
        ("Hand wash station rental", "/services/hand-wash-stations"),
        ("Standard porta potty rental", "/services/standard-porta-potty"),
    ],
    "luxury-vs-standard-porta-potties.html": [
        ("Standard porta potty rental", "/services/standard-porta-potty"),
        ("Luxury restroom trailer rental", "/services/luxury-restroom-trailers"),
        ("VIP trailer rental", "/services/vip-trailers-rental"),
    ],
    "porta-potty-permits-guide.html": [
        ("Construction porta potty rental", "/services/construction-porta-potty-rentals"),
        ("Event restroom trailer rental", "/services/event-restroom-trailers"),
        ("Standard porta potty rental", "/services/standard-porta-potty"),
    ],
    "porta-potty-placement-guide.html": [
        ("Construction porta potty rental", "/services/construction-porta-potty-rentals"),
        ("Standard porta potty rental", "/services/standard-porta-potty"),
        ("Crane-hook porta potty", "/services/crane-hook-porta-potty-rentals"),
    ],
    "porta-potty-servicing-schedule.html": [
        ("Construction porta potty rental", "/services/construction-porta-potty-rentals"),
        ("Septic pumping &amp; holding tanks", "/services/septic-pumping-holding-tanks"),
        ("Standard porta potty rental", "/services/standard-porta-potty"),
    ],
    "same-day-porta-potty-rental.html": [
        ("Emergency / short-term rentals", "/services/emergency-short-term-rentals"),
        ("Standard porta potty rental", "/services/standard-porta-potty"),
        ("Event restroom trailer rental", "/services/event-restroom-trailers"),
    ],
    "winter-porta-potty-tips.html": [
        ("Standard porta potty rental", "/services/standard-porta-potty"),
        ("Hand wash station rental", "/services/hand-wash-stations"),
        ("Construction porta potty rental", "/services/construction-porta-potty-rentals"),
    ],
}

MARKER = "<!-- related-block-v1 -->"


def build_block(svc_links: list[tuple[str, str]], city_slug: str, city_label: str) -> str:
    items = "\n".join(
        f'      <li><a href="{href}" class="text-blue-700 underline hover:text-blue-900 font-semibold">{label}</a></li>'
        for label, href in svc_links
    )
    return (
        f'\n{MARKER}\n'
        '<aside class="max-w-3xl mx-auto px-4 my-12 bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">\n'
        '  <h3 class="font-extrabold text-lg text-gray-900 mb-3">Need a quote? We deliver same-day.</h3>\n'
        '  <p class="text-gray-700 mb-3">Related rentals you can book today:</p>\n'
        '  <ul class="space-y-1 mb-4">\n'
        f'{items}\n'
        '  </ul>\n'
        '  <p class="text-gray-700 text-sm">'
        f'Looking local? See our <a href="/porta-potty-rental-{city_slug}" class="text-blue-700 underline font-semibold">{city_label} porta potty rentals</a> '
        'or <a href="/locations" class="text-blue-700 underline font-semibold">all 224 service areas</a>.</p>\n'
        '  <p class="mt-4 font-bold text-gray-900">Call <a href="tel:+18336529344" class="text-green-700 underline">(833) 652-9344</a> for an instant quote.</p>\n'
        '</aside>\n'
    )


def patch(filename: str, svc_links: list[tuple[str, str]], idx: int) -> bool:
    path = f"blog/{filename}"
    if not os.path.exists(path):
        return False
    html = open(path, encoding="utf-8").read()
    if MARKER in html:
        return False
    city_slug, city_label = CITY_ROTATION[idx % len(CITY_ROTATION)]
    block = build_block(svc_links, city_slug, city_label)
    new_html, n = re.subn(r"<footer", lambda _m: block + "<footer", html, count=1)
    if n == 0:
        new_html, n = re.subn(r"</body>", lambda _m: block + "</body>", html, count=1)
    if n == 0:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    fixed = 0
    for i, (filename, svc_links) in enumerate(sorted(RELATED.items())):
        if patch(filename, svc_links, i):
            print(f"  added related block to blog/{filename}")
            fixed += 1
        else:
            print(f"  skipped blog/{filename}")
    print(f"\nUpdated {fixed} blog posts.")


if __name__ == "__main__":
    main()
