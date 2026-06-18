#!/usr/bin/env python3
"""
City page quality deep-dive:
  1. Local specificity (landmarks, neighborhoods, county name present)
  2. Schema richness (geo coords, reviews, service area, opening hours)
  3. Content sections completeness (FAQ, reviews, service cards, nearby cities)
  4. Google Maps embed presence
  5. Hero image assigned (not placeholder/missing)
  6. Word count distribution
  7. Nearby city links
  8. Review count and rating in schema
  9. Pages with duplicate H1 text across cities
  10. Missing area/neighborhood names
"""
import os, re
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.abspath(__file__))

def read(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ''

def strip_tags(html):
    return re.sub(r'<[^>]+>', ' ', html)

def wc(html):
    return len(strip_tags(html).split())

city_dirs = sorted([d for d in os.listdir(ROOT)
                    if d.startswith('porta-potty-rental-')
                    and os.path.isdir(os.path.join(ROOT, d))])

results = []

for slug in city_dirs:
    path = os.path.join(ROOT, slug, 'index.html')
    html = read(path)
    if not html:
        results.append({'slug': slug, 'error': 'no index.html'})
        continue

    issues = []
    info   = {'slug': slug}

    # ── word count ────────────────────────────────────────────────────
    words = wc(html)
    info['words'] = words
    if words < 1000:
        issues.append(f'LOW_WORDS({words})')

    # ── schema fields ─────────────────────────────────────────────────
    has_geo      = 'latitude' in html and 'longitude' in html
    has_reviews  = '"Review"' in html or '"review"' in html or 'reviewRating' in html
    has_hours    = 'openingHours' in html or 'opens' in html
    has_service_area = 'serviceArea' in html or 'areaServed' in html
    has_price    = 'priceRange' in html
    has_aggregate = 'aggregateRating' in html or 'AggregateRating' in html

    info['has_geo']       = has_geo
    info['has_reviews']   = has_reviews
    info['has_hours']     = has_hours
    info['has_service_area'] = has_service_area
    info['has_price']     = has_price
    info['has_aggregate'] = has_aggregate

    if not has_geo:       issues.append('NO_SCHEMA_GEO')
    if not has_reviews:   issues.append('NO_SCHEMA_REVIEWS')
    if not has_hours:     issues.append('NO_SCHEMA_HOURS')
    if not has_price:     issues.append('NO_SCHEMA_PRICE')
    if not has_aggregate: issues.append('NO_AGGREGATE_RATING')

    # ── review count in schema ────────────────────────────────────────
    review_count = len(re.findall(r'"@type":\s*"Review"', html))
    info['review_count'] = review_count
    if review_count < 2:
        issues.append(f'FEW_REVIEWS({review_count})')

    # ── FAQ section ───────────────────────────────────────────────────
    faq_questions = len(re.findall(r'FAQPage|Question.*acceptedAnswer|<h3[^>]*>[^<]{20,}', html))
    has_faq_schema = 'FAQPage' in html
    has_faq_html   = bool(re.search(r'(?i)faq|frequently asked', html))
    info['has_faq'] = has_faq_schema or has_faq_html
    if not (has_faq_schema or has_faq_html):
        issues.append('NO_FAQ')

    # ── service cards ─────────────────────────────────────────────────
    svc_links = len(re.findall(r'href=["\']/services/', html))
    info['svc_links'] = svc_links
    if svc_links < 4:
        issues.append(f'FEW_SERVICE_LINKS({svc_links})')

    # ── nearby city links ─────────────────────────────────────────────
    nearby = len(re.findall(r'href=["\']/porta-potty-rental-', html))
    info['nearby_links'] = nearby
    if nearby == 0:
        issues.append('NO_NEARBY_LINKS')
    elif nearby < 3:
        issues.append(f'FEW_NEARBY_LINKS({nearby})')

    # ── Google Maps embed ─────────────────────────────────────────────
    has_map_embed = 'maps.google.com/maps' in html and 'embed' in html
    info['has_map_embed'] = has_map_embed
    if not has_map_embed:
        issues.append('NO_MAP_EMBED')

    # ── hero image ────────────────────────────────────────────────────
    hero_img = re.search(r'hero[^"\']*\.(webp|jpg|jpeg|png)', html, re.IGNORECASE)
    has_hero = bool(hero_img) or 'hero-banner-images' in html
    info['has_hero'] = has_hero
    if not has_hero:
        issues.append('NO_HERO_IMAGE')

    # ── local areas/neighborhoods ─────────────────────────────────────
    area_count = len(re.findall(r'"@type":\s*"Neighborhood"', html))
    info['area_count'] = area_count
    if area_count < 2:
        issues.append(f'FEW_NEIGHBORHOODS({area_count})')

    # ── H1 text ───────────────────────────────────────────────────────
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    h1_text = re.sub(r'\s+', ' ', strip_tags(h1.group(1))).strip() if h1 else ''
    info['h1'] = h1_text

    # ── phone number ─────────────────────────────────────────────────
    if 'tel:' not in html:
        issues.append('NO_PHONE')

    info['issues']      = issues
    info['issue_count'] = len(issues)
    results.append(info)

# ── summary ────────────────────────────────────────────────────────────────
total = len(results)
errors = [r for r in results if 'error' in r]
valid  = [r for r in results if 'error' not in r]

print('=' * 70)
print(f'CITY PAGE QUALITY AUDIT — {total} pages')
print('=' * 70)

clean = sum(1 for r in valid if r['issue_count'] == 0)
print(f'\nPages with no issues : {clean} / {len(valid)} ({clean*100//len(valid)}%)')
if errors:
    print(f'Pages with no file   : {len(errors)}')
    for r in errors:
        print(f'  {r["slug"]}: {r["error"]}')

# Issue frequency
issue_freq = Counter()
for r in valid:
    for iss in r['issues']:
        key = re.sub(r'\([^)]*\)', '', iss)
        issue_freq[key] += 1

print('\n── Issue frequency ──────────────────────────────────────────────────')
for issue, cnt in issue_freq.most_common():
    bar = '█' * (cnt * 40 // max(issue_freq.values()))
    print(f'  {issue:<30s} {cnt:4d} / {len(valid)}  {bar}')

# ── schema coverage ────────────────────────────────────────────────────────
print('\n── Schema coverage ──────────────────────────────────────────────────')
for field, key in [('geo coords', 'has_geo'), ('reviews', 'has_reviews'),
                   ('opening hours', 'has_hours'), ('service area', 'has_service_area'),
                   ('price range', 'has_price'), ('aggregate rating', 'has_aggregate')]:
    n = sum(1 for r in valid if r.get(key))
    print(f'  {field:<20}: {n:4d} / {len(valid)}  ({n*100//len(valid)}%)')

# ── word count ─────────────────────────────────────────────────────────────
print('\n── Word count ───────────────────────────────────────────────────────')
buckets = [(0, 1000, '<1000 (thin)'), (1000, 2000, '1000-2000'),
           (2000, 3000, '2000-3000'), (3000, 5000, '3000-5000'), (5000, 99999, '5000+')]
for lo, hi, label in buckets:
    n = sum(1 for r in valid if lo <= r.get('words', 0) < hi)
    bar = '█' * (n * 30 // len(valid))
    print(f'  {label:<18}: {n:4d}  {bar}')

# ── nearby links ───────────────────────────────────────────────────────────
print('\n── Nearby city links ────────────────────────────────────────────────')
for lo, hi, label in [(0, 1, '0 (none)'), (1, 3, '1-2'), (3, 6, '3-5'), (6, 99, '6+')]:
    n = sum(1 for r in valid if lo <= r.get('nearby_links', 0) < hi)
    print(f'  {label:<12}: {n:4d}')

# ── review count ───────────────────────────────────────────────────────────
print('\n── Review count in schema ───────────────────────────────────────────')
for lo, hi, label in [(0, 1, '0'), (1, 2, '1'), (2, 4, '2-3'), (4, 99, '4+')]:
    n = sum(1 for r in valid if lo <= r.get('review_count', 0) < hi)
    print(f'  {label:<6}: {n:4d}')

# ── worst pages ────────────────────────────────────────────────────────────
print('\n── Pages with most issues ───────────────────────────────────────────')
worst = sorted(valid, key=lambda r: r['issue_count'], reverse=True)
for r in worst[:40]:
    if r['issue_count'] == 0:
        break
    print(f'  [{r["issue_count"]}] {r["slug"]:<55} {", ".join(r["issues"])}')

# ── specific issue lists ────────────────────────────────────────────────────
for issue_key, label in [
    ('NO_NEARBY_LINKS',  'Pages with NO nearby city links'),
    ('NO_MAP_EMBED',     'Pages with no Google Maps embed'),
    ('NO_FAQ',           'Pages with no FAQ section'),
    ('NO_HERO_IMAGE',    'Pages with no hero image'),
]:
    pages = [r['slug'] for r in valid if any(issue_key in i for i in r['issues'])]
    if pages:
        print(f'\n── {label} ({len(pages)}) ─────────────────────────────────────')
        for pg in pages[:30]:
            print(f'  {pg}')

print('\n' + '=' * 70)
