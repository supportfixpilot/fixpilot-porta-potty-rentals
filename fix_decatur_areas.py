#!/usr/bin/env python3
"""Fix Atlanta neighborhoods incorrectly placed in non-Atlanta pages (Decatur, South Fulton)."""

import re

ATLANTA_NEIGHBORHOODS_IN_SCHEMA = [
    '"name": "Virginia-Highland"',
    '"name": "Inman Park"',
    '"name": "Old Fourth Ward"',
    '"name": "Poncey-Highland"',
    '"name": "Ansley Park"',
    '"name": "Piedmont Park"',
    '"name": "Candler Park"',
    '"name": "Morningside"',
    '"name": "Grant Park"',
]

# Pages confirmed to have Atlanta neighborhood bleed
PAGES_TO_FIX = [
    "porta-potty-rental-decatur-ga/index.html",
    "porta-potty-rental-south-fulton-ga/index.html",
]

# Correct areaServed neighborhoods for Decatur
DECATUR_NEIGHBORHOODS = [
    '{"@type": "Neighborhood", "name": "Downtown Decatur"}',
    '{"@type": "Neighborhood", "name": "Oakhurst"}',
    '{"@type": "Neighborhood", "name": "Avondale Estates"}',
    '{"@type": "Neighborhood", "name": "Lake Claire"}',
    '{"@type": "Neighborhood", "name": "Druid Hills"}',
    '{"@type": "City", "name": "Decatur"}',
    '{"@type": "City", "name": "Tucker"}',
    '{"@type": "City", "name": "Stone Mountain"}',
    '{"@type": "City", "name": "Lithonia"}',
    '{"@type": "City", "name": "Conyers"}',
]

# Correct areaServed for South Fulton
SOUTH_FULTON_NEIGHBORHOODS = [
    '{"@type": "City", "name": "South Fulton"}',
    '{"@type": "Neighborhood", "name": "College Park"}',
    '{"@type": "Neighborhood", "name": "East Point"}',
    '{"@type": "Neighborhood", "name": "Union City"}',
    '{"@type": "Neighborhood", "name": "Fairburn"}',
    '{"@type": "City", "name": "Palmetto"}',
    '{"@type": "City", "name": "Chattahoochee Hills"}',
    '{"@type": "City", "name": "Riverdale"}',
    '{"@type": "City", "name": "Forest Park"}',
    '{"@type": "City", "name": "Jonesboro"}',
]


def fix_page(path: str, correct_neighborhoods: list[str]) -> bool:
    with open(path, encoding='utf-8', errors='replace') as f:
        html = f.read()

    # Remove Atlanta-specific neighborhood entries from areaServed in schema
    changed = False
    for nb in ATLANTA_NEIGHBORHOODS_IN_SCHEMA:
        if nb in html:
            # Remove the entire JSON object containing this neighborhood
            pattern = r'\s*\{[^{}]*' + re.escape(nb) + r'[^{}]*\},?'
            new_html = re.sub(pattern, '', html)
            if new_html != html:
                html = new_html
                changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def main():
    fixes = {
        "porta-potty-rental-decatur-ga/index.html": DECATUR_NEIGHBORHOODS,
        "porta-potty-rental-south-fulton-ga/index.html": SOUTH_FULTON_NEIGHBORHOODS,
    }

    for path, neighborhoods in fixes.items():
        try:
            if fix_page(path, neighborhoods):
                print(f"Fixed: {path}")
            else:
                print(f"No changes needed: {path}")
        except FileNotFoundError:
            print(f"Not found: {path}")


if __name__ == '__main__':
    main()
