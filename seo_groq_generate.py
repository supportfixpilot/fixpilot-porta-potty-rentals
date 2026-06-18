#!/usr/bin/env python3
"""
seo_groq_generate.py  — Achieve 90%+ uniqueness via Groq API.

Instead of just adding a section, this script generates REPLACEMENT content
for the two biggest sources of shared text between cities:
  1. All 15 FAQ question+answer pairs (replacing the template FAQ)
  2. The "Your Experts" prose section

Combined these two account for ~800-900 shared 6-grams between same-state cities.
Replacing them with per-city AI-written content drops shared content to ~250
(structural only), achieving 90-95%+ uniqueness for ALL city pairs.

Also adds a ~400-word unique "Local Market Insight" section as bonus.

Usage:
  Put your keys in groq_keys.txt (one per line), then:
  python3 seo_groq_generate.py

Safe to re-run — cached results in .groq_cache/ are reused.
"""

import re, json, time, threading, sys
from pathlib import Path
from urllib import request, error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, ".")
from seo_uniquify import get_city_data

KEYS_FILE   = "groq_keys.txt"
CACHE_DIR   = Path(".groq_cache")
MODEL       = "llama-3.3-70b-versatile"
MODEL_FAST  = "llama3-8b-8192"
GROQ_URL    = "https://api.groq.com/openai/v1/chat/completions"
MAX_WORKERS = 25
TIMEOUT     = 45
CACHE_DIR.mkdir(exist_ok=True)


# ── KEY MANAGER ──────────────────────────────────────────────────────────────
class KeyManager:
    def __init__(self, keys):
        self.keys = list(keys)
        self._idx = 0
        self._lock = threading.Lock()
        self._cooldown = {}

    def get_key(self):
        with self._lock:
            now = time.time()
            for _ in range(len(self.keys)):
                key = self.keys[self._idx % len(self.keys)]
                self._idx += 1
                if now >= self._cooldown.get(key, 0):
                    return key
            soonest = min(self._cooldown, key=lambda k: self._cooldown[k])
            time.sleep(max(0, self._cooldown[soonest] - time.time()) + 0.1)
            return soonest

    def cooldown(self, key, secs=60):
        with self._lock:
            self._cooldown[key] = time.time() + secs
            print(f"    [rate-limited] ...{key[-6:]}, cooling {secs}s")


# ── API CALL ─────────────────────────────────────────────────────────────────
def groq(km, prompt, slug, fast=False):
    model = MODEL_FAST if fast else MODEL
    key = km.get_key()
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1400,
        "temperature": 0.85,
    }).encode()
    req = request.Request(GROQ_URL, data=payload, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    try:
        with request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code == 429:
            try:
                ra = int(json.loads(body).get("error", {}).get("retry_after", 60))
            except Exception:
                ra = 60
            km.cooldown(key, ra)
            return groq(km, prompt, slug, fast)
        if e.code == 503 and not fast:
            return groq(km, prompt, slug, fast=True)
        raise


# ── PROMPTS ──────────────────────────────────────────────────────────────────
def prompt_faq(city):
    c = city
    profile_context = {
        "oilgas":     f"oil & gas operations, industrial construction, and energy sector workers near {c['landmark1']}",
        "events":     f"live events, weddings, festivals near {c['landmark2']}, and outdoor gatherings throughout {c['county']}",
        "coastal":    f"beach events, marina construction, and coastal tourism near {c['landmark1']}",
        "college":    f"university athletics, campus construction, and student events near {c['landmark1']}",
        "tech":       f"tech campus construction, corporate events, and innovation economy near {c['landmark1']}",
        "suburban":   f"residential construction, home renovations, HOA events in {c['a1']} and {c['a2']}",
        "government": f"military installations, government infrastructure, and public works near {c['landmark1']}",
    }.get(c["profile"], f"construction and events near {c['landmark1']}")

    return f"""You are writing FAQ content for a porta potty rental company serving {c['name']}, {c['state']}.

City facts:
- City: {c['name']}, {c['county']}, {c['state_name']}
- Neighborhoods: {c['a1']}, {c['a2']}, {c['a3']}, {c['a4']}, {c['a5']}
- Landmarks: {c['landmark1']}, {c['landmark2']}
- Primary market: {profile_context}

Write exactly 12 FAQ questions and answers for this specific city. Requirements:
- EVERY answer must mention {c['name']}, {c['county']}, OR one of the specific neighborhoods/landmarks above
- Questions must be specific to {c['name']} (not generic questions that could apply to any city)
- Include questions about: delivery speed, neighborhoods served, OSHA compliance, pricing, construction, events, ADA units, emergency service, and 3-4 questions unique to {c['name']}'s specific market ({profile_context})
- Each answer: 60-90 words
- Include specific ZIP codes, street names, or venue names from {c['name']} where relevant

Format each FAQ as:
Q: [question]
A: [answer]

Write all 12 now:"""


def prompt_expert(city):
    c = city
    return f"""Write a 3-paragraph "About Our {c['name']} Team" section for FixPilot Porta Potty Rentals.

City: {c['name']}, {c['county']}, {c['state_name']}
Neighborhoods: {c['a1']}, {c['a2']}, {c['a3']}, {c['a4']}, {c['a5']}
Landmarks: {c['landmark1']}, {c['landmark2']}

Requirements:
- Paragraph 1 (~80 words): How FixPilot serves {c['name']}'s construction market, mentioning {c['county']}, {c['landmark1']}, and neighborhoods {c['a1']} and {c['a2']}
- Paragraph 2 (~80 words): How FixPilot serves {c['name']}'s event market, mentioning {c['landmark2']}, {c['a3']}, and {c['a4']}
- Paragraph 3 (~60 words): Why {c['name']} customers choose FixPilot, mentioning {c['a5']}, same-day delivery to {c['county']}, and (833) 652-9344

Every single sentence must contain at least one of: {c['name']}, {c['county']}, {c['a1']}, {c['a2']}, {c['a3']}, {c['a4']}, {c['a5']}, {c['landmark1']}, or {c['landmark2']}.

Write 3 paragraphs, no headers, no bullet points:"""


def prompt_local_market(city):
    c = city
    return f"""Write 3 paragraphs of SEO body text for a porta potty rental company serving {c['name']}, {c['state']}.

City: {c['name']}, {c['county']}, {c['state_name']}
Neighborhoods: {c['a1']}, {c['a2']}, {c['a3']}, {c['a4']}, {c['a5']}
Landmarks: {c['landmark1']}, {c['landmark2']}

Paragraph 1 (~130 words): Describe the SPECIFIC local construction/industry market in {c['name']} — real employers, real development projects, real economic activity near {c['landmark1']}, {c['a1']}, and {c['a2']}.

Paragraph 2 (~130 words): Describe SPECIFIC local events, festivals, sports teams, or gatherings in {c['name']} near {c['landmark2']}, {c['a3']}, and {c['a4']} that create demand for portable restrooms.

Paragraph 3 (~100 words): Why contractors and event planners in {c['a5']} and throughout {c['county']} choose FixPilot — specific, local, mentioning (833) 652-9344.

Every sentence must contain at least one proper noun specific to {c['name']}. No generic content.
3 plain paragraphs, no headers:"""


# ── CONTENT PARSERS ───────────────────────────────────────────────────────────
def parse_faqs(text, city):
    """Parse Q: / A: blocks into HTML + JSON schema."""
    pairs = []
    current_q = current_a = None
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('Q:') or line.startswith('Q.') or (line[:3].lower() == 'q: '):
            if current_q and current_a:
                pairs.append((current_q.strip(), current_a.strip()))
            current_q = re.sub(r'^Q[.:\d]+\s*', '', line, flags=re.IGNORECASE).strip()
            current_a = None
        elif line.startswith('A:') or line.startswith('A.') or (line[:3].lower() == 'a: '):
            current_a = re.sub(r'^A[.:\d]+\s*', '', line, flags=re.IGNORECASE).strip()
        elif current_a is not None and line:
            current_a += ' ' + line
        elif current_q is not None and current_a is None and line:
            current_q += ' ' + line
    if current_q and current_a:
        pairs.append((current_q.strip(), current_a.strip()))
    return pairs[:15]  # max 15


def build_faq_html(pairs, city):
    slug = city["slug"]
    items = ""
    for i, (q, a) in enumerate(pairs, 1):
        fid = f"faq-ai-{i}"
        items += (
            f'\n                <div id="{fid}" class="border border-gray-100 rounded-xl p-6 shadow-sm">\n'
            f'                    <h3 class="font-semibold text-lg text-gray-800 mb-2">{i}. {q}</h3>\n'
            f'                    <p class="text-gray-600 text-sm">{a}</p>\n'
            f'                </div>'
        )
    return (
        f'    <section id="faq" class="py-20 bg-white">\n'
        f'        <div class="container mx-auto px-4">\n'
        f'            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 text-center">'
        f'{city["name"]} Porta Potty Rental — Frequently Asked Questions</h2>\n'
        f'            <p class="text-gray-600 max-w-2xl mx-auto text-lg text-center mb-12">'
        f'Real answers for {city["name"]} customers. More questions? Call (833) 652-9344 anytime.</p>\n'
        f'            <div class="space-y-6 max-w-4xl mx-auto">{items}\n'
        f'            </div>\n'
        f'        </div>\n'
        f'    </section>'
    )


def build_faq_schema(pairs, city):
    slug = city["slug"]
    entries = []
    for i, (q, a) in enumerate(pairs, 1):
        entries.append(
            '        {\n'
            '          "@type": "Question",\n'
            f'          "@id": "https://fixpilotportapottyrentals.com/porta-potty-rental-{slug}/#faq-ai-{i}",\n'
            f'          "name": {json.dumps(q)},\n'
            '          "acceptedAnswer": {"@type": "Answer", "text": ' + json.dumps(a) + '}\n'
            '        }'
        )
    return (
        '    <script type="application/ld+json">\n'
        '    {\n'
        '      "@context": "https://schema.org",\n'
        '      "@type": "FAQPage",\n'
        '      "mainEntity": [\n'
        + ',\n'.join(entries) + '\n'
        '      ]\n'
        '    }\n'
        '    </script>'
    )


def inject_all(html, city, faq_text, expert_text, market_text):
    slug = city["slug"]

    # 1. Replace FAQ schema
    pairs = parse_faqs(faq_text, city)
    if pairs:
        new_schema = build_faq_schema(pairs, city)
        _s = new_schema
        html = re.sub(
            r'<script type="application/ld\+json">\s*\{\s*"@context"\s*:\s*"https://schema\.org",\s*"@type"\s*:\s*"FAQPage".*?</script>',
            lambda m: _s, html, flags=re.DOTALL
        )
        # 2. Replace FAQ HTML section
        new_faq = build_faq_html(pairs, city)
        _f = new_faq
        html = re.sub(
            r'<section id="faq"[^>]*>.*?</section>',
            lambda m: _f, html, flags=re.DOTALL
        )

    # 3. Replace expert prose section
    if expert_text and len(expert_text) > 100:
        paras = [p.strip() for p in expert_text.split('\n\n') if len(p.strip()) > 50]
        expert_html = ''.join(f'<p>{p}</p>\n' for p in paras[:3])
        _e = expert_html
        html = re.sub(
            r'(<div class="prose prose-lg mx-auto text-gray-600">)\s*(<p>.*?</p>\s*)*(</div>)',
            lambda m: m.group(1) + '\n' + _e + m.group(3),
            html, flags=re.DOTALL, count=1
        )

    # 4. Replace or add local market section
    if market_text and len(market_text) > 100:
        paras = [p.strip() for p in market_text.split('\n\n') if len(p.strip()) > 50]
        paras_html = '\n'.join(
            f'    <p class="text-gray-700 leading-relaxed mb-5 text-base">{p}</p>'
            for p in paras[:4]
        )
        new_market = (
            f'<section class="py-16 bg-gray-50 border-t border-gray-200" id="ai-local-context">\n'
            f'  <div class="container mx-auto px-4 max-w-4xl">\n'
            f'    <h2 class="text-3xl md:text-4xl font-extrabold text-brand-900 mb-6">'
            f'Portable Sanitation in {city["name"]}, {city["state"]} — {city["county"]} Market</h2>\n'
            f'{paras_html}\n'
            f'  </div>\n'
            f'</section>'
        )
        _m = new_market
        if 'id="ai-local-context"' in html:
            html = re.sub(
                r'<section[^>]*id="ai-local-context".*?</section>',
                lambda m: _m, html, flags=re.DOTALL, count=1
            )
        else:
            html = re.sub(
                r'(<section id="related-cities")',
                lambda m: _m + '\n' + m.group(1), html, count=1
            )
    return html


# ── PER-CITY WORKER ───────────────────────────────────────────────────────────
def process_city(slug, km, force=False):
    page = Path(f"porta-potty-rental-{slug}/index.html")
    if not page.exists():
        return slug, "missing"
    city = get_city_data(slug)
    if city is None:
        return slug, "skip"

    faq_cache    = CACHE_DIR / f"{slug}_faq.txt"
    expert_cache = CACHE_DIR / f"{slug}_expert.txt"
    market_cache = CACHE_DIR / f"{slug}_market.txt"

    def load_or_gen(cache, prompt_fn, label):
        if cache.exists() and not force:
            return cache.read_text(encoding="utf-8"), "cached"
        try:
            text = groq(km, prompt_fn(city), slug)
            if not text or len(text) < 80:
                return None, "empty"
            cache.write_text(text, encoding="utf-8")
            return text, "generated"
        except Exception as ex:
            return None, f"error:{ex}"

    faq_text,    s1 = load_or_gen(faq_cache,    prompt_faq,          "faq")
    expert_text, s2 = load_or_gen(expert_cache, prompt_expert,       "expert")
    market_text, s3 = load_or_gen(market_cache, prompt_local_market, "market")

    if faq_text is None and expert_text is None:
        return slug, s1

    html = page.read_text(encoding="utf-8")
    patched = inject_all(html, city, faq_text or "", expert_text or "", market_text or "")
    if patched != html:
        page.write_text(patched, encoding="utf-8")
        status = "new" if "generated" in (s1, s2, s3) else "cached"
        return slug, status
    return slug, "noop"


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    if not Path(KEYS_FILE).exists():
        print(f"ERROR: Create '{KEYS_FILE}' with one Groq API key per line.")
        sys.exit(1)
    keys = [k.strip() for k in Path(KEYS_FILE).read_text().splitlines()
            if k.strip() and not k.strip().startswith('#')]
    if not keys:
        print(f"ERROR: No keys in {KEYS_FILE}")
        sys.exit(1)

    print(f"Loaded {len(keys)} key(s)  |  Model: {MODEL}  |  Workers: {MAX_WORKERS}")
    km = KeyManager(keys)
    force = "--force" in sys.argv

    def is_city(slug):
        p = slug.rsplit("-", 1)
        return len(p) == 2 and p[1].upper() in {
            "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL",
            "IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT",
            "NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI",
            "SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
        }

    slugs = [
        p.name[len("porta-potty-rental-"):]
        for p in sorted(Path(".").iterdir())
        if p.is_dir() and p.name.startswith("porta-potty-rental-")
        and (p/"index.html").exists()
    ]
    city_slugs = [s for s in slugs if is_city(s)]

    cached = sum(1 for s in city_slugs if (CACHE_DIR/f"{s}_faq.txt").exists())
    print(f"Cities: {len(city_slugs)}  |  FAQ cached: {cached}")
    print()

    counts = {"new": 0, "cached": 0, "error": 0, "skip": 0, "noop": 0}
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(process_city, s, km, force): s for s in city_slugs}
        done = 0
        for fut in as_completed(futs):
            slug = futs[fut]
            done += 1
            try:
                _, status = fut.result()
            except Exception as e:
                status = f"error:{e}"

            if status.startswith("error"):
                counts["error"] += 1
                print(f"  [{done:3}/{len(city_slugs)}] ✗  {slug}: {status}")
            elif status in ("skip", "missing", "noop"):
                counts["skip"] += 1
            else:
                counts[status] = counts.get(status, 0) + 1
                tag = "✓ NEW   " if status == "new" else "  cached"
                print(f"  [{done:3}/{len(city_slugs)}] {tag} {slug}")

    print(f"\nDone in {time.time()-start:.1f}s  |  New: {counts['new']}  Cached: {counts['cached']}  Errors: {counts['error']}")
    if counts["error"]:
        print("Re-run to retry failed cities.")

if __name__ == "__main__":
    main()
