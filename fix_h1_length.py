#!/usr/bin/env python3
"""
Fix 1: Trim H1 span text on 12 city pages where normalized text > 80 chars.
Strategy: remove the last "· phrase" segment from the span until under 75 chars.
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

city_dirs = sorted([d for d in os.listdir(ROOT) if d.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(ROOT, d))])

H1_PATTERN = re.compile(r'(<h1[^>]*>)(.*?)(</h1>)', re.DOTALL)
SPAN_PATTERN = re.compile(r'(<span[^>]*>)(.*?)(</span>)', re.DOTALL)

def normalized_h1_len(html_snippet):
    text = re.sub(r'<[^>]+>', ' ', html_snippet)
    return len(re.sub(r'\s+', ' ', text).strip())

def trim_span_text(span_text, target=74):
    """Remove trailing · segments until len <= target."""
    parts = span_text.split(' · ')
    while len(' · '.join(parts)) > target and len(parts) > 1:
        parts.pop()
    return ' · '.join(parts)

fixed = 0

for d in city_dirs:
    path = os.path.join(ROOT, d, 'index.html')
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        html = f.read()

    m = H1_PATTERN.search(html)
    if not m:
        continue

    h1_content = m.group(2)
    norm_len = normalized_h1_len(h1_content)
    if norm_len <= 80:
        continue

    # Find the span inside the H1 and trim its text content
    span_m = SPAN_PATTERN.search(h1_content)
    if not span_m:
        print(f'  SKIP (no span): {d}  ({norm_len})')
        continue

    span_open = span_m.group(1)
    span_text = span_m.group(2).strip()
    span_close = span_m.group(3)

    # Trim text to bring full H1 normalized text under 75 chars
    # "Porta Potty Rental in " = 22 chars base; add span text
    prefix_len = 22  # "Porta Potty Rental in "
    trimmed = trim_span_text(span_text, target=74 - prefix_len)  # 52 chars for span
    # But trim_span_text above isn't right — let's target the full visible text
    # Full visible = "Porta Potty Rental in " + span_text
    # Just trim span text to fit under 75 - 22 = 53... that's too aggressive
    # Better: trim while (22 + len(span_text) > 75):
    parts = span_text.split(' · ')
    while (22 + len(' · '.join(parts))) > 75 and len(parts) > 1:
        parts.pop()
    new_span_text = ' · '.join(parts)

    new_span = f'{span_open}{new_span_text}{span_close}'
    new_h1_content = h1_content[:span_m.start()] + new_span + h1_content[span_m.end():]
    new_h1 = m.group(1) + new_h1_content + m.group(3)
    new_html = html[:m.start()] + new_h1 + html[m.end():]

    new_norm = normalized_h1_len(new_h1_content)
    print(f'  {d}:  {norm_len} → {new_norm}')
    print(f'    before: {span_text}')
    print(f'    after:  {new_span_text}')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    fixed += 1

print(f'\nFixed {fixed} H1 tags.')
