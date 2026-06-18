import re
import os

BASE = "/Users/hasanulrubel/Playground/PPC/porta-potty-rental"

FILES = [
    "porta-potty-rental-arlington-tx/index.html",
    "porta-potty-rental-frederick-md/index.html",
    "porta-potty-rental-glendale-ca/index.html",
    "porta-potty-rental-mesa-az/index.html",
    "porta-potty-rental-naperville-il/index.html",
    "porta-potty-rental-oakland-ca/index.html",
    "porta-potty-rental-paradise-ca/index.html",
]

SERVICE_URLS = [
    # Order matters: more specific patterns first
    ("luxury", "https://fixpilotportapottyrentals.com/services/luxury-restroom-trailers"),
    ("crane-hook", "https://fixpilotportapottyrentals.com/services/crane-hook-porta-potty-rentals"),
    ("crane hook", "https://fixpilotportapottyrentals.com/services/crane-hook-porta-potty-rentals"),
    ("flushable", "https://fixpilotportapottyrentals.com/services/flushable-portable-toilets"),
    ("construction", "https://fixpilotportapottyrentals.com/services/construction-porta-potty-rentals"),
    ("standard", "https://fixpilotportapottyrentals.com/services/standard-porta-potty"),
    ("deluxe", "https://fixpilotportapottyrentals.com/services/deluxe-porta-potty"),
    ("ada", "https://fixpilotportapottyrentals.com/services/ada-compliant-units"),
    ("hand wash", "https://fixpilotportapottyrentals.com/services/hand-wash-stations"),
    ("hand sanitizer", "https://fixpilotportapottyrentals.com/services/hand-wash-stations"),
    ("event restroom", "https://fixpilotportapottyrentals.com/services/event-restroom-trailers"),
    ("septic", "https://fixpilotportapottyrentals.com/services/septic-pumping-holding-tanks"),
    ("holding tank", "https://fixpilotportapottyrentals.com/services/septic-pumping-holding-tanks"),
    ("porta potty on trailer", "https://fixpilotportapottyrentals.com/services/porta-potty-on-trailer"),
    ("trailer mounted", "https://fixpilotportapottyrentals.com/services/porta-potty-on-trailer"),
    ("on trailer", "https://fixpilotportapottyrentals.com/services/porta-potty-on-trailer"),
    ("vip", "https://fixpilotportapottyrentals.com/services/vip-trailers-rental"),
    ("emergency", "https://fixpilotportapottyrentals.com/services/emergency-short-term-rentals"),
    ("disaster", "https://fixpilotportapottyrentals.com/services/emergency-short-term-rentals"),
    ("short-term", "https://fixpilotportapottyrentals.com/services/emergency-short-term-rentals"),
    ("rolling", "https://fixpilotportapottyrentals.com/services/rolling-porta-potty-rental"),
    ("restroom", "https://fixpilotportapottyrentals.com/services/luxury-restroom-trailers"),
    ("trailer", "https://fixpilotportapottyrentals.com/services/luxury-restroom-trailers"),
    ("fancy", "https://fixpilotportapottyrentals.com/services/fancy-portable-restroom-trailers-for-rent"),
]


def get_url(h3_text):
    t = h3_text.lower().strip()
    for keyword, url in SERVICE_URLS:
        if keyword in t:
            return url
    print(f"  ⚠ NO MATCH for: {h3_text!r}")
    return None


def process_file(rel_path):
    path = os.path.join(BASE, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Find the services section
    section_start = html.find('<section id="services"')
    if section_start == -1:
        print(f"❌ No services section in {rel_path}")
        return False
    section_end = html.find("</section>", section_start)
    if section_end == -1:
        print(f"❌ No closing section tag in {rel_path}")
        return False
    section_end += len("</section>")

    services_section = html[section_start:section_end]

    # Split into cards by finding grid card divs
    # Each card starts with a <div that has card classes
    # We'll find each <h3> to identify the card and its service name

    modified_section = services_section
    changes = 0

    # Find all h3 elements in the section
    h3_pattern = re.compile(r'<h3[^>]*>(.*?)</h3>')
    h3_matches = list(h3_pattern.finditer(services_section))

    print(f"  Found {len(h3_matches)} cards in {rel_path}")

    for h3_match in h3_matches:
        h3_text = h3_match.group(1).strip()
        url = get_url(h3_text)
        if url is None:
            continue

        # After the h3, find "Get a Quote" text
        # We look for the pattern: <div ...>\n          Get a Quote\n        </div>
        # or <a href="tel:..." ...>Get a Quote</a>
        
        # Search for Get a Quote after this h3 but before the next h3 or end of section
        search_start = h3_match.end()
        next_h3 = h3_pattern.search(services_section, search_start)
        search_end = next_h3.start() if next_h3 else len(services_section)

        quote_area = services_section[search_start:search_end]

        # Check if there's already an <a> tag with Get a Quote
        a_pattern = re.compile(r'<a\s[^>]*href="tel:[^"]*"[^>]*>\s*Get a Quote\s*</a>')
        a_match = a_pattern.search(quote_area)
        
        if a_match:
            # Replace href in existing anchor tag
            old_a = a_match.group(0)
            new_a = old_a.replace('href="tel:+18336529344"', f'href="{url}"')
            # Calculate absolute position
            abs_start = search_start + a_match.start()
            abs_end = search_start + a_match.end()
            old_in_section = modified_section[abs_start:abs_end]
            modified_section = modified_section[:abs_start] + new_a + modified_section[abs_end:]
            changes += 1
            print(f"  ✅ Updated link: {h3_text} -> {url}")
        else:
            # Find div with "Get a Quote" text
            div_pattern = re.compile(r'(<div\s+class="([^"]*)"\s*>)\s*\n\s*Get a Quote\s*\n\s*</div>', re.DOTALL)
            div_match = div_pattern.search(quote_area)
            if div_match:
                div_classes = div_match.group(2)
                old_div = div_match.group(0)
                
                # Determine appropriate anchor classes based on original div classes
                anchor_classes = div_classes
                # Add link-specific classes if not already present
                extra_classes = "font-medium text-gray-700 hover:text-green-600 transition"
                if "font" not in anchor_classes:
                    pass  # we handle below
                
                new_a = f'<a href="{url}" class="{div_classes} font-medium text-gray-700 hover:text-green-600 transition">\n          Get a Quote\n        </a>'
                
                abs_start = search_start + div_match.start()
                abs_end = search_start + div_match.end()
                modified_section = modified_section[:abs_start] + new_a + modified_section[abs_end:]
                changes += 1
                print(f"  ✅ Replaced div: {h3_text} -> {url}")
            else:
                # Try to find "Get a Quote" text more broadly
                # Maybe it's inside a <div> with different whitespace
                broad_pattern = re.compile(r'<div\s+class="([^"]*)"[^>]*>\s*Get a Quote\s*</div>', re.DOTALL)
                broad_match = broad_pattern.search(quote_area)
                if broad_match:
                    div_classes = broad_match.group(1)
                    old_div = broad_match.group(0)
                    new_a = f'<a href="{url}" class="{div_classes} font-medium text-gray-700 hover:text-green-600 transition">Get a Quote</a>'
                    abs_start = search_start + broad_match.start()
                    abs_end = search_start + broad_match.end()
                    modified_section = modified_section[:abs_start] + new_a + modified_section[abs_end:]
                    changes += 1
                    print(f"  ✅ Replaced (broad): {h3_text} -> {url}")
                else:
                    print(f"  ⚠ Could not find Get a Quote element for: {h3_text}")

    if changes > 0:
        html = html[:section_start] + modified_section + html[section_end:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✅ {changes} changes written to {rel_path}")
    else:
        print(f"  ⚠ No changes for {rel_path}")

    return changes > 0


total = 0
for f in FILES:
    print(f"\n=== {f} ===")
    if process_file(f):
        total += 1

print(f"\n✅ Done! {total} files updated.")
