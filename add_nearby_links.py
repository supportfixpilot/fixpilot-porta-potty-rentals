#!/usr/bin/env python3
"""Add nearby city links to pages that have fewer than 3.
Uses geographic proximity (lat/lon) to find the nearest existing city pages."""

import re, glob, math
from pathlib import Path

DOMAIN = "https://fixpilotportapottyrentals.com"

def get_page_data(path):
    """Extract slug, lat, lon, state from a city page."""
    html = open(path, encoding='utf-8', errors='replace').read()
    slug = path.split('/')[0]

    lat_m = re.search(r'"latitude":\s*([\d.\-]+)', html)
    lon_m = re.search(r'"longitude":\s*([\d.\-]+)', html)
    state_m = re.search(r'-([a-z]{2})$', slug)
    title_m = re.search(r'<title>(.*?)</title>', html)

    city_m = re.search(r'Porta Potty Rental ([^|—·,]+)', title_m.group(1) if title_m else '')

    return {
        'slug': slug,
        'path': path,
        'lat': float(lat_m.group(1)) if lat_m else None,
        'lon': float(lon_m.group(1)) if lon_m else None,
        'state': state_m.group(1).upper() if state_m else '',
        'city': city_m.group(1).strip() if city_m else slug,
        'html': html,
    }


def haversine(lat1, lon1, lat2, lon2):
    """Distance in miles between two lat/lon points."""
    R = 3959
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def add_nearby_links(page_data: dict, all_pages: list) -> tuple[str, bool]:
    html = page_data['html']
    slug = page_data['slug']
    lat, lon = page_data['lat'], page_data['lon']
    state = page_data['state']

    # Count existing nearby links
    existing_links = set(re.findall(r'href="/porta-potty-rental-([a-z]+-[a-z]{2})"', html))

    if len(existing_links) >= 5:
        return html, False

    # Find nearest pages not already linked
    candidates = []
    for other in all_pages:
        if other['slug'] == slug: continue
        if other['slug'].split('-')[-1] != slug.split('-')[-1]:
            # Different state — include if within 150 miles
            pass

        other_slug_short = other['slug'].replace('porta-potty-rental-', '')
        # Skip if already linked
        if other_slug_short in existing_links or other['slug'] in existing_links:
            continue

        # Calculate distance if both have coords
        if lat and lon and other['lat'] and other['lon']:
            dist = haversine(lat, lon, other['lat'], other['lon'])
        else:
            # Same state gets priority without distance
            dist = 50 if other['state'] == state else 500

        candidates.append((dist, other))

    # Sort by distance, prefer same state
    candidates.sort(key=lambda x: (x[0] if x[1]['state'] == state else x[0] + 200))

    # Take top candidates to fill up to 5 nearby links
    needed = max(0, 5 - len(existing_links))
    new_links = candidates[:needed]

    if not new_links:
        return html, False

    # Find the related-cities section to add cards
    related_section = re.search(
        r'(<section id="related-cities".*?<div class="grid[^>]*>)(.*?)(</div>\s*</div>\s*</section>)',
        html, re.DOTALL
    )

    if not related_section:
        return html, False

    new_cards = ''
    for dist, other in new_links:
        other_slug_short = other['slug'].replace('porta-potty-rental-', '')
        # Get city name from other page
        other_title = re.search(r'<title>(.*?)</title>', other['html'])
        other_city_m = re.search(r'Porta Potty Rental ([^|—·,]+)', other_title.group(1) if other_title else '')
        other_city = other_city_m.group(1).strip() if other_city_m else other['city']

        new_cards += f'''
      <a href="/porta-potty-rental-{other_slug_short}" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all border border-brand-200 group">
        <h4 class="font-black text-brand-950 text-lg mb-2 group-hover:text-cta transition">{other_city}</h4>
        <p class="text-sm text-brand-700">Porta Potty Rental in {other_city}</p>
        <span class="text-cta text-sm font-semibold mt-3 inline-block">Learn More →</span>
      </a>'''

    new_html = html[:related_section.end(2)] + new_cards + html[related_section.end(2):]
    return new_html, True


def main():
    pages_paths = sorted(glob.glob('porta-potty-rental-*-*/index.html'))

    print(f"Loading {len(pages_paths)} pages...")
    all_pages = [get_page_data(p) for p in pages_paths]
    # Filter out pages without coords
    pages_with_coords = [p for p in all_pages if p['lat'] and p['lon']]
    print(f"Pages with coordinates: {len(pages_with_coords)}")

    fixed = 0
    for page in all_pages:
        html = page['html']
        existing = re.findall(r'href="/porta-potty-rental-([a-z]+-[a-z]{2})"', html)

        if len(existing) >= 4:
            continue

        new_html, changed = add_nearby_links(page, pages_with_coords)

        if changed:
            Path(page['path']).write_text(new_html, encoding='utf-8')
            fixed += 1

    print(f"Added nearby links to {fixed} pages")

    # Verify results
    still_missing = 0
    for path in pages_paths:
        html = open(path, encoding='utf-8', errors='replace').read()
        nearby = re.findall(r'href="/porta-potty-rental-[a-z]+-[a-z]{2}"', html)
        if len(nearby) < 3:
            still_missing += 1

    print(f"Pages still with < 3 nearby links: {still_missing}")


if __name__ == '__main__':
    main()
