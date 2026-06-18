#!/usr/bin/env python3
"""Fix missing OG tags on blog and service pages."""
import re
from pathlib import Path

ROOT = Path(__file__).parent
OG_IMAGE = "https://fixpilotportapottyrentals.com/hero-banner-images/1.%2020260226_225037_822.webp"
SITE_NAME = "FixPilot Porta Potty Rentals"

def get(text, pattern):
    m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ''

def fix_file(path, og_type='website'):
    text = path.read_text(encoding='utf-8', errors='ignore')

    has_og_title = bool(re.search(r'og:title', text, re.IGNORECASE))
    has_og_desc  = bool(re.search(r'og:description', text, re.IGNORECASE))
    has_og_image = bool(re.search(r'og:image', text, re.IGNORECASE))
    has_og_url   = bool(re.search(r'og:url', text, re.IGNORECASE))
    has_og_site  = bool(re.search(r'og:site_name', text, re.IGNORECASE))

    if has_og_title and has_og_desc and has_og_image:
        return False  # already complete

    # Gather values from existing meta
    title = get(text, r'<title[^>]*>(.*?)</title>')
    desc  = get(text, r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']')
    if not desc:
        desc = get(text, r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']')
    canonical = get(text, r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']')

    new_tags = []

    if not has_og_title and title:
        new_tags.append(f'    <meta property="og:title" content="{title}">')
    if not has_og_desc and desc:
        new_tags.append(f'    <meta property="og:description" content="{desc}">')
    if not has_og_image:
        new_tags.append(f'    <meta property="og:image" content="{OG_IMAGE}">')
    if not has_og_url and canonical:
        new_tags.append(f'    <meta property="og:url" content="{canonical}">')
    if not has_og_site:
        new_tags.append(f'    <meta property="og:site_name" content="{SITE_NAME}">')
    if not re.search(r'og:type', text, re.IGNORECASE):
        new_tags.append(f'    <meta property="og:type" content="{og_type}">')

    if not new_tags:
        return False

    inject = '\n'.join(new_tags)

    # Insert after </title> if present, else before </head>
    if re.search(r'</title>', text, re.IGNORECASE):
        new_text = re.sub(
            r'(</title>)',
            r'\1\n' + inject,
            text, count=1, flags=re.IGNORECASE
        )
    else:
        new_text = re.sub(
            r'(</head>)',
            inject + r'\n\1',
            text, count=1, flags=re.IGNORECASE
        )

    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        return True
    return False

def main():
    counts = {'blog': 0, 'service': 0}

    for f in sorted(ROOT.glob('blog/*.html')):
        if fix_file(f, og_type='article'):
            counts['blog'] += 1

    for f in sorted(ROOT.glob('services/*.html')):
        if fix_file(f, og_type='website'):
            counts['service'] += 1

    print(f"Fixed OG tags — blog:{counts['blog']}  service:{counts['service']}")

if __name__ == '__main__':
    main()
