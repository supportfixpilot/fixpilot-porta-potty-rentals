#!/usr/bin/env python3
"""
seo_ai_enrich.py — Optional third pass using Claude API to generate
~400 words of truly unique per-city local context.

Requires: ANTHROPIC_API_KEY environment variable
Run AFTER seo_uniquify.py and seo_dedup2.py.

Each city gets a unique 3-paragraph (400-word) section about:
  1. Local construction market specific to that city
  2. Local events/venues specific to that city
  3. Why customers in that city choose FixPilot

These paragraphs are 100% unique per city because they're written
by Claude with city-specific knowledge. Saves a cache file in
.ai_cache/{slug}.txt so cities don't get regenerated on reruns.

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 seo_ai_enrich.py              # all cities
  python3 seo_ai_enrich.py atlanta-ga   # single city test
"""

import os, re, json, time
from pathlib import Path
import urllib.request, urllib.error

CACHE_DIR = Path(".ai_cache")
CACHE_DIR.mkdir(exist_ok=True)

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not API_KEY:
    print("ERROR: Set ANTHROPIC_API_KEY environment variable first.")
    print("  export ANTHROPIC_API_KEY=sk-ant-...")
    exit(1)

import sys
sys.path.insert(0, ".")
from seo_uniquify import get_city_data

def call_claude(prompt, model="claude-haiku-4-5-20251001"):
    """Call Claude API via urllib (no SDK needed)."""
    payload = json.dumps({
        "model": model,
        "max_tokens": 600,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["content"][0]["text"]


def generate_unique_context(city):
    """Generate 400 unique words about this specific city's porta potty market."""
    c = city
    prompt = f"""Write 3 short paragraphs (total ~400 words) of SEO body text for a porta potty rental company serving {c['name']}, {c['state_name']}.

City: {c['name']}, {c['state']}
County: {c['county']}
Neighborhoods: {', '.join(c['areas'])}
Key landmarks: {c['landmark1']}, {c['landmark2']}
Market type: {c['profile']}

Paragraph 1 (~140 words): Describe the specific local construction activity in {c['name']} — mention specific real projects, corridors, or industries unique to this city. Reference {c['landmark1']} and {c['county']}.

Paragraph 2 (~130 words): Describe the event and seasonal demand in {c['name']} — mention specific real events, festivals, sports teams, or venues unique to this city. Reference {c['landmark2']} and specific neighborhoods.

Paragraph 3 (~130 words): Describe why local contractors and event planners in {c['name']} trust FixPilot — mention specific neighborhoods ({c['areas'][0]}, {c['areas'][1]}) and local logistics advantages.

Write in plain prose, no bullet points, no headers. Use the city name naturally throughout. Make it genuinely specific to {c['name']} — not generic content that could apply to any city."""

    return call_claude(prompt)


def inject_ai_context(html, city, ai_text):
    """Inject AI-generated text into the local-market section."""
    paragraphs = [p.strip() for p in ai_text.split('\n\n') if p.strip() and len(p.strip()) > 50]
    paras_html = '\n'.join(f'<p class="text-gray-700 leading-relaxed mb-5 text-base ai-unique">{p}</p>' for p in paragraphs)

    # Inject after the first <p> in the local-market section
    def injector(m):
        inner = m.group(0)
        # Insert after the first </p>
        insert_pos = inner.find('</p>') + 4
        return inner[:insert_pos] + '\n    ' + paras_html + inner[insert_pos:]

    html_new = re.sub(
        r'<section[^>]*id="local-market".*?</section>',
        injector,
        html, flags=re.DOTALL, count=1
    )
    return html_new if html_new != html else html


def main():
    import sys
    base = Path(".")

    # Optionally process single city
    filter_slug = sys.argv[1] if len(sys.argv) > 1 else None

    dirs = sorted(p for p in base.iterdir()
                  if p.is_dir() and p.name.startswith("porta-potty-rental-"))

    processed = errors = skipped = 0
    for d in dirs:
        slug = d.name[len("porta-potty-rental-"):]
        if filter_slug and slug != filter_slug:
            continue
        page = d / "index.html"
        if not page.exists():
            continue
        city = get_city_data(slug)
        if city is None:
            continue

        cache_file = CACHE_DIR / f"{slug}.txt"
        if cache_file.exists():
            ai_text = cache_file.read_text()
            print(f"  CACHE {slug}")
        else:
            try:
                print(f"  GEN   {slug}...", end="", flush=True)
                ai_text = generate_unique_context(city)
                cache_file.write_text(ai_text)
                print(f" done ({len(ai_text)} chars)")
                time.sleep(0.3)  # gentle rate limit
            except Exception as e:
                print(f" ERROR: {e}")
                errors += 1
                continue

        html = page.read_text(encoding="utf-8")
        patched = inject_ai_context(html, city, ai_text)
        if patched != html:
            page.write_text(patched, encoding="utf-8")
            processed += 1
        else:
            skipped += 1

    print(f"\nDone. Processed: {processed}  Cached: {processed}  Errors: {errors}  Skipped: {skipped}")
    if errors > 0:
        print("Re-run to retry failed cities (they have no cache file).")


if __name__ == "__main__":
    main()
