#!/usr/bin/env python3
"""Fix broken placeholder hero image references and URL-encode filenames with spaces."""

import glob
import os
import re

HERO_DIR = "hero-banner-images"
CITY_GLOB = "porta-potty-rental-*-*/index.html"
DOMAIN = "https://fixpilotportapottyrentals.com"


def get_hero_images():
    """Get list of available hero images."""
    return sorted(f for f in os.listdir(HERO_DIR) if f.endswith('.webp'))


def url_encode_filename(filename: str) -> str:
    """URL-encode spaces and special chars in filename."""
    return filename.replace(' ', '%20')


def fix_placeholder_hero(html: str, replacement_img: str) -> tuple[str, bool]:
    """Replace placeholder-xxx.webp with a real hero image."""
    if 'placeholder-' not in html:
        return html, False
    # Replace the placeholder image in CSS background
    new_html = re.sub(
        r"url\('../hero-banner-images/placeholder-[^']+\.webp'\)",
        f"url('../hero-banner-images/{replacement_img}')",
        html
    )
    return new_html, new_html != html


def fix_og_image_spaces(html: str) -> tuple[str, bool]:
    """URL-encode spaces in OG/Twitter image URLs and schema image fields."""
    changed = False
    # Fix meta og:image and twitter:image and schema image fields
    def encode_url(m):
        nonlocal changed
        url = m.group(0)
        new_url = re.sub(r'hero-banner-images/([^"\']+)',
                         lambda x: 'hero-banner-images/' + x.group(1).replace(' ', '%20'),
                         url)
        if new_url != url:
            changed = True
        return new_url

    # Fix URLs in content= attributes and JSON-LD strings
    new_html = re.sub(
        r'https://fixpilotportapottyrentals\.com/hero-banner-images/[^"\']+',
        encode_url,
        html
    )
    return new_html, changed


def fix_css_background_spaces(html: str) -> tuple[str, bool]:
    """URL-encode spaces in CSS background-image url() references."""
    changed = False
    def encode_bg(m):
        nonlocal changed
        inner = m.group(1)
        new_inner = inner.replace(' ', '%20')
        if new_inner != inner:
            changed = True
            return f"url('{new_inner}')"
        return m.group(0)

    new_html = re.sub(r"url\('(\.\./hero-banner-images/[^']+)'\)", encode_bg, html)
    return new_html, changed


def main():
    hero_images = get_hero_images()
    if not hero_images:
        print("No hero images found!")
        return

    # Use a mid-range image as replacement for broken placeholders
    replacement_img = hero_images[len(hero_images) // 2]

    paths = sorted(glob.glob(CITY_GLOB))
    fixed_placeholder = 0
    fixed_og_spaces = 0
    fixed_css_spaces = 0

    for path in paths:
        with open(path, encoding='utf-8', errors='replace') as f:
            html = f.read()

        modified = False

        # Fix broken placeholder images
        new_html, changed = fix_placeholder_hero(html, replacement_img)
        if changed:
            html = new_html
            fixed_placeholder += 1
            modified = True

        # Fix OG/schema image URL spaces
        new_html, changed = fix_og_image_spaces(html)
        if changed:
            html = new_html
            fixed_og_spaces += 1
            modified = True

        # Fix CSS background URL spaces
        new_html, changed = fix_css_background_spaces(html)
        if changed:
            html = new_html
            fixed_css_spaces += 1
            modified = True

        if modified:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)

    print(f"Fixed placeholder images: {fixed_placeholder}")
    print(f"Fixed OG/schema URL spaces: {fixed_og_spaces}")
    print(f"Fixed CSS background URL spaces: {fixed_css_spaces}")


if __name__ == '__main__':
    main()
