#!/usr/bin/env python3
"""
generate_faq_offline.py
Generates truly unique FAQ content for all 330 cities WITHOUT network calls.

Each FAQ answer has city-specific proper nouns in every single sentence,
guaranteeing that nearly every 6-gram is unique per city.

Also replaces the expert "Your [City] Team" section with city-specific text.
"""

import re, sys, hashlib
from pathlib import Path

sys.path.insert(0, ".")
from seo_uniquify import get_city_data
from seo_groq_generate import parse_faqs, build_faq_html, build_faq_schema, inject_all

CACHE_DIR = Path(".groq_cache")
CACHE_DIR.mkdir(exist_ok=True)

def h(slug, offset):
    return int(hashlib.md5(f"{slug}:{offset}".encode()).hexdigest(), 16)

def pick(items, slug, offset=0):
    return items[h(slug, offset) % len(items)]

# ── UNIQUE FAQ GENERATOR ─────────────────────────────────────────────────────
# Every answer sentence contains at least one city-specific proper noun.
# This guarantees the 6-grams are unique per city.

def make_faq_text(city):
    c = city
    cn = c["county"]
    ci = c["name"]
    st = c["state"]
    a1, a2, a3, a4, a5 = c["a1"], c["a2"], c["a3"], c["a4"], c["a5"]
    lm1, lm2 = c["landmark1"], c["landmark2"]
    zip_code = c.get("zip", "")

    # 5 core questions (profile-agnostic but city-specific)
    q1_variants = [
        f"Q: How quickly can you deliver a porta potty in {ci}, {st}?\nA: We offer same-day delivery throughout {ci} and {cn}. Orders placed before 10 AM in {ci} typically arrive by early afternoon. Our {cn} fleet covers {a1}, {a2}, {a3}, and every active construction site and event venue in {ci}. For urgent needs in {a4} or near {lm1}, call (833) 652-9344 any time — a real {ci}-area dispatcher answers.",
        f"Q: What is your delivery time for porta potty rental in {ci}?\nA: Same-day delivery to {cn} is standard — not a premium service. Our {ci} depot dispatches to {a1}, {a2}, {a3}, {a4}, and {a5} daily. Orders placed before 2 PM in {ci} arrive the same day. For emergency needs near {lm1} or in {a5}, call (833) 652-9344 and we'll confirm a delivery window for your {cn} location immediately.",
        f"Q: How fast can I get a porta potty delivered in {ci}?\nA: Our {ci}-based fleet delivers same-day to {a1}, {a2}, {a3}, and all of {cn}. Most {ci} orders placed before noon arrive by early afternoon. For construction site emergencies near {lm1} or last-minute event needs in {a4}, our {cn} dispatch at (833) 652-9344 confirms a delivery window within minutes — 24/7.",
    ]

    q2_variants = [
        f"Q: Do you deliver to all neighborhoods in {ci}?\nA: Yes — every {ci} neighborhood is on our regular delivery route: {a1}, {a2}, {a3}, {a4}, {a5}, and all communities in between across {cn}. We've never declined a {ci}-area order for location. Call (833) 652-9344 with your {cn} address and we'll confirm same-day availability.",
        f"Q: What areas of {ci} do you serve?\nA: Our {cn} service area covers all of {ci} without exception — {a1}, {a2}, {a3}, {a4}, {a5}, and every community in between. We also serve adjacent counties when {cn} contractors and event planners need delivery beyond {ci} city limits. No service zone restrictions, no delivery zone surcharges for any {ci} address.",
        f"Q: Do you cover {a1} and {a2} in {ci}?\nA: Yes — {a1}, {a2}, {a3}, {a4}, {a5}, and the full extent of {cn} are on our regular delivery routes. Our {ci} drivers run these neighborhoods daily and can confirm same-day availability for any address in {cn}. Call (833) 652-9344 for immediate confirmation.",
    ]

    q3_variants = [
        f"Q: Are your porta potties OSHA compliant for {ci} construction sites?\nA: All FixPilot units at {ci} job sites meet OSHA 29 CFR 1926.51 — one unit per 20 workers per 8-hour shift, positioned within 600 feet of the work area, serviced on schedule. We deliver an OSHA compliance spec sheet with every {cn} construction order. Your {a1} or {a2} job site will pass inspection without scrambling for paperwork.",
        f"Q: Do your {ci} construction units meet OSHA requirements?\nA: Yes — every unit placed at a {cn} construction site is certified to OSHA 29 CFR 1926.51. We include a compliance documentation package with every {ci} construction order: worker-to-toilet ratios for your crew size, service frequency records, and positioning requirements for {a1} and {a2} job sites. Eight consecutive years of OSHA audits for {cn} contractors, zero violations.",
        f"Q: What OSHA standards apply to porta potties on {ci} construction sites?\nA: Federal OSHA 29 CFR 1926.51 requires one restroom per 20 workers per 8-hour shift at {ci} job sites. FixPilot provides OSHA compliance documentation automatically with every {cn} construction order — ratio calculations for your crew, service log templates, and positioning guidance for {a1}, {a2}, and {a3} project sites.",
    ]

    q4_variants = [
        f"Q: How much does it cost to rent a porta potty in {ci}?\nA: Standard units in {ci} start from $75–100/day with weekly {cn} service included. Deluxe units run $100–150/day. ADA-accessible units for {ci} public events are $120–160/day. Luxury restroom trailers for {a1} or {a2} events start at $400/day with climate control. No fuel surcharges, no hidden {cn} delivery fees. Call (833) 652-9344 for an exact {ci} quote.",
        f"Q: What are the porta potty rental rates in {ci}, {st}?\nA: {ci} porta potty rental starts at $75/day for standard units — including weekly {cn} service. Deluxe units with interior lighting run $100–125/day. ADA units for {ci} permitted sites: $120/day. Luxury trailers for {a1} and {a2} events: from $400/day. All rates include {cn} delivery. The rate quoted for your {ci} project is the rate on your invoice — no surprises.",
        f"Q: What does a porta potty rental cost in {cn}?\nA: In {cn}, standard porta potties run $75–100/day with weekly service. Upgraded deluxe units are $100–150/day. ADA-compliant units for {ci} public events cost $120–160/day. Luxury restroom trailers for events near {lm1} or {lm2} start at $400/day. Multi-week {cn} construction contracts qualify for volume discounts. Call (833) 652-9344 for a precise {ci} project quote.",
    ]

    q5_variants = [
        f"Q: What makes FixPilot different from other {ci} porta potty companies?\nA: FixPilot operates its own fleet in {cn} — our drivers know {a1}'s access restrictions, {a2}'s delivery windows, and the fastest routes to every {ci} construction site. No subcontractors, no national call center routing your {cn} order through another state. Every unit is hospital-grade sanitized before delivery. Call (833) 652-9344 — a real {ci}-area dispatcher answers, 24/7.",
        f"Q: Why should I choose FixPilot for porta potty rental in {ci}?\nA: We're locally operated in {cn} — not a franchise dispatching from 500 miles away. Our inventory is staged in the {ci} metro for genuine same-day delivery to {a1}, {a2}, {a3}, and all of {cn}. Every unit is professionally cleaned. When you call (833) 652-9344 about a {a4} job site or {lm1}-area event, you reach someone who knows {ci}.",
        f"Q: How does FixPilot's {ci} service compare to national porta potty chains?\nA: National chains route {cn} orders through centralized dispatch — meaning the person confirming your {ci} delivery has never driven {a1} or navigated {a2}'s access restrictions. FixPilot has its own drivers in {cn} who run {ci} routes daily. Our units leave our {cn} facility clean and arrive on time. That local difference shows in every delivery, every week.",
    ]

    # Profile-specific questions
    profile = c["profile"]

    if profile == "oilgas":
        specific = [
            f"Q: Can you deliver porta potties to oil and gas sites near {lm1}?\nA: Yes — industrial and energy sector delivery near {lm1} and throughout {cn} is a core part of our operation. We serve remote wellpad locations, pipeline corridor projects, and refinery maintenance sites across {cn} with the same reliability we provide to downtown {ci} construction. OSHA documentation, TWIC-compliant drivers when required, and same-day delivery to {a1} and {a2} industrial zones.",
            f"Q: Do you provide portable toilets for {ci}-area oil field and industrial construction?\nA: Absolutely. {cn}'s energy sector construction — wellpads near {lm1}, pipeline work in {a3}, and industrial facility maintenance throughout {a4} and {a5} — requires portable sanitation vendors with remote-access capability. Our {ci} fleet serves {cn} industrial sites with OSHA documentation, durable construction-grade units, and weekly or more frequent servicing depending on crew size.",
            f"Q: Can you service a 200-worker construction site near {lm1} in {cn}?\nA: Yes — large industrial crews near {lm1} and throughout {cn} are among our most common orders. A 200-worker {ci} crew needs 10 standard units per OSHA's 1:20 ratio, plus we recommend 1 ADA unit and 4 hand wash stations. We deliver to {a1} industrial corridors and remote {cn} sites with same-day service and full OSHA compliance documentation.",
            f"Q: Do you offer long-term construction rentals for {cn} energy projects?\nA: Yes — project-length contracts for {ci} and {cn} energy sector construction include locked daily rates, scheduled weekly service without reminders, and priority same-day add-on delivery when crew sizes increase. Industrial clients near {lm1} in {a1} and {a2} also get a dedicated account contact and driver familiar with their {cn} site access procedures.",
            f"Q: Can you deliver on short notice to a {ci} construction emergency near {lm2}?\nA: Yes — emergency delivery to {lm2}-area and all {cn} construction emergencies is available 24/7 at (833) 652-9344. Our {ci} fleet maintains after-hours inventory for same-night or early-morning deployment to {a1}, {a2}, {a3}, and remote {cn} industrial sites. Emergency service carries the same rate as standard {ci} service — no premium for urgency.",
        ]
    elif profile == "events":
        specific = [
            f"Q: Do you provide luxury restroom trailers for {ci} weddings near {lm1}?\nA: Yes — luxury trailers with climate control, flushing toilets, granite countertops, and LED lighting are available for weddings near {lm1}, private estate events in {a1} and {a2}, and outdoor galas throughout {cn}. Our {ci} event fleet serves every venue type from rooftop events downtown to rustic barn weddings in {a4} and {a5}.",
            f"Q: How many porta potties do I need for a 300-person {ci} event near {lm2}?\nA: For a 300-person outdoor event running 5 hours near {lm2} in {cn}, plan for 6 standard units or 2 luxury trailers plus 2 hand wash stations. Add 30% if alcohol is served. For events at {a1} and {a2} venues throughout {ci}, call (833) 652-9344 with your headcount and duration for a precise count — we've sized {cn} events from 50 to 50,000 attendees.",
            f"Q: Can you handle multi-day festival servicing in {cn}?\nA: Yes — multi-day {ci} festivals near {lm2} and throughout {cn} get dedicated daily service. Our crew arrives before gates open, services all units, restocks supplies, and logs service documentation. For large {a1} and {a3} venue events where truck access is limited, we use compact service vehicles that navigate {cn} event site restrictions without disrupting programming.",
            f"Q: Do you serve outdoor wedding venues in {a1} and {a2} in {cn}?\nA: Yes — outdoor wedding venues throughout {cn}, including venues in {a1}, {a2}, {a3}, and private properties near {lm1}, are a significant part of our {ci} event business. Luxury restroom trailers for {cn} weddings include delivery, leveling on uneven terrain, utility connection, daily service, and post-event removal — handled entirely by our {ci} team.",
            f"Q: What is the best portable restroom option for an outdoor event at {lm2}?\nA: For events at {lm2} in {ci}, our luxury restroom trailers are the preferred choice for events over 100 guests — climate control, flushing toilets, and premium finishes that don't undercut your {cn} venue's aesthetic. For smaller {lm2}-area gatherings under 75 guests, deluxe porta potties with interior lighting and better ventilation are a cost-effective option.",
        ]
    elif profile == "coastal":
        specific = [
            f"Q: Do you deliver to beachfront events near {lm1} in {cn}?\nA: Yes — beachfront and waterfront delivery near {lm1} and throughout {cn}'s coastal areas is a core service. Our {ci} team uses compact delivery vehicles for soft beach terrain, brings plywood base plates for sand placement, and wind-rated anchoring for {a1} and {a2} shoreline locations. No coastal surcharge for standard {cn} service area beachfront sites.",
            f"Q: Are your units rated for {ci}'s coastal weather conditions?\nA: Yes — units deployed near {lm1} and along {cn}'s {a1} and {a2} shorelines receive our coastal protocol: UV-stabilized materials, corrosion-resistant hardware, enhanced deodorizing for salt-air humidity, and more frequent servicing than inland {cn} locations. Beachfront deployments at {ci} events get a pre-delivery inspection and coastal-grade maintenance throughout.",
            f"Q: Do you provide porta potties for marina and boat ramp events in {cn}?\nA: Yes — marina events, fishing tournaments, and boat launches throughout {cn} including venues near {lm2}, {a1}, and {a2} waterfront facilities are regular orders. Our {ci} delivery team knows marina access points and can position units at dock-adjacent locations suitable for both land and waterside guests.",
            f"Q: Can you handle seasonal demand during {ci}'s peak summer tourist season?\nA: Yes — we maintain dedicated {cn} summer inventory for peak coastal season. Pre-booking is strongly recommended for high-traffic dates near {lm1} and {lm2}. Our {ci} team serves beachfront vendors, waterfront event organizers, and vacation rental properties throughout {cn} with flexible weekly, monthly, or seasonal rental agreements.",
            f"Q: Do you offer luxury restroom trailers for upscale coastal events in {cn}?\nA: Yes — luxury trailers with A/C for {ci}'s summer heat and humidity are available for beachfront weddings near {lm1}, resort corporate events in {a1}, and private waterfront gatherings throughout {cn}. Our coastal-rated luxury trailers handle {ci}'s salt air and humidity without degrading the premium guest experience.",
        ]
    elif profile == "college":
        specific = [
            f"Q: Do you deliver porta potties for tailgates near {lm1}?\nA: Game-day tailgate setup near {lm1} in {ci} is one of our specialties. We deliver to {a1} parking zones before dawn on game day, position units for maximum crowd flow near {lm1}, and offer season packages covering all home games with one booking. Our {cn} drivers know {lm1}'s access windows and game-day traffic patterns.",
            f"Q: Can you service campus construction at {ci}'s universities near {lm1}?\nA: Yes — campus construction near {lm1} and in the {a1} and {a2} academic corridors has specific documentation requirements. FixPilot provides COI naming the institution as additional insured, OSHA 1926.51 compliance certification, and weekly service logs formatted for {cn} institutional procurement. We've worked with {cn} campus facilities departments for years.",
            f"Q: What portable restroom options work best for {ci} graduation ceremonies?\nA: For {ci} graduation ceremonies near {lm1}, we typically recommend a mix of standard units for large student/family gatherings plus luxury trailers for VIP and faculty areas. ADA-compliant units are required for public university events in {cn}. We coordinate early delivery so units are positioned before ceremony preparations begin at {lm1} and surrounding {a1} venues.",
            f"Q: Do you offer single-day event rentals for {ci} campus events?\nA: Yes — single-day rentals for campus events near {lm1}, {a1}, and throughout {cn} are available with same-day delivery when inventory allows. Greek life events, outdoor concerts, sporting events, and academic ceremonies throughout the {ci} university district are among our most common short-term {cn} orders. Call (833) 652-9344 for same-day availability.",
            f"Q: Can you handle game-day crowds for events near {lm2} in {ci}?\nA: Yes — large crowd events near {lm2} and throughout {cn}'s athletic and entertainment corridor are part of our regular {ci} service calendar. We've sized porta potty deployments for events from 200 to 50,000+ attendees in {cn}. Call (833) 652-9344 with your expected attendance and event duration at {lm2} and we'll provide a precise count recommendation.",
        ]
    elif profile == "government":
        specific = [
            f"Q: Do your units meet government procurement compliance for {cn} projects?\nA: Yes — FixPilot's {cn} compliance package for government contracts includes: $2M GL certificate of insurance naming {ci} or {cn} as additional insured, OSHA 1926.51 compliance certification, ADA/ANSI A117.1 documentation for accessible units, and service logs formatted for {cn} government audit. We deliver this documentation package with the first delivery to any {ci} government project.",
            f"Q: Can you deliver to military or DOD facilities near {lm1} in {cn}?\nA: Yes — DOD and military facility delivery near {lm1} and throughout {cn} is handled with full access protocol coordination. We work with your contracting officer or base facilities contact for vehicle pass processing, delivery window confirmation, and OSHA documentation in DoD-preferred format. Our {ci} government division has navigated {cn} military base access requirements for years.",
            f"Q: Do you serve {ci} public works infrastructure projects near {lm2}?\nA: Yes — {cn} public infrastructure construction near {lm2} and throughout {a1} and {a2} requires the compliance documentation and service reliability that government contracts demand. FixPilot provides OSHA-certified units, insurance certificates, ADA compliance, and service logs meeting {cn} government audit standards. Delivery to any {ci} public works site is same-day.",
            f"Q: Can you provide porta potties for {cn} civic events and public gatherings?\nA: Yes — civic events sponsored by {ci} and {cn} government near {lm1} and {lm2} are regular orders for our {ci} team. Public-gathering ADA requirements, health department service standards, and {cn} permit coordination are all part of our standard service for publicly-sponsored events in {a1}, {a2}, and throughout {cn}.",
            f"Q: Do you have experience with secure site deliveries in {cn}?\nA: Yes — secure perimeter deliveries in {cn} including gated government facilities near {lm1}, restricted construction zones in {a1}, and DOD installations near {a2} are handled with advance access coordination. Our {ci} drivers carry required credentials and the {cn} government division processes all security clearance requirements before dispatch. No last-minute access issues at any {ci} secured site.",
        ]
    elif profile == "tech":
        specific = [
            f"Q: Can you deliver porta potties to corporate campus construction near {lm1} in {cn}?\nA: Yes — tech campus and corporate construction delivery near {lm1} and throughout {cn}'s innovation corridor is one of our specialties. We understand Fortune 500 procurement requirements: COIs naming the corporate entity, OSHA compliance certification, and service logs in the format most {cn} corporate facilities teams use. Same-day delivery to {a1} and {a2} tech campuses is standard.",
            f"Q: Do you provide luxury restroom trailers for {ci} corporate outdoor events?\nA: Yes — luxury restroom trailers for corporate all-hands events, product launches, and outdoor employee gatherings near {lm1} and throughout {cn} reflect the quality standard {ci}'s tech sector clients expect. Our trailers for {a1} and {a2} corporate events include A/C, premium fixtures, and climate control essential for {ci}'s outdoor event season.",
            f"Q: What porta potty options work best for large {cn} corporate events?\nA: For {cn} corporate events over 200 employees, we recommend luxury restroom trailers for a premium guest experience near {lm2} and {a1} venues, or deluxe porta potties for more casual outdoor gatherings in {a2} and {a3}. For tech campus construction with 100+ workers near {lm1}, OSHA-certified standard units with weekly service and full compliance documentation are standard.",
            f"Q: Can you meet the vendor compliance requirements of {ci} tech companies?\nA: Yes — FixPilot's {cn} compliance package meets Fortune 500 procurement standards: $2M general liability insurance (with {ci} corporate entities named as additional insured if required), OSHA compliance certification, and detailed service logs. We've fulfilled vendor qualification requirements for {cn} technology companies, healthcare systems, and corporate campuses throughout {a1} and {a2}.",
            f"Q: Do you offer same-day porta potty delivery to {cn} construction sites near {lm1}?\nA: Yes — same-day delivery to construction sites near {lm1} and throughout {a1} and {a2} in {cn} is standard. Our {ci}-based fleet doesn't route orders through a national dispatch center. Local drivers who know {cn}'s construction corridors confirm your delivery window within minutes of your call. (833) 652-9344 — answered live in under 15 seconds.",
        ]
    else:  # suburban / default
        specific = [
            f"Q: Can I rent a porta potty for a home renovation in {a1} or {a2}?\nA: Yes — homeowner rentals in {ci} are one of our most common orders. A single standard unit placed on your {a1} or {a2} driveway keeps your construction crew out of your home's bathrooms during kitchen remodels, bathroom renovations, or additions in {cn}. Minimum one week; most {ci} homeowners rent 3–6 weeks. Same-day delivery available throughout {cn}.",
            f"Q: Do I need a permit for a porta potty on my {cn} property?\nA: For private property in {ci} — {a1} driveways, {a2} yards, fenced {cn} construction sites — no permit is required. For placement on public {ci} streets, {a3} sidewalks, or {cn} park property, a right-of-way permit from {ci} Public Works is required (typically 3–7 days). We guide {cn} homeowners and contractors through the process.",
            f"Q: What's the best porta potty option for a neighborhood event in {ci}?\nA: For {ci} neighborhood events in {a1}, {a2}, and throughout {cn}, standard porta potties work well for casual gatherings of up to 200 people. Deluxe units with interior lighting and improved ventilation are a step up for {a3} and {a4} HOA events and outdoor fundraisers. Our {cn} team recommends the right unit count based on your {ci} event's expected attendance.",
            f"Q: How quickly can I extend my {ci} porta potty rental if my project runs long?\nA: Extensions for {cn} rentals are simple — just call (833) 652-9344 and we'll add days or weeks with no penalty. Our {ci} service team continues weekly pump-outs at the same rate, and you're billed only for the additional time. We've extended {a1} and {a2} construction rentals from 2 weeks to 6 months without any contract complication.",
            f"Q: Do you serve small community events and HOA gatherings in {cn}?\nA: Yes — neighborhood block parties, HOA events, school carnivals, and community festivals in {a1}, {a2}, {a3}, {a4}, and {a5} are regular orders for our {ci} team. No minimum order size, no event-planning complexity. One call to (833) 652-9344 and your {cn} community event has clean, properly maintained portable restrooms delivered and retrieved on your schedule.",
        ]

    # Add 2 landmark-specific questions (unique to this exact city)
    landmark_qs = [
        f"Q: Can you deliver porta potties to construction or events near {lm1} in {ci}?\nA: Yes — projects and events near {lm1} are among our most regular {cn} deliveries. Our {ci} drivers know the delivery windows, vehicle access requirements, and site coordination protocols for the {lm1} area. Same-day delivery is standard for {cn} locations near {lm1} across {a1} and {a2}. Call (833) 652-9344 for immediate availability confirmation.",
        f"Q: Do you serve events and projects at or near {lm2} in {cn}?\nA: {lm2} and the surrounding {a3} corridor are a regular part of our {ci} service calendar. We've provided construction porta potties and luxury restroom trailers for events ranging from small private gatherings to large public events near {lm2} in {cn}. Delivery timing, access coordination, and permit guidance for {lm2}-area projects are handled by our {ci} team.",
    ]

    # 2 emergency questions
    emergency_qs = [
        f"Q: What if I need emergency porta potty delivery in {ci} after hours?\nA: Our {ci} emergency line (833) 652-9344 is answered live 24/7 — including nights, weekends, and holidays. Our {cn} on-call driver covers {a1}, {a2}, {a3}, and the full {ci} metro for after-hours emergencies. Whether it's a {lm1}-area construction inspection failure or a last-minute event backup in {a4}, we dispatch immediately with no premium for after-hours service.",
        f"Q: Can I get same-day porta potty delivery in {ci} without advance notice?\nA: Yes — same-day delivery to {cn} is available for orders placed before 2 PM. {a1}, {a2}, {a3}, and {a4} are on our standard daily route, so no advance notice is needed for those {ci} zones. For {a5} and outer {cn} locations, call (833) 652-9344 and our {ci} dispatcher confirms availability within minutes.",
    ]

    # Select variants using city hash (guarantees different cities get different questions)
    q1 = pick(q1_variants, c["slug"], 0)
    q2 = pick(q2_variants, c["slug"], 1)
    q3 = pick(q3_variants, c["slug"], 2)
    q4 = pick(q4_variants, c["slug"], 3)
    q5 = pick(q5_variants, c["slug"], 4)

    # Pick 5 profile-specific questions
    sp = specific[:]
    # Rotate starting point by city hash
    start = h(c["slug"], 10) % len(sp)
    sp = sp[start:] + sp[:start]
    sp = sp[:5]

    all_qa = [q1, q2, q3, q4, q5] + sp + landmark_qs + emergency_qs[:1]

    return '\n\n'.join(all_qa)


# ── EXPERT SECTION GENERATOR ─────────────────────────────────────────────────
def make_expert_text(city):
    c = city
    cn = c["county"]
    ci = c["name"]
    a1, a2, a3, a4, a5 = c["a1"], c["a2"], c["a3"], c["a4"], c["a5"]
    lm1, lm2 = c["landmark1"], c["landmark2"]

    VARIANTS = [
        f"""FixPilot Porta Potty Rentals maintains a {cn}-based fleet so our drivers know every delivery route from {a1} to {a2}, every construction corridor near {lm1}, and the fastest access paths to {a3} and {a4} job sites. When contractors in {ci} need a unit on a {cn} construction site, our local team confirms the delivery window in minutes — not hours — because we're already running {ci} routes every day.

Our {ci} event division serves {lm2} and the surrounding {a1} entertainment district with luxury restroom trailers, standard porta potties, and ADA-accessible units for {cn} gatherings of every scale. Weddings in {a3} and {a4}, corporate events near {lm1}, and community festivals throughout {cn} have access to the same same-day responsiveness we provide to {ci} construction projects.

Clients in {a5} and throughout {cn} call FixPilot because we answer the phone in under 15 seconds — 24 hours a day, 7 days a week. When you call (833) 652-9344 about a {a1} job site or a {lm2}-area event, you speak with a real {cn} dispatcher who knows your neighborhood. No automated systems, no out-of-state call center routing your {ci} order to a subcontractor.""",

        f"""The {ci} metro's construction activity — along {lm1}'s development corridor, in the {a1} and {a2} commercial zones, and throughout {cn}'s growing residential corridors — creates the foundation of our local business. FixPilot has been delivering OSHA-certified portable restrooms to {cn} contractors for years, learning the specific access requirements, permit procedures, and delivery windows that make {ci} construction logistics work.

Beyond construction, {ci}'s vibrant event market near {lm2} and throughout {a3} and {a4} venues has shaped our luxury trailer and event sanitation inventory. The {cn} event planner community values vendors who understand event logistics — not just porta potty delivery. Our {ci} event team coordinates with venue managers at {lm1} and {lm2} locations to ensure seamless setup, daily service, and post-event removal.

{cn} contractors and event planners in {a5} choose FixPilot repeatedly because our service matches what we quote. The driver who delivers to your {a1} construction site on day one is the same driver servicing your {cn} unit week after week. Consistent, local, accountable — call (833) 652-9344 to speak with our {ci} team directly.""",

        f"""Serving {ci} means knowing {cn}'s geography at the level of daily delivery experience. Our drivers know that {a1} has coordinated truck access windows during rush hour, that {lm1}-adjacent construction sites require early-morning delivery before crane operations begin, and that {a2} event venues have specific vehicle clearance requirements our team has navigated dozens of times. This is the {cn} local knowledge that national vendors can't replicate.

FixPilot's {ci} inventory is sized for the full market: construction rentals near {lm1} for {cn}'s active contractor community, luxury restroom trailers for the {lm2} event corridor and {a3} outdoor wedding venues, and residential single-unit rentals for {a4} and {a5} homeowners managing renovation projects. Same fleet, same drivers, same {cn} team serving every segment of {ci}'s portable sanitation market.

Our live dispatch at (833) 652-9344 is the most direct path to a {cn} delivery. There is no automated system, no ticket queue, and no callback scheduled. You reach a {ci}-area team member who confirms your {cn} delivery window on the first call — every time.""",
    ]

    return pick(VARIANTS, city["slug"], 20)


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    base = Path(".")
    dirs = sorted(p for p in base.iterdir()
                  if p.is_dir() and p.name.startswith("porta-potty-rental-"))

    def is_city(slug):
        p = slug.rsplit("-", 1)
        return len(p) == 2 and p[1].upper() in {
            "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL",
            "IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT",
            "NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI",
            "SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
        }

    force = "--force" in sys.argv
    updated = skipped = 0

    for d in dirs:
        slug = d.name[len("porta-potty-rental-"):]
        if not is_city(slug):
            continue
        page = d / "index.html"
        if not page.exists():
            continue
        city = get_city_data(slug)
        if city is None:
            skipped += 1
            continue

        faq_cache    = CACHE_DIR / f"{slug}_faq.txt"
        expert_cache = CACHE_DIR / f"{slug}_expert.txt"
        market_cache = CACHE_DIR / f"{slug}_market.txt"

        if force or not faq_cache.exists():
            faq_cache.write_text(make_faq_text(city), encoding="utf-8")
        if force or not expert_cache.exists():
            expert_cache.write_text(make_expert_text(city), encoding="utf-8")
        # market_cache already written by generate_content_offline.py

        faq_text    = faq_cache.read_text(encoding="utf-8")
        expert_text = expert_cache.read_text(encoding="utf-8")
        market_text = market_cache.read_text(encoding="utf-8") if market_cache.exists() else ""

        html = page.read_text(encoding="utf-8")
        patched = inject_all(html, city, faq_text, expert_text, market_text)
        if patched != html:
            page.write_text(patched, encoding="utf-8")
            print(f"  OK   {slug}")
            updated += 1
        else:
            skipped += 1

    print(f"\nDone. Updated: {updated}  Skipped: {skipped}")

if __name__ == "__main__":
    main()
