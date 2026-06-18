#!/usr/bin/env python3
"""Regenerate sitemap.xml from on-disk pages with real per-file lastmod.

Source of truth = file mtime (so a page only gets a fresh lastmod when actually
modified). Output covers:
  - homepage
  - /locations
  - all /porta-potty-rental-{slug-state}/ city pages
  - all /services/{slug}.html service pages
  - all /blog/{slug}.html blog pages

URLs are emitted without trailing slash and without `.html` (matches canonicals
and Cloudflare folder-index resolution). Run before each deploy.
"""
from __future__ import annotations
import datetime as dt
import glob
import os
import xml.sax.saxutils as sx

DOMAIN = "https://fixpilotportapottyrentals.com"


def lastmod(path: str) -> str:
    return dt.datetime.fromtimestamp(os.path.getmtime(path), tz=dt.timezone.utc).strftime("%Y-%m-%d")


def url_for(path: str) -> str | None:
    if path == "index.html":
        return DOMAIN + "/"
    if path == "locations.html":
        return DOMAIN + "/locations"
    if path.startswith("services/") and path.endswith(".html"):
        return DOMAIN + "/services/" + os.path.basename(path)[:-5]
    if path.startswith("blog/") and path.endswith(".html"):
        slug = os.path.basename(path)[:-5]
        if slug == "index":
            return DOMAIN + "/blog"
        return DOMAIN + "/blog/" + slug
    if path.startswith("porta-potty-rental-") and path.endswith("/index.html"):
        slug = path[: -len("/index.html")]
        return DOMAIN + "/" + slug
    return None


def emit(loc: str, lm: str, freq: str, prio: str) -> str:
    return (
        f"  <url>\n"
        f"    <loc>{sx.escape(loc)}</loc>\n"
        f"    <lastmod>{lm}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"    <priority>{prio}</priority>\n"
        f"  </url>"
    )


def main() -> None:
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # Homepage
    if os.path.exists("index.html"):
        out.append(emit(DOMAIN + "/", lastmod("index.html"), "weekly", "1.00"))

    # Locations hub
    if os.path.exists("locations.html"):
        out.append(emit(DOMAIN + "/locations", lastmod("locations.html"), "weekly", "0.90"))

    # Blog index
    if os.path.exists("blog/index.html"):
        out.append(emit(DOMAIN + "/blog", lastmod("blog/index.html"), "weekly", "0.80"))

    # Calculator (will move to /calculator in a later task; emit both for now)
    # — only if /calculator/index.html exists
    if os.path.exists("calculator/index.html"):
        out.append(emit(DOMAIN + "/calculator", lastmod("calculator/index.html"),
                        "monthly", "0.80"))

    # State hub pages (porta-potty-rental-texas, -north-carolina, etc.)
    STATES = {
        "alabama", "arizona", "arkansas", "california", "colorado", "connecticut",
        "florida", "georgia", "idaho", "illinois", "indiana", "iowa", "kansas",
        "kentucky", "louisiana", "massachusetts", "maryland", "michigan", "minnesota",
        "mississippi", "missouri", "montana", "nebraska", "north-carolina",
        "new-jersey", "nevada", "new-york", "ohio", "oklahoma", "oregon",
        "pennsylvania", "south-carolina", "tennessee", "texas", "utah", "virginia",
        "washington", "wisconsin", "wyoming",
    }
    for state in sorted(STATES):
        path = f"porta-potty-rental-{state}/index.html"
        if os.path.exists(path):
            out.append(emit(f"{DOMAIN}/porta-potty-rental-{state}",
                            lastmod(path), "weekly", "0.85"))

    # County hub pages (porta-potty-rental-harris-county-tx, etc.)
    for path in sorted(glob.glob("porta-potty-rental-*-county-*/index.html")):
        slug = path[: -len("/index.html")][len("porta-potty-rental-"):]
        out.append(emit(f"{DOMAIN}/porta-potty-rental-{slug}",
                        lastmod(path), "weekly", "0.85"))

    # Use-cases hub
    if os.path.exists("use-cases/index.html"):
        out.append(emit(f"{DOMAIN}/use-cases", lastmod("use-cases/index.html"),
                        "monthly", "0.85"))

    # Industries hub + landing pages
    if os.path.exists("industries/index.html"):
        out.append(emit(f"{DOMAIN}/industries", lastmod("industries/index.html"),
                        "monthly", "0.85"))
    for path in sorted(glob.glob("industries/*.html")):
        if path.endswith("/index.html"):
            continue
        slug = os.path.basename(path)[:-5]
        out.append(emit(f"{DOMAIN}/industries/{slug}", lastmod(path),
                        "monthly", "0.80"))

    # Compare hub + comparison pages
    if os.path.exists("compare/index.html"):
        out.append(emit(f"{DOMAIN}/compare", lastmod("compare/index.html"),
                        "monthly", "0.80"))
    for path in sorted(glob.glob("compare/*.html")):
        if path.endswith("/index.html"):
            continue
        slug = os.path.basename(path)[:-5]
        out.append(emit(f"{DOMAIN}/compare/{slug}", lastmod(path),
                        "monthly", "0.75"))

    # Cost map
    if os.path.exists("cost-map/index.html"):
        out.append(emit(f"{DOMAIN}/cost-map", lastmod("cost-map/index.html"),
                        "monthly", "0.85"))

    # Wedding calculator
    if os.path.exists("calculator/wedding/index.html"):
        out.append(emit(f"{DOMAIN}/calculator/wedding",
                        lastmod("calculator/wedding/index.html"), "monthly", "0.85"))

    # ZIP-code pages
    for path in sorted(glob.glob("zip/*-porta-potty-rental/index.html")):
        slug = path[: -len("/index.html")][len("zip/"):]
        out.append(emit(f"{DOMAIN}/zip/{slug}", lastmod(path), "monthly", "0.75"))

    # Spanish pages
    if os.path.exists("es/index.html"):
        out.append(emit(f"{DOMAIN}/es", lastmod("es/index.html"), "monthly", "0.85"))
    for path in sorted(glob.glob("es/renta-de-banos-portatiles-*-*/index.html")):
        slug = path[: -len("/index.html")][len("es/"):]
        out.append(emit(f"{DOMAIN}/es/{slug}", lastmod(path), "monthly", "0.80"))

    # About / team
    if os.path.exists("about/team/index.html"):
        out.append(emit(f"{DOMAIN}/about/team", lastmod("about/team/index.html"),
                        "monthly", "0.60"))

    # City pages
    for path in sorted(glob.glob("porta-potty-rental-*-*/index.html")):
        # Skip state hubs that look like city slugs (e.g. porta-potty-rental-north-carolina)
        slug = path[: -len("/index.html")][len("porta-potty-rental-"):]
        if slug in STATES:
            continue
        # Skip county hubs (already emitted above)
        if "-county-" in slug:
            continue
        url = url_for(path)
        if url:
            out.append(emit(url, lastmod(path), "monthly", "0.80"))

    # Service pages
    for path in sorted(glob.glob("services/*.html")):
        url = url_for(path)
        if url:
            out.append(emit(url, lastmod(path), "monthly", "0.80"))

    # Blog posts
    for path in sorted(glob.glob("blog/*.html")):
        if path.endswith("/index.html"):
            continue
        url = url_for(path)
        if url:
            out.append(emit(url, lastmod(path), "monthly", "0.70"))

    out.append("</urlset>\n")
    open("sitemap.xml", "w", encoding="utf-8").write("\n".join(out))

    n = sum(1 for line in out if line.startswith("  <url>"))
    print(f"Generated sitemap.xml with {n} URLs.")


if __name__ == "__main__":
    main()
