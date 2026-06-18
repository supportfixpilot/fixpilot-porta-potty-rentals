import os
import re
import random
import sys
import argparse


def find_best_match(service_slug, service_dir):
    slug_words = set(service_slug.replace("-", " ").replace("/", " ").lower().split())
    best_folder = None
    best_score = 0

    for folder in os.listdir(service_dir):
        folder_path = os.path.join(service_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        folder_words = set(folder.replace("-", " ").replace("_", " ").replace("/", " ").lower().split())
        score = len(slug_words.intersection(folder_words))

        if score == 0:
            for w1 in slug_words:
                for w2 in folder_words:
                    if w1 in w2 or w2 in w1:
                        score += 0.5

        if score > best_score:
            best_score = score
            best_folder = folder

    return best_folder


def update_hero_image(html, hero_dir):
    hero_images = [
        f for f in os.listdir(hero_dir)
        if os.path.isfile(os.path.join(hero_dir, f)) and not f.startswith(".")
    ]

    if not hero_images:
        print("⚠️ No hero images found")
        return html

    chosen = random.choice(hero_images)

    new_path_relative = f"../../hero-banner-images/{chosen}"
    new_path_url = f"https://fixpilotportapottyrentals.com/hero-banner-images/{chosen}"

    html = re.sub(
        r"url\(['\"]?.*hero-banner[^'\")]*['\"]?\)",
        f"url('{new_path_relative}')",
        html
    )

    html = re.sub(
        r'href=["\'].*hero-banner[^"\']*["\']',
        f'href="{new_path_url}"',
        html
    )

    html = re.sub(
        r'href=["\'].*og-image[^"\']*["\']',
        f'href="{new_path_url}"',
        html
    )

    html = re.sub(
        r'content=["\']https://fixpilotportapottyrentals\.com/.+?/og-image[^"\']+["\']',
        f'content="{new_path_url}"',
        html
    )

    html = re.sub(
        r'content=["\']https://fixpilotportapottyrentals\.com/hero-banner-images/[^"\']+["\']',
        f'content="{new_path_url}"',
        html
    )

    html = re.sub(
        r'(["\']image["\']\s*:\s*")https://fixpilotportapottyrentals\.com/.+?/[^"]+(")',
        rf'\1{new_path_url}\2',
        html
    )

    print(f"✅ Hero image → {chosen}")
    return html


def update_google_maps(html):
    city_match = re.search(r'"addressLocality"\s*:\s*"([^"]+)"', html)
    state_match = re.search(r'"addressRegion"\s*:\s*"([^"]+)"', html)
    zip_match = re.search(r'"postalCode"\s*:\s*"([^"]+)"', html)

    if not (city_match and state_match and zip_match):
        print("⚠️ Could not find structured data for city/state/zip")
        return html

    city = city_match.group(1)
    state = state_match.group(1)
    postal_code = zip_match.group(1)

    map_query = f"{city}+{state}+{postal_code}"
    map_query_iframe = f"{city}+{state}"

    html = re.sub(
        r'"hasMap"\s*:\s*"https://maps\.google\.com/maps\?q=[^"]+"',
        f'"hasMap": "https://maps.google.com/maps?q={map_query}"',
        html
    )

    html = re.sub(
        r'<iframe[^>]+src="https?://[^"]*maps\.google\.com/maps\?q=[^"&]+[^"]*"',
        lambda m: re.sub(
            r'src="[^"]+"',
            f'src="https://maps.google.com/maps?q={map_query_iframe}&t=&z=13&ie=UTF8&iwloc=&output=embed"',
            m.group(0)
        ),
        html
    )

    print(f"✅ Google Maps updated for {city}, {state} {postal_code}")
    return html


def populate_images(city_dir, service_dir, hero_dir):
    html_file = os.path.join(city_dir, "index.html")

    if not os.path.exists(html_file):
        print("❌ index.html not found")
        return

    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    html = update_hero_image(html, hero_dir)
    html = update_google_maps(html)

    section_match = re.search(r'<section[^>]+id=["\']services["\'][^>]*>(.*?)</section>', html, re.DOTALL)

    if section_match:
        section_html = section_match.group(1)
        img_tags = re.findall(r'<img[^>]+>', section_html)

        print(f"Found {len(img_tags)} service images")

        for img_tag in img_tags:

            alt_match = re.search(r'alt=["\']([^"\']+)["\']', img_tag)
            if not alt_match:
                continue

            service_name = alt_match.group(1).strip()

            folder_name = find_best_match(service_name, service_dir)

            if not folder_name:
                print(f"❌ No folder match for {service_name}")
                continue

            folder_path = os.path.join(service_dir, folder_name)

            images = [
                f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith(".")
            ]

            if not images:
                print(f"⚠️ Empty folder {folder_name}")
                continue

            chosen = random.choice(images)

            new_src = f"../../service-images/{folder_name}/{chosen}"

            new_img_tag = re.sub(
                r'src=["\'][^"\']+["\']',
                f'src="{new_src}"',
                img_tag
            )

            html = html.replace(img_tag, new_img_tag)

            print(f"✅ {service_name} → {folder_name}/{chosen}")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    print("✨ index.html updated")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("cities", nargs="*", help="City folders")
    parser.add_argument("--service-dir", default="./service-images")
    parser.add_argument("--hero-dir", default="./hero-banner-images")

    args = parser.parse_args()

    locations_dir = os.path.join(os.getcwd(), "locations")

    cities = list(args.cities)

    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if line:
                cities.append(line)

    if not cities:
        print("❌ No cities provided")
        sys.exit(1)

    for city in cities:

        city_slug = city.lower().replace(" ", "-")
        city_dir = os.path.join(locations_dir, city_slug)

        if not os.path.isdir(city_dir):
            print(f"❌ City folder not found: {city_slug}")
            continue

        print(f"\n🚀 Processing: {city_slug}")
        populate_images(city_dir, args.service_dir, args.hero_dir)