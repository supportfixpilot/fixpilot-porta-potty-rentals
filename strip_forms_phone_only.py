#!/usr/bin/env python3
"""Strip the quote form from every city + state hub page and replace with a
phone-only call-to-action panel. Preserves the city/state label and the
calculator note that was injected inside the form section.

Idempotent: skips pages already converted (no <form> + has #call-cta marker).
"""
from __future__ import annotations
import glob
import re

# Match the entire <section id="quote-form" ...> ... </section> block
# (greedy on closing because nothing inside this section uses nested <section>)
SECTION_RE = re.compile(
    r'<section id="quote-form"[^>]*>(?P<body>.*?)</section>',
    re.DOTALL,
)

CITY_LABEL_RE = re.compile(r'<meta name="geo\.placename" content="([^"]+)"')
H2_RE = re.compile(r"<h2[^>]*>([^<]+)</h2>")

# Pull the calculator note that was injected into the bullet list, if present.
CALC_NOTE_RE = re.compile(
    r'<p class="text-gray-600 text-sm mt-3">[^<]*<a href="/calculator"[^<]*</a>[^<]*</p>',
    re.DOTALL,
)


def call_panel(city_label: str, calculator_note: str | None) -> str:
    note = (
        calculator_note
        or '<p class="text-gray-600 text-sm mt-4">Need to figure unit count first? Try our free '
           '<a href="/calculator" class="font-bold text-brand-700 underline">porta potty calculator</a>.</p>'
    )
    return f'''
<section id="call-cta" class="py-12 md:py-16 bg-gradient-to-br from-brand-50 to-white border-b border-gray-200">
  <div class="container mx-auto px-4">
    <div class="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto items-center">
      <div>
        <h2 class="text-3xl md:text-4xl font-extrabold text-brand-900 mb-3">Free quote in under 60 seconds &mdash; {city_label}</h2>
        <p class="text-gray-700 mb-4 text-lg">No forms. No callbacks. Talk to a real dispatcher right now and lock in delivery.</p>
        <ul class="space-y-2 text-gray-700">
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">&check;</span> Same-day delivery to most of {city_label.split(",")[0].strip()}</li>
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">&check;</span> Standard, deluxe, luxury trailers, ADA, hand wash</li>
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">&check;</span> No hidden fuel surcharges. Transparent pricing.</li>
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">&check;</span> Licensed &amp; $2M insured &middot; OSHA + ADA compliant</li>
        </ul>
        {note}
      </div>
      <aside class="bg-white rounded-2xl shadow-xl p-6 md:p-10 border-t-8 border-cta text-center">
        <p class="inline-block bg-green-100 text-green-800 text-xs font-extrabold uppercase tracking-widest px-3 py-1 rounded-full mb-3">Open 24 / 7 &middot; Live Dispatch</p>
        <p class="text-gray-700 mb-4">Tap below &mdash; we answer in under 15 seconds.</p>
        <a href="tel:+18336529344"
           class="block w-full bg-cta hover:bg-orange-700 text-white font-extrabold text-2xl md:text-3xl py-5 px-4 rounded-2xl shadow-xl transition-colors pulse-btn mb-3">
          <i class="fas fa-phone mr-2"></i>(833) 652-9344
        </a>
        <p class="text-sm text-gray-600">Free quote &middot; no obligation &middot; same-day delivery available.</p>
      </aside>
    </div>
  </div>
</section>
'''


def patch(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    if 'id="call-cta"' in html and 'id="quote-form"' not in html:
        return False  # already converted
    if 'id="quote-form"' not in html:
        return False  # nothing to do

    cl = CITY_LABEL_RE.search(html)
    city_label = cl.group(1) if cl else "Your City"

    # Try to preserve the calculator note we injected earlier.
    section_match = SECTION_RE.search(html)
    calc_note = None
    if section_match:
        m = CALC_NOTE_RE.search(section_match.group("body"))
        if m:
            calc_note = m.group(0)

    panel = call_panel(city_label, calc_note)

    new_html = SECTION_RE.sub(lambda _m: panel, html, count=1)
    if new_html == html:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    paths = (
        glob.glob("porta-potty-rental-*-*/index.html")
        + glob.glob("porta-potty-rental-texas/index.html")
        + glob.glob("porta-potty-rental-california/index.html")
        + glob.glob("porta-potty-rental-florida/index.html")
        + glob.glob("porta-potty-rental-new-york/index.html")
        + glob.glob("porta-potty-rental-colorado/index.html")
        + glob.glob("porta-potty-rental-maryland/index.html")
        + glob.glob("porta-potty-rental-minnesota/index.html")
        + glob.glob("porta-potty-rental-arizona/index.html")
        + glob.glob("porta-potty-rental-tennessee/index.html")
        + glob.glob("porta-potty-rental-illinois/index.html")
    )
    fixed = 0
    skipped = 0
    for path in sorted(set(paths)):
        try:
            if patch(path):
                fixed += 1
            else:
                skipped += 1
        except FileNotFoundError:
            pass
    print(f"Converted {fixed} pages to phone-only CTA; {skipped} skipped.")


if __name__ == "__main__":
    main()
