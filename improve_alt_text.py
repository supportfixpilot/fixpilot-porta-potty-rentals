#!/usr/bin/env python3
"""Improve image alt text on city pages.

Current pattern: alt="Standard Porta Potty Rental Austin TX"
After:           alt="Standard porta potty rental in Austin, TX"

Rules:
  - First word stays capitalized; rest of service name lowercased.
  - Insert "in" between service name and city.
  - Insert comma before the state code.
  - State code stays uppercase.
  - Skip alts that are clearly already natural sentences.
"""
from __future__ import annotations
import glob
import re

ALT_PATTERN = re.compile(r'alt="([^"]+)"')

SKIP_HINTS = (" in ", ", ", "wedding setting", "construction worker", "construction skyline",
              "skyline", "icon", "logo")


def improve(alt: str) -> str | None:
    if any(hint in alt.lower() for hint in SKIP_HINTS):
        return None
    # Match "...<city words> <STATE>" at end (state = 2 caps)
    m = re.match(r"^(.+?)\s+([A-Z]{2})$", alt.strip())
    if not m:
        return None
    body = m.group(1).strip()
    state = m.group(2)

    # Heuristic: split body into "service phrase" + "city".
    # Treat city as the trailing 1-3 capitalized words.
    words = body.split()
    # Find longest trailing run of words starting with uppercase letter
    # but stop at known service-noun words.
    SERVICE_TAILS = {"Rentals", "Rental", "Unit", "Units", "Trailer", "Trailers",
                     "Stations", "Station", "Toilets", "Toilet", "Setup", "Removal",
                     "Pumping", "Tanks", "Tank", "Hook", "On", "For", "Rent",
                     "Porta", "Potty", "Wash", "Hand", "Septic", "Holding",
                     "Compliant", "Restroom", "Restrooms", "Bathroom",
                     "Pricing", "Delivery", "Dimensions", "Service", "Services",
                     "Construction", "Site", "Sites", "Needs", "Job", "Event",
                     "Accessible", "Industrial", "Wheelchair", "Commercial",
                     "Standard", "Deluxe", "Luxury", "Premium", "Mobile"}
    # Walk from end while word looks like a place name (and not in SERVICE_TAILS).
    i = len(words)
    place_words: list[str] = []
    while i > 0:
        w = words[i - 1]
        if not w[:1].isupper():
            break
        if w in SERVICE_TAILS:
            break
        place_words.insert(0, w)
        i -= 1
        if len(place_words) >= 3:
            break
    if not place_words:
        return None
    service = " ".join(words[:i]).strip()
    place = " ".join(place_words)
    if not service:
        return None

    # Lowercase service after first word for natural reading.
    parts = service.split()
    parts = [parts[0]] + [p.lower() if p[0].isupper() and p.lower() not in
                          {"ada-compliant"} else p for p in parts[1:]]
    service_natural = " ".join(parts)
    # Don't lowercase "ADA" / "VIP" tokens.
    service_natural = re.sub(r"\bada\b", "ADA", service_natural)
    service_natural = re.sub(r"\bada-compliant\b", "ADA-compliant", service_natural, flags=re.I)
    service_natural = re.sub(r"\bvip\b", "VIP", service_natural, flags=re.I)
    service_natural = re.sub(r"\bosha\b", "OSHA", service_natural, flags=re.I)

    return f"{service_natural} in {place}, {state}"


def patch(path: str) -> int:
    html = open(path, encoding="utf-8").read()
    changes = 0

    def replace(m: re.Match[str]) -> str:
        nonlocal changes
        improved = improve(m.group(1))
        if improved and improved != m.group(1):
            changes += 1
            return f'alt="{improved}"'
        return m.group(0)

    new = ALT_PATTERN.sub(replace, html)
    if changes:
        open(path, "w", encoding="utf-8").write(new)
    return changes


def main() -> None:
    total = 0
    files = 0
    for path in sorted(glob.glob("porta-potty-rental-*-*/index.html")):
        n = patch(path)
        if n:
            files += 1
            total += n
    print(f"Improved {total} alt strings in {files} city pages.")


if __name__ == "__main__":
    main()
