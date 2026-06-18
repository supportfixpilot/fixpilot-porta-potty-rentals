#!/usr/bin/env python3
"""Add EquipmentRentalShop to LocalBusiness schema @type arrays on all city pages."""

import glob
import re

CITY_GLOB = "porta-potty-rental-*-*/index.html"


def add_equipment_type(html: str) -> tuple[str, bool]:
    # Match "@type": ["LocalBusiness", "HomeAndConstructionBusiness"]
    # Add EquipmentRentalShop if not already present
    pattern = r'"@type"\s*:\s*\["LocalBusiness",\s*"HomeAndConstructionBusiness"\]'
    replacement = '"@type": ["LocalBusiness", "HomeAndConstructionBusiness", "EquipmentRentalShop"]'

    if 'EquipmentRentalShop' in html:
        return html, False

    new_html = re.sub(pattern, replacement, html)
    return new_html, new_html != html


def main():
    paths = sorted(glob.glob(CITY_GLOB))
    fixed = 0
    for path in paths:
        with open(path, encoding='utf-8', errors='replace') as f:
            html = f.read()
        new_html, changed = add_equipment_type(html)
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            fixed += 1
    print(f"Added EquipmentRentalShop to {fixed}/{len(paths)} pages")


if __name__ == '__main__':
    main()
