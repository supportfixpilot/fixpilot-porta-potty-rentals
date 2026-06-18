#!/usr/bin/env python3
"""
Fix 2: Add geo.position and ICBM meta tags to 35 state-level pages.
Uses approximate geographic center of each US state.
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

# State geographic centers (lat, lon)
STATE_COORDS = {
    'US-AL': (32.8067, -86.7911),
    'US-AZ': (34.0489, -111.0937),
    'US-AR': (34.7999, -92.1999),
    'US-CA': (36.7783, -119.4179),
    'US-CO': (39.5501, -105.7821),
    'US-CT': (41.6032, -73.0877),
    'US-FL': (27.6648, -81.5158),
    'US-GA': (32.1574, -82.9071),
    'US-ID': (44.0682, -114.7420),
    'US-IL': (40.6331, -89.3985),
    'US-IN': (40.2672, -86.1349),
    'US-IA': (41.8780, -93.0977),
    'US-KS': (39.0119, -98.4842),
    'US-KY': (37.8393, -84.2700),
    'US-LA': (31.2448, -92.1450),
    'US-MD': (39.0458, -76.6413),
    'US-MA': (42.4072, -71.3824),
    'US-MI': (44.3148, -85.6024),
    'US-MN': (46.7296, -94.6859),
    'US-MS': (32.3547, -89.3985),
    'US-MO': (37.9643, -91.8318),
    'US-MT': (46.8797, -110.3626),
    'US-NE': (41.4925, -99.9018),
    'US-NV': (38.8026, -116.4194),
    'US-OH': (40.4173, -82.9071),
    'US-OK': (35.0078, -97.0929),
    'US-OR': (43.8041, -120.5542),
    'US-PA': (41.2033, -77.1945),
    'US-TN': (35.5175, -86.5804),
    'US-TX': (31.9686, -99.9018),
    'US-UT': (39.3210, -111.0937),
    'US-VA': (37.4316, -78.6569),
    'US-WA': (47.7511, -120.7401),
    'US-WI': (43.7844, -88.7879),
    'US-WY': (43.0760, -107.2902),
}

GEO_REGION_PAT = re.compile(r'<meta name="geo\.region" content="([^"]+)">')
GEO_PLACE_PAT  = re.compile(r'(<meta name="geo\.placename"[^>]+>)')

fixed = 0

for slug in sorted(os.listdir(ROOT)):
    if not (slug.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(ROOT, slug))):
        continue
    path = os.path.join(ROOT, slug, 'index.html')
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        html = f.read()

    if 'geo.position' in html:
        continue  # already has it

    region_m = GEO_REGION_PAT.search(html)
    if not region_m:
        continue
    region = region_m.group(1)  # e.g. "US-AL"

    coords = STATE_COORDS.get(region)
    if not coords:
        print(f'  NO COORDS for {region} in {slug}')
        continue

    lat, lon = coords
    geo_pos_tag  = f'<meta name="geo.position" content="{lat};{lon}">'
    icbm_tag     = f'<meta name="ICBM" content="{lat}, {lon}">'
    inject        = f'\n    {geo_pos_tag}\n    {icbm_tag}'

    # Insert after the geo.placename tag
    place_m = GEO_PLACE_PAT.search(html)
    if place_m:
        insert_at = place_m.end()
        html = html[:insert_at] + inject + html[insert_at:]
    else:
        # Fallback: insert after geo.region
        insert_at = region_m.end()
        html = html[:insert_at] + inject + html[insert_at:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  + {slug}: {lat}, {lon}')
    fixed += 1

print(f'\nAdded geo.position to {fixed} state pages.')
