#!/usr/bin/env python3
"""Generate state hub pages.

Each hub:
  - URL  /porta-potty-rental-{state-slug}
  - file /porta-potty-rental-{state-slug}/index.html
  - lists every city we serve in that state, plus state-specific regulatory hooks

Slug rules:
  - state slug is lowercase full state name with hyphens, e.g. "texas",
    "north-carolina"
  - We use a separate folder name `porta-potty-rental-{state-slug}`
"""
from __future__ import annotations
import os
from collections import defaultdict

STATE_FULL = {
    "AL": ("Alabama", "alabama"), "AZ": ("Arizona", "arizona"),
    "CA": ("California", "california"), "CO": ("Colorado", "colorado"),
    "CT": ("Connecticut", "connecticut"), "FL": ("Florida", "florida"),
    "GA": ("Georgia", "georgia"), "ID": ("Idaho", "idaho"),
    "IL": ("Illinois", "illinois"), "IN": ("Indiana", "indiana"),
    "KS": ("Kansas", "kansas"), "KY": ("Kentucky", "kentucky"),
    "LA": ("Louisiana", "louisiana"), "MA": ("Massachusetts", "massachusetts"),
    "MD": ("Maryland", "maryland"), "MI": ("Michigan", "michigan"),
    "MN": ("Minnesota", "minnesota"), "MO": ("Missouri", "missouri"),
    "NC": ("North Carolina", "north-carolina"), "NJ": ("New Jersey", "new-jersey"),
    "NV": ("Nevada", "nevada"), "NY": ("New York", "new-york"),
    "OH": ("Ohio", "ohio"), "OK": ("Oklahoma", "oklahoma"),
    "PA": ("Pennsylvania", "pennsylvania"), "SC": ("South Carolina", "south-carolina"),
    "TN": ("Tennessee", "tennessee"), "TX": ("Texas", "texas"),
    "VA": ("Virginia", "virginia"), "WA": ("Washington", "washington"),
    "WI": ("Wisconsin", "wisconsin"),
    # Extended states
    "AR": ("Arkansas", "arkansas"), "IA": ("Iowa", "iowa"),
    "MS": ("Mississippi", "mississippi"), "MT": ("Montana", "montana"),
    "ND": ("North Dakota", "north-dakota"), "NE": ("Nebraska", "nebraska"),
    "NM": ("New Mexico", "new-mexico"), "OR": ("Oregon", "oregon"),
    "SD": ("South Dakota", "south-dakota"), "UT": ("Utah", "utah"),
    "WY": ("Wyoming", "wyoming"),
}

# Color palette per state hub (vary for visual identity)
STATE_PALETTE = {
    "TX": ("#fef2f2 #fee2e2 #fca5a5 #ef4444 #dc2626 #b91c1c #991b1b #7f1d1d", "#dc2626"),
    "CA": ("#fff7ed #ffedd5 #fdba74 #f97316 #ea580c #c2410c #9a3412 #7c2d12", "#dc2626"),
    "FL": ("#ecfdf5 #d1fae5 #6ee7b7 #10b981 #059669 #047857 #065f46 #064e3b", "#ea580c"),
    "NY": ("#eff6ff #dbeafe #93c5fd #3b82f6 #2563eb #1d4ed8 #1e40af #1e3a8a", "#ea580c"),
    "CO": ("#f5f3ff #ede9fe #c4b5fd #8b5cf6 #7c3aed #6d28d9 #5b21b6 #4c1d95", "#ea580c"),
    "AZ": ("#fff7ed #ffedd5 #fdba74 #f97316 #ea580c #c2410c #9a3412 #7c2d12", "#dc2626"),
    "TN": ("#fef3c7 #fde68a #fcd34d #f59e0b #d97706 #b45309 #92400e #78350f", "#dc2626"),
    "GA": ("#ecfdf5 #d1fae5 #6ee7b7 #10b981 #059669 #047857 #065f46 #064e3b", "#dc2626"),
    "MI": ("#eff6ff #dbeafe #93c5fd #3b82f6 #2563eb #1d4ed8 #1e40af #1e3a8a", "#dc2626"),
    "NC": ("#f0f9ff #e0f2fe #7dd3fc #0ea5e9 #0284c7 #0369a1 #075985 #0c4a6e", "#ea580c"),
    "WA": ("#f0fdfa #ccfbf1 #5eead4 #14b8a6 #0d9488 #0f766e #115e59 #134e4a", "#ea580c"),
    "AL": ("#fef2f2 #fee2e2 #fca5a5 #ef4444 #dc2626 #b91c1c #991b1b #7f1d1d", "#fbbf24"),
    "NV": ("#fef3c7 #fde68a #fcd34d #f59e0b #d97706 #b45309 #92400e #78350f", "#dc2626"),
    "NJ": ("#f0f9ff #e0f2fe #7dd3fc #0ea5e9 #0284c7 #0369a1 #075985 #0c4a6e", "#dc2626"),
    "MO": ("#fef2f2 #fee2e2 #fca5a5 #ef4444 #dc2626 #b91c1c #991b1b #7f1d1d", "#1d4ed8"),
    "IN": ("#fefce8 #fef9c3 #fef08a #fde047 #facc15 #eab308 #ca8a04 #a16207", "#1d4ed8"),
    "KY": ("#eff6ff #dbeafe #93c5fd #3b82f6 #2563eb #1d4ed8 #1e40af #1e3a8a", "#dc2626"),
}
DEFAULT_PALETTE = ("#eff6ff #dbeafe #93c5fd #3b82f6 #2563eb #1d4ed8 #1e40af #1e3a8a", "#ea580c")


def state_intro(name: str, st: str, n: int) -> str:
    return (
        f"FixPilot Porta Potty Rentals serves {n} cities across {name}, with same-day "
        f"delivery in metro areas and 24/7 dispatch statewide. Whether you're running a "
        f"construction site, planning a wedding, organizing a festival, or handling an "
        f"emergency, we have the right unit and the right schedule. "
        "Call <a href=\"tel:+18336529344\" class=\"text-cta font-bold underline\">"
        "(833) 652-9344</a> for an instant quote."
    )


STATE_REGULATORY: dict[str, str] = {
    "TX": "Texas construction sites must comply with OSHA 1926.51 and the Texas Department of "
          "Licensing and Regulation rules. We supply OSHA-ratio documentation with every order.",
    "CA": "California work-site sanitation falls under Cal/OSHA Title 8 §1526 and §3366. "
          "Cal/OSHA's ratios are stricter than federal OSHA — our default California unit "
          "counts use the Cal/OSHA tables.",
    "FL": "Florida hurricane season demands portable sanitation backup plans. Our Florida fleet "
          "stages pre-positioned units for rapid storm response and includes wind-rated tie-down kits.",
    "NY": "New York City requires DOT permits for porta potty placement on public right-of-way. "
          "We file the permit on your behalf and include weight-rated mats for sidewalk placement.",
    "CO": "Colorado's high-altitude conditions mean cold-weather servicing for most of the year. "
          "We use winter-grade deodorizer and heated hand wash stations from October through April.",
    "AZ": "Arizona summer heat (115°F+) requires aggressive deodorizing and ventilation. Our "
          "Arizona units include heat-resistant blue solution and shade-positioning recommendations.",
    "TN": "Tennessee construction-site sanitation follows OSHA 1926.51. We provide ratio sheets "
          "and weekly servicing logs your TOSHA inspector can sign off on.",
    "GA": "Georgia humidity demands more frequent servicing for odor control. Our Georgia routes "
          "default to twice-weekly service for sites with 20+ workers per unit.",
    "MI": "Michigan winter operations include heated hand wash stations, antifreeze additives, "
          "and snow-clearance scheduling so your driveway stays accessible to our trucks.",
    "NC": "North Carolina coastal events need wind-rated tie-downs (we include these standard "
          "April–November) and elevated placement during hurricane watches.",
    "WA": "Washington wet-season placement uses mud mats and elevated platforms. Winter water-line "
          "drain protocols on hand wash stations standard November–March.",
    "AL": "Alabama humidity drives twice-weekly servicing as the default for sites with 20+ workers. "
          "Hurricane tie-downs included on Gulf Coast deployments June–November.",
    "NV": "Nevada summer heat (115°F+) requires heat-resistant deodorizer and shade-positioning. "
          "Las Vegas event-calendar surge windows benefit from advance booking.",
    "NJ": "New Jersey construction sites follow federal OSHA. NYC-metro DOT permits required for "
          "right-of-way placement near the boroughs; we file these routinely.",
    "MO": "Missouri tornado season (March–June) generates emergency-sanitation surge demand. "
          "Our Missouri fleet pre-stages capacity during severe-weather watches.",
    "IN": "Indiana winter operations include antifreeze additives November–March. Indianapolis 500 "
          "weekend (Memorial Day) drives state-wide fleet deployment.",
    "KY": "Kentucky construction follows federal OSHA. Derby-week surge demand in Louisville drives "
          "May supply constraints; book early for events near Churchill Downs.",
}


def template(state_full: str, state_slug: str, st: str, cities: list[tuple[str, str]]) -> str:
    palette, cta_color = STATE_PALETTE.get(st, DEFAULT_PALETTE)
    p = palette.split()
    title = f"Porta Potty Rental {state_full} — {len(cities)} Cities · Same-Day Delivery"
    description = (
        f"Porta potty rental across {state_full}: {len(cities)} cities, same-day delivery, "
        f"OSHA-compliant, ADA units, luxury restroom trailers. Call (833) 652-9344 for an instant quote."
    )
    canonical = f"https://fixpilotportapottyrentals.com/porta-potty-rental-{state_slug}"

    city_cards = []
    for city, slug in sorted(cities):
        city_cards.append(
            f'      <a href="/porta-potty-rental-{slug}" class="bg-white rounded-xl p-5 shadow-md hover:shadow-xl hover:-translate-y-0.5 transition-all border border-brand-200 group block">\n'
            f'        <h3 class="font-extrabold text-brand-950 text-lg mb-1 group-hover:text-cta transition">{city}</h3>\n'
            f'        <p class="text-sm text-brand-700">Porta Potty Rental in {city}, {st}</p>\n'
            '        <span class="text-cta text-sm font-semibold mt-2 inline-block">View →</span>\n'
            '      </a>'
        )

    regulatory = STATE_REGULATORY.get(st,
                                      f"{state_full} sanitation projects follow federal OSHA 29 CFR 1926.51. "
                                      "We supply ratio documentation with every quote.")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta name="geo.region" content="US-{st}">
<meta name="geo.placename" content="{state_full}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://fixpilotportapottyrentals.com/hero-banner-images/1.%2020260226_225037_822.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://fixpilotportapottyrentals.com/hero-banner-images/1.%2020260226_225037_822.webp">

<link rel="stylesheet" href="/assets/tw.css">
<style>:root{{--brand-50:{p[0]};--brand-100:{p[1]};--brand-300:{p[2]};--brand-500:{p[3]};--brand-600:{p[4]};--brand-700:{p[5]};--brand-800:{p[6]};--brand-900:{p[7]};--brand-950:{p[7]};--cta:{cta_color}}}</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Porta Potty Rental {state_full}",
  "description": "{description}",
  "url": "{canonical}",
  "isPartOf": {{"@type": "WebSite", "name": "FixPilot Porta Potty Rentals", "url": "https://fixpilotportapottyrentals.com"}},
  "breadcrumb": {{
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://fixpilotportapottyrentals.com/"}},
      {{"@type": "ListItem", "position": 2, "name": "Locations", "item": "https://fixpilotportapottyrentals.com/locations"}},
      {{"@type": "ListItem", "position": 3, "name": "{state_full}", "item": "{canonical}"}}
    ]
  }}
}}
</script>

</head>
<body class="bg-brand-50 text-brand-900">

<header class="bg-white shadow-md sticky top-0 z-40">
  <div class="container mx-auto px-4 py-4 flex items-center justify-between">
    <a href="/" class="flex items-center gap-2">
      <div class="w-10 h-10 bg-brand-600 rounded-lg flex items-center justify-center"><span class="text-white font-bold text-xl">F</span></div>
      <span class="text-xl font-bold">FixPilot</span>
    </a>
    <nav class="hidden md:flex items-center gap-6 text-sm font-bold">
      <a href="/locations" class="hover:text-brand-700">Locations</a>
      <a href="/services/standard-porta-potty" class="hover:text-brand-700">Services</a>
      <a href="/calculator" class="hover:text-brand-700">Calculator</a>
      <a href="/blog" class="hover:text-brand-700">Blog</a>
    </nav>
    <a href="tel:+18336529344" class="bg-cta text-white px-4 py-2 rounded-lg font-bold hover:bg-orange-700"><i class="fas fa-phone mr-2"></i>(833) 652-9344</a>
  </div>
</header>

<section class="py-12 md:py-16 bg-gradient-to-br from-brand-100 to-white">
  <div class="container mx-auto px-4 max-w-5xl">
    <nav class="text-sm mb-4 text-gray-600">
      <a href="/" class="text-brand-700 hover:underline">Home</a> /
      <a href="/locations" class="text-brand-700 hover:underline">Locations</a> /
      <span>{state_full}</span>
    </nav>
    <h1 class="text-4xl md:text-5xl font-extrabold text-brand-950 mb-3">Porta Potty Rental in {state_full}</h1>
    <p class="text-lg md:text-xl text-brand-800 mb-6">{state_intro(state_full, st, len(cities))}</p>
    <div class="flex flex-wrap gap-3">
      <a href="tel:+18336529344" class="bg-cta hover:bg-orange-700 text-white font-extrabold py-3 px-6 rounded-xl shadow-lg pulse-btn">Call (833) 652-9344</a>
      <a href="/calculator" class="bg-white border-2 border-brand-700 text-brand-800 font-bold py-3 px-6 rounded-xl">Free unit calculator</a>
    </div>
  </div>
</section>

<section class="py-12 md:py-16 bg-white">
  <div class="container mx-auto px-4 max-w-6xl">
    <h2 class="text-3xl md:text-4xl font-extrabold text-brand-950 mb-2">{len(cities)} Cities We Serve in {state_full}</h2>
    <p class="text-brand-700 mb-8">All cities offer same-day delivery in metro core, next-day everywhere else.</p>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
{chr(10).join(city_cards)}
    </div>
  </div>
</section>

<section class="py-12 md:py-16 bg-brand-50">
  <div class="container mx-auto px-4 max-w-5xl">
    <h2 class="text-3xl md:text-4xl font-extrabold text-brand-950 mb-3">{state_full}-specific compliance &amp; logistics</h2>
    <p class="text-brand-800 text-lg mb-6">{regulatory}</p>
    <div class="grid md:grid-cols-2 gap-6">
      <a href="/services/construction-porta-potty-rentals" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-brand-200">
        <h3 class="font-extrabold text-brand-950 text-xl mb-2">Construction sites</h3>
        <p class="text-brand-700">OSHA-ratio documentation, weekly servicing logs, crane-hookable units for high-rise builds.</p>
      </a>
      <a href="/services/luxury-restroom-trailers" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-brand-200">
        <h3 class="font-extrabold text-brand-950 text-xl mb-2">Weddings &amp; events</h3>
        <p class="text-brand-700">Climate-controlled luxury restroom trailers, optional attendants, pre-event walkthroughs.</p>
      </a>
      <a href="/services/ada-compliant-units" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-brand-200">
        <h3 class="font-extrabold text-brand-950 text-xl mb-2">ADA-compliant units</h3>
        <p class="text-brand-700">Wheelchair-accessible, grab bars, ground-level entry. Required at most permitted public events.</p>
      </a>
      <a href="/services/emergency-short-term-rentals" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-brand-200">
        <h3 class="font-extrabold text-brand-950 text-xl mb-2">Emergency / disaster</h3>
        <p class="text-brand-700">24/7 dispatch, hurricane &amp; wildfire response staging, hospital and shelter deployment.</p>
      </a>
    </div>
  </div>
</section>

<section id="quote-form" class="py-12 md:py-16 bg-gradient-to-br from-brand-50 to-white">
  <div class="container mx-auto px-4 max-w-3xl">
    <div class="bg-white rounded-2xl shadow-xl p-6 md:p-8 border-t-8 border-cta">
      <h2 class="text-2xl md:text-3xl font-extrabold text-brand-950 mb-2">Free quote in 60 seconds — {state_full}</h2>
      <p class="text-gray-600 mb-5">We text or call back within 15 minutes, 24/7.</p>
      <form action="https://formspree.io/f/REPLACE_WITH_FORM_ID" method="POST" class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <label class="block md:col-span-1"><span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">Name</span>
          <input name="name" required class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-cta focus:outline-none"></label>
        <label class="block md:col-span-1"><span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">Phone</span>
          <input name="phone" type="tel" required class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-cta focus:outline-none"></label>
        <label class="block md:col-span-1"><span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">City &amp; ZIP</span>
          <input name="city" required placeholder="e.g. Austin 78701" class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-cta focus:outline-none"></label>
        <label class="block md:col-span-1"><span class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-1">Date</span>
          <input name="needed_date" type="date" required class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-cta focus:outline-none"></label>
        <input name="state" type="hidden" value="{state_full}">
        <input name="_subject" type="hidden" value="New quote request – {state_full}">
        <input name="_gotcha" type="text" tabindex="-1" autocomplete="off" style="display:none">
        <button type="submit" class="md:col-span-2 mt-2 w-full bg-cta hover:bg-orange-700 text-white font-extrabold text-lg py-4 rounded-xl shadow-lg">Get My Free Quote →</button>
      </form>
      <p class="text-center text-sm text-gray-500 mt-3">Or call <a href="tel:+18336529344" class="font-bold text-brand-700 underline">(833) 652-9344</a></p>
    </div>
  </div>
</section>

<footer class="bg-brand-950 text-brand-100 py-12 mt-8">
  <div class="container mx-auto px-4 text-center">
    <p class="mb-2">© FixPilot Porta Potty Rentals — 224 cities, 50 states, 24/7 dispatch.</p>
    <p><a href="tel:+18336529344" class="text-cta font-bold">(833) 652-9344</a> · <a href="/locations" class="hover:underline">All service areas</a> · <a href="/blog" class="hover:underline">Blog</a></p>
  </div>
</footer>

<!-- Mobile sticky call CTA -->
<div id="mobile-cta" class="fixed bottom-0 left-0 right-0 bg-cta shadow-2xl transform translate-y-full transition-transform duration-300 z-50 md:hidden flex items-stretch" style="z-index: 9999;">
  <a href="tel:+18336529344" class="flex-1 py-4 text-center text-white font-extrabold text-lg"><i class="fas fa-phone-alt mr-2 animate-pulse"></i>Call (833) 652-9344</a>
  <button id="mobile-cta-dismiss" type="button" aria-label="Hide call button" class="px-4 text-white/80 hover:text-white text-2xl leading-none">&times;</button>
</div>
<script>
(function () {{
  var cta = document.getElementById('mobile-cta');
  var dismiss = document.getElementById('mobile-cta-dismiss');
  if (!cta) return;
  var dismissed = false;
  try {{ dismissed = sessionStorage.getItem('mobileCtaDismissed') === '1'; }} catch (e) {{}}
  if (dismissed) {{ cta.style.display = 'none'; return; }}
  window.addEventListener('scroll', function () {{
    if (dismissed) return;
    cta.style.transform = window.scrollY > 300 ? 'translateY(0)' : 'translateY(100%)';
  }}, {{ passive: true }});
  if (dismiss) {{
    dismiss.addEventListener('click', function (e) {{
      e.preventDefault();
      dismissed = true;
      cta.style.transform = 'translateY(100%)';
      setTimeout(function () {{ cta.style.display = 'none'; }}, 300);
      try {{ sessionStorage.setItem('mobileCtaDismissed', '1'); }} catch (e) {{}}
    }});
  }}
}})();
</script>

</body>
</html>
'''


def main() -> None:
    states = defaultdict(list)
    for d in sorted(os.listdir(".")):
        if d.startswith("porta-potty-rental-") and os.path.isdir(d):
            slug = d[len("porta-potty-rental-"):]
            if not slug or len(slug) < 4 or slug[-3] != "-":
                continue
            st = slug[-2:].upper()
            if st not in STATE_FULL:
                continue
            city = " ".join(w.capitalize() for w in slug[:-3].split("-"))
            states[st].append((city, slug))

    # All states that have city pages
    targets = sorted(states.keys(), key=lambda s: -len(states[s]))

    written = 0
    for st in targets:
        full, slug = STATE_FULL[st]
        folder = f"porta-potty-rental-{slug}"
        os.makedirs(folder, exist_ok=True)
        out = f"{folder}/index.html"
        if os.path.exists(out):
            print(f"  exists: {out}")
            continue
        html = template(full, slug, st, states[st])
        open(out, "w", encoding="utf-8").write(html)
        print(f"  wrote: {out} ({len(states[st])} cities)")
        written += 1

    print(f"\nWrote {written} state hub pages.")


if __name__ == "__main__":
    main()
