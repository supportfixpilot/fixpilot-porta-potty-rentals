#!/usr/bin/env python3
"""Add a contextual link to /calculator on every service and city page.

For service pages: insert near the top, just below the hero CTA.
For city pages:    insert into the existing quote-form section as a tertiary CTA.

Idempotent: skips pages that already link to /calculator.
"""
from __future__ import annotations
import glob
import re

SERVICE_BANNER = '''
<aside class="bg-amber-50 border-l-4 border-amber-400 px-6 py-4 text-amber-900">
  <p class="text-sm md:text-base">
    <strong>Not sure how many units you need?</strong>
    Try our free <a href="/calculator" class="underline font-bold">porta potty calculator</a>
    — guest count or worker count → exact unit recommendation in seconds.
  </p>
</aside>
'''

CITY_NOTE = (
    '<p class="text-gray-600 text-sm mt-3">Not sure how many units? Use our free '
    '<a href="/calculator" class="font-bold text-brand-700 underline">porta potty calculator</a>.</p>'
)


def patch_service(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    if "/calculator" in html:
        return False
    # Insert immediately after the </header>
    new_html, n = re.subn(r"(</header>)", lambda m: m.group(1) + SERVICE_BANNER, html, count=1)
    if n == 0:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def patch_city(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    if "/calculator" in html:
        return False
    # Insert into the quote-form section, right after the bullet list.
    # Use the closing </ul> inside that section as the anchor.
    new_html, n = re.subn(
        r'(<section id="quote-form"[\s\S]*?</ul>)',
        lambda m: m.group(1) + CITY_NOTE,
        html,
        count=1,
    )
    if n == 0:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    sf = sum(1 for p in sorted(glob.glob("services/*.html")) if patch_service(p))
    cf = sum(1 for p in sorted(glob.glob("porta-potty-rental-*-*/index.html")) if patch_city(p))
    print(f"Service pages patched: {sf}")
    print(f"City pages patched:    {cf}")


if __name__ == "__main__":
    main()
