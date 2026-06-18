#!/usr/bin/env python3
"""
Master SEO quality fixer - brings ALL pages to 100/100 technical SEO quality.
Fixes: hreflang, EquipmentRentalShop type, meta desc length, title length,
       geo.position, H1 content, word count (county pages), FAQPage schema,
       and injects structured FAQ + review blocks into thin county/state pages.
"""

import glob, re, os
from pathlib import Path

DOMAIN = "https://fixpilotportapottyrentals.com"
PHONE = "(833) 652-9344"
PHONE_SCHEMA = "+18336529344"

# ── 1. HREFLANG ──────────────────────────────────────────────────────────────

def inject_hreflang(html: str, slug: str) -> tuple[str, bool]:
    if 'hreflang' in html:
        return html, False
    url = f"{DOMAIN}/{slug}"
    tags = f"""    <link rel="alternate" hreflang="en-US" href="{url}">
    <link rel="alternate" hreflang="x-default" href="{url}">"""
    # Inject after canonical
    new_html = re.sub(
        r'(<link rel="canonical"[^>]+>)',
        r'\1\n' + tags,
        html, count=1
    )
    return new_html, new_html != html


# ── 2. EQUIPMENT RENTAL SHOP TYPE ────────────────────────────────────────────

def fix_schema_type(html: str) -> tuple[str, bool]:
    if 'EquipmentRentalShop' in html:
        return html, False

    changed = False

    # Pattern 1: ["LocalBusiness", "HomeAndConstructionBusiness"]
    p1 = r'"@type":\s*\["LocalBusiness",\s*"HomeAndConstructionBusiness"\]'
    r1 = '"@type": ["LocalBusiness", "HomeAndConstructionBusiness", "EquipmentRentalShop"]'
    new_html = re.sub(p1, r1, html)
    if new_html != html:
        return new_html, True

    # Pattern 2: "@type": "LocalBusiness" (single)
    p2 = r'"@type":\s*"LocalBusiness"'
    r2 = '"@type": ["LocalBusiness", "EquipmentRentalShop"]'
    new_html = re.sub(p2, r2, html, count=1)
    if new_html != html:
        return new_html, True

    # Pattern 3: CollectionPage (county/state hub pages)
    p3 = r'"@type":\s*"CollectionPage"'
    r3 = '"@type": ["CollectionPage", "LocalBusiness", "EquipmentRentalShop"]'
    new_html = re.sub(p3, r3, html)
    if new_html != html:
        return new_html, True

    return html, False


# ── 3. META DESCRIPTION LENGTH FIX ───────────────────────────────────────────

def fix_meta_desc(html: str) -> tuple[str, bool]:
    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if not m:
        return html, False
    desc = m.group(1)
    if len(desc) <= 165:
        return html, False
    # Truncate at last word boundary before 162, add ellipsis
    truncated = desc[:162].rsplit(' ', 1)[0].rstrip('.,;:') + '.'
    new_html = html.replace(m.group(0), f'<meta name="description" content="{truncated}"')
    return new_html, new_html != html


# ── 4. TITLE LENGTH FIX ──────────────────────────────────────────────────────

def fix_title_length(html: str) -> tuple[str, bool]:
    m = re.search(r'<title>(.*?)</title>', html)
    if not m:
        return html, False
    title = m.group(1)
    if len(title) <= 70:
        return html, False
    # Strategy: remove middle filler
    # e.g. "Porta Potty Rental X, ST — Y County | Same-Day Delivery"
    # → "Porta Potty Rental X, ST — Same-Day · From $75/Day"

    # Remove " | County" segments
    new_title = re.sub(r'\s*\|\s*[^|·—]+County[^|·—]*', '', title)
    # Remove " | Parish" segments
    new_title = re.sub(r'\s*\|\s*[^|·—]+Parish[^|·—]*', '', new_title)
    # Remove "| Same-Day Delivery" if already covered
    new_title = re.sub(r'\s*\|\s*Same-Day Delivery', '', new_title)
    # Clean up double separators
    new_title = re.sub(r'[\s·—]+$', '', new_title)

    if len(new_title) > 70:
        # Hard truncate at 67 + "..."
        new_title = new_title[:67].rsplit(' ', 1)[0] + '...'

    if new_title == title:
        return html, False

    new_html = html.replace(f'<title>{title}</title>', f'<title>{new_title}</title>')
    return new_html, new_html != html


# ── 5. GEO POSITION ──────────────────────────────────────────────────────────

# Coordinates for pages missing geo.position
GEO_DATA = {
    'porta-potty-rental-allegheny-county-pa': ('40.4406', '-79.9959', 'US-PA', 'Pittsburgh, Pennsylvania'),
    'porta-potty-rental-babylon-town-ny': ('40.6901', '-73.3246', 'US-NY', 'Babylon Town, New York'),
    'porta-potty-rental-baltimore-county-md': ('39.4062', '-76.6100', 'US-MD', 'Baltimore County, Maryland'),
    'porta-potty-rental-bexar-county-tx': ('29.4241', '-98.4936', 'US-TX', 'Bexar County, Texas'),
    'porta-potty-rental-broward-county-fl': ('26.1224', '-80.1373', 'US-FL', 'Broward County, Florida'),
    'porta-potty-rental-clark-county-nv': ('36.1716', '-115.1391', 'US-NV', 'Clark County, Nevada'),
    'porta-potty-rental-cook-county-il': ('41.8819', '-87.6278', 'US-IL', 'Cook County, Illinois'),
    'porta-potty-rental-cuyahoga-county-oh': ('41.4993', '-81.6944', 'US-OH', 'Cuyahoga County, Ohio'),
    'porta-potty-rental-dallas-county-tx': ('32.7767', '-96.7970', 'US-TX', 'Dallas County, Texas'),
    'porta-potty-rental-dallas-fort-worth-tx': ('32.9000', '-97.0641', 'US-TX', 'Dallas-Fort Worth, Texas'),
    'porta-potty-rental-davidson-county-tn': ('36.1627', '-86.7816', 'US-TN', 'Davidson County, Tennessee'),
    'porta-potty-rental-douglas-county-ne': ('41.2565', '-95.9345', 'US-NE', 'Douglas County, Nebraska'),
    'porta-potty-rental-fairfax-county-va': ('38.8462', '-77.3064', 'US-VA', 'Fairfax County, Virginia'),
    'porta-potty-rental-franklin-county-oh': ('39.9612', '-82.9988', 'US-OH', 'Franklin County, Ohio'),
    'porta-potty-rental-fulton-county-ga': ('33.7490', '-84.3880', 'US-GA', 'Fulton County, Georgia'),
    'porta-potty-rental-hamilton-county-tn': ('35.1617', '-85.2505', 'US-TN', 'Hamilton County, Tennessee'),
    'porta-potty-rental-harris-county-tx': ('29.7604', '-95.3698', 'US-TX', 'Harris County, Texas'),
    'porta-potty-rental-hennepin-county-mn': ('44.9778', '-93.2650', 'US-MN', 'Hennepin County, Minnesota'),
    'porta-potty-rental-hillsborough-county-fl': ('27.9944', '-82.3018', 'US-FL', 'Hillsborough County, Florida'),
    'porta-potty-rental-hempstead-town-ny': ('40.7137', '-73.6156', 'US-NY', 'Hempstead Town, New York'),
    'porta-potty-rental-huntington-ny': ('40.8676', '-73.4257', 'US-NY', 'Huntington, New York'),
    'porta-potty-rental-islip-ny': ('40.7298', '-73.2127', 'US-NY', 'Islip, New York'),
    'porta-potty-rental-jefferson-county-ky': ('38.1938', '-85.6385', 'US-KY', 'Jefferson County, Kentucky'),
    'porta-potty-rental-king-county-wa': ('47.6062', '-122.3321', 'US-WA', 'King County, Washington'),
    'porta-potty-rental-knox-county-tn': ('35.9951', '-83.9185', 'US-TN', 'Knox County, Tennessee'),
    'porta-potty-rental-long-island-ny': ('40.7891', '-73.1350', 'US-NY', 'Long Island, New York'),
    'porta-potty-rental-los-angeles-county-ca': ('34.0522', '-118.2437', 'US-CA', 'Los Angeles County, California'),
    'porta-potty-rental-maricopa-county-az': ('33.4484', '-112.0740', 'US-AZ', 'Maricopa County, Arizona'),
    'porta-potty-rental-marion-county-in': ('39.7684', '-86.1581', 'US-IN', 'Marion County, Indiana'),
    'porta-potty-rental-mecklenburg-county-nc': ('35.2271', '-80.8431', 'US-NC', 'Mecklenburg County, North Carolina'),
    'porta-potty-rental-miami-dade-county-fl': ('25.7617', '-80.1918', 'US-FL', 'Miami-Dade County, Florida'),
    'porta-potty-rental-multnomah-county-or': ('45.5051', '-122.6750', 'US-OR', 'Multnomah County, Oregon'),
    'porta-potty-rental-nassau-county-ny': ('40.6901', '-73.5901', 'US-NY', 'Nassau County, New York'),
    'porta-potty-rental-north-hempstead-ny': ('40.8010', '-73.6898', 'US-NY', 'North Hempstead, New York'),
    'porta-potty-rental-oklahoma-county-ok': ('35.4676', '-97.5164', 'US-OK', 'Oklahoma County, Oklahoma'),
    'porta-potty-rental-orange-county-ca': ('33.7175', '-117.8311', 'US-CA', 'Orange County, California'),
    'porta-potty-rental-orange-county-fl': ('28.5383', '-81.3792', 'US-FL', 'Orange County, Florida'),
    'porta-potty-rental-oyster-bay-ny': ('40.8676', '-73.5318', 'US-NY', 'Oyster Bay, New York'),
    'porta-potty-rental-riverside-county-ca': ('33.9806', '-117.3755', 'US-CA', 'Riverside County, California'),
    'porta-potty-rental-sacramento-county-ca': ('38.5816', '-121.4944', 'US-CA', 'Sacramento County, California'),
    'porta-potty-rental-salt-lake-county-ut': ('40.7608', '-111.8910', 'US-UT', 'Salt Lake County, Utah'),
    'porta-potty-rental-san-diego-county-ca': ('32.7157', '-117.1611', 'US-CA', 'San Diego County, California'),
    'porta-potty-rental-santa-clara-county-ca': ('37.3382', '-121.8863', 'US-CA', 'Santa Clara County, California'),
    'porta-potty-rental-shelby-county-tn': ('35.1495', '-90.0490', 'US-TN', 'Shelby County, Tennessee'),
    'porta-potty-rental-suffolk-county-ma': ('42.3601', '-71.0589', 'US-MA', 'Suffolk County, Massachusetts'),
    'porta-potty-rental-suffolk-county-ny': ('40.9176', '-72.7498', 'US-NY', 'Suffolk County, New York'),
    'porta-potty-rental-tarrant-county-tx': ('32.7555', '-97.3308', 'US-TX', 'Tarrant County, Texas'),
    'porta-potty-rental-travis-county-tx': ('30.2672', '-97.7431', 'US-TX', 'Travis County, Texas'),
    'porta-potty-rental-wayne-county-mi': ('42.3314', '-83.0458', 'US-MI', 'Wayne County, Michigan'),
    'porta-potty-rental-brookhaven-ny': ('40.7851', '-72.9165', 'US-NY', 'Brookhaven, New York'),
    'porta-potty-rental-brooklyn-park-mn': ('45.0942', '-93.3752', 'US-MN', 'Brooklyn Park, Minnesota'),
    # State pages
    'porta-potty-rental-new-jersey': ('40.0583', '-74.4057', 'US-NJ', 'New Jersey'),
    'porta-potty-rental-new-mexico': ('34.5199', '-105.8701', 'US-NM', 'New Mexico'),
    'porta-potty-rental-new-york': ('42.1657', '-74.9481', 'US-NY', 'New York'),
    'porta-potty-rental-north-carolina': ('35.7596', '-79.0193', 'US-NC', 'North Carolina'),
}


def inject_geo(html: str, slug: str) -> tuple[str, bool]:
    if 'geo.position' in html:
        return html, False
    if slug not in GEO_DATA:
        return html, False

    lat, lon, region, placename = GEO_DATA[slug]

    geo_tags = f"""    <meta name="geo.region" content="{region}">
    <meta name="geo.placename" content="{placename}">
    <meta name="geo.position" content="{lat};{lon}">
    <meta name="ICBM" content="{lat}, {lon}">"""

    # Inject before canonical
    new_html = re.sub(
        r'(<link rel="canonical")',
        geo_tags + '\n    ' + r'\1',
        html, count=1
    )
    return new_html, new_html != html


# ── 6. H1 FIX ────────────────────────────────────────────────────────────────

def fix_empty_h1(html: str) -> tuple[str, bool]:
    m = re.search(r'<h1([^>]*)>(.*?)</h1>', html, re.DOTALL)
    if not m:
        return html, False
    h1_content = m.group(2)
    h1_text = re.sub(r'<[^>]+>', '', h1_content).strip()
    if len(h1_text) >= 10:
        return html, False

    # Extract city name from title
    t = re.search(r'<title>(.*?)</title>', html)
    title = t.group(1) if t else ''
    city_m = re.search(r'Porta Potty Rental (.*?)(?:\s*[—|·]|$)', title)
    if not city_m:
        return html, False
    city_part = city_m.group(1).strip()

    new_h1_content = f'\n                    Porta Potty Rental in<br>\n                    <span class="text-brand-300">{city_part} — Fast &amp; Affordable</span>\n                '
    new_html = html.replace(m.group(0), f'<h1{m.group(1)}>{new_h1_content}</h1>')
    return new_html, new_html != html


# ── 7. FAQPAGE SCHEMA FOR COUNTY/STATE PAGES ─────────────────────────────────

def get_county_faqs(slug: str, html: str) -> str:
    """Generate FAQ schema for county/state pages that lack it."""
    t = re.search(r'<title>(.*?)</title>', html)
    title = t.group(1) if t else slug

    # Extract city/county name
    m = re.search(r'Porta Potty Rental (.*?)(?:\s*[—|·]|$)', title)
    location = m.group(1).strip() if m else slug.replace('-', ' ').title()

    # Extract state from slug
    state_m = re.search(r'-([a-z]{2})/index\.html$', slug + '/index.html') if not slug.endswith('.html') else None
    state_m = re.search(r'-([a-z]{2})$', slug)
    state = state_m.group(1).upper() if state_m else 'US'

    faqs = [
        (f"How much does portable toilet rental cost in {location}?",
         f"Standard porta potty rental in {location} starts at $75/day or $199/week. Luxury restroom trailers for events start at $595. OSHA-compliant construction packages with weekly servicing are available. Call (833) 652-9344 for a free quote."),
        (f"Do you offer same-day porta potty delivery in {location}?",
         f"Yes. FixPilot offers same-day delivery throughout {location} for orders placed before 1 PM. Emergency 24/7 dispatch is available for urgent needs. Call (833) 652-9344 for immediate availability."),
        (f"What types of portable toilets are available in {location}?",
         f"We offer standard porta potties, ADA-compliant units, luxury restroom trailers, flushable portable toilets, hand wash stations, and septic pumping services throughout {location}."),
        (f"Are your porta potties OSHA-compliant for {location} construction sites?",
         f"Yes. All units meet OSHA 29 CFR 1926.51 requirements. We include ratio documentation with every construction order — essential for OSHA inspections at {location} job sites."),
        (f"Do you serve all areas within {location}?",
         f"Yes. We serve all communities within {location} and surrounding areas. Contact us at (833) 652-9344 to confirm same-day availability for your specific location."),
        (f"Can I rent luxury restroom trailers in {location}?",
         f"Yes. Our climate-controlled luxury restroom trailers are available for events, weddings, and corporate functions throughout {location}. Starting at $595 per event. Call (833) 652-9344 for availability."),
    ]

    items = []
    for i, (q, a) in enumerate(faqs):
        items.append(f'''        {{
          "@type": "Question",
          "name": "{q}",
          "acceptedAnswer": {{"@type": "Answer", "text": "{a}"}}
        }}''')

    schema = f'''
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
{",\n".join(items)}
      ]
    }}
    </script>'''
    return schema


def inject_faqpage_schema(html: str, slug: str) -> tuple[str, bool]:
    if 'FAQPage' in html:
        return html, False

    schema = get_county_faqs(slug, html)

    # Inject before </head>
    new_html = html.replace('</head>', schema + '\n</head>', 1)
    return new_html, new_html != html


# ── 8. INJECT FAQ HTML SECTION FOR THIN PAGES ────────────────────────────────

def inject_faq_html_section(html: str, slug: str) -> tuple[str, bool]:
    """For county pages with <800 words, inject an FAQ HTML section."""
    text = re.sub(r'<[^>]+>', ' ', html)
    word_count = len(text.split())

    if word_count >= 800:
        return html, False
    if 'faq-item' in html or 'id="faq"' in html:
        return html, False

    t = re.search(r'<title>(.*?)</title>', html)
    title = t.group(1) if t else ''
    m = re.search(r'Porta Potty Rental (.*?)(?:\s*[—|·]|$)', title)
    location = m.group(1).strip() if m else slug.replace('-', ' ').title()

    faq_section = f"""
  <!-- FAQ Section -->
  <section id="faq" class="py-16 bg-white">
    <div class="container mx-auto px-4 max-w-3xl">
      <h2 class="text-3xl font-bold text-gray-900 mb-10 text-center">Portable Toilet Rental {location} — FAQ</h2>
      <div class="space-y-4">
        <div class="border border-gray-200 rounded-xl overflow-hidden">
          <div class="p-5 bg-brand-50">
            <h3 class="font-bold text-gray-800 mb-2">How much does portable toilet rental cost in {location}?</h3>
            <p class="text-gray-700 text-sm">Standard porta potty rental in {location} starts at <strong>$75/day or $199/week</strong>. Luxury restroom trailers for events start at $595. OSHA-compliant construction packages with weekly servicing are available. <a href="tel:{PHONE_SCHEMA}" class="text-brand-700 font-semibold underline">Call {PHONE}</a> for a free quote.</p>
          </div>
        </div>
        <div class="border border-gray-200 rounded-xl overflow-hidden">
          <div class="p-5 bg-brand-50">
            <h3 class="font-bold text-gray-800 mb-2">Do you offer same-day porta potty delivery in {location}?</h3>
            <p class="text-gray-700 text-sm">Yes. FixPilot offers same-day delivery throughout {location} for orders placed before 1 PM. Emergency 24/7 dispatch available. <a href="tel:{PHONE_SCHEMA}" class="text-brand-700 font-semibold underline">Call {PHONE}</a> for immediate availability.</p>
          </div>
        </div>
        <div class="border border-gray-200 rounded-xl overflow-hidden">
          <div class="p-5 bg-brand-50">
            <h3 class="font-bold text-gray-800 mb-2">Are your units OSHA-compliant for {location} construction sites?</h3>
            <p class="text-gray-700 text-sm">Yes. All units meet OSHA 29 CFR 1926.51 requirements. We include ratio documentation with every construction order — essential for inspections at {location} job sites.</p>
          </div>
        </div>
        <div class="border border-gray-200 rounded-xl overflow-hidden">
          <div class="p-5 bg-brand-50">
            <h3 class="font-bold text-gray-800 mb-2">What areas within {location} do you serve?</h3>
            <p class="text-gray-700 text-sm">We serve all communities within {location} and surrounding areas with same-day or next-day delivery. <a href="tel:{PHONE_SCHEMA}" class="text-brand-700 font-semibold underline">Call {PHONE}</a> to confirm availability for your specific location.</p>
          </div>
        </div>
        <div class="border border-gray-200 rounded-xl overflow-hidden">
          <div class="p-5 bg-brand-50">
            <h3 class="font-bold text-gray-800 mb-2">Can I rent luxury restroom trailers in {location}?</h3>
            <p class="text-gray-700 text-sm">Yes. Our climate-controlled luxury restroom trailers — perfect for outdoor weddings, corporate events, and upscale outdoor venues — are available throughout {location}. Starting at $595/event.</p>
          </div>
        </div>
        <div class="border border-gray-200 rounded-xl overflow-hidden">
          <div class="p-5 bg-brand-50">
            <h3 class="font-bold text-gray-800 mb-2">What types of portable toilets are available in {location}?</h3>
            <p class="text-gray-700 text-sm">We offer standard porta potties, ADA-compliant units, luxury restroom trailers, flushable portable toilets, hand wash stations, and septic pumping services. All units are cleaned, sanitized, and OSHA-compliant.</p>
          </div>
        </div>
      </div>
      <!-- Resource links -->
      <div class="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <a href="/blog/porta-potty-rental-costs-2026.html" class="flex gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition">
          <span class="text-xl">💰</span><div><p class="font-bold text-brand-900 text-sm">2026 Cost Guide</p><p class="text-xs text-gray-500">Pricing by unit type</p></div>
        </a>
        <a href="/blog/osha-requirements-construction-sites.html" class="flex gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition">
          <span class="text-xl">🦺</span><div><p class="font-bold text-brand-900 text-sm">OSHA Guide</p><p class="text-xs text-gray-500">Construction compliance</p></div>
        </a>
        <a href="/calculator" class="flex gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition">
          <span class="text-xl">🧮</span><div><p class="font-bold text-brand-900 text-sm">Free Calculator</p><p class="text-xs text-gray-500">Instant estimate</p></div>
        </a>
      </div>
    </div>
  </section>

"""
    # Inject before footer
    footer_idx = html.rfind('<footer')
    if footer_idx == -1:
        footer_idx = html.rfind('</body>')
    if footer_idx == -1:
        return html, False

    new_html = html[:footer_idx] + faq_section + html[footer_idx:]
    return new_html, True


# ── 9. LOCAL BUSINESS SCHEMA FOR COUNTY PAGES ────────────────────────────────

def inject_localbusiness_schema(html: str, slug: str) -> tuple[str, bool]:
    if '"LocalBusiness"' in html or 'LocalBusiness' in html:
        return html, False

    t = re.search(r'<title>(.*?)</title>', html)
    title = t.group(1) if t else ''
    m = re.search(r'Porta Potty Rental (.*?)(?:\s*[—|·]|$)', title)
    location = m.group(1).strip() if m else 'Local Area'

    # Get geo from existing meta
    lat_m = re.search(r'geo\.position.*?content=\"([0-9.\-]+);([0-9.\-]+)\"', html)
    lat, lon = (lat_m.group(1), lat_m.group(2)) if lat_m else ('39.0', '-98.0')

    state_m = re.search(r'-([a-z]{2})$', slug)
    state = state_m.group(1).upper() if state_m else 'US'

    schema = f'''
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": ["LocalBusiness", "EquipmentRentalShop"],
      "name": "FixPilot Porta Potty Rentals",
      "description": "FixPilot provides portable toilet and luxury restroom trailer rentals throughout {location}. OSHA-compliant, same-day delivery available.",
      "telephone": "{PHONE_SCHEMA}",
      "url": "https://fixpilotportapottyrentals.com/{slug}",
      "areaServed": "{location}",
      "geo": {{"@type": "GeoCoordinates", "latitude": {lat}, "longitude": {lon}}},
      "openingHoursSpecification": {{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "00:00", "closes": "23:59"}}
    }}
    </script>'''

    new_html = html.replace('</head>', schema + '\n</head>', 1)
    return new_html, new_html != html


# ── MAIN ─────────────────────────────────────────────────────────────────────

def process_page(path: str) -> dict:
    slug = path.split('/')[0]
    html = Path(path).read_text(encoding='utf-8', errors='replace')
    original = html
    fixes = []

    html, changed = inject_hreflang(html, slug)
    if changed: fixes.append('hreflang')

    html, changed = fix_schema_type(html)
    if changed: fixes.append('schema_type')

    html, changed = fix_meta_desc(html)
    if changed: fixes.append('meta_desc_length')

    html, changed = fix_title_length(html)
    if changed: fixes.append('title_length')

    html, changed = inject_geo(html, slug)
    if changed: fixes.append('geo_tags')

    html, changed = fix_empty_h1(html)
    if changed: fixes.append('h1_content')

    html, changed = inject_localbusiness_schema(html, slug)
    if changed: fixes.append('localbusiness_schema')

    html, changed = inject_faqpage_schema(html, slug)
    if changed: fixes.append('faqpage_schema')

    html, changed = inject_faq_html_section(html, slug)
    if changed: fixes.append('faq_html_section')

    if html != original:
        Path(path).write_text(html, encoding='utf-8')

    return {'path': path, 'fixes': fixes}


def main():
    paths = sorted(glob.glob('porta-potty-rental-*-*/index.html'))
    # Also fix state pages
    state_paths = sorted(glob.glob('porta-potty-rental-*/index.html'))
    # Remove city pages from state paths
    city_set = set(paths)
    state_only = [p for p in state_paths if p not in city_set]

    all_paths = paths + state_only

    total_fixes = {}
    fixed_count = 0

    for path in all_paths:
        result = process_page(path)
        if result['fixes']:
            fixed_count += 1
            for f in result['fixes']:
                total_fixes[f] = total_fixes.get(f, 0) + 1

    print(f"Pages modified: {fixed_count}/{len(all_paths)}")
    print("\nFixes applied:")
    for fix, count in sorted(total_fixes.items(), key=lambda x: -x[1]):
        print(f"  {fix}: {count} pages")


if __name__ == '__main__':
    main()
