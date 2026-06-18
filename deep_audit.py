#!/usr/bin/env python3
"""
Deep quality audit — checks things the basic SEO audit doesn't cover:
  1. Image alt text (missing/empty)
  2. Internal broken links (links to pages that don't exist on disk)
  3. Schema completeness (LocalBusiness required fields)
  4. Service card links (city pages linking to /services/ pages)
  5. Tel: link presence (phone CTA)
  6. Content similarity across city pages (template leakage)
  7. Blog ↔ service/city internal links
  8. Canonical URL vs actual file path mismatch
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

# ── collect pages ──────────────────────────────────────────────────────────
city_dirs  = sorted([d for d in os.listdir(ROOT) if d.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(ROOT, d))])
svc_files  = sorted([f for f in os.listdir(os.path.join(ROOT, 'services')) if f.endswith('.html') and not f.endswith('.legacy')])
blog_files = sorted([f for f in os.listdir(os.path.join(ROOT, 'blog')) if f.endswith('.html')])

# Build a set of known paths (relative to ROOT) for link validation
known_paths = set()
for d in city_dirs:
    known_paths.add(f'/{d}/')
    known_paths.add(f'/{d}')
for f in svc_files:
    known_paths.add(f'/services/{f}')
    known_paths.add(f'/services/{f[:-5]}')  # without .html
for f in blog_files:
    known_paths.add(f'/blog/{f}')
    known_paths.add(f'/blog/{f[:-5]}')
known_paths.update(['/', '/locations', '/locations.html', '/about', '/blog', '/services',
                    '/sitemap.xml', '/robots.txt', '#', 'tel:', 'mailto:'])

print('=' * 70)
print('DEEP QUALITY AUDIT')
print('=' * 70)

# ── 1. Image alt text ─────────────────────────────────────────────────────
print('\n── 1. Image alt text issues ─────────────────────────────────────────')
missing_alt = []
empty_alt   = []
IMG_PAT = re.compile(r'<img([^>]+)>', re.IGNORECASE)

for slug in city_dirs[:]:
    path = os.path.join(ROOT, slug, 'index.html')
    html = read(path)
    for m in IMG_PAT.finditer(html):
        attrs = m.group(1)
        if 'alt=' not in attrs.lower():
            missing_alt.append(slug)
        elif re.search(r'alt=["\']["\']', attrs):
            empty_alt.append(slug)

for f in svc_files:
    path = os.path.join(ROOT, 'services', f)
    html = read(path)
    for m in IMG_PAT.finditer(html):
        attrs = m.group(1)
        if 'alt=' not in attrs.lower():
            missing_alt.append(f'services/{f}')
        elif re.search(r'alt=["\']["\']', attrs):
            empty_alt.append(f'services/{f}')

missing_pages = len(set(missing_alt))
empty_pages   = len(set(empty_alt))
print(f'  Pages with imgs missing alt entirely : {missing_pages}')
print(f'  Pages with empty alt="" on imgs      : {empty_pages}')
if set(missing_alt):
    for pg in sorted(set(missing_alt))[:10]:
        n = missing_alt.count(pg)
        print(f'    {pg}: {n} img(s) missing alt')
if set(empty_alt):
    for pg in sorted(set(empty_alt))[:10]:
        n = empty_alt.count(pg)
        print(f'    {pg}: {n} img(s) with empty alt')

# ── 2. Internal broken links ──────────────────────────────────────────────
print('\n── 2. Internal broken links ─────────────────────────────────────────')
HREF_PAT = re.compile(r'href=["\']([^"\'#][^"\']*)["\']', re.IGNORECASE)
broken = defaultdict(list)
checked = 0

all_pages = (
    [(os.path.join(ROOT, d, 'index.html'), f'/{d}/') for d in city_dirs] +
    [(os.path.join(ROOT, 'services', f), f'/services/{f}') for f in svc_files] +
    [(os.path.join(ROOT, 'blog', f), f'/blog/{f}') for f in blog_files]
)

for path, page_slug in all_pages:
    html = read(path)
    for m in HREF_PAT.finditer(html):
        href = m.group(1)
        # Only check internal links
        if href.startswith('http') or href.startswith('//') or href.startswith('tel:') or href.startswith('mailto:'):
            continue
        # Normalize
        href_clean = href.split('?')[0].split('#')[0].rstrip('/')
        if not href_clean or href_clean in ('', '.', '..'):
            continue

        # Check if it resolves on disk
        if href_clean.startswith('/'):
            disk_path = os.path.join(ROOT, href_clean.lstrip('/'))
        else:
            disk_path = os.path.join(ROOT, href_clean)

        # Check as-is, as index.html, or as .html
        exists = (os.path.exists(disk_path) or
                  os.path.exists(disk_path + '/index.html') or
                  os.path.exists(disk_path + '.html') or
                  os.path.exists(os.path.join(disk_path, 'index.html')))
        if not exists:
            broken[page_slug].append(href_clean)
        checked += 1

print(f'  Links checked: {checked:,}')
total_broken = sum(len(v) for v in broken.values())
print(f'  Broken internal links found: {total_broken} across {len(broken)} pages')
for pg, links in sorted(broken.items(), key=lambda x: -len(x[1]))[:20]:
    uniq = list(dict.fromkeys(links))[:5]
    print(f'  [{len(links)}] {pg}')
    for l in uniq:
        print(f'         → {l}')

# ── 3. Schema LocalBusiness completeness ─────────────────────────────────
print('\n── 3. Schema LocalBusiness completeness (city pages) ────────────────')
SCHEMA_FIELDS = ['addressLocality', 'addressRegion', 'postalCode', 'telephone',
                 'hasMap', 'geo', 'latitude', 'longitude']
missing_fields = defaultdict(list)

for slug in city_dirs:
    path = os.path.join(ROOT, slug, 'index.html')
    html = read(path)
    if 'LocalBusiness' not in html and 'local_business' not in html.lower():
        missing_fields['NO_LOCALBUSINESS_SCHEMA'].append(slug)
        continue
    for field in SCHEMA_FIELDS:
        if field not in html:
            missing_fields[field].append(slug)

print(f'  Schema field coverage across {len(city_dirs)} city pages:')
for field, pages in sorted(missing_fields.items(), key=lambda x: -len(x[1])):
    print(f'  Missing {field:<20}: {len(pages):4d} pages  {pages[0] if pages else ""}')

# ── 4. Service card links ─────────────────────────────────────────────────
print('\n── 4. Service card → /services/ link coverage (city pages sample) ───')
no_service_links = []
weak_service_links = []
for slug in city_dirs:
    path = os.path.join(ROOT, slug, 'index.html')
    html = read(path)
    svc_hrefs = re.findall(r'href=["\'](/services/[^"\']+)["\']', html)
    if not svc_hrefs:
        no_service_links.append(slug)
    elif len(set(svc_hrefs)) < 3:
        weak_service_links.append((slug, len(set(svc_hrefs))))

print(f'  City pages with NO /services/ links : {len(no_service_links)}')
print(f'  City pages with <3 /services/ links : {len(weak_service_links)}')
if no_service_links:
    for pg in no_service_links[:10]:
        print(f'    {pg}')

# ── 5. Phone CTA (tel: links) ─────────────────────────────────────────────
print('\n── 5. Missing phone CTA (tel: link) ─────────────────────────────────')
no_tel = []
for slug in city_dirs:
    path = os.path.join(ROOT, slug, 'index.html')
    html = read(path)
    if 'tel:' not in html:
        no_tel.append(slug)
for f in svc_files:
    path = os.path.join(ROOT, 'services', f)
    html = read(path)
    if 'tel:' not in html:
        no_tel.append(f'services/{f}')
print(f'  Pages missing tel: links: {len(no_tel)}')
for pg in no_tel[:10]:
    print(f'    {pg}')

# ── 6. City page content similarity (FAQ/boilerplate leakage) ────────────
print('\n── 6. City page FAQ/boilerplate similarity (6-gram check) ──────────')
def ngrams(text, n=6):
    words = text.lower().split()
    return set(zip(*[words[i:] for i in range(n)]))

# Sample 20 city pages and check shared 6-gram count
sample = city_dirs[:10] + city_dirs[100:110]
texts = {}
for slug in sample:
    path = os.path.join(ROOT, slug, 'index.html')
    html = read(path)
    texts[slug] = ngrams(strip_tags(html))

# Find pairs with high overlap
high_sim = []
slugs = list(texts.keys())
for i in range(len(slugs)):
    for j in range(i+1, len(slugs)):
        a, b = slugs[i], slugs[j]
        shared = len(texts[a] & texts[b])
        total  = min(len(texts[a]), len(texts[b]))
        pct    = shared * 100 // total if total else 0
        if pct > 30:
            high_sim.append((pct, shared, a, b))

high_sim.sort(reverse=True)
print(f'  Pairs with >30% shared 6-grams (from 20-page sample):')
if high_sim:
    for pct, shared, a, b in high_sim[:10]:
        print(f'  {pct:3d}%  ({shared} shared)  {a}  ↔  {b}')
else:
    print('  None — content is well-differentiated')

# ── 7. Blog internal linking to city/service pages ───────────────────────
print('\n── 7. Blog posts: internal links to city/service pages ──────────────')
no_internal = []
for f in blog_files:
    path = os.path.join(ROOT, 'blog', f)
    html = read(path)
    city_links = re.findall(r'href=["\'](/porta-potty-rental-[^"\']+)["\']', html)
    svc_links  = re.findall(r'href=["\'](/services/[^"\']+)["\']', html)
    if not city_links and not svc_links:
        no_internal.append(f)

print(f'  Blog posts with no links to city or service pages: {len(no_internal)}')
for f in no_internal[:15]:
    print(f'    blog/{f}')

# ── 8. Canonical URL vs slug mismatch ────────────────────────────────────
print('\n── 8. Canonical URL mismatches ──────────────────────────────────────')
DOMAIN = 'fixpilotportapottyrentals.com'
canon_issues = []
for slug in city_dirs:
    path = os.path.join(ROOT, slug, 'index.html')
    html = read(path)
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if canon:
        url = canon.group(1)
        expected = f'https://{DOMAIN}/{slug}'
        if url.rstrip('/') != expected.rstrip('/'):
            canon_issues.append((slug, url, expected))

print(f'  Canonical mismatches: {len(canon_issues)}')
for slug, got, want in canon_issues[:15]:
    print(f'  {slug}')
    print(f'    got : {got}')
    print(f'    want: {want}')

print('\n' + '=' * 70)
