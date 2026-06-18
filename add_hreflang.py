#!/usr/bin/env python3
"""Add hreflang annotations to the 5 English city pages that have Spanish equivalents.

For each pair, adds:
  <link rel="alternate" hreflang="en-US" href="...en page">
  <link rel="alternate" hreflang="es-US" href="...es page">
  <link rel="alternate" hreflang="x-default" href="...en page">

Inserted right after the existing <link rel="canonical">.
Idempotent.
"""
from __future__ import annotations
import re

PAIRS = [
    ("porta-potty-rental-houston-tx",       "renta-de-banos-portatiles-houston-tx"),
    ("porta-potty-rental-los-angeles-ca",   "renta-de-banos-portatiles-los-angeles-ca"),
    ("porta-potty-rental-miami-fl",         "renta-de-banos-portatiles-miami-fl"),
    ("porta-potty-rental-san-antonio-tx",   "renta-de-banos-portatiles-san-antonio-tx"),
    ("porta-potty-rental-phoenix-az",       "renta-de-banos-portatiles-phoenix-az"),
]


def patch(en_slug: str, es_slug: str) -> bool:
    path = f"{en_slug}/index.html"
    html = open(path, encoding="utf-8").read()
    if "hreflang=\"es-US\"" in html:
        return False
    block = (
        f'  <link rel="alternate" hreflang="en-US" href="https://fixpilotportapottyrentals.com/{en_slug}">\n'
        f'  <link rel="alternate" hreflang="es-US" href="https://fixpilotportapottyrentals.com/es/{es_slug}">\n'
        f'  <link rel="alternate" hreflang="x-default" href="https://fixpilotportapottyrentals.com/{en_slug}">\n'
    )
    new_html, n = re.subn(
        r'(<link rel="canonical"[^>]*>\s*\n)',
        lambda m: m.group(1) + block,
        html,
        count=1,
    )
    if n == 0:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    fixed = 0
    for en, es in PAIRS:
        if patch(en, es):
            fixed += 1
            print(f"  added hreflang to {en}/index.html")
    print(f"\nUpdated {fixed} English pages with Spanish hreflang.")


if __name__ == "__main__":
    main()
