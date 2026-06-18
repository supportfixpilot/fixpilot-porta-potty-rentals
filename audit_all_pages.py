#!/usr/bin/env python3
"""
Comprehensive SEO + Content Quality Audit
Checks: titles, meta descriptions, H1/H2 structure, canonical, schema,
        OG/Twitter tags, geo meta, word count, file size, duplicates.
Outputs a full report + per-category CSV.
"""
import os, re, sys
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── helpers ────────────────────────────────────────────────────────────────

def read(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ''

def strip_tags(html):
    return re.sub(r'<[^>]+>', ' ', html)

def word_count(html):
    return len(strip_tags(html).split())

def get(pattern, html, group=1, flags=re.DOTALL | re.IGNORECASE):
    m = re.search(pattern, html, flags)
    return m.group(group).strip() if m else ''

def getall(pattern, html, flags=re.DOTALL | re.IGNORECASE):
    return re.findall(pattern, html, flags)

# ── per-page audit ─────────────────────────────────────────────────────────

def audit_page(path, page_type):
    html = read(path)
    if not html:
        return {'path': path, 'type': page_type, 'error': 'unreadable'}

    size_kb = os.path.getsize(path) / 1024
    issues = []

    # Title
    title = get(r'<title>(.*?)</title>', html)
    if not title:
        issues.append('MISSING_TITLE')
    else:
        tl = len(title)
        if tl < 30:
            issues.append(f'TITLE_TOO_SHORT({tl})')
        elif tl > 70:
            issues.append(f'TITLE_TOO_LONG({tl})')

    # Meta description — support both attribute orderings and quote styles
    desc = get(r'<meta\s+name="description"\s+content="(.*?)"', html)
    if not desc:
        desc = get(r"<meta\s+name='description'\s+content='(.*?)'", html)
    if not desc:
        desc = get(r'<meta\s+content="(.*?)"\s+name="description"', html)
    if not desc:
        issues.append('MISSING_META_DESC')
    else:
        dl = len(desc)
        if dl < 100:
            issues.append(f'DESC_TOO_SHORT({dl})')
        elif dl > 165:
            issues.append(f'DESC_TOO_LONG({dl})')

    # Canonical
    canonical = get(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', html)
    if not canonical:
        issues.append('MISSING_CANONICAL')
    elif not canonical.startswith('https://'):
        issues.append('CANONICAL_NOT_HTTPS')

    # H1 — normalize whitespace before measuring length
    h1s = getall(r'<h1[^>]*>(.*?)</h1>', html)
    h1_raw = h1s[0] if h1s else ''
    h1_text = re.sub(r'\s+', ' ', strip_tags(h1_raw)).strip()
    if not h1s:
        issues.append('MISSING_H1')
    elif len(h1s) > 1:
        issues.append(f'MULTIPLE_H1({len(h1s)})')
    elif len(h1_text) > 80:
        issues.append(f'H1_TOO_LONG({len(h1_text)})')

    # H2 count
    h2_count = len(getall(r'<h2[^>]', html))
    if h2_count == 0:
        issues.append('NO_H2')
    elif h2_count < 3 and page_type in ('city', 'service'):
        issues.append(f'FEW_H2({h2_count})')

    # Schema
    if 'application/ld+json' not in html:
        issues.append('NO_SCHEMA')

    # OG tags
    if 'og:title' not in html:
        issues.append('NO_OG_TITLE')
    if 'og:description' not in html:
        issues.append('NO_OG_DESC')
    if 'og:image' not in html:
        issues.append('NO_OG_IMAGE')

    # Twitter card
    if 'twitter:card' not in html:
        issues.append('NO_TWITTER_CARD')

    # Geo meta (city pages only)
    if page_type == 'city':
        if 'geo.region' not in html:
            issues.append('NO_GEO_REGION')
        if 'geo.position' not in html:
            issues.append('NO_GEO_POSITION')

    # Word count
    wc = word_count(html)
    if page_type == 'city' and wc < 600:
        issues.append(f'THIN_CONTENT({wc}w)')
    elif page_type == 'blog' and wc < 1000:
        issues.append(f'THIN_BLOG({wc}w)')
    elif page_type == 'service' and wc < 500:
        issues.append(f'THIN_SERVICE({wc}w)')

    # File size
    if size_kb > 200:
        issues.append(f'OVERSIZED({size_kb:.0f}KB)')
    elif size_kb < 10 and page_type != 'other':
        issues.append(f'UNDERSIZED({size_kb:.0f}KB)')

    # Robots meta
    robots = get(r'<meta\s+name=["\']robots["\']\s+content=["\'](.*?)["\']', html)
    if robots and ('noindex' in robots.lower() or 'nofollow' in robots.lower()):
        issues.append(f'ROBOTS_RESTRICTED({robots})')

    # Broken placeholder text — look in visible text only, not HTML attributes
    visible = re.sub(r'<[^>]+>', ' ', html)
    for placeholder in ['[CITY]', '[STATE]', '[INSERT', 'FIXME']:
        if placeholder.lower() in visible.lower():
            issues.append(f'PLACEHOLDER_TEXT({placeholder})')

    return {
        'path': path,
        'type': page_type,
        'title': title,
        'title_len': len(title),
        'desc': desc,
        'desc_len': len(desc),
        'canonical': canonical,
        'h1': h1_text[:80],
        'h1_count': len(h1s),
        'h2_count': h2_count,
        'word_count': wc,
        'size_kb': round(size_kb, 1),
        'has_schema': 'application/ld+json' in html,
        'issues': issues,
        'issue_count': len(issues),
    }

# ── collect pages ──────────────────────────────────────────────────────────

def collect_pages():
    pages = []

    # City pages
    for d in sorted(os.listdir(ROOT)):
        if d.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(ROOT, d)):
            p = os.path.join(ROOT, d, 'index.html')
            if os.path.exists(p):
                pages.append((p, 'city', d))

    # Service pages
    svc_dir = os.path.join(ROOT, 'services')
    if os.path.isdir(svc_dir):
        for f in sorted(os.listdir(svc_dir)):
            if f.endswith('.html') and not f.endswith('.legacy'):
                pages.append((os.path.join(svc_dir, f), 'service', f'services/{f}'))

    # Blog pages
    blog_dir = os.path.join(ROOT, 'blog')
    if os.path.isdir(blog_dir):
        for f in sorted(os.listdir(blog_dir)):
            if f.endswith('.html'):
                pages.append((os.path.join(blog_dir, f), 'blog', f'blog/{f}'))

    # Root index + locations
    for f in ['index.html', 'locations.html', '404.html']:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            pages.append((p, 'root', f))

    return pages

# ── run audit ──────────────────────────────────────────────────────────────

def run():
    pages = collect_pages()
    results = []
    for path, ptype, slug in pages:
        r = audit_page(path, ptype)
        r['slug'] = slug
        results.append(r)

    # ── duplicate detection ────────────────────────────────────────────────
    title_counts = Counter(r['title'] for r in results if r.get('title'))
    desc_counts  = Counter(r['desc']  for r in results if r.get('desc'))

    for r in results:
        if title_counts.get(r.get('title', ''), 0) > 1:
            r['issues'].append(f"DUPLICATE_TITLE(x{title_counts[r['title']]})")
            r['issue_count'] += 1
        if desc_counts.get(r.get('desc', ''), 0) > 1:
            r['issues'].append(f"DUPLICATE_DESC(x{desc_counts[r['desc']]})")
            r['issue_count'] += 1

    # ── summary stats ──────────────────────────────────────────────────────
    total = len(results)
    by_type = defaultdict(list)
    for r in results:
        by_type[r['type']].append(r)

    issue_freq = Counter()
    for r in results:
        for iss in r.get('issues', []):
            key = re.sub(r'\([^)]*\)', '', iss)  # strip params for grouping
            issue_freq[key] += 1

    clean = sum(1 for r in results if r.get('issue_count', 0) == 0)

    print('=' * 70)
    print('PORTA POTTY RENTAL SITE — SEO + CONTENT AUDIT')
    print('=' * 70)
    print(f'\nTotal pages audited : {total}')
    print(f'Pages with no issues: {clean} ({clean*100//total}%)')
    print(f'Pages with issues   : {total - clean}')

    print('\n── By page type ──────────────────────────────────────────────────')
    for ptype in ('city', 'service', 'blog', 'root'):
        pages_t = by_type.get(ptype, [])
        if not pages_t:
            continue
        avg_wc  = sum(r.get('word_count', 0) for r in pages_t) // len(pages_t)
        avg_kb  = sum(r.get('size_kb', 0) for r in pages_t) / len(pages_t)
        w_issues = sum(1 for r in pages_t if r.get('issue_count', 0) > 0)
        print(f'  {ptype:8s}: {len(pages_t):4d} pages | avg word count {avg_wc:,} | avg size {avg_kb:.1f} KB | {w_issues} have issues')

    print('\n── Top issues (all pages) ───────────────────────────────────────')
    for issue, cnt in issue_freq.most_common(25):
        bar = '█' * (cnt * 40 // max(issue_freq.values()))
        print(f'  {issue:<35s} {cnt:4d}  {bar}')

    print('\n── Word count distribution (city pages) ─────────────────────────')
    city_wc = sorted(r.get('word_count', 0) for r in by_type.get('city', []))
    if city_wc:
        buckets = [(0, 500, 'thin <500'), (500, 800, '500-800'), (800, 1200, '800-1200'),
                   (1200, 2000, '1200-2000'), (2000, 999999, '> 2000')]
        for lo, hi, label in buckets:
            n = sum(1 for w in city_wc if lo <= w < hi)
            print(f'  {label:<15}: {n:4d}  {"█"*(n*30//len(city_wc))}')

    print('\n── File size distribution (city pages) ──────────────────────────')
    city_kb = sorted(r.get('size_kb', 0) for r in by_type.get('city', []))
    if city_kb:
        buckets = [(0, 20, '<20 KB'), (20, 50, '20-50 KB'), (50, 100, '50-100 KB'),
                   (100, 150, '100-150 KB'), (150, 999, '>150 KB')]
        for lo, hi, label in buckets:
            n = sum(1 for k in city_kb if lo <= k < hi)
            print(f'  {label:<15}: {n:4d}  {"█"*(n*30//len(city_kb))}')

    print('\n── Pages with most issues ───────────────────────────────────────')
    worst = sorted(results, key=lambda r: r.get('issue_count', 0), reverse=True)[:30]
    for r in worst:
        if r.get('issue_count', 0) == 0:
            break
        slug = r['slug']
        issues_str = ', '.join(r.get('issues', []))
        print(f'  [{r["issue_count"]}] {slug:<55s}  {issues_str}')

    # ── per-type breakdowns ────────────────────────────────────────────────
    for ptype, label in [('city', 'CITY PAGES'), ('service', 'SERVICE PAGES'), ('blog', 'BLOG PAGES')]:
        pages_t = [r for r in results if r['type'] == ptype and r.get('issue_count', 0) > 0]
        if not pages_t:
            continue
        print(f'\n{"─"*70}')
        print(f'{label} — pages with issues ({len(pages_t)} of {len(by_type.get(ptype,[]))})')
        print(f'{"─"*70}')
        for r in sorted(pages_t, key=lambda x: x.get('issue_count', 0), reverse=True)[:50]:
            issues_str = ', '.join(r.get('issues', []))
            print(f'  {r["slug"]:<55s}  {issues_str}')

    # ── duplicate titles ──────────────────────────────────────────────────
    dup_titles = {t: cnt for t, cnt in title_counts.items() if cnt > 1}
    if dup_titles:
        print(f'\n── Duplicate titles ({len(dup_titles)} groups) ──────────────────────────')
        for title, cnt in sorted(dup_titles.items(), key=lambda x: -x[1])[:20]:
            pages_with = [r['slug'] for r in results if r.get('title') == title]
            print(f'  x{cnt} "{title[:70]}"')
            for pg in pages_with[:4]:
                print(f'       {pg}')

    # ── duplicate descriptions ───────────────────────────────────────────
    dup_descs = {d: cnt for d, cnt in desc_counts.items() if cnt > 1}
    if dup_descs:
        print(f'\n── Duplicate meta descriptions ({len(dup_descs)} groups) ─────────────')
        for desc, cnt in sorted(dup_descs.items(), key=lambda x: -x[1])[:20]:
            pages_with = [r['slug'] for r in results if r.get('desc') == desc]
            print(f'  x{cnt} "{desc[:100]}"')
            for pg in pages_with[:4]:
                print(f'       {pg}')

    # ── CSV output ────────────────────────────────────────────────────────
    csv_path = os.path.join(ROOT, 'audit_results.csv')
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write('slug,type,title_len,desc_len,h1_count,h2_count,word_count,size_kb,has_schema,issue_count,issues\n')
        for r in results:
            issues_str = '|'.join(r.get('issues', []))
            f.write(f'"{r["slug"]}",{r["type"]},{r.get("title_len",0)},{r.get("desc_len",0)},'
                    f'{r.get("h1_count",0)},{r.get("h2_count",0)},{r.get("word_count",0)},'
                    f'{r.get("size_kb",0)},{r.get("has_schema","")},{r.get("issue_count",0)},"{issues_str}"\n')

    print(f'\n✓ Full CSV saved → audit_results.csv')
    print('=' * 70)


if __name__ == '__main__':
    run()
