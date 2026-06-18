#!/usr/bin/env python3
"""
expand_thin_blogs.py — Expand thin blog posts to 1,200+ words via Groq API.

Usage:
    python3 expand_thin_blogs.py YOUR_GROQ_API_KEY

For each thin post (<1000w) it generates an additional ~400-word section
(a "Pro Tips" or "Frequently Asked Questions" block) and injects it before
the closing </article> tag. Safe to re-run — skips posts already at 1,000+w.

Requires: groq API key with access to llama3-70b-8192 (or falls back to llama3-8b-8192).
"""

import re, json, sys, time, os
from urllib import request, error

ROOT = os.path.dirname(os.path.abspath(__file__))

THIN_POSTS = [
    'ada-compliant-porta-potties.html',
    'event-sanitation-checklist.html',
    'hand-wash-station-requirements.html',
    'how-many-porta-potties-for-wedding.html',
    'luxury-vs-standard-porta-potties.html',
    'same-day-porta-potty-rental.html',
]

GROQ_URL  = 'https://api.groq.com/openai/v1/chat/completions'
MODEL     = 'llama-3.3-70b-versatile'
FALLBACK  = 'llama3-8b-8192'

PROMPTS = {
    'ada-compliant-porta-potties.html': (
        'ADA-Compliant Portable Restrooms',
        "Write a FAQ section for a blog post about ADA-compliant portable restrooms. "
        "Include 5 real questions renters ask (with detailed answers): cost premium vs standard, "
        "how to verify a unit is truly ADA compliant, whether outdoor events need ADA units, "
        "grab bar placement specs, and how to request ADA units from a rental company. "
        "Use HTML: each Q as <h3> inside a <div class='faq-item'>, answer as <p>. "
        "Tone: practical, authoritative, helpful. About 400 words."
    ),
    'event-sanitation-checklist.html': (
        'Event Sanitation Planning Checklist',
        "Write a 'Pro Tips from Event Coordinators' section for a blog about event sanitation planning. "
        "Cover: how to handle late-arriving deliveries, tip for alcohol-heavy events (need 20% more units), "
        "VIP area restroom strategy, how to label units clearly for guests, and a 'game day' checklist "
        "for the event morning. Use HTML: intro paragraph, bullet list tips, and a final CTA paragraph. "
        "Tone: experienced, practical. About 400 words."
    ),
    'hand-wash-station-requirements.html': (
        'Hand Wash Stations OSHA Requirements',
        "Write a 'State-Specific Hand Wash Station Rules' section for a blog about OSHA hand wash requirements. "
        "Cover California (Cal/OSHA), Texas, New York, Florida, and Washington state — how each differs from "
        "federal OSHA for hand wash stations at construction sites and events. Include a simple HTML table "
        "comparing state vs federal requirements, then 3-4 paragraphs on the most common violations and how "
        "to avoid them. Tone: compliance-focused, clear. About 400 words."
    ),
    'how-many-porta-potties-for-wedding.html': (
        'How Many Porta Potties for a Wedding',
        "Write a 'Real Wedding Case Studies' section for a blog about porta potty counts for weddings. "
        "Create 3 realistic case studies: (1) 100-guest rustic barn wedding in Texas, (2) 200-guest outdoor "
        "garden wedding in California, (3) 400-guest upscale tented wedding in New York. For each: guest count, "
        "venue type, alcohol yes/no, units recommended, total cost range, and what went wrong when they "
        "underestimated. Use HTML: <h3> for each case, <p> paragraphs. Tone: story-driven, practical. ~400 words."
    ),
    'luxury-vs-standard-porta-potties.html': (
        'Luxury vs Standard Porta Potties',
        "Write a 'Real Cost Breakdown: What You Actually Pay' section for a blog comparing luxury restroom "
        "trailers vs standard porta potties. Cover: typical price per unit/day for standard ($75-125), "
        "luxury 2-station ($450-600), luxury 4-station ($800-1100), luxury 8-station ($1500-2200). "
        "Include what's included in each tier (servicing, delivery, attendant), hidden fees to watch for, "
        "and when the luxury upgrade ROI actually makes sense (weddings over 100 guests, corporate events). "
        "Use HTML table for pricing, then 3 paragraphs. Tone: transparent, helpful. About 400 words."
    ),
    'same-day-porta-potty-rental.html': (
        'Same-Day Porta Potty Rental',
        "Write a 'Real Scenarios Where Same-Day Delivery Works (and Doesn't)' section for a blog about "
        "same-day porta potty rentals. Cover 4 scenarios: (1) construction site emergency after unit tips over, "
        "(2) last-minute outdoor birthday party for 50 people, (3) festival organizer who forgot to book, "
        "(4) film production needing units for a remote location shoot. For each: likelihood of same-day success, "
        "why/why not, and what to say when calling to maximize chances. "
        "Use HTML: <h3> for each scenario, <p> paragraphs. Tone: realistic, helpful. About 400 words."
    ),
}

def groq_request(api_key, prompt, model):
    payload = json.dumps({
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You are a professional content writer for a porta potty rental company. Write clean, well-structured HTML content only — no markdown, no preamble, no explanations. Start directly with the HTML.'},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': 900,
        'temperature': 0.7,
    }).encode()

    req = request.Request(GROQ_URL, data=payload, headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    })
    try:
        with request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data['choices'][0]['message']['content'].strip()
    except error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f'HTTP {e.code}: {body[:300]}')

def word_count(html):
    return len(re.sub(r'<[^>]+>', ' ', html).split())

def expand_post(post_file, api_key):
    path = os.path.join(ROOT, 'blog', post_file)
    with open(path, encoding='utf-8') as f:
        html = f.read()

    wc = word_count(html)
    if wc >= 1000:
        print(f'  SKIP {post_file} — already {wc}w')
        return

    section_title, prompt = PROMPTS[post_file]
    print(f'  Generating expansion for {post_file} ({wc}w)...')

    new_section = None
    for model in [MODEL, FALLBACK]:
        try:
            new_section = groq_request(api_key, prompt, model)
            print(f'    ✓ Got content via {model}')
            break
        except RuntimeError as e:
            print(f'    ! {model} failed: {e}')
            time.sleep(2)

    if not new_section:
        print(f'    ✗ All models failed for {post_file}')
        return

    # Wrap in a section with heading
    injection = f'''
      <section class="mt-8 pt-8 border-t border-gray-200">
        <h2 class="text-2xl font-black text-brand-900 mb-5">{section_title} — Extended Guide</h2>
        {new_section}
      </section>
'''

    # Inject before </article>
    if '</article>' in html:
        html = html.replace('</article>', injection + '\n      </article>', 1)
    else:
        # Fallback: inject before </main>
        html = html.replace('</main>', injection + '\n  </main>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    new_wc = word_count(html)
    print(f'    ✓ {post_file}: {wc}w → {new_wc}w (+{new_wc - wc}w)')


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 expand_thin_blogs.py YOUR_GROQ_API_KEY')
        sys.exit(1)

    api_key = sys.argv[1].strip()
    print(f'Using key: {api_key[:8]}...')
    print()

    for post in THIN_POSTS:
        expand_post(post, api_key)
        time.sleep(1.5)  # rate limit headroom

    print('\nDone. Re-run audit_all_pages.py to verify.')


if __name__ == '__main__':
    main()
