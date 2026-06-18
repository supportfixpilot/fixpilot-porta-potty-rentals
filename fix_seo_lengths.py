#!/usr/bin/env python3
"""Fix title lengths, meta description lengths, and broken OG tags."""
import re
from pathlib import Path

ROOT = Path(__file__).parent

def get_attr(text, tag_pattern, attr='content'):
    """Extract attribute value handling both quote types correctly."""
    m = re.search(tag_pattern + r'\s+' + attr + r'=(["\'])(.*?)\1', text, re.DOTALL | re.IGNORECASE)
    if m: return m.group(2).strip(), m.group(1)
    m = re.search(attr + r'=(["\'])(.*?)\1\s+' + tag_pattern, text, re.DOTALL | re.IGNORECASE)
    if m: return m.group(2).strip(), m.group(1)
    return '', '"'

def get_title(text):
    m = re.search(r'<title[^>]*>(.*?)</title>', text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ''

def get_desc(text):
    m = re.search(r'<meta\s+name=(["\'])description\1\s+content=(["\'])(.*?)\2', text, re.DOTALL | re.IGNORECASE)
    if m: return m.group(3).strip()
    m = re.search(r'<meta\s+content=(["\'])(.*?)\1\s+name=(["\'])description\3', text, re.DOTALL | re.IGNORECASE)
    return m.group(2).strip() if m else ''

def trim_title(title, max_len=65):
    if len(title) <= max_len:
        return title
    # Try removing trailing price/delivery fragments
    for suffix in [' · From $75/Day', ' · From $75', ' Delivery', '/Day', ' | FixPilot',
                   ': Full Guide 2026', ': A Practical Guide', ': What You Need to Know',
                   ': Complete Guide', ': How to Choose', ': Complete Rental Guide 2026']:
        if title.endswith(suffix) and len(title) - len(suffix) <= max_len:
            return title[:-len(suffix)]
    # Remove | FixPilot if present
    if ' | FixPilot' in title:
        shorter = title.replace(' | FixPilot', '')
        if len(shorter) <= max_len:
            return shorter
        title = shorter
    # Truncate at last word boundary before max_len
    if len(title) > max_len:
        cut = title[:max_len].rsplit(' ', 1)[0].rstrip(' ·|—').rstrip()
        return cut
    return title

def trim_desc(desc, max_len=160):
    if len(desc) <= max_len:
        return desc
    # Try to cut at last sentence boundary
    for boundary in ['. ', '! ', '? ', '; ']:
        idx = desc.rfind(boundary, 0, max_len - 3)
        if idx > 100:
            return desc[:idx + 1]
    # Fall back to word boundary
    cut = desc[:max_len - 3].rsplit(' ', 1)[0]
    return cut + '...'

def fix_file(path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    new = text
    changed = []

    # --- Fix title ---
    title = get_title(text)
    if title and len(title) > 65:
        new_title = trim_title(title)
        if new_title != title:
            new = re.sub(r'(<title[^>]*>)(.*?)(</title>)',
                         lambda m: m.group(1) + new_title + m.group(3),
                         new, count=1, flags=re.DOTALL | re.IGNORECASE)
            # Also fix og:title if it matches the old title
            new = re.sub(
                r'(property="og:title"\s+content=")' + re.escape(title) + r'"',
                r'\g<1>' + new_title + '"',
                new, flags=re.IGNORECASE)
            new = re.sub(
                r'(content=")' + re.escape(title) + r'"\s+property="og:title"',
                r'\g<1>' + new_title + '" property="og:title"',
                new, flags=re.IGNORECASE)
            changed.append(f'title: {len(title)}→{len(new_title)}')

    # --- Fix meta description length ---
    desc = get_desc(text)
    if desc and len(desc) > 165:
        new_desc = trim_desc(desc)
        if new_desc != desc:
            # Replace in name=description tag
            new = re.sub(
                r'(<meta\s+name=(["\'])description\2\s+content=)(["\'])' + re.escape(desc) + r'\3',
                lambda m: m.group(1) + m.group(3) + new_desc + m.group(3),
                new, count=1, flags=re.IGNORECASE)
            changed.append(f'desc: {len(desc)}→{len(new_desc)}')

    # --- Fix broken og:description (set by previous script with wrong quote handling) ---
    # Detect if og:description is suspiciously short (< 40 chars) while name=description is good
    og_desc_m = re.search(r'property="og:description"\s+content="([^"]*)"', new, re.IGNORECASE)
    if og_desc_m:
        og_val = og_desc_m.group(1)
        name_desc = get_desc(new)
        if len(og_val) < 40 and name_desc and len(name_desc) >= 40:
            # Replace with name description (truncated to 160 if needed)
            replacement = trim_desc(name_desc, 160)
            new = re.sub(
                r'property="og:description"\s+content="[^"]*"',
                f'property="og:description" content="{replacement}"',
                new, count=1, flags=re.IGNORECASE)
            changed.append(f'og:desc fixed: "{og_val}"→{len(replacement)} chars')

    if new != text:
        path.write_text(new, encoding='utf-8')
        return changed
    return []

def main():
    stats = {'city': 0, 'service': 0, 'blog': 0, 'root': 0}

    page_groups = [
        ('city',    ROOT.glob('porta-potty-rental-*/index.html')),
        ('service', ROOT.glob('services/*.html')),
        ('blog',    ROOT.glob('blog/*.html')),
        ('root',    [ROOT / 'index.html', ROOT / 'locations.html']),
    ]

    for gname, files in page_groups:
        for f in sorted(files):
            if not f.exists(): continue
            changes = fix_file(f)
            if changes:
                stats[gname] += 1
                if gname != 'city':  # city pages are too many to print individually
                    print(f'  {f.name}: {", ".join(changes)}')

    print(f"\nDone — city:{stats['city']}  service:{stats['service']}  blog:{stats['blog']}  root:{stats['root']}")

if __name__ == '__main__':
    main()
