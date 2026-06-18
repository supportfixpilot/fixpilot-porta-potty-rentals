#!/usr/bin/env python3
"""
fix_schema_json.py — Fix two pre-existing JSON-LD bugs across city/county pages:
  1. Two JSON objects concatenated in one <script> tag → split into two tags
  2. Missing commas between array items (review objects) → insert commas
"""
import os, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))

SCRIPT_PAT = re.compile(
    r'(<script[^>]+application/ld\+json[^>]*>)(.*?)(</script>)',
    re.DOTALL | re.IGNORECASE
)

def fix_missing_commas(block):
    """Fix missing commas between adjacent JSON objects in arrays: } { → }, {"""
    return re.sub(r'\}\s*\n(\s*)\{', r'},\n\1{', block)

def split_two_objects(block):
    """If block contains two top-level JSON objects, return list of both as strings."""
    stripped = block.strip()
    # Try to find where first object ends by counting braces
    depth = 0
    in_str = False
    escape = False
    first_end = -1
    for i, ch in enumerate(stripped):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_str:
            escape = True
            continue
        if ch == '"' and not escape:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                first_end = i
                break
    if first_end == -1 or first_end >= len(stripped) - 1:
        return None
    rest = stripped[first_end+1:].strip()
    if not rest or rest[0] != '{':
        return None
    return [stripped[:first_end+1], rest]

fixed_split   = 0
fixed_commas  = 0
already_valid = 0
unfixable     = 0

city_dirs = sorted([d for d in os.listdir(ROOT)
    if d.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(ROOT, d))])

for slug in city_dirs:
    path = os.path.join(ROOT, slug, 'index.html')
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        html = f.read()

    changed = False
    new_html = html

    for m in SCRIPT_PAT.finditer(html):
        open_tag = m.group(1)
        block    = m.group(2)
        close_tag = m.group(3)
        original  = m.group(0)

        # Already valid?
        try:
            json.loads(block)
            already_valid += 1
            continue
        except json.JSONDecodeError as e:
            pass

        # Try fix 1: missing commas between objects in arrays
        fixed_block = fix_missing_commas(block)
        try:
            json.loads(fixed_block)
            new_script = open_tag + fixed_block + close_tag
            new_html = new_html.replace(original, new_script, 1)
            fixed_commas += 1
            changed = True
            continue
        except json.JSONDecodeError:
            pass

        # Try fix 2: two objects concatenated → split into two script tags
        parts = split_two_objects(block.strip())
        if parts:
            valid_parts = []
            all_valid = True
            for p in parts:
                try:
                    json.loads(p)
                    valid_parts.append(p)
                except json.JSONDecodeError:
                    all_valid = False
                    break
            if all_valid:
                new_scripts = '\n'.join(
                    f'{open_tag}\n  {p}\n{close_tag}' for p in valid_parts
                )
                new_html = new_html.replace(original, new_scripts, 1)
                fixed_split += 1
                changed = True
                continue

        unfixable += 1

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)

print(f'Fixed split (two objects → two tags) : {fixed_split}')
print(f'Fixed commas (missing array commas)  : {fixed_commas}')
print(f'Unfixable (need manual review)       : {unfixable}')
