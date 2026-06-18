#!/usr/bin/env python3
"""
Round 2 fixes: inject H1 into pages that lack it, add missing geo coordinates,
fix EquipmentRentalShop on remaining pages, and fix missing meta descriptions.
"""

import glob, re
from pathlib import Path

DOMAIN = "https://fixpilotportapottyrentals.com"

# ── COMPREHENSIVE GEO DATA ────────────────────────────────────────────────────
# All city pages missing geo.position coords
CITY_GEO = {
    # California
    'porta-potty-rental-anaheim-ca': ('33.8366', '-117.9143', 'US-CA', 'Anaheim, California'),
    'porta-potty-rental-auburn-ca': ('38.8963', '-121.0769', 'US-CA', 'Auburn, California'),
    'porta-potty-rental-bakersfield-ca': ('35.3733', '-119.0187', 'US-CA', 'Bakersfield, California'),
    'porta-potty-rental-bloomington-ca': ('34.0658', '-117.3975', 'US-CA', 'Bloomington, California'),
    'porta-potty-rental-brea-ca': ('33.9167', '-117.9000', 'US-CA', 'Brea, California'),
    'porta-potty-rental-buena-park-ca': ('33.8675', '-117.9981', 'US-CA', 'Buena Park, California'),
    'porta-potty-rental-chula-vista-ca': ('32.6401', '-117.0842', 'US-CA', 'Chula Vista, California'),
    'porta-potty-rental-east-anaheim-ca': ('33.8366', '-117.8731', 'US-CA', 'East Anaheim, California'),
    'porta-potty-rental-fresno-ca': ('36.7378', '-119.7871', 'US-CA', 'Fresno, California'),
    'porta-potty-rental-fullerton-ca': ('33.8704', '-117.9242', 'US-CA', 'Fullerton, California'),
    'porta-potty-rental-fullerton-north-ca': ('33.9000', '-117.9242', 'US-CA', 'North Fullerton, California'),
    'porta-potty-rental-glendale-ca': ('34.1425', '-118.2551', 'US-CA', 'Glendale, California'),
    'porta-potty-rental-irvine-ca': ('33.6846', '-117.8265', 'US-CA', 'Irvine, California'),
    'porta-potty-rental-la-habra-ca': ('33.9319', '-117.9462', 'US-CA', 'La Habra, California'),
    'porta-potty-rental-lake-forest-ca': ('33.6469', '-117.6892', 'US-CA', 'Lake Forest, California'),
    'porta-potty-rental-lakewood-ca': ('33.8536', '-118.1337', 'US-CA', 'Lakewood, California'),
    'porta-potty-rental-long-beach-ca': ('33.7701', '-118.1937', 'US-CA', 'Long Beach, California'),
    'porta-potty-rental-paradise-ca': ('39.7596', '-121.6219', 'US-CA', 'Paradise, California'),
    'porta-potty-rental-spring-valley-ca': ('32.7449', '-116.9989', 'US-CA', 'Spring Valley, California'),
    'porta-potty-rental-southwest-anaheim-ca': ('33.8175', '-117.9314', 'US-CA', 'Southwest Anaheim, California'),
    'porta-potty-rental-west-anaheim-ca': ('33.8366', '-117.9600', 'US-CA', 'West Anaheim, California'),
    'porta-potty-rental-tustin-ca': ('33.7458', '-117.8260', 'US-CA', 'Tustin, California'),
    # Colorado
    'porta-potty-rental-colorado-springs-co': ('38.8339', '-104.8214', 'US-CO', 'Colorado Springs, Colorado'),
    'porta-potty-rental-aurora-co': ('39.7294', '-104.8319', 'US-CO', 'Aurora, Colorado'),
    'porta-potty-rental-arvada-co': ('39.8028', '-105.0875', 'US-CO', 'Arvada, Colorado'),
    'porta-potty-rental-centennial-co': ('39.5806', '-104.8772', 'US-CO', 'Centennial, Colorado'),
    'porta-potty-rental-highlands-ranch-co': ('39.5528', '-104.9697', 'US-CO', 'Highlands Ranch, Colorado'),
    'porta-potty-rental-longmont-co': ('40.1672', '-105.1019', 'US-CO', 'Longmont, Colorado'),
    'porta-potty-rental-loveland-co': ('40.3978', '-105.0749', 'US-CO', 'Loveland, Colorado'),
    # Maryland
    'porta-potty-rental-ellicott-city-md': ('39.2679', '-76.7983', 'US-MD', 'Ellicott City, Maryland'),
    'porta-potty-rental-frederick-md': ('39.4143', '-77.4105', 'US-MD', 'Frederick, Maryland'),
    'porta-potty-rental-germantown-md': ('39.1731', '-77.2717', 'US-MD', 'Germantown, Maryland'),
    'porta-potty-rental-glen-burnie-md': ('39.1620', '-76.6275', 'US-MD', 'Glen Burnie, Maryland'),
    'porta-potty-rental-sandy-spring-md': ('39.1437', '-77.0191', 'US-MD', 'Sandy Spring, Maryland'),
    'porta-potty-rental-waldorf-md': ('38.6240', '-76.9175', 'US-MD', 'Waldorf, Maryland'),
    # Florida
    'porta-potty-rental-coral-springs-fl': ('26.2709', '-80.2706', 'US-FL', 'Coral Springs, Florida'),
    'porta-potty-rental-lehigh-acres-fl': ('26.6118', '-81.6390', 'US-FL', 'Lehigh Acres, Florida'),
    'porta-potty-rental-miami-gardens-fl': ('25.9420', '-80.2456', 'US-FL', 'Miami Gardens, Florida'),
    'porta-potty-rental-palm-bay-fl': ('27.9906', '-80.6634', 'US-FL', 'Palm Bay, Florida'),
    'porta-potty-rental-pembroke-pines-fl': ('26.0026', '-80.3433', 'US-FL', 'Pembroke Pines, Florida'),
    'porta-potty-rental-pompano-beach-fl': ('26.2379', '-80.1248', 'US-FL', 'Pompano Beach, Florida'),
    'porta-potty-rental-port-st-lucie-fl': ('27.2730', '-80.3582', 'US-FL', 'Port St. Lucie, Florida'),
    # Texas
    'porta-potty-rental-college-station-tx': ('30.6280', '-96.3344', 'US-TX', 'College Station, Texas'),
    'porta-potty-rental-wichita-falls-tx': ('33.9137', '-98.4934', 'US-TX', 'Wichita Falls, Texas'),
    # New York
    'porta-potty-rental-rochester-ny': ('43.1566', '-77.6088', 'US-NY', 'Rochester, New York'),
    'porta-potty-rental-yonkers-ny': ('40.9312', '-73.8988', 'US-NY', 'Yonkers, New York'),
    # Nevada
    'porta-potty-rental-enterprise-nv': ('36.0269', '-115.2375', 'US-NV', 'Enterprise, Nevada'),
    'porta-potty-rental-sunrise-manor-nv': ('36.2158', '-115.0583', 'US-NV', 'Sunrise Manor, Nevada'),
    # Illinois
    'porta-potty-rental-elgin-il': ('42.0354', '-88.2826', 'US-IL', 'Elgin, Illinois'),
    'porta-potty-rental-joliet-il': ('41.5250', '-88.0817', 'US-IL', 'Joliet, Illinois'),
    'porta-potty-rental-naperville-il': ('41.7508', '-88.1535', 'US-IL', 'Naperville, Illinois'),
    'porta-potty-rental-rockford-il': ('42.2711', '-89.0937', 'US-IL', 'Rockford, Illinois'),
    'porta-potty-rental-schaumburg-il': ('42.0334', '-88.0834', 'US-IL', 'Schaumburg, Illinois'),
    # Minnesota
    'porta-potty-rental-duluth-mn': ('46.7867', '-92.1005', 'US-MN', 'Duluth, Minnesota'),
    'porta-potty-rental-lakeville-mn': ('44.6497', '-93.2428', 'US-MN', 'Lakeville, Minnesota'),
    'porta-potty-rental-woodbury-mn': ('44.9239', '-92.9594', 'US-MN', 'Woodbury, Minnesota'),
    # Massachusetts
    'porta-potty-rental-cambridge-ma': ('42.3736', '-71.1097', 'US-MA', 'Cambridge, Massachusetts'),
    'porta-potty-rental-lowell-ma': ('42.6334', '-71.3162', 'US-MA', 'Lowell, Massachusetts'),
    'porta-potty-rental-plymouth-ma': ('41.9584', '-70.6673', 'US-MA', 'Plymouth, Massachusetts'),
    'porta-potty-rental-worcester-ma': ('42.2626', '-71.8023', 'US-MA', 'Worcester, Massachusetts'),
    # Michigan
    'porta-potty-rental-warren-city-mi': ('42.4775', '-83.0277', 'US-MI', 'Warren, Michigan'),
    # Washington
    'porta-potty-rental-kent-wa': ('47.3809', '-122.2348', 'US-WA', 'Kent, Washington'),
    # Kentucky
    'porta-potty-rental-bowling-green-ky': ('36.9685', '-86.4808', 'US-KY', 'Bowling Green, Kentucky'),
    'porta-potty-rental-owensboro-ky': ('37.7719', '-87.1111', 'US-KY', 'Owensboro, Kentucky'),
    # Louisiana
    'porta-potty-rental-metairie-la': ('29.9827', '-90.1640', 'US-LA', 'Metairie, Louisiana'),
}


def inject_geo(html: str, slug: str) -> tuple[str, bool]:
    if 'geo.position' in html:
        return html, False
    if slug not in CITY_GEO:
        return html, False
    lat, lon, region, placename = CITY_GEO[slug]
    tags = f"""    <meta name="geo.region" content="{region}">
    <meta name="geo.placename" content="{placename}">
    <meta name="geo.position" content="{lat};{lon}">
    <meta name="ICBM" content="{lat}, {lon}">"""
    new_html = re.sub(r'(<link rel="canonical")', tags + '\n    ' + r'\1', html, count=1)
    if new_html == html:
        # Fallback: inject after <head>
        new_html = html.replace('<head>', '<head>\n' + tags, 1)
    return new_html, new_html != html


def inject_h1(html: str, slug: str) -> tuple[str, bool]:
    """Inject H1 for pages that have no H1 or an empty H1."""
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    h1text = re.sub(r'<[^>]+>', '', h1.group(1)).strip() if h1 else ''
    if len(h1text) >= 10:
        return html, False

    # Get city from title or slug
    t = re.search(r'<title>(.*?)</title>', html)
    title = t.group(1) if t else ''
    city_m = re.search(r'Porta Potty Rental ([^|—·]+)', title)
    city_part = city_m.group(1).strip() if city_m else slug.replace('-', ' ').title()

    h1_html = f'<h1 class="text-3xl md:text-4xl font-black text-brand-900 mb-3">Porta Potty Rental <span class="text-brand-600">{city_part}</span></h1>'

    # If existing empty H1, replace it
    if h1 and len(h1text) < 10:
        new_html = html.replace(h1.group(0), h1_html, 1)
        return new_html, new_html != html

    # Find first H2 and inject H1 before it
    h2 = re.search(r'<h2', html)
    if h2:
        insert_pos = h2.start()
        new_html = html[:insert_pos] + h1_html + '\n        ' + html[insert_pos:]
        return new_html, True

    return html, False


def fix_missing_meta_desc(html: str, slug: str) -> tuple[str, bool]:
    """Generate and inject meta description for pages missing it."""
    d = re.search(r'name="description" content="([^"]+)"', html)
    if d:
        return html, False

    t = re.search(r'<title>(.*?)</title>', html)
    title = t.group(1) if t else ''
    city_m = re.search(r'Porta Potty Rental ([^|—·]+)', title)
    location = city_m.group(1).strip() if city_m else slug.replace('-', ' ').title()

    desc = f"Portable toilet rental in {location} from $75/day. Same-day delivery, OSHA-compliant units, luxury restroom trailers, ADA units. Call (833) 652-9344 for a free quote."
    if len(desc) > 160:
        desc = desc[:157] + '...'

    meta_tag = f'<meta name="description" content="{desc}">'

    # Inject after <title>
    new_html = re.sub(r'(</title>)', r'\1\n    ' + meta_tag, html, count=1)
    return new_html, new_html != html


def fix_equipment_rental_type_v2(html: str) -> tuple[str, bool]:
    """Additional patterns for EquipmentRentalShop that were missed."""
    if 'EquipmentRentalShop' in html:
        return html, False

    patterns = [
        (r'"@type":\s*\["LocalBusiness",\s*"EquipmentRentalShop"\]',
         '"@type": ["LocalBusiness", "EquipmentRentalShop"]'),
    ]

    # Try to find any @type with LocalBusiness and add EquipmentRentalShop
    new_html = re.sub(
        r'"@type":\s*\["LocalBusiness"\]',
        '"@type": ["LocalBusiness", "EquipmentRentalShop"]',
        html
    )
    if new_html != html:
        return new_html, True

    # Single string LocalBusiness
    new_html = re.sub(
        r'"@type":\s*"LocalBusiness"(?!\s*,|\s*\])',
        '"@type": ["LocalBusiness", "EquipmentRentalShop"]',
        html, count=1
    )
    return new_html, new_html != html


def main():
    paths = sorted(glob.glob('porta-potty-rental-*-*/index.html'))
    fixes_applied = {}
    modified = 0

    for path in paths:
        slug = path.split('/')[0]
        html = Path(path).read_text(encoding='utf-8', errors='replace')
        original = html
        page_fixes = []

        html, c = inject_geo(html, slug)
        if c: page_fixes.append('geo')

        html, c = inject_h1(html, slug)
        if c: page_fixes.append('h1')

        html, c = fix_missing_meta_desc(html, slug)
        if c: page_fixes.append('meta_desc')

        html, c = fix_equipment_rental_type_v2(html)
        if c: page_fixes.append('equip_type')

        if html != original:
            Path(path).write_text(html, encoding='utf-8')
            modified += 1
            for f in page_fixes:
                fixes_applied[f] = fixes_applied.get(f, 0) + 1

    print(f"Modified: {modified}/{len(paths)} pages")
    for f, c in sorted(fixes_applied.items(), key=lambda x: -x[1]):
        print(f"  {f}: {c}")


if __name__ == '__main__':
    main()
