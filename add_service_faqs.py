#!/usr/bin/env python3
"""Add FAQPage JSON-LD + a visible FAQ section to service pages that lack it.

Targets: ada-compliant-units, construction-porta-potty-rentals, deluxe-porta-potty,
hand-wash-stations, luxury-restroom-trailers, standard-porta-potty.

For each, inject:
  1. A <script type="application/ld+json"> block with FAQPage schema (in <head>).
  2. A visible <section id="faq"> with the same Q&A (in <body>) so the schema
     content matches what users see (Google requirement).

Idempotent.
"""
from __future__ import annotations
import json
import os
import re

FAQ_DATA: dict[str, list[tuple[str, str]]] = {
    "standard-porta-potty.html": [
        ("How much does a standard porta potty rental cost?",
         "Standard porta potty rentals typically run $50–$75 per day, $175–$250 per week, "
         "and $450–$650 per month — including delivery, weekly servicing, and pickup. "
         "Final pricing depends on city, distance from our depot, and how many units you need. "
         "Call (833) 652-9344 for a same-day quote in your zip code."),
        ("How quickly can a standard porta potty be delivered?",
         "Most standard rentals arrive same-day or next-day. Order before 12 PM local time and we "
         "deliver the same business day to most of the 224 cities we serve. Emergency dispatch is "
         "available 24/7 — call us and we'll route the closest truck."),
        ("How many porta potties do I need?",
         "A good rule of thumb: 1 unit per 50 attendees for a 4-hour event, or 1 unit per 10 workers "
         "for a 40-hour construction week (OSHA 1926.51). Use our free "
         "<a href=\"/calculator\">porta potty calculator</a> to get an exact recommendation in seconds."),
        ("How often is a standard porta potty serviced?",
         "Weekly servicing is included by default. Higher-traffic events and construction sites can "
         "be scheduled for twice-weekly or daily service for an additional fee. Servicing pumps the "
         "tank, restocks paper and sanitizer, and refreshes the deodorizer — typically 10–15 minutes per unit."),
        ("Will a standard porta potty damage my driveway or yard?",
         "No. Standard units sit on three feet that distribute load evenly and won't crack asphalt, "
         "concrete, or pavers. On grass, they may leave temporary impressions if left for weeks during "
         "wet weather — placing on plywood prevents this entirely."),
        ("Are standard porta potties OSHA compliant for construction sites?",
         "Yes. Our standard units meet OSHA 29 CFR 1926.51 sanitation requirements: enclosed, vented, "
         "lockable, with toilet paper and a hand sanitizer dispenser. We supply the unit-to-worker "
         "ratio chart with your quote so your foreman has documentation for inspections."),
        ("What's the difference between a standard and a deluxe porta potty?",
         "Standard units have a basic toilet and urinal with a hand sanitizer dispenser. "
         "<a href=\"/services/deluxe-porta-potty\">Deluxe units</a> add a sink with foot-pump running water, "
         "interior light, hook, and mirror — better for events and longer construction stays."),
        ("Do I need a permit to place a porta potty?",
         "On private property, usually no permit is required. On public streets or sidewalks, most "
         "cities require a right-of-way permit (typically $25–$100). We'll tell you whether your "
         "specific address needs one when you call for a quote."),
    ],
    "deluxe-porta-potty.html": [
        ("How much does a deluxe porta potty cost?",
         "Deluxe porta potty rentals run $85–$125 per day, $275–$375 per week, "
         "and $550–$800 per month. The premium over a standard unit covers the sink, "
         "running water, interior light, and additional restocking time."),
        ("What does a deluxe porta potty include?",
         "Sink with foot-pump running water, paper towel dispenser, mirror, coat hook, "
         "interior LED light, and a slightly larger interior than a standard unit. Same "
         "rugged construction, same weekly servicing."),
        ("When should I choose deluxe over standard?",
         "Pick deluxe when guests will be on-site for more than 4 hours, when food is served "
         "(handwashing matters more), or for longer construction projects where worker comfort "
         "improves productivity. For weddings and upscale events, consider a "
         "<a href=\"/services/luxury-restroom-trailers\">luxury restroom trailer</a> instead."),
        ("How is the running water supplied?",
         "Deluxe units carry a self-contained 5–8 gallon fresh-water tank that's refilled at each "
         "weekly service. The foot pump means no electricity is required — they work anywhere."),
        ("Are deluxe porta potties ADA compliant?",
         "No — deluxe units have a slightly larger interior but do not meet the 60-inch turning "
         "radius and grab-bar requirements. For ADA needs use our "
         "<a href=\"/services/ada-compliant-units\">ADA-compliant units</a> instead."),
        ("How quickly can a deluxe unit be delivered?",
         "Same-day delivery is available in most of the 224 cities we serve. Order before noon for "
         "same-day in metro areas; otherwise next-day delivery is standard."),
    ],
    "luxury-restroom-trailers.html": [
        ("How much does a luxury restroom trailer cost?",
         "2-station trailers: $300–$450/day. 4-station: $500–$750/day. "
         "8-station: $800–$1,200/day. Multi-day weddings and weekend events typically book a "
         "Friday-pickup-to-Monday-return rate that's roughly 2.5× the day rate. Call (833) 652-9344 "
         "for a quote tied to your specific guest count and date."),
        ("How many luxury trailer stations do I need?",
         "Roughly 1 station per 75–100 guests for a 4-hour event with alcohol service, or "
         "1 station per 100–150 guests for daytime events without alcohol. The "
         "<a href=\"/calculator\">calculator</a> recommends an exact unit and station count."),
        ("What amenities are included in a luxury restroom trailer?",
         "Climate control (heat + A/C), flushing porcelain toilets, running hot and cold water, "
         "vanity mirrors and lighting, premium finishes, sound system on most models, and "
         "interior music. 4-station and larger units have separate men's and women's sides."),
        ("What's the difference between luxury and VIP trailers?",
         "Luxury trailers cover most weddings, corporate events, and upscale parties. "
         "<a href=\"/services/vip-trailers-rental\">VIP trailers</a> step up to celebrity-level: marble finishes, "
         "concierge attendants, branded interior wraps, and 8+ station capacity. VIPs start at $799/day."),
        ("Do luxury restroom trailers need power and water hookups?",
         "Power: yes — a standard 110V outlet from a generator or building. Water: not strictly required "
         "(internal fresh-water tank lasts most events) but a garden-hose hookup extends capacity for "
         "multi-day rentals."),
        ("Can luxury trailers be set up on grass or gravel?",
         "Yes. Our drivers level the trailer with included pads. We'll review the placement spot with "
         "you before booking — soft mud or steep grades may need plywood support."),
        ("How long does setup take?",
         "30–45 minutes for a 2- or 4-station trailer. 8-station units take about an hour. We arrive "
         "1–2 hours before your event start time so everything's tested and ready before guests show up."),
        ("Do you provide attendants?",
         "Optional add-on: $35–$60/hour. Recommended for weddings over 200 guests and any event "
         "where the trailer represents your brand. Attendants restock supplies, keep mirrors "
         "clean, and direct guests."),
    ],
    "construction-porta-potty-rentals.html": [
        ("How many porta potties does OSHA require on a construction site?",
         "OSHA 29 CFR 1926.51 requires: 1 toilet for ≤20 workers, 1 toilet + 1 urinal for 20–199 "
         "workers, and 1 toilet + 1 urinal per 40 workers above 200. "
         "<a href=\"/blog/osha-requirements-construction-sites\">Full OSHA construction guide here</a>."),
        ("How much does a construction porta potty cost per month?",
         "Most construction rentals run $150–$225 per month including weekly service. "
         "Long-term contracts (3+ months) typically save 10–15%. Bulk rentals (5+ units on the "
         "same site) get further discounts."),
        ("Can you deliver a porta potty same day to a job site?",
         "Yes — we dispatch same-day in 224 cities for orders placed before noon. Construction "
         "trailers and remote sites are typical fits. Call (833) 652-9344 with the address and "
         "we'll confirm a delivery window."),
        ("Do you offer crane-hookable porta potties for high-rise sites?",
         "Yes. Our <a href=\"/services/crane-hook-porta-potty-rentals\">crane-hook units</a> include "
         "a reinforced lifting frame rated for safe hoisting between floors. Common on residential "
         "tower and commercial high-rise builds."),
        ("How often should a construction porta potty be serviced?",
         "Weekly is standard. Sites with 20+ workers per unit usually upgrade to twice-weekly. "
         "Sites in extreme heat (Phoenix, Las Vegas, Houston in summer) often add deodorizer "
         "boost service to keep odor controlled."),
        ("What happens if a worker damages a unit?",
         "Normal wear is included. Significant damage (vandalism, knockover, fire) is billed at "
         "replacement cost — typically $150–$400 for standard units. We'll document with photos "
         "and call the site contact before any charge."),
    ],
    "ada-compliant-units.html": [
        ("How much does an ADA-compliant porta potty rental cost?",
         "ADA-compliant units rent for $100–$150 per day, $350–$500 per week, "
         "and $700–$1,000 per month. The premium over standard reflects the larger footprint, "
         "grab bars, and reinforced ramp design."),
        ("What makes a porta potty ADA compliant?",
         "ADA requires a 60-inch interior turning radius for wheelchairs, grab bars on both sides "
         "of the toilet, ground-level entry (no step), an accessible-height toilet seat, and a "
         "lower paper-towel/sanitizer dispenser. Our units meet all 28 CFR Part 36 requirements."),
        ("How many ADA units does my event need?",
         "Best practice: at least 1 ADA unit per event, plus 1 ADA unit per 20 standard units. "
         "Most municipalities require a 5% ADA ratio for permitted public events. The "
         "<a href=\"/calculator\">calculator</a> applies this ratio automatically."),
        ("Are ADA porta potties wheelchair accessible?",
         "Yes. Ground-level entry (no step up), 36-inch wide door, 60-inch interior turning radius, "
         "and grab bars. Service animals are welcome inside."),
        ("Can ADA units be placed on uneven ground?",
         "They need a level surface for the door to swing freely and for the grab bars to hold "
         "their alignment. Our drivers use leveling pads on slopes up to 5°; steeper terrain "
         "requires a plywood platform we can supply for $25–$50."),
        ("Do ADA units include a sink?",
         "Most do — interior sink with foot-pump running water, paper towels, and a soap "
         "dispenser at accessible height. Confirm with us when booking; we have both sink-equipped "
         "and standard ADA models."),
    ],
    "hand-wash-stations.html": [
        ("How much does a hand wash station rental cost?",
         "Standalone hand wash stations rent for $35–$50 per day, $90–$140 per week, "
         "and $250–$400 per month. Often paired with porta potty rentals; bundled pricing "
         "saves about 15%."),
        ("How many hand wash stations do I need for an event?",
         "Roughly 1 station per 75–100 guests for events with food service. For construction "
         "sites, OSHA requires hand wash facilities when workers handle hazardous materials — "
         "1 station per 25 workers is a safe default."),
        ("Are hand wash stations required by OSHA on construction sites?",
         "OSHA 1926.51(f) requires soap, towels, and water for handwashing whenever workers are "
         "exposed to chemicals, lead, or other hazards. For general construction without specific "
         "hazards, hand sanitizer-only stations are acceptable but full hand wash stations are "
         "best practice and often required by general contractors."),
        ("What do hand wash stations include?",
         "Two-basin design with foot-pump operation, fresh-water tank (15–25 gallons), gray-water "
         "catchment, soap dispenser with refill, and paper-towel dispenser. No electricity needed."),
        ("How long does a hand wash station's water tank last?",
         "About 200–300 handwashings between refills. For a 100-guest 4-hour event, one station's "
         "tank typically covers the entire event without refill. Heavy-use sites get scheduled "
         "twice-weekly servicing."),
        ("Can hand wash stations be used in winter?",
         "Yes, but the water must be drained nightly below freezing or use our heated-jacket option "
         "(+$25/week). For winter events, hand sanitizer-only stations are simpler — ask when you call."),
    ],
}

FAQ_SCHEMA_TEMPLATE = '<script type="application/ld+json">{schema}</script>'


def build_schema(qa: list[tuple[str, str]]) -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    # Strip HTML tags from answer text for the schema (Google prefers clean text;
                    # the visible answer keeps the links).
                    "text": re.sub(r"<[^>]+>", "", a),
                },
            }
            for q, a in qa
        ],
    }, indent=None)


def build_visible_section(qa: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'    <details class="bg-white border border-gray-200 rounded-lg p-5 group">\n'
        f'      <summary class="font-bold text-lg text-gray-900 cursor-pointer flex justify-between items-center">'
        f'<span>{q}</span><span class="text-green-600 group-open:rotate-45 transition-transform text-2xl leading-none">+</span></summary>\n'
        f'      <div class="text-gray-700 mt-3 leading-relaxed">{a}</div>\n'
        f'    </details>'
        for q, a in qa
    )
    return (
        '\n<section id="faq" class="py-16 bg-gray-50 border-t border-gray-200">\n'
        '  <div class="max-w-3xl mx-auto px-4">\n'
        '    <h2 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2 text-center">Frequently Asked Questions</h2>\n'
        '    <p class="text-gray-600 mb-8 text-center">Real answers — not marketing fluff. Still got questions? Call (833) 652-9344.</p>\n'
        '    <div class="space-y-3">\n'
        + items +
        '\n    </div>\n'
        '  </div>\n'
        '</section>\n'
    )


def patch(filename: str, qa: list[tuple[str, str]]) -> bool:
    path = f"services/{filename}"
    if not os.path.exists(path):
        return False
    html = open(path, encoding="utf-8").read()
    if '"FAQPage"' in html:
        return False

    schema_block = '<script type="application/ld+json">' + build_schema(qa) + '</script>\n'
    visible = build_visible_section(qa)

    # Insert FAQ schema right before </head>
    html2, n1 = re.subn(r"</head>", lambda _m: schema_block + "</head>", html, count=1)
    if n1 == 0:
        return False

    # Insert visible section: prefer right before <footer>, fall back to before </body>.
    html3, n2 = re.subn(r"<footer", lambda _m: visible + "<footer", html2, count=1)
    if n2 == 0:
        html3, n2 = re.subn(r"</body>", lambda _m: visible + "</body>", html2, count=1)
    if n2 == 0:
        return False

    open(path, "w", encoding="utf-8").write(html3)
    return True


def main() -> None:
    fixed = 0
    for filename, qa in FAQ_DATA.items():
        if patch(filename, qa):
            print(f"  added FAQ to services/{filename}")
            fixed += 1
        else:
            print(f"  skipped services/{filename}")
    print(f"\nAdded FAQ to {fixed} pages.")


if __name__ == "__main__":
    main()
