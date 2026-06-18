#!/usr/bin/env python3
"""
Site-wide improvements:
1. Fix 40 state-abbreviation broken links → full state-name URLs
2. Fix 26 missing city/state links → state-page fallback or removal
3. Fix 3 malformed ../zip/ links
4. Add Twitter card meta tags to 31 blog/service pages
5. Remove empty greensboro-nc link from locations.html
6. Fix location count claim in locations.html
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent

# ── 1. State abbreviation → full-name page mapping ──────────────────────────
STATE_MAP = {
    'al': 'alabama',       'ar': 'arkansas',      'az': 'arizona',
    'ca': 'california',    'co': 'colorado',       'ct': 'connecticut',
    'fl': 'florida',       'ga': 'georgia',        'il': 'illinois',
    'in': 'indiana',       'ks': 'kansas',         'ky': 'kentucky',
    'la': 'louisiana',     'ma': 'massachusetts',  'md': 'maryland',
    'mi': 'michigan',      'mn': 'minnesota',      'mo': 'missouri',
    'ms': 'mississippi',   'mt': 'montana',        'nc': 'north-carolina',
    'nd': 'north-dakota',  'ne': 'nebraska',       'nj': 'new-jersey',
    'nv': 'nevada',        'ny': 'new-york',       'oh': 'ohio',
    'ok': 'oklahoma',      'or': 'oregon',         'pa': 'pennsylvania',
    'sc': 'south-carolina','sd': 'south-dakota',   'tn': 'tennessee',
    'tx': 'texas',         'ut': 'utah',           'va': 'virginia',
    'wa': 'washington',    'wi': 'wisconsin',
    'wv': 'charleston-wv', # no state page — fallback to capital city
    'wy': 'wyoming',
}

# Missing city → best valid fallback (state page or nearest city)
MISSING_CITY_MAP = {
    '/porta-potty-rental-alaska':        '/porta-potty-rental-anchorage-ak',
    '/porta-potty-rental-arlington-va':  '/porta-potty-rental-virginia',
    '/porta-potty-rental-beaverton-or':  '/porta-potty-rental-portland-or',
    '/porta-potty-rental-carmel-in':     '/porta-potty-rental-indiana',
    '/porta-potty-rental-cedar-park-tx': '/porta-potty-rental-austin-tx',
    '/porta-potty-rental-concord-nc':    '/porta-potty-rental-north-carolina',
    '/porta-potty-rental-fayetteville-nc':'/porta-potty-rental-north-carolina',
    '/porta-potty-rental-fishers-in':    '/porta-potty-rental-indiana',
    '/porta-potty-rental-gastonia-nc':   '/porta-potty-rental-north-carolina',
    '/porta-potty-rental-hawaii':        '/porta-potty-rental-honolulu-hi',
    '/porta-potty-rental-maine':         '/porta-potty-rental-portland-me',
    '/porta-potty-rental-mansfield-tx':  '/porta-potty-rental-fort-worth-tx',
    '/porta-potty-rental-mesquite-tx':   '/porta-potty-rental-dallas-tx',
    '/porta-potty-rental-new-hampshire': '/porta-potty-rental-manchester-nh',
    '/porta-potty-rental-pasadena-tx':   '/porta-potty-rental-houston-tx',
    '/porta-potty-rental-pflugerville-tx':'/porta-potty-rental-austin-tx',
    '/porta-potty-rental-philadelphia-pa':'/porta-potty-rental-pennsylvania',
    '/porta-potty-rental-rhode-island':  '/porta-potty-rental-providence-ri',
    '/porta-potty-rental-roswell-ga':    '/porta-potty-rental-atlanta-ga',
    '/porta-potty-rental-san-marcos-tx': '/porta-potty-rental-austin-tx',
    '/porta-potty-rental-sandy-springs-ga':'/porta-potty-rental-atlanta-ga',
    '/porta-potty-rental-towson-md':     '/porta-potty-rental-baltimore-md',
    '/porta-potty-rental-vermont':       '/porta-potty-rental-burlington-vt',
    '/porta-potty-rental-washington-dc': '/porta-potty-rental-virginia',
    '/porta-potty-rental-west-virginia': '/porta-potty-rental-charleston-wv',
}

def fix_links(text):
    """Replace broken internal links with valid ones."""
    # State abbreviation links
    def replace_abbr(m):
        abbr = m.group(1)
        full = STATE_MAP.get(abbr)
        if full:
            return f'href="/porta-potty-rental-{full}"'
        return m.group(0)
    text = re.sub(r'href="/porta-potty-rental-([a-z]{2})"', replace_abbr, text)

    # Missing city/state links
    for broken, fixed in MISSING_CITY_MAP.items():
        text = text.replace(f'href="{broken}"', f'href="{fixed}"')

    # Malformed ../zip/ links — replace the whole <a> with just its text content
    text = re.sub(
        r'<a\s+href="/porta-potty-rental-\.\./zip/[^"]*"[^>]*>(.*?)</a>',
        r'\1', text, flags=re.DOTALL | re.IGNORECASE)

    return text

def add_twitter_card(text, page_type='summary_large_image'):
    """Inject twitter:card meta if missing."""
    if 'twitter:card' in text:
        return text
    tag = f'    <meta name="twitter:card" content="{page_type}">\n'
    # Insert after og:image line if present, else before </head>
    if re.search(r'og:image', text, re.IGNORECASE):
        text = re.sub(
            r'(.*og:image.*\n)',
            r'\1' + tag,
            text, count=1, flags=re.IGNORECASE | re.DOTALL)
    else:
        text = re.sub(r'(</head>)', tag + r'\1', text, count=1, flags=re.IGNORECASE)
    return text

def count_actual_locations(locations_html):
    """Count unique city pill links in locations.html."""
    hrefs = re.findall(r'href="(/porta-potty-rental-[^"]+)".*?truncate">', locations_html, re.DOTALL)
    return len(hrefs)

def main():
    stats = {}

    # ── Fix broken links across all HTML files ───────────────────────────────
    link_fixes = 0
    for f in sorted(ROOT.glob('**/*.html')):
        text = f.read_text(encoding='utf-8', errors='ignore')
        new = fix_links(text)
        if new != text:
            f.write_text(new, encoding='utf-8')
            link_fixes += 1
    stats['link_fixes'] = link_fixes

    # ── Add Twitter cards to blog and service pages ──────────────────────────
    twitter_fixes = 0
    for f in list(ROOT.glob('blog/*.html')) + list(ROOT.glob('services/*.html')):
        text = f.read_text(encoding='utf-8', errors='ignore')
        new = add_twitter_card(text)
        if new != text:
            f.write_text(new, encoding='utf-8')
            twitter_fixes += 1
    stats['twitter_fixes'] = twitter_fixes

    # ── Fix locations.html: remove greensboro-nc (empty folder), update count ─
    loc_path = ROOT / 'locations.html'
    loc = loc_path.read_text(encoding='utf-8')

    # Remove the greensboro-nc pill line (empty folder, no index.html)
    loc = re.sub(
        r'\s*<a href="/porta-potty-rental-greensboro-nc"[^>]*>Greensboro</a>\n?',
        '', loc)

    # Update NC city count from 6 back to 5
    loc = loc.replace('North Carolina (6 cities)', 'North Carolina (5 cities)')

    # Count actual city pills now
    actual = count_actual_locations(loc)

    # Update stale "224" count everywhere in locations.html
    for old in ['224 service locations', '224 porta potty rental locations',
                'Browse 224', '224 cities', '"numberOfItems": 224']:
        if old in loc:
            new_val = old.replace('224', str(actual))
            loc = loc.replace(old, new_val)

    loc_path.write_text(loc, encoding='utf-8')
    stats['location_count'] = actual

    print(f"Done:")
    print(f"  Files with link fixes:  {stats['link_fixes']}")
    print(f"  Twitter cards added:    {stats['twitter_fixes']}")
    print(f"  Location count updated: 224 → {stats['location_count']} (locations.html)")

if __name__ == '__main__':
    main()
