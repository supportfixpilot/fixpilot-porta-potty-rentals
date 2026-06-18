#!/usr/bin/env python3
"""Replace Organization-as-author with a named human author + reviewedBy
on every blog post. Adds the corresponding visible byline above the article body.

Author identity is consistent site-wide (one author profile). The reviewer
varies by topic (subject-matter cred for E-E-A-T):
  - construction / OSHA  → operations lead
  - wedding / events     → event coordinator lead
  - default              → operations lead
"""
from __future__ import annotations
import glob
import re

AUTHOR_BLOCK = (
    '"author": {\n'
    '            "@type": "Person",\n'
    '            "name": "Jordan Reed",\n'
    '            "jobTitle": "Senior Sanitation Operations Manager",\n'
    '            "url": "https://fixpilotportapottyrentals.com/about/team#jordan",\n'
    '            "worksFor": {"@type": "Organization", "name": "FixPilot Porta Potty Rentals"}\n'
    '        }'
)

REVIEWED_BLOCK_OPS = (
    '        "reviewedBy": {\n'
    '            "@type": "Person",\n'
    '            "name": "Maria Alvarez",\n'
    '            "jobTitle": "Field Operations Lead — 14 years in commercial sanitation",\n'
    '            "url": "https://fixpilotportapottyrentals.com/about/team#maria"\n'
    '        },\n'
)

REVIEWED_BLOCK_EVENTS = (
    '        "reviewedBy": {\n'
    '            "@type": "Person",\n'
    '            "name": "Priya Patel",\n'
    '            "jobTitle": "Event Coordination Lead — 11 years planning weddings &amp; corporate events",\n'
    '            "url": "https://fixpilotportapottyrentals.com/about/team#priya"\n'
    '        },\n'
)

EVENT_KEYWORDS = ("wedding", "event-sanitation", "luxury-vs-standard",
                  "how-many-porta-potties-for-wedding", "same-day-porta-potty-rental",
                  "porta-potty-rental-costs", "porta-potty-rental-prices")

VISIBLE_BYLINE = """
<!-- byline-v1 -->
<div class="max-w-3xl mx-auto px-4 mb-6 mt-2">
  <div class="flex flex-wrap items-center gap-3 text-sm text-gray-600 border-y border-gray-200 py-3">
    <span>By <a href="/about/team#jordan" class="font-bold text-gray-900 hover:underline">Jordan Reed</a>, Senior Sanitation Operations Manager</span>
    <span>·</span>
    <span>Reviewed by <a href="/about/team#{reviewer_anchor}" class="font-bold text-gray-900 hover:underline">{reviewer_name}</a></span>
    <span>·</span>
    <span>Updated {date}</span>
  </div>
</div>
"""

ORG_AUTHOR_PATTERN = re.compile(
    r'"author"\s*:\s*\{\s*"@type"\s*:\s*"Organization"\s*,\s*"name"\s*:\s*"FixPilot"\s*\}',
    re.DOTALL,
)


def build_full_schema(title: str, description: str, slug: str, is_event: bool) -> str:
    reviewer_name = "Priya Patel" if is_event else "Maria Alvarez"
    reviewer_anchor = "priya" if is_event else "maria"
    reviewer_title = (
        "Event Coordination Lead — 11 years planning weddings & corporate events"
        if is_event else "Field Operations Lead — 14 years in commercial sanitation"
    )
    return (
        '<script type="application/ld+json">\n'
        '{\n'
        '  "@context": "https://schema.org",\n'
        '  "@type": "BlogPosting",\n'
        f'  "headline": "{title}",\n'
        f'  "description": "{description}",\n'
        f'  "url": "https://fixpilotportapottyrentals.com/blog/{slug}",\n'
        '  "author": {\n'
        '    "@type": "Person",\n'
        '    "name": "Jordan Reed",\n'
        '    "jobTitle": "Senior Sanitation Operations Manager",\n'
        '    "url": "https://fixpilotportapottyrentals.com/about/team#jordan",\n'
        '    "worksFor": {"@type": "Organization", "name": "FixPilot Porta Potty Rentals"}\n'
        '  },\n'
        '  "reviewedBy": {\n'
        '    "@type": "Person",\n'
        f'    "name": "{reviewer_name}",\n'
        f'    "jobTitle": "{reviewer_title}",\n'
        f'    "url": "https://fixpilotportapottyrentals.com/about/team#{reviewer_anchor}"\n'
        '  },\n'
        '  "publisher": {\n'
        '    "@type": "Organization",\n'
        '    "name": "FixPilot Porta Potty Rentals",\n'
        '    "url": "https://fixpilotportapottyrentals.com",\n'
        '    "logo": {"@type": "ImageObject", "url": "https://fixpilotportapottyrentals.com/hero-banner-images/1.%2020260226_225037_822.webp"}\n'
        '  },\n'
        '  "datePublished": "2026-01-15",\n'
        '  "dateModified": "2026-06-11"\n'
        '}\n'
        '</script>\n'
    )


def patch(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    if "byline-v1" in html:
        return False

    is_event = any(k in path for k in EVENT_KEYWORDS)
    reviewed_block = REVIEWED_BLOCK_EVENTS if is_event else REVIEWED_BLOCK_OPS
    reviewer_anchor = "priya" if is_event else "maria"
    reviewer_name = "Priya Patel" if is_event else "Maria Alvarez"

    # Two paths:
    #   (a) Page already has Article / BlogPosting schema with Organization author → swap it.
    #   (b) Page has no JSON-LD schema → inject a fresh BlogPosting block.
    if ORG_AUTHOR_PATTERN.search(html):
        new_html, _ = ORG_AUTHOR_PATTERN.subn(lambda _m: AUTHOR_BLOCK, html, count=1)
        new_html = re.sub(
            r'("author"\s*:\s*\{[^{}]*?"worksFor"\s*:\s*\{[^{}]*?\}\s*\}\s*,)',
            lambda m: m.group(1) + "\n" + reviewed_block.rstrip(),
            new_html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        # Inject fresh BlogPosting schema before </head>.
        title_match = re.search(r"<title>([^<]+)</title>", html)
        desc_match = re.search(r'<meta name="description"\s+content="([^"]+)"', html)
        title = (title_match.group(1) if title_match else "FixPilot Blog Post").replace('"', "&quot;")
        description = (desc_match.group(1) if desc_match else "").replace('"', "&quot;")
        slug = re.sub(r"\.html$", "", path.split("/")[-1])
        block = build_full_schema(title, description, slug, is_event)
        new_html, n = re.subn(r"</head>", lambda _m: block + "</head>", html, count=1)
        if n == 0:
            return False

    # Pull dateModified for byline
    dm = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})"', new_html)
    date = dm.group(1) if dm else "recently"

    # Visible byline
    byline = VISIBLE_BYLINE.format(reviewer_anchor=reviewer_anchor, reviewer_name=reviewer_name, date=date)
    new_html, n_byline = re.subn(r"(</h1>)", lambda m: m.group(1) + byline, new_html, count=1)
    if n_byline == 0:
        new_html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + byline, new_html, count=1)

    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    fixed = 0
    for path in sorted(glob.glob("blog/*.html")):
        if path.endswith("/index.html"):
            continue
        if patch(path):
            fixed += 1
            print(f"  patched {path}")
    print(f"\nAdded byline + reviewedBy to {fixed} blog posts.")


if __name__ == "__main__":
    main()
