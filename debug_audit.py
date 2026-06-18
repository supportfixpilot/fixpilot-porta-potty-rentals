import re, os

root = '/Users/sohag/Playground/Practice/porta-potty-rental'

# Test the audit regex on the actual blog files that were flagged
files = [
    'blog/event-sanitation-checklist.html',
    'blog/osha-requirements-construction-sites.html',
    'blog/premium-restroom-trailer-service-guide.html',
]

for f in files:
    with open(os.path.join(root, f)) as fh:
        html = fh.read()
    # The pattern used in audit_all_pages.py
    m1 = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html)
    # Correct simple pattern
    m2 = re.search(r'<meta\s+name="description"\s+content="(.*?)"', html)
    m3 = re.search(r'<meta\s+name=.description.\s+content=.(.*?).', html)
    print(f'{f}:')
    print(f'  audit regex:   {len(m1.group(1)) if m1 else "NO MATCH"} chars')
    print(f'  simple regex:  {len(m2.group(1)) if m2 else "NO MATCH"} chars')

# Now re-check the H1 length issue with normalized whitespace
city_dirs = sorted([d for d in os.listdir(root) if d.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(root, d))])

h1_over80 = []
for d in city_dirs:
    path = os.path.join(root, d, 'index.html')
    if not os.path.exists(path): continue
    with open(path) as fh:
        html = fh.read()
    h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if h1s:
        text = re.sub(r'<[^>]+>', ' ', h1s[0])
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 80:
            h1_over80.append((d, len(text), text))

print(f'\nH1 > 80 chars (normalized): {len(h1_over80)}')
for slug, length, text in h1_over80[:10]:
    print(f'  {length}: {text[:100]}')
