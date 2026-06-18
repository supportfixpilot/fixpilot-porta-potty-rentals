import os, re

root = '/Users/sohag/Playground/Practice/porta-potty-rental'
blog_dir = f'{root}/blog'

issues = [
    'event-sanitation-checklist.html',
    'premium-restroom-trailer-service-guide.html',
    'osha-requirements-construction-sites.html',
    'portable-toilet-for-small-business.html',
    'flushable-portable-toilet-guide.html',
    'how-porta-potty-service-works.html',
    'vip-restroom-trailer-guide.html',
    'ada-compliant-porta-potties.html',
    'hand-wash-station-requirements.html',
    'how-many-porta-potties-for-wedding.html',
    'luxury-vs-standard-porta-potties.html',
    'same-day-porta-potty-rental.html',
]

for f in issues:
    path = f'{blog_dir}/{f}'
    if not os.path.exists(path):
        print(f'{f}: NOT FOUND')
        continue
    with open(path) as fh:
        html = fh.read()
    desc = re.search(r'<meta\s+name="description"\s+content="(.*?)"', html)
    title = re.search(r'<title>(.*?)</title>', html)
    text = re.sub(r'<[^>]+>', ' ', html)
    wc = len(text.split())
    desc_val = desc.group(1) if desc else 'MISSING'
    print(f'{f}:')
    print(f'  title: {title.group(1) if title else "MISSING"}')
    print(f'  desc({len(desc_val)}): [{desc_val}]')
    print(f'  words: {wc}')
    print()
