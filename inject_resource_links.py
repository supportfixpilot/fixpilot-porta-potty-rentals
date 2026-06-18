#!/usr/bin/env python3
"""Inject a 'Helpful Resources' section linking to blog posts and the calculator
   into every city page, inserted just before the #related-cities section."""

import glob
import re

CITY_GLOB = "porta-potty-rental-*-*/index.html"

RESOURCES_SECTION = """
  <!-- Helpful Resources -->
  <section class="py-12 bg-white border-t border-gray-100">
    <div class="container mx-auto px-4">
      <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6 text-center">Helpful Resources</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
        <a href="/blog/porta-potty-rental-costs-2026.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
          <span class="text-2xl">💰</span>
          <div>
            <p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">2026 Rental Cost Guide</p>
            <p class="text-xs text-gray-500 mt-1">Standard, deluxe &amp; luxury pricing explained</p>
          </div>
        </a>
        <a href="/blog/how-many-porta-potties-do-you-need.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
          <span class="text-2xl">🔢</span>
          <div>
            <p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">How Many Units Do You Need?</p>
            <p class="text-xs text-gray-500 mt-1">Calculate the right number for your event or site</p>
          </div>
        </a>
        <a href="/blog/osha-requirements-construction-sites.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
          <span class="text-2xl">🦺</span>
          <div>
            <p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">OSHA Compliance Guide</p>
            <p class="text-xs text-gray-500 mt-1">Requirements for construction sites</p>
          </div>
        </a>
        <a href="/services/construction-porta-potty-rentals.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
          <span class="text-2xl">🏗️</span>
          <div>
            <p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">Construction Site Services</p>
            <p class="text-xs text-gray-500 mt-1">OSHA-compliant units for job sites</p>
          </div>
        </a>
        <a href="/services/luxury-restroom-trailers.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
          <span class="text-2xl">✨</span>
          <div>
            <p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">Luxury Restroom Trailers</p>
            <p class="text-xs text-gray-500 mt-1">VIP-grade trailers for weddings &amp; events</p>
          </div>
        </a>
        <a href="/calculator" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
          <span class="text-2xl">🧮</span>
          <div>
            <p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">Free Quote Calculator</p>
            <p class="text-xs text-gray-500 mt-1">Get an instant estimate in 60 seconds</p>
          </div>
        </a>
      </div>
    </div>
  </section>

"""

INJECT_BEFORE = '<section id="related-cities"'
INJECT_BEFORE_ALT = 'id="related-cities"'


def inject_resources(html: str) -> tuple[str, bool]:
    # Skip if already injected
    if 'Helpful Resources' in html:
        return html, False

    # Find the related-cities section
    idx = html.find(INJECT_BEFORE)
    if idx == -1:
        # Try alternate pattern
        idx = html.find(INJECT_BEFORE_ALT)
        if idx != -1:
            idx = html.rfind('<section', 0, idx)

    # Fallback: inject before footer
    if idx == -1:
        idx = html.rfind('<footer')
    if idx == -1:
        idx = html.rfind('</body>')
    if idx == -1:
        return html, False

    new_html = html[:idx] + RESOURCES_SECTION + html[idx:]
    return new_html, True


def main():
    paths = sorted(glob.glob(CITY_GLOB))
    injected = 0
    skipped = 0
    for path in paths:
        with open(path, encoding='utf-8', errors='replace') as f:
            html = f.read()
        new_html, changed = inject_resources(html)
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            injected += 1
        else:
            skipped += 1
    print(f"Injected resource links into {injected} pages, {skipped} skipped (already done or no related-cities section)")


if __name__ == '__main__':
    main()
