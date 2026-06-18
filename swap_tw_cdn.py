#!/usr/bin/env python3
"""Swap Tailwind CDN runtime for the production build.

For every HTML page:
  1. Find the <script src="https://cdn.tailwindcss.com"></script> tag.
  2. Find the inline <script>tailwind.config = {...}</script> that follows it.
  3. Extract the brand color hex values + cta hex from the config.
  4. Replace both scripts with:
       <link rel="stylesheet" href="/assets/tw.css">
       <style>:root{--brand-50:#xxx;...--brand-900:#xxx;--cta:#xxx}</style>
  5. Idempotent: skip pages already migrated.

Run: python3 swap_tw_cdn.py
"""
from __future__ import annotations
import glob
import re

PAGES = (
    glob.glob("porta-potty-rental-*-*/index.html")
    + glob.glob("services/*.html")
    + glob.glob("blog/*.html")
    + ["index.html", "locations.html"]
)

CDN_TAG = re.compile(r'<script\s+src="https://cdn\.tailwindcss\.com"[^>]*>\s*</script>')
INLINE_CONFIG = re.compile(
    r'<script>\s*tailwind\.config\s*=\s*(\{.*?\})\s*</script>',
    re.DOTALL,
)
ALT_INLINE_CONFIG = re.compile(
    r'<script[^>]*>\s*tailwind\.config\s*=\s*(\{.*?\})\s*</script>',
    re.DOTALL,
)
BRAND_KV = re.compile(r"(\d{2,3})\s*:\s*'(#[0-9a-fA-F]{3,8})'")
CTA_HEX = re.compile(r"cta\s*:\s*'(#[0-9a-fA-F]{3,8})'")

DEFAULT_BRAND = {
    "50": "#eff6ff", "100": "#dbeafe", "200": "#bfdbfe", "300": "#93c5fd",
    "400": "#60a5fa", "500": "#3b82f6", "600": "#2563eb", "700": "#1d4ed8",
    "800": "#1e40af", "900": "#1e3a8a", "950": "#172554",
}
DEFAULT_CTA = "#ea580c"


def extract_palette(config_body: str) -> tuple[dict[str, str], str]:
    brand_section = re.search(r"brand\s*:\s*\{([^}]*)\}", config_body, re.DOTALL)
    palette = dict(DEFAULT_BRAND)
    if brand_section:
        for shade, hex_val in BRAND_KV.findall(brand_section.group(1)):
            palette[shade] = hex_val
    cta_match = CTA_HEX.search(config_body)
    cta = cta_match.group(1) if cta_match else DEFAULT_CTA
    return palette, cta


def build_replacement(palette: dict[str, str], cta: str, css_href: str) -> str:
    parts = [f"--brand-{k}:{v}" for k, v in sorted(palette.items(), key=lambda kv: int(kv[0]))]
    parts.append(f"--cta:{cta}")
    style_block = "<style>:root{" + ";".join(parts) + "}</style>"
    return f'<link rel="stylesheet" href="{css_href}">\n  {style_block}'


def css_href_for(path: str) -> str:
    """Always root-relative — Cloudflare Pages serves /assets/tw.css."""
    return "/assets/tw.css"


def migrate(path: str) -> str:
    html = open(path, encoding="utf-8").read()
    if "/assets/tw.css" in html and "cdn.tailwindcss.com" not in html:
        return "skip-already-migrated"
    if "cdn.tailwindcss.com" not in html:
        return "skip-no-cdn"

    config_match = INLINE_CONFIG.search(html) or ALT_INLINE_CONFIG.search(html)
    palette, cta = (DEFAULT_BRAND.copy(), DEFAULT_CTA)
    if config_match:
        palette, cta = extract_palette(config_match.group(1))

    replacement = build_replacement(palette, cta, css_href_for(path))

    new_html = CDN_TAG.sub(replacement, html, count=1)
    new_html = INLINE_CONFIG.sub("", new_html, count=1)
    new_html = ALT_INLINE_CONFIG.sub("", new_html, count=1)

    if new_html == html:
        return "skip-no-change"

    open(path, "w", encoding="utf-8").write(new_html)
    return "migrated"


def main() -> None:
    counts = {"migrated": 0, "skip-already-migrated": 0, "skip-no-cdn": 0, "skip-no-change": 0}
    for path in sorted(set(PAGES)):
        try:
            result = migrate(path)
        except FileNotFoundError:
            continue
        counts[result] = counts.get(result, 0) + 1
    for k, v in counts.items():
        print(f"  {k:25s} {v}")


if __name__ == "__main__":
    main()
