#!/usr/bin/env python3
"""Inject a quote form section into every city page right after the hero.

Stable insertion point: the closing </section> tag of the first
<section class="hero-bg ..."> block.

The form has 5 fields (name, phone, city, date, use case), uses Formspree as a
fallback transport (replace REPLACE_WITH_FORM_ID before deploy), and includes a
honey-pot anti-spam input. Idempotent: skips pages where the section is already
present.
"""
from __future__ import annotations
import glob
import re

HERO_END = re.compile(
    r'(<section[^>]*(?:class="hero-bg|background-image:[^"]*hero-banner|class="[^"]*bg-cover[^"]*"[^>]*style="background-image)[^>]*>.*?</section>)',
    re.DOTALL,
)

CITY_LABEL = re.compile(
    r'<meta name="geo\.placename" content="([^"]+)"',
)


def form_block(city_label: str) -> str:
    return f'''
<section id="quote-form" class="py-12 md:py-16 bg-gradient-to-br from-brand-50 to-white border-b border-gray-200">
  <div class="container mx-auto px-4">
    <div class="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto items-center">
      <div>
        <h2 class="text-3xl md:text-4xl font-extrabold text-brand-900 mb-3">Free Quote in 60 Seconds — {city_label}</h2>
        <p class="text-gray-700 mb-4 text-lg">Tell us when and where. We text or call back within 15 minutes, 24 / 7.</p>
        <ul class="space-y-2 text-gray-700">
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">✓</span> Same-day delivery to most of {city_label.split(",")[0]}</li>
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">✓</span> Standard, deluxe, luxury trailers, ADA, hand wash</li>
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">✓</span> No hidden fuel surcharges. Transparent pricing.</li>
          <li class="flex items-start gap-2"><span class="text-green-600 font-bold mt-0.5">✓</span> Licensed &amp; $2M insured · OSHA + ADA compliant</li>
        </ul>
        <p class="mt-5 text-gray-600 text-sm">
          Prefer to call? <a href="tel:+18336529344" class="font-bold text-brand-700 underline">(833) 652-9344</a>
        </p>
      </div>
      <form action="https://formspree.io/f/REPLACE_WITH_FORM_ID" method="POST"
            class="bg-white rounded-2xl shadow-xl p-6 md:p-8 border-t-8 border-cta">
        <div class="grid grid-cols-1 gap-3">
          <label class="block">
            <span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">Name</span>
            <input name="name" required autocomplete="name"
                   class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-brand-600 focus:outline-none">
          </label>
          <label class="block">
            <span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">Phone</span>
            <input name="phone" type="tel" required autocomplete="tel" placeholder="(555) 555-1234"
                   class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-brand-600 focus:outline-none">
          </label>
          <label class="block">
            <span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">Date Needed</span>
            <input name="needed_date" type="date" required
                   class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-brand-600 focus:outline-none">
          </label>
          <label class="block">
            <span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">What's it for?</span>
            <select name="use_case"
                    class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-brand-600 focus:outline-none bg-white">
              <option value="">Select use case…</option>
              <option>Construction site</option>
              <option>Wedding</option>
              <option>Festival or event</option>
              <option>Backyard / party</option>
              <option>Film / TV production</option>
              <option>Emergency / disaster</option>
              <option>Other</option>
            </select>
          </label>
        </div>
        <input name="city" type="hidden" value="{city_label}">
        <input name="_subject" type="hidden" value="New quote request – {city_label}">
        <input name="_gotcha" type="text" tabindex="-1" autocomplete="off" style="display:none">
        <button type="submit"
                class="mt-4 w-full bg-cta hover:bg-orange-700 text-white font-extrabold text-lg py-4 rounded-xl transition shadow-lg">
          Get My Free Quote →
        </button>
      </form>
    </div>
  </div>
</section>
'''


def patch(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    if 'id="quote-form"' in html:
        return False
    cl = CITY_LABEL.search(html)
    city_label = cl.group(1) if cl else "Your City"

    new_html, n = HERO_END.subn(
        lambda m: m.group(1) + form_block(city_label),
        html,
        count=1,
    )
    if n == 0:
        # Fallback: pages without a real hero — insert after the closing </header>.
        new_html, n = re.subn(
            r"(</header>)",
            lambda m: m.group(1) + form_block(city_label),
            html,
            count=1,
        )
    if n == 0:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    fixed = 0
    skipped = 0
    for path in sorted(glob.glob("porta-potty-rental-*-*/index.html")):
        if patch(path):
            fixed += 1
        else:
            skipped += 1
    print(f"Injected quote form into {fixed} city pages; {skipped} skipped (already present or no hero).")


if __name__ == "__main__":
    main()
