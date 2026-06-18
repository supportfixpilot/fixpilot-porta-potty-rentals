#!/usr/bin/env python3
"""IndexNow ping for Bing/Yandex. Cheap, legitimate, no quota.

Setup: place a key file at the site root with the same name as your IndexNow key:
  https://fixpilotportapottyrentals.com/<KEY>.txt
where the file contents are <KEY>.

Usage:
  python3 indexnow_ping.py              # ping the whole sitemap
  python3 indexnow_ping.py URL ...       # ping specific URLs

Env: INDEXNOW_KEY (set this; do NOT commit the value).
"""
from __future__ import annotations
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HOST = "fixpilotportapottyrentals.com"
KEY = os.environ.get("INDEXNOW_KEY")
ENDPOINT = "https://api.indexnow.org/IndexNow"


def urls_from_sitemap(path: str = "sitemap.xml") -> list[str]:
    root = ET.parse(path).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text.strip() for loc in root.findall("s:url/s:loc", ns) if loc.text]


def ping(urls: list[str]) -> None:
    if not KEY:
        sys.exit("Set INDEXNOW_KEY env var first. See https://www.indexnow.org/")
    if not urls:
        print("No URLs to ping.")
        return
    body = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }
    import json
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"IndexNow {resp.status}: pinged {len(urls)} URLs")


def main() -> None:
    urls = sys.argv[1:] or urls_from_sitemap()
    # IndexNow accepts up to 10000 URLs per request — single batch is fine here
    ping(urls)


if __name__ == "__main__":
    main()
