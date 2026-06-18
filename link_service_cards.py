#!/usr/bin/env python3
"""Add links from location page service cards to main service pages."""

import os
import re
import html as html_mod

SERVICE_URLS = {
    "standard-porta-potty": "https://fixpilotportapottyrentals.com/services/standard-porta-potty",
    "deluxe-porta-potty": "https://fixpilotportapottyrentals.com/services/deluxe-porta-potty",
    "luxury-restroom-trailers": "https://fixpilotportapottyrentals.com/services/luxury-restroom-trailers",
    "ada-compliant-units": "https://fixpilotportapottyrentals.com/services/ada-compliant-units",
    "hand-wash-stations": "https://fixpilotportapottyrentals.com/services/hand-wash-stations",
    "construction-porta-potty-rentals": "https://fixpilotportapottyrentals.com/services/construction-porta-potty-rentals",
    "flushable-portable-toilets": "https://fixpilotportapottyrentals.com/services/flushable-portable-toilets",
    "event-restroom-trailers": "https://fixpilotportapottyrentals.com/services/event-restroom-trailers",
    "crane-hook-porta-potty-rentals": "https://fixpilotportapottyrentals.com/services/crane-hook-porta-potty-rentals",
    "septic-pumping-holding-tanks": "https://fixpilotportapottyrentals.com/services/septic-pumping-holding-tanks",
    "rolling-porta-potty-rental": "https://fixpilotportapottyrentals.com/services/rolling-porta-potty-rental",
    "porta-potty-on-trailer": "https://fixpilotportapottyrentals.com/services/porta-potty-on-trailer",
    "vip-trailers-rental": "https://fixpilotportapottyrentals.com/services/vip-trailers-rental",
    "emergency-short-term-rentals": "https://fixpilotportapottyrentals.com/services/emergency-short-term-rentals",
    "restroom-trailer-setup-removal": "https://fixpilotportapottyrentals.com/services/restroom-trailer-setup-removal",
    "sporting-events-porta-potty-rental": "https://fixpilotportapottyrentals.com/services/sporting-events-porta-potty-rental",
    "parks-farms-film-shoots-porta-potty-rental": "https://fixpilotportapottyrentals.com/services/parks-farms-film-shoots-porta-potty-rental",
    "handicap-portable-toilets": "https://fixpilotportapottyrentals.com/services/handicap-portable-toilets",
    "fancy-portable-restroom-trailers-for-rent": "https://fixpilotportapottyrentals.com/services/fancy-portable-restroom-trailers-for-rent",
}

CTA_TEXTS = [
    "Call for Quote", "Call for Emergency", "Call for Service",
    "Call to Rent", "Call to Service",
    "Get a Quote", "Get Quote", "Get Pricing",
    "Request a Unit", "Quote",
]


def map_service_name_to_url(name: str) -> str | None:
    """Match a service card h3 text to a service URL."""
    n = html_mod.unescape(name.lower().strip())

    if "ada" in n:
        return SERVICE_URLS["ada-compliant-units"]
    if "handicap" in n:
        return SERVICE_URLS["handicap-portable-toilets"]
    if "luxury" in n or "restroom trailer" in n or "bathroom trailer" in n or "portable bathroom trailer" in n or "upscale event" in n:
        return SERVICE_URLS["luxury-restroom-trailers"]
    if "executive vip" in n or ("vip" in n and "flushable" not in n):
        return SERVICE_URLS["vip-trailers-rental"]
    if "emergency" in n or "disaster" in n or "short-term" in n:
        return SERVICE_URLS["emergency-short-term-rentals"]
    if "crane hook" in n or "high-rise" in n or "industrial & crane" in n:
        return SERVICE_URLS["crane-hook-porta-potty-rentals"]
    if "septic" in n or "holding tank" in n:
        return SERVICE_URLS["septic-pumping-holding-tanks"]
    if "porta potty on trailer" in n or "porta potty on wheels" in n or "porta potty on a trailer" in n or "trailer mounted" in n or "trailer-mounted" in n:
        return SERVICE_URLS["porta-potty-on-trailer"]
    if "rolling" in n:
        return SERVICE_URLS["rolling-porta-potty-rental"]
    if "construction" in n:
        return SERVICE_URLS["construction-porta-potty-rentals"]
    if "deluxe" in n:
        return SERVICE_URLS["deluxe-porta-potty"]
    if "flushable" in n:
        return SERVICE_URLS["flushable-portable-toilets"]
    if "event restroom" in n or "large event" in n:
        return SERVICE_URLS["event-restroom-trailers"]
    if "standard" in n:
        return SERVICE_URLS["standard-porta-potty"]
    if "hand wash" in n or "hand sanitizer" in n or "portable sinks" in n or "sinks &" in n or "sanitizer" in n:
        return SERVICE_URLS["hand-wash-stations"]
    if "setup" in n or "removal" in n or "trailer setup" in n or "white-glove" in n or "full-service" in n:
        return SERVICE_URLS["restroom-trailer-setup-removal"]
    if "sporting event" in n:
        return SERVICE_URLS["sporting-events-porta-potty-rental"]
    if "parks" in n or "farm" in n or "film" in n:
        return SERVICE_URLS["parks-farms-film-shoots-porta-potty-rental"]
    if "fancy" in n:
        return SERVICE_URLS["fancy-portable-restroom-trailers-for-rent"]
    if "vip" in n:
        return SERVICE_URLS["vip-trailers-rental"]
    if "bathroom" in n or "restroom" in n:
        return SERVICE_URLS["luxury-restroom-trailers"]

    return None


def find_card_boundaries(html: str, card_start: int) -> tuple[int, int]:
    """Find the boundaries of a service-card div."""
    # Find the opening <div tag before 'service-card'
    div_start = html.rfind("<div", 0, card_start)
    if div_start == -1:
        return -1, -1
    depth = 1
    pos = div_start + 4
    while depth > 0:
        next_open = html.find("<div", pos)
        next_close = html.find("</div>", pos)
        if next_close == -1:
            return -1, -1
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + 6
    return div_start, pos


def replace_cta_in_card(card_content: str, url: str) -> str | None:
    """Find the CTA in a card and replace with a service page link."""
    for text in CTA_TEXTS:
        pos = card_content.find(text)
        if pos == -1:
            continue

        # Skip if inside an <h3> tag
        before_text = card_content[max(0, pos - 100):pos]
        if "<h3" in before_text:
            continue

        before = card_content[:pos]

        # CASE 1: Text is inside an <a> tag
        a_matches = list(re.finditer(r'<a\s[^>]*>', before))
        if a_matches:
            last_a = a_matches[-1]
            a_open_start = last_a.start()
            a_open_end = last_a.end()
            a_tag_text = last_a.group(0)

            after = card_content[pos:]
            close_a = after.find("</a>")
            if close_a != -1:
                close_a_abs = pos + close_a
                inner = card_content[a_open_end:close_a_abs]
                classes_match = re.search(r'class="([^"]*)"', a_tag_text)
                classes = classes_match.group(1) if classes_match else ""
                new_a_tag = f'<a href="{url}" class="{classes}">'
                new_anchor = new_a_tag + inner + "</a>"
                return card_content[:a_open_start] + new_anchor + card_content[close_a_abs + 4:]

        # CASE 2: Text is directly inside a <div>
        div_matches = list(re.finditer(r'<div\s[^>]*>', before))
        if div_matches:
            last_div = div_matches[-1]
            div_open_start = last_div.start()
            div_open_end = last_div.end()
            div_open_tag = last_div.group(0)

            after = card_content[pos:]
            close_div = after.find("</div>")
            if close_div != -1:
                close_div_abs = pos + close_div
                div_inner = card_content[div_open_end:close_div_abs]
                stripped = div_inner.strip()
                if stripped == text:
                    classes_match = re.search(r'class="([^"]*)"', div_open_tag)
                    classes = classes_match.group(1) if classes_match else ""
                    all_classes = classes
                    if "block" not in all_classes.split():
                        all_classes = all_classes + " block" if all_classes else "block"
                    new_link = f'<a href="{url}" class="{all_classes}">{text}</a>'
                    return card_content[:div_open_start] + new_link + card_content[close_div_abs + 6:]

    return None


def process_file(filepath: str) -> bool:
    """Process a single location index.html file. Returns True if modified."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    original = html

    modified = False
    result = []
    last_end = 0

    for m in re.finditer(r'service-card', html):
        card_start, card_end = find_card_boundaries(html, m.start())
        if card_start == -1 or card_end == -1:
            continue

        card_content = html[card_start:card_end]

        # Extract h3
        h3_match = re.search(r'<h3[^>]*>(.*?)</h3>', card_content, re.DOTALL)
        if not h3_match:
            continue
        h3_text = h3_match.group(1).strip()
        url = map_service_name_to_url(h3_text)
        if url is None:
            continue

        # Skip if already has a service page link
        if f'href="{url}"' in card_content:
            continue
        if 'href="https://fixpilotportapottyrentals.com/services/' in card_content:
            continue

        new_card = replace_cta_in_card(card_content, url)
        if new_card is None:
            continue

        result.append(html[last_end:card_start])
        result.append(new_card)
        last_end = card_end
        modified = True

    if modified:
        result.append(html[last_end:])
        new_html = "".join(result)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_html)
        return True
    return False


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    modified = 0
    skipped_no_card = 0
    already_done = 0
    errors = []

    for entry in sorted(os.listdir(base_dir)):
        if not entry.startswith("porta-potty-rental-") or not os.path.isdir(os.path.join(base_dir, entry)):
            continue
        fpath = os.path.join(base_dir, entry, "index.html")
        if not os.path.exists(fpath):
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            html = f.read()

        if "service-card" not in html:
            skipped_no_card += 1
            continue

        try:
            if process_file(fpath):
                modified += 1
            else:
                already_done += 1
        except Exception as e:
            errors.append((entry, str(e)))
            import traceback
            traceback.print_exc()

    total_scanned = modified + already_done + skipped_no_card
    print(f"\nScanned: {total_scanned} directories")
    print(f"Modified: {modified}")
    print(f"Already linked: {already_done}")
    print(f"Skipped (no service-card): {skipped_no_card}")
    print(f"Errors: {len(errors)}")
    for loc, err in errors:
        print(f"  Error in {loc}: {err}")


if __name__ == "__main__":
    main()
