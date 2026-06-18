#!/usr/bin/env python3
"""Diversify city page <title> and <meta description> by tier.

Tiers (by population/SEO value):
  - Tier 1 (top metros): include price ($75/day starting), CTA, phone
  - Tier 2 (mid metros):  USP-led variant
  - Tier 3 (sub-areas):   parent-city reference

Title length kept under 70 chars for SERP rendering. Meta description under
160 chars where possible.

Idempotent: skipping pages where the title contains "From $" or "—" already
suggests a previous diversify pass.
"""
from __future__ import annotations
import glob
import re

# Top-50 metros — Tier 1 treatment
TIER1 = {
    "houston-tx", "phoenix-az", "san-antonio-tx", "san-diego-ca", "dallas-tx",
    "austin-tx", "jacksonville-fl", "fort-worth-tx", "san-jose-ca", "charlotte-nc",
    "indianapolis-in", "seattle-wa", "denver-co", "boston-ma", "el-paso-tx",
    "nashville-tn", "detroit-mi", "memphis-tn", "portland-or", "las-vegas-nv",
    "louisville-ky", "baltimore-md", "milwaukee-wi", "albuquerque-nm", "tucson-az",
    "fresno-ca", "sacramento-ca", "kansas-city-mo", "mesa-az", "atlanta-ga",
    "omaha-ne", "colorado-springs-co", "raleigh-nc", "miami-fl", "long-beach-ca",
    "virginia-beach-va", "oakland-ca", "minneapolis-mn", "tulsa-ok", "arlington-tx",
    "tampa-fl", "new-orleans-la", "wichita-ks", "cleveland-oh", "bakersfield-ca",
    "aurora-co", "anaheim-ca", "honolulu-hi", "santa-ana-ca", "riverside-ca",
    "corpus-christi-tx", "lexington-ky", "stockton-ca", "henderson-nv",
    "saint-paul-mn", "st-louis-mo", "cincinnati-oh", "pittsburgh-pa",
}

# Sub-areas — Tier 3 treatment
TIER3_KEYWORDS = ("east-anaheim", "west-anaheim", "southwest-anaheim",
                  "fullerton-north", "north-las-vegas", "south-fulton",
                  "babylon-town", "hempstead-town", "north-hempstead",
                  "warren-city", "long-island")


def slug_from_path(path: str) -> str:
    folder = path.split("/")[0]
    return folder[len("porta-potty-rental-"):]


def tier_for(slug: str) -> int:
    if any(k in slug for k in TIER3_KEYWORDS):
        return 3
    if slug in TIER1:
        return 1
    return 2


def parent_city(slug: str) -> str | None:
    """Return parent-city slug for known sub-areas."""
    if "anaheim" in slug and slug != "anaheim-ca":
        return "Anaheim"
    if slug == "fullerton-north-ca":
        return "Fullerton"
    if slug == "north-las-vegas-nv":
        return "Las Vegas"
    if slug in {"babylon-town-ny", "hempstead-town-ny", "north-hempstead-ny", "long-island-ny"}:
        return "Long Island"
    if slug == "south-fulton-ga":
        return "Atlanta"
    if slug == "warren-city-mi":
        return "Detroit"
    return None


CITY_RE = re.compile(r'<title>\s*Porta Potty Rental ([^,<|]+),\s*([A-Z]{2})\s*\|')
COUNTY_RE = re.compile(r'<title>[^<]*\|\s*([^<|]+ County|[^<|]+ Parish)\s*\|', re.IGNORECASE)
META_DESC_RE = re.compile(r'(<meta name="description"[^>]*content=")[^"]*(")')
TITLE_RE = re.compile(r'(<title>)[^<]*(</title>)')


def build_title(city: str, state: str, county: str | None, slug: str) -> str:
    tier = tier_for(slug)
    if tier == 1:
        # ~67 chars max
        return f"Porta Potty Rental {city}, {state} — Same-Day · From $75/Day"
    if tier == 3:
        parent = parent_city(slug) or city
        return f"Porta Potty Rental {city}, {state} | Serving {parent} 24/7"
    # Tier 2
    if county:
        return f"Porta Potty Rental {city}, {state} · {county} · Free 60-sec Quote"
    return f"Porta Potty Rental {city}, {state} · Free Quote in 60 Seconds"


def build_meta(city: str, state: str, county: str | None, slug: str) -> str:
    tier = tier_for(slug)
    if tier == 1:
        return (
            f"{city} porta potty rental from $75/day. Same-day delivery, OSHA-compliant, "
            f"luxury restroom trailers, ADA units, hand wash stations. Call (833) 652-9344."
        )
    if tier == 3:
        parent = parent_city(slug) or city
        return (
            f"Porta potty rental in {city}, {state} — same-day delivery from our {parent} depot. "
            "Construction, weddings, festivals, emergencies. Free 60-second quote: (833) 652-9344."
        )
    region = county or f"{state} metro"
    return (
        f"{city} porta potty rental — same-day delivery throughout {region}. Standard, "
        "deluxe, luxury trailers, ADA, hand wash. 24/7 dispatch · (833) 652-9344."
    )


def patch(path: str) -> bool:
    html = open(path, encoding="utf-8").read()

    title_match = re.search(r"<title>([^<]+)</title>", html)
    if not title_match:
        return False
    old_title = title_match.group(1)
    if "From $" in old_title or "60-sec" in old_title or "Serving" in old_title:
        return False  # already diversified

    cm = CITY_RE.search(html)
    if not cm:
        return False
    city = cm.group(1).strip()
    state = cm.group(2).strip()

    county = None
    cm2 = COUNTY_RE.search(html)
    if cm2:
        county = cm2.group(1).strip()

    slug = slug_from_path(path)

    new_title = build_title(city, state, county, slug)
    new_meta = build_meta(city, state, county, slug)

    new_html = TITLE_RE.sub(lambda _m: f"<title>{new_title}</title>", html, count=1)
    new_html = META_DESC_RE.sub(lambda m: f'{m.group(1)}{new_meta}{m.group(2)}', new_html, count=1)

    if new_html == html:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    fixed = 0
    for path in sorted(glob.glob("porta-potty-rental-*-*/index.html")):
        if patch(path):
            fixed += 1
    print(f"Diversified title + meta on {fixed} pages.")


if __name__ == "__main__":
    main()
