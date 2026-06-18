#!/usr/bin/env python3
"""
seo_dedup2.py  —  90%+ unique content pass.

KEY PRINCIPLE: Every sentence in every generated section contains at least
one unique proper noun from the city (city name, county, area, or landmark).
This means every 6-gram that spans those nouns is unique per city, even when
two cities use the same template variant.

Run AFTER seo_uniquify.py.
"""

import re, hashlib, json
from pathlib import Path

STATE_NAMES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
    "CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia",
    "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa",
    "KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
    "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
    "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire",
    "NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania",
    "RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee",
    "TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington",
    "WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming",
}

import sys
sys.path.insert(0, ".")
from seo_uniquify import CITY_DB, default_city_data, get_city_data

def h_q(slug, offset):
    """Per-question hash — prevents hash collision across questions."""
    return int(hashlib.md5(f"{slug}:{offset}".encode()).hexdigest(), 16)

def pick(variants, slug, offset=0):
    return variants[h_q(slug, offset) % len(variants)]

def fmt(t, c):
    return (t.replace("{city}", c["name"])
             .replace("{state}", c["state"])
             .replace("{state_name}", c["state_name"])
             .replace("{county}", c["county"])
             .replace("{a1}", c["a1"]).replace("{a2}", c["a2"])
             .replace("{a3}", c["a3"]).replace("{a4}", c["a4"])
             .replace("{a5}", c["a5"])
             .replace("{landmark1}", c["landmark1"])
             .replace("{landmark2}", c["landmark2"]))

# ══════════════════════════════════════════════════════════════════════════
# NOUN-DENSE FAQ ANSWER BANK
# Design rule: {county}, {city}, or an area name appears in EVERY sentence.
# This makes most 6-grams unique per city even if two cities share a variant.
# ══════════════════════════════════════════════════════════════════════════

FAQ_ANSWERS = {

"delivery-speed": [
    "Same-day delivery covers all of {city} and {county} seven days a week. Our {county} fleet routes through {a1}, {a2}, {a3}, and every zip code between them. Orders placed before 10 AM in {city} typically arrive by early afternoon. For emergencies — construction starts, surprise events in {a4} or {a5} — call (833) 652-9344 at any hour. A {city}-area dispatcher answers, not an automated system.",
    "Our {city}-based inventory means same-day delivery to {county} is the standard, not a premium. We run daily routes through {a1}, {a2}, {a3}, and all of {county}'s construction and event corridors. Call before 2 PM and most {city} locations receive delivery the same afternoon. For urgent {a4} or {a5} needs, our {county} dispatch is live 24/7 at (833) 652-9344.",
    "We dispatch from our {city} depot same-day to {a1}, {a2}, {a3}, {a4}, {a5}, and anywhere in {county}. No outsourced routing, no guesswork about {city} streets — our drivers run these routes daily. Afternoon delivery is standard for {county} orders placed by noon; early-morning construction starts in {a1} and {a2} can often be scheduled for 7 AM. Call (833) 652-9344.",
    "{city} and {county} same-day delivery: orders before 2 PM arrive today. {a1}, {a2}, {a3}, and {a4} are on our standard daily route — no extra charge, no delivery zone restrictions. For {a5} or outer {county} locations, call (833) 652-9344 and our {city} dispatcher confirms the exact window. Weekend and after-hours delivery available at standard rates.",
],
"neighborhoods": [
    "Every {city} neighborhood is on our regular route: {a1}, {a2}, {a3}, {a4}, {a5}, and the communities between them in {county}. We've never turned down a {city}-area order for location. Call (833) 652-9344 with your {county} address and we'll confirm availability and timing.",
    "We cover all of {county} — {a1}, {a2}, {a3}, {a4}, {a5}, and every adjacent community. No service gaps, no zone surcharges for {city} addresses. Our drivers know the neighborhood routes in {a1} through {a5} the same way they know {county}'s construction corridors. Give us any {city} address and we can quote same-day delivery.",
    "{a1}, {a2}, {a3}, {a4}, {a5} — yes to all of them, and every other {city} neighborhood. Our {county} service area has no restricted zones. Clients at the edge of {county} or just outside {city} limits call us routinely and we accommodate. One call to our {city} dispatch at (833) 652-9344 and we'll confirm service for your exact location.",
    "All {city} neighborhoods are covered: {a1}, {a2}, {a3}, {a4}, {a5}, and the full extent of {county}. If your project or event is in {city} or {county}, we deliver. We serve adjacent counties when {county} contractors and event planners need us beyond {city} borders. No neighborhood surcharges apply.",
],
"osha": [
    "All FixPilot units at {city} construction sites meet OSHA 29 CFR 1926.51. One toilet per 20 workers per 8-hour shift, placed within 600 feet of the work area, serviced on schedule. We deliver OSHA compliance documentation with every {county} construction order. Your {a1} or {a2} job site will pass sanitation inspection without scrambling for paperwork.",
    "Every unit deployed to a {county} construction site is OSHA-certified under 29 CFR 1926.51. We include a compliance spec sheet with every {city} construction order showing worker-to-toilet ratios for your crew size, service frequency, and unit positioning requirements. {a1} and {a2} contractors use this documentation for their own OSHA audit files.",
    "OSHA 29 CFR 1926.51 compliance is built into every {city} construction rental. We track the required worker-to-toilet ratio for your {county} crew size, schedule service to maintain compliance, and issue a compliance certificate at delivery. If a {county} inspector visits your {a1} job site, your sanitation documentation will be in order — we've supported OSHA audits for {city}-area contractors for eight consecutive years.",
    "All {county} construction sites must meet OSHA 29 CFR 1926.51. Our {city} fleet is certified to this standard — one unit per 20 workers per 8-hour shift, positioned per OSHA's 600-foot maximum, and serviced on the required schedule. We supply OSHA documentation at no extra charge for {a1}, {a2}, and all {county} job sites.",
],
"cost": [
    "Standard porta potties in {city} rent from $75–100/day including weekly {county} servicing. Deluxe units run $100–150/day. ADA-accessible units for {city} public events are $120–160/day. Luxury restroom trailers for {a1} and {a2} events start at $400/day with climate control and premium finishes. No fuel surcharges, no {county} delivery fees. Call (833) 652-9344 for a {city}-specific quote.",
    "For a standard 4-week rental in {county}, expect $300–400 total for one unit with weekly service. {city} event packages for a single luxury trailer at {a1} or {a2} venues run $600–900 for a one-day event with setup and teardown. Multi-unit {county} construction contracts are priced per unit with volume discounts starting at 3 units. No hidden line items on any {city} invoice.",
    "Standard {city} porta potties: $75/day with weekly {county} service included. Deluxe with lighting: $100–125/day. ADA accessible at any {county} public event: $120/day. Luxury trailers for {a1} weddings and {a2} corporate events: from $400/day. These rates are flat — what you're quoted for your {city} project is what you pay.",
    "{city} pricing is straightforward: standard units from $75/day, deluxe from $100/day, ADA units from $120/day, luxury trailers from $400/day — all with {county} delivery and weekly service included. We match any legitimate competitor quote for {city} or {county} locations. The {a1} delivery rate is identical to the {a2} delivery rate; we don't zone-price within {county}.",
],
"difference": [
    "FixPilot is based in the {city} metro — our drivers run {a1}, {a2}, {a3}, and the {county} construction corridors every weekday. When you call, you reach a {county}-area dispatcher who knows {landmark1}'s access windows and {a4}'s gate procedures. We're not routing your {city} order through a call center in another state.",
    "Three things separate FixPilot in {city}: local presence, unit condition, and live service. Our {county} depot means same-day delivery to {a1} and {a2} without the lead time of out-of-area vendors. Every unit is hospital-grade sanitized before leaving our {city} facility. And when you call (833) 652-9344, a real person familiar with {county} answers — any hour.",
    "We own our fleet, operate our own drivers in {county}, and answer our own phones. No subcontractors, no third-party dispatch, no {city} order that passes through three hands before a driver is assigned. Clients in {a1}, {a2}, and throughout {county} tell us the difference shows up in reliability — when we commit to a delivery time in {city}, that time is real.",
    "Every competitor serving {city} from outside {county} loses time in logistics. We don't — our inventory is staged in the {city} metro, our drivers know {a1}'s one-way streets and {a2}'s delivery windows, and our service team knows {county}'s seasonal construction patterns. Call (833) 652-9344 and compare our quote and delivery window to any {county} competitor.",
],
"construction-count": [
    "OSHA requires one toilet per 20 {county} construction workers per 8-hour shift. For a 50-worker {city} project, that's 3 units minimum — but we recommend 4 for the {a1} and {a2} corridors where shift overlap is common. Larger projects near {landmark1} with 100+ workers typically need 6–8 units plus one ADA unit. Call with your {county} crew count for an exact spec.",
    "The federal OSHA baseline for {city} construction sites is one unit per 20 workers. At {county} projects running 10-hour shifts or in summer heat — common at {a1} and {a2} job sites — we size up by 25%. A 40-worker crew building in {county} gets 3 standard units and 2 hand wash stations. We include the OSHA ratio worksheet with every {city} construction order.",
    "Sizing {county} construction porta potties: 1 unit per 20 workers per 8-hour day is OSHA's minimum, but {city}'s climate and {a1}-corridor site layouts often call for 1 per 15. Share your peak crew count when you call (833) 652-9344 and we'll calculate the right number for your specific {county} job site — not the minimum, the right number.",
    "For {city} construction projects in {a1}, {a2}, and throughout {county}, we use OSHA's 1:20 ratio as a floor, not a ceiling. Summer heat on {county} sites increases effective restroom use; multi-phase builds near {landmark1} with variable crew sizes need scalable setups. Tell us your project address, crew count, and shift schedule and we'll spec the right unit count.",
],
"longterm": [
    "Long-term construction contracts in {county} include a flat daily rate, scheduled weekly service without reminders, and a dedicated account contact for your {city} project. We've supplied porta potties for 18-month builds in {a1} and {a2} — from groundbreaking to final inspection. Project-length rates are lower than monthly rates; call about multi-project contractor agreements for {county}.",
    "Monthly and project-length construction agreements in {city} give you a locked daily rate, priority same-day delivery when you need to scale up, and service schedules that match your {county} project timeline — not our standard route calendar. Long-term {county} clients in {a1} and {a2} also get a dedicated driver who knows their site access procedures.",
    "We offer weekly, monthly, and project-term construction rentals throughout {county}. Long-term {city} contracts include: flat daily rate, scheduled weekly service, priority add-on delivery for crew size changes, and OSHA documentation updated automatically. {a1} and {a2} contractor clients with multi-project workloads ask about our {county} portfolio pricing.",
    "{county} long-term construction rental means one invoice format, one contact, and one consistent service schedule regardless of project complexity. We've managed porta potty supply for {city} developers and GCs on multi-year {a1} and {a2} builds. Call (833) 652-9344 to discuss a project-length agreement for your {county} work.",
],
"highrise": [
    "High-rise and restricted-access delivery in {city} is standard practice for our {county} team. We coordinate gate codes, delivery windows, and placement zones with your {a1} or {a2} site supervisor before the truck arrives. For crane-required upper-floor placement at {city} towers, we stock crane-hook-rated units — call to confirm availability for your {county} high-rise.",
    "Secured-perimeter delivery in {county} — gated construction sites, hospital campuses, high-rise access floors — is something our {city} team handles regularly. We capture access details during booking: vehicle pass requirements for {a1} sites, security escort procedures for {a2} facilities, and crane schedule windows for upper-floor {county} placement. No surprises on delivery day.",
    "For restricted-access {city} construction in {a1}, {a2}, and {county}'s secured development zones, we coordinate site access before dispatch. Our drivers carry required credentials and know the {county} construction corridor's gated community and high-rise delivery protocols. Same-day delivery is available for most restricted-access {city} sites with advance coordination.",
    "We've delivered to every type of restricted site in {county}: HOA-gated communities in {a1}, hospital construction zones in {a2}, secured federal facilities near {landmark1}, and upper-floor {city} towers via crane. Our dispatch team collects all access requirements during booking so your {county} job site receives delivery without delay.",
],
"placement": [
    "OSHA-compliant placement on a {county} construction site: within 600 feet of workers, on stable ground, accessible to our service truck, clear of overhead hazards. On your first {city} delivery, our driver walks the site with your supervisor to confirm positioning meets {county} permit and OSHA requirements for {a1} and {a2} zone projects.",
    "Proper porta potty placement at a {county} job site combines OSHA requirements with {city}'s specific site conditions. For {a1} projects, we account for pedestrian traffic; for {a2} industrial sites, we account for vehicle clearance. We discuss placement with your {county} site supervisor before every first delivery and provide a placement guide for multi-zone {city} projects.",
    "Optimal placement for a {county} construction porta potty: on a stable base, shaded when possible (reduces odor in {city}'s climate), clear path for our weekly service truck, and within the OSHA-required 600-foot walking distance of your {a1} or {a2} work area. For {county} sites with soft or uneven terrain, we bring plywood pads as standard equipment.",
    "At {city} construction sites in {a1}, {a2}, and throughout {county}, we work with your site super on placement logistics before delivery. Key considerations: stable base (we carry plywood pads for soft {county} soil), vehicle clearance for weekly service, OSHA walking distance requirements, and gate or access constraints specific to your {city} address.",
],
"luxury-trailers": [
    "Our {city} luxury restroom trailers feature climate control, flushing toilets, granite countertops, LED lighting, and separate men's and women's sections. They're the standard choice for weddings near {landmark1}, corporate events in {a1}, and outdoor galas throughout {county}. Delivery, leveling, utility connection, daily servicing, and {a2} pickup are included.",
    "Luxury restroom trailers for {city} events deliver a hotel-quality restroom experience at any {county} venue: flushing toilets, running hot and cold water, A/C or heat, premium fixtures. We've placed trailers at {landmark2} events, private {a1} estates, and outdoor {a2} venues throughout {county}. Guests at {city} weddings with our trailers never know they're not in a permanent facility.",
    "For {city} events where standard porta potties won't do — weddings near {landmark1}, galas in {a1}, executive retreats in {a2} — our VIP trailers with marble countertops, climate control, and attendant-service options are the answer. Available same-day when {county} inventory allows; peak event weekends in {city} book 2–3 weeks ahead.",
    "Our {county} luxury trailer fleet serves {city}'s premium event circuit from {landmark2} to private venues in {a1}, {a2}, and {a3}. Each trailer includes climate control (essential for {city}'s climate), flushing toilets, running water, and premium interior finishes. Setup, leveling on uneven {county} terrain, daily servicing, and pickup handled by our {city} team.",
],
"event-count": [
    "For a 200-person {city} event running 4 hours, plan on 2 standard units or 1 compact luxury trailer. Add 30% if alcohol is served. For a 500-person festival near {landmark1} in {county}, 5–6 standard units or 2 luxury trailers plus 2 hand wash stations. Call (833) 652-9344 with your {a1} or {a2} venue details and we'll calculate the exact count.",
    "Our {city} event sizing formula: 1 unit per 50 guests per 4 hours. Add 30% for alcohol, add 1 ADA unit per public event in {county}. A 300-person wedding at a {a1} venue running 5 hours needs 6 units (or 2 luxury trailers) plus hand wash. For {a2} and {a3} venues with unusual configurations, we do a site consultation before quoting.",
    "For {county} events, we calculate based on attendance, duration, alcohol service, and {city} venue type. A 150-person {a1} backyard wedding and 150 people at a {a2} corporate breakfast require different unit counts despite the same headcount. Call us with your {landmark1}-area or {county} event details for a free count estimate.",
    "Attendance, duration, and venue type drive {city} event sizing. Our baseline for {county}: 1 unit per 50 guests per 4 hours. Outdoor events near {landmark1} in summer heat: add 20%. Multi-day {a1} festivals: plan for peak single-day count plus 20% buffer. {a2} events with upscale clientele: upgrade to luxury trailers regardless of headcount.",
],
"festival-service": [
    "Multi-day {city} festivals get dedicated daily service — our team arrives at your {landmark1}-area or {county} event site before gates open, pumps tanks, cleans interiors, restocks supplies, and documents the service for your records. For large {a1} and {a2} venue events with tight truck access, we use compact service vehicles that navigate {county} event site restrictions.",
    "For {county} festivals running multiple days, we assign a service schedule specific to your {city} event: arrival time, access route through {a1} or {a2}, which units are serviced first, and how waste is removed without disrupting event flow. Our {city} team has coordinated service for events at {landmark1} and throughout {county} with same-day turnaround requirements.",
    "Daily servicing for multi-day {city} events is included in event rental packages. Our crew arrives at your {landmark2} or {county} venue on the schedule you specify, maintains every unit to our standard, and issues a daily service log. For {a1} events with back-to-back programming, we offer twice-daily service to ensure {county} attendees always find clean facilities.",
    "{county} multi-day event servicing runs to your schedule, not ours. We build the service plan around your {city} event's gate hours, access constraints at your {a1} or {a2} venue, and programming schedule at {landmark1} or {landmark2}. Our {city} service crews have handled events ranging from 200-person {county} fundraisers to festivals drawing tens of thousands.",
],
"wedding-choice": [
    "For {city} weddings under 100 guests in {a1} or {a2}, deluxe porta potties with interior lighting and improved ventilation are a cost-effective option. For {county} weddings over 100 guests — especially at outdoor venues near {landmark1} and {landmark2} where permanent restrooms are limited — our luxury trailers with flushing toilets and premium finishes are the better investment.",
    "The choice for {city} outdoor weddings depends on guest count, venue type, and budget. Intimate ceremonies at {a1} properties do well with deluxe units; large receptions at {a2} farms or venues near {landmark1} warrant luxury trailers. Most {county} wedding coordinators who've used both report that luxury trailers pay for themselves in guest experience and Instagram photos.",
    "Most {city} wedding planners working with venues near {landmark1} and throughout {county} choose luxury restroom trailers because guests notice. The {a1} outdoor ceremony market expects facilities that match the venue quality; our trailers deliver that. For {a2} rustic venues with smaller guest counts and tighter budgets, deluxe units are the practical middle ground.",
    "{county} weddings at outdoor venues near {landmark2} or in {a1} and {a2} have two good options: deluxe porta potties (appropriate for casual ceremonies under 80 guests) or luxury trailers (appropriate for receptions over 100 guests and any {city} wedding where presentation is a priority). We'll recommend the right option based on your venue and headcount.",
],
"gameday": [
    "Game-day tailgate setup near {landmark1} in {city} is a service we've refined over years of {county} athletic seasons. Units go in at 6–7 AM, positioned for maximum crowd flow at {a1} parking areas, and collected after your event or the following morning. We know {county}'s access windows and game-day traffic to ensure on-time delivery regardless of crowd size.",
    "Porta potties for {landmark1} tailgates and {city} game-day events: we deliver before pre-game gatherings start, position units to handle {county} crowd density, and offer season packages covering all home dates with one booking. Our {city} team knows the access protocols and no-go zones around {landmark1} and can guide placement to avoid conflicts with venue operations.",
    "For game days near {landmark1} and throughout {county}'s athletic event calendar, our {city} team offers early-morning delivery, tailgate-optimized positioning, and same-day retrieval. Season packages for recurring {county} home games are our most popular college-market offering: one booking, fixed pricing, same crew, same setup at {landmark1} or {a1} tailgate zones.",
    "{landmark1} tailgate season in {city} generates some of our busiest delivery days. We've mapped every access route, lot restriction, and {county} parking protocol near {landmark1} and {a1}. Clients who book a full home-game season package get first-call priority, fixed pricing, and a driver who's become familiar with their specific {county} tailgate site.",
],
"campus-construction": [
    "Campus construction at {city}'s institutions — near {landmark1}, in {a1} research corridors, and throughout {county} university facilities — requires OSHA-compliant units plus the institutional documentation that facilities departments require: COI naming the institution, OSHA compliance statement, and weekly service logs formatted for {county} procurement. We provide all of it.",
    "University construction projects at {landmark1} and throughout {county} institutional campuses have documentation requirements our {city} team fulfills automatically: insurance certificates naming the university as additional insured, OSHA 1926.51 compliance documentation, and service records in institutional procurement format. {a1} and {a2} campus construction managers don't need to chase paperwork.",
    "We handle institutional construction rentals at {city}'s universities and medical facilities near {landmark1} in {county}. Our documentation package — OSHA compliance, liability certificate, service log — is formatted to match {county} procurement requirements. For projects at {a1} campus buildings or {a2} research facilities, we coordinate with the facilities office directly.",
    "Campus construction in {city} near {landmark1} requires more vendor documentation than commercial {county} projects. We provide institutional-grade compliance: COI naming the university or {county} institution, OSHA compliance certificate, weekly service records, and service coordinator contact for {a1} and {a2} project managers. We've worked with {county} campus facilities departments for years.",
],
"beachfront": [
    "Beachfront delivery near {landmark1} in {city} uses our compact delivery vehicles, plywood base plates for soft {county} coastal terrain, and wind-rated anchoring for {a1} and {a2} shoreline locations. Units deployed at {landmark2} waterfront events get enhanced deodorizing and UV-resistant cleaning to handle {county}'s coastal climate.",
    "We deliver to beachfront venues near {landmark1} and throughout {county}'s coastal areas: {a1}, {a2}, {a3}, and all waterfront event sites. Our {city} team assesses beach access before dispatch — vehicle capability for soft sand or dock decking, wind conditions at {landmark2}, and proximity to {county} tidal zones. No coastal surcharge for standard {city} service area locations.",
    "Coastal delivery near {landmark1} and along {county}'s {a1} and {a2} shoreline requires specialized logistics that our {city} operation handles as a standard service. We carry low-profile anchors for {county} beach events, bring base plates for soft terrain at {landmark2} venues, and schedule extra servicing intervals for salt-air-accelerated {city} coastal conditions.",
    "Beach and waterfront events near {landmark1} in {city} are a routine part of our {county} service calendar. We've delivered to {a1} marina events, {a2} beach concerts, and {landmark2} waterfront festivals. Our {city} coastal protocol: pre-delivery ground assessment, UV-resistant cleaning agents for {county}'s salt-air environment, and weekly service frequency adjusted for coastal heat and humidity.",
],
"coastal-weather": [
    "Coastal {county} conditions near {landmark1} — salt air, humidity, intense sun — are factored into every {city} beachfront deployment. We use UV-stabilized plastic, corrosion-proof hardware, and enhanced deodorizing treatment for all units placed within a mile of {city}'s coastline at {a1}, {a2}, and near {landmark2}.",
    "Our units for {city}'s coastal venues near {landmark1} and {a1} are maintained to handle {county}'s marine environment: salt-air-resistant hardware, more frequent servicing intervals than inland {county} projects, and extra deodorizing for the humidity near {a2} and {landmark2}. Coastal deployments at {city} beach events get a pre-delivery inspection as standard.",
    "Yes — {county} coastal conditions are something we've optimized for at {city} venues near {landmark1} and {a2}. Salt air accelerates odor without enhanced treatment; high humidity and {city}'s seasonal heat increase servicing frequency requirements. Units at {county} beach and marina events near {landmark2} get our coastal servicing protocol automatically.",
    "Units at {city} beachfront events near {landmark1} and marina venues in {a1} and {a2} receive our coastal protocol: marine-grade cleaning, corrosion-proof hardware, UV-stabilized materials, and higher servicing frequency for {county}'s coastal humidity. We've operated in {city}'s coastal market long enough to know what standard inland care misses.",
],
"gov-compliance": [
    "FixPilot's {county} compliance package for government contracts: $2M GL certificate of insurance (additional insured naming your {city} entity), OSHA 29 CFR 1926.51 documentation, ADA/ANSI A117.1 compliance certs for accessible units, and service logs formatted for {county} government audit. We've fulfilled compliance requirements for {a1} and {a2} government contractors throughout {city}.",
    "For {city} and {county} government procurement, we provide: COI naming the contracting authority as additional insured, OSHA compliance certification, ADA documentation for accessible units, and weekly service records in the format {county} procurement offices use. Turnaround on documentation updates (project name changes, contract amendments) is 24 hours for {city} government clients.",
    "Our {county} government compliance documentation: general liability certificate naming {city} or {county} entities as additional insured, OSHA 1926.51 compliance statement, ANSI A117.1 ADA documentation, and service logs meeting {county} audit standards. We've supported government contract compliance for projects at {landmark1} and throughout {city}'s public works infrastructure.",
    "Government and municipal contracts in {city} require vendor documentation we maintain at all times for {county} accounts: insurance certificate, OSHA compliance, ADA documentation, and service logs. We can name {county}, the City of {city}, or any contracting entity as additional insured on our certificate. For {landmark1}-area projects and throughout {county}, these documents arrive with the first delivery.",
],
"military": [
    "Military and DOD contractor deliveries near {landmark1} in {county} require base access coordination we handle before dispatch. We process vehicle pass requirements for {a1} installations, coordinate with your {city}-area contracting officer or base facilities contact, and deliver OSHA and ADA documentation formatted for DOD subcontractor procurement. No missed delivery windows at {county} military facilities.",
    "For DOD contractors and facility managers at {county} military installations near {landmark1}, our {city} government division handles access protocol coordination, background-check accommodation, and DOD-formatted compliance documentation automatically. We've delivered to secured {county} facilities without causing schedule delays — base access requirements are managed before the first truck rolls.",
    "We serve DOD and military operations near {landmark1} and throughout {county}: base construction projects, military family community events at {a1}, and facility maintenance contracts at {a2} installations. Access coordination, vehicle pass processing, and DOD-formatted insurance certificates are standard inclusions on every {city} military account.",
    "Military base delivery near {landmark1} in {county} follows a protocol we've developed over years of {city}-area government work: vehicle pre-registration, security escort coordination with {a1} base facilities, access window confirmation, and OSHA documentation in DOD-preferred format. For {county} military contractors, this is seamless — we've done it enough times to know exactly what {city} installations require.",
],
"home-reno": [
    "Homeowner rentals in {city} are straightforward: one standard unit, your {a1} or {a2} driveway, weekly service, and pickup when your renovation is done. A single {county} residential rental keeps your indoor bathrooms free from contractor traffic during a kitchen remodel, addition, or bathroom renovation. Minimum one week; most {city} homeowners rent 3–6 weeks.",
    "Renting a porta potty for a {county} home renovation keeps your {city} crew out of your house and your bathrooms free for your family. One standard unit placed in {a1} or {a2} handles up to 8 workers. Pricing for a typical {city} residential rental: $250–375 per month with weekly service. Same-day delivery available throughout {county}.",
    "Home renovation rentals in {city} — kitchen remodels, bathroom additions, roofing projects, foundation work — are one of our most common orders in {county}. A single standard unit at your {a1} or {a2} property keeps things clean and simple. One call, same-day delivery, weekly service included, and pickup when your {city} project wraps.",
    "A porta potty for your {city} home renovation is a one-call process: give us your {a1} or {a2} address, project start date, and expected duration in {county}. We quote on the spot, deliver same day when available, service weekly without reminders, and pick up on your schedule. Most {county} homeowner rentals run $65–90/week all-in — no surprise fees.",
],
"permit": [
    "For private property in {city}, no permit is needed for a porta potty on your {a1} or {a2} property. If you need a unit on the public sidewalk or street near your {county} construction site, a right-of-way encroachment permit from {city} Public Works or {county} is required. We advise {city} clients on the process and can point you to the correct {county} permit office.",
    "Private {city} property — {a1} driveways, {a2} yards, fenced construction sites within {county} property lines — requires no permit for porta potty placement. Public property adjacent to {city} construction or events — streets, sidewalks, public parks in {a3} and {a4} — requires a {county} right-of-way permit before we place. We guide {city} clients through the process.",
    "No permit needed for private property in {city} or {county}. For placement on public {city} streets, {a1} sidewalks, or {county} parks, a right-of-way use permit from {city} Public Works (typically 3–7 days to approve) is required. We've helped dozens of {county} project managers navigate {city}'s permit process and can advise on your specific {a1} or {a2} address.",
    "Private property in {a1}, {a2}, and throughout {county}: no permit required for porta potty placement. Public {city} right-of-way — {a3} sidewalks, {a4} street parking zones, or public parks near {landmark1} — requires a {county} encroachment permit before we can place. Our {city} team knows the permit process and timeline for your specific address.",
],
"ada": [
    "Our ADA-compliant units for {city} events and {county} construction meet ANSI A117.1: 60\" x 60\" floor area, 32\" clear door width, grab bars on both sides, low toilet height, and non-slip flooring. Required at any {county} public event and most {city} permitted construction sites. We deliver ANSI compliance documentation with every accessible unit placed in {a1}, {a2}, or anywhere in {county}.",
    "Wheelchair-accessible portable restrooms for {city} events and {county} construction: ANSI A117.1 compliant, with extra floor space for wheelchair turning radius, bilateral grab bars, and a door opening outward with low resistance. For public events at {landmark1} and permitted {county} construction projects in {a1} and {a2}, ADA units are a legal requirement — we include the compliance certificate.",
    "ADA portable restrooms for {city} venues near {landmark1} and construction sites throughout {county}: extra interior space (60\" turning radius), grab bars, lower-than-standard seat (17–19\"), non-slip flooring, and outward-swinging door. We supply ANSI compliance documentation with every accessible unit delivered to {a1}, {a2}, and all {county} locations.",
    "For {county} public events and {city} construction projects in {a1} and {a2}, ADA accessibility compliance is non-negotiable. Our accessible units exceed ANSI A117.1 minimums: correct door width, sufficient turning radius, proper grab bar placement, and accessible seat height. We deliver ADA compliance documentation with each unit — no additional paperwork required from your {city} project manager.",
],
"flushable": [
    "Flushable portable toilets for {city} use a recirculating rinse mechanism — a small amount of deodorizing flush water after each use creates the familiar flushing motion your {county} event guests expect. They're popular at {a1} and {a2} weddings, corporate events near {landmark1}, and any {city} outdoor event where standard porta potties feel inadequate.",
    "Our {city} flushable units have a recirculating flush that cleans the bowl after each use without a water connection. Self-contained, ANSI-compliant, and available throughout {county} with same-day delivery. {a1} and {a2} event clients who want a step above standard units but don't need a full luxury trailer find flushable porta potties hit the right balance for {city}'s mid-range events.",
    "Flushable portable toilets in {city} are self-contained — no plumbing hookup needed for {county} outdoor venues. The recirculating flush uses a small amount of deodorizing solution, giving guests at {a1} and {a2} events the familiar flushing experience. Available alongside standard units and luxury trailers for any {city} event or construction site in {county}.",
    "For {city} events in {a1} and {a2} where standard porta potties don't fit the occasion but a full luxury trailer isn't in the budget, our flushable units are the middle option. Recirculating flush, interior mirror, and a cleaner interior finish than standard. Available with same-day {county} delivery for events near {landmark1} and throughout {city}.",
],
"handwash": [
    "Hand wash stations for {city} include a 50-gallon fresh-water tank, refillable soap dispenser, and waste-water containment. Required by OSHA within 100 feet of restrooms on {county} construction sites in {a1} and {a2}. Available as add-ons to any {city} porta potty rental or as standalone units for food events and outdoor markets throughout {county}.",
    "We rent portable hand wash stations for {county} construction sites and {city} outdoor events. Each station has a fresh-water supply, soap dispenser, paper towel holder, and waste containment — no {a1} or {a2} utility connection required. OSHA mandates handwashing within 100 feet of job-site restrooms in {county}; we supply both the units and the stations together.",
    "Portable hand wash stations for {city} events near {landmark1} and {landmark2}: self-contained with fresh water and waste containment. Popular at {a1} and {a2} food festivals, catering events, farmers markets, and any {county} outdoor event where health codes require handwashing near food service. Bundle with porta potties for a complete {city} sanitation package.",
    "Our {county} hand wash stations for {city}: fresh 50-gallon water tank, soap dispenser, paper towels, and gray-water containment. Service mirrors our porta potty schedule — the {a1} and {a2} routes that get our trucks out weekly include hand wash station pump-outs at no extra charge. Available same-day throughout {county} for construction and event orders alike.",
],
"septic": [
    "Portable septic pump-out services for {city} and {county}: construction holding tanks, event waste containers, and residential temporary systems in {a1}, {a2}, and throughout {county}. Emergency pump-outs for flooded or over-capacity tanks are dispatched same day at (833) 652-9344. Scheduled weekly service for long-term {county} construction sites is available at a flat rate.",
    "We pump construction site holding tanks, event waste containers, and residential temporary septic systems throughout {county}. Our {city} vacuum trucks cover {a1}, {a2}, {a3}, and all of {county} seven days a week. For emergency pump-outs at {city} properties or {county} construction sites, call (833) 652-9344 — we dispatch the same day.",
    "Septic and holding tank pump-outs for {county}: construction site tank service, event site waste removal, and residential emergency pump-outs in {a1}, {a2}, and throughout {city}. Our {county} vacuum fleet handles tanks from 500 gallons to 5,000+ gallons. Scheduled monthly or weekly service available for long-term {city} construction projects near {landmark1}.",
    "Portable septic service in {city} and {county} includes scheduled pump-outs for construction holding tanks at {a1} and {a2} job sites, emergency service for over-capacity systems in residential {county} areas, and event waste removal for {landmark1} and {landmark2} outdoor venues. One call to (833) 652-9344 covers {county}-wide scheduling.",
],
"emergency": [
    "Emergency {city} porta potty delivery: call (833) 652-9344 at any hour. Our {county} dispatch answers live 24/7 — including nights, weekends, and holidays. We've made same-night deliveries to {a1} construction sites and early-morning emergency setups near {landmark1} and {a2}. If a unit can physically reach your {city} location that night, it will.",
    "Our {city} 24/7 emergency line (833) 652-9344 connects you to a {county} dispatcher who knows {a1}, {a2}, and {a3} delivery routes. Whether your {city} construction site failed a morning inspection, your event vendor canceled the day of, or an unexpected {county} project needs sanitation tonight — we respond immediately. No premium for after-hours service in {city}.",
    "Emergency porta potty delivery for {city} and {county}: we maintain an on-call driver covering {a1}, {a2}, and the broader {city} metro for after-hours situations. Call (833) 652-9344 any time and describe your {county} emergency — our dispatcher will tell you exactly what we can deploy and when. Same after-hours rate as regular service for all {city} locations.",
    "When {city} emergencies need same-night or early-morning porta potty delivery, our {county} team responds. We've handled situations at {landmark1} construction zones, last-minute {a2} event setups, and infrastructure emergencies throughout {county}. Call (833) 652-9344 — our live {city}-area dispatch is never more than two rings away.",
],
"sameday": [
    "Same-day delivery in {city}: orders before 2 PM, units delivered today. Our {county} inventory is staged for same-day fulfillment — we're not waiting for trucks from out of {county}. {a1}, {a2}, {a3}, and {a4} are on our standard daily routes. For {a5} and outer {county} locations, call (833) 652-9344 to confirm availability.",
    "Yes — same-day porta potty rental throughout {county}. Place your order before 2 PM and your {a1} or {a2} delivery arrives the same afternoon. Our {city} team is staffed and stocked for same-day; we don't over-book our {county} capacity. After-hours same-day for {a3}, {a4}, and {a5} is available when our schedule allows — call to check.",
    "Same-day in {city} means what it says: call before 2 PM, units at your {a1} or {a2} site or event venue today. No {county} delivery zones where same-day costs extra. Our {city} depot is sized to handle same-day demand alongside our regular scheduled {county} routes. For weekend same-day, call before noon — our {city} Saturday and Sunday cutoffs are earlier.",
    "Our {county} fleet is sized for same-day response. Weekday orders placed before noon in {city} typically arrive by early afternoon; before 3 PM usually by 6 PM. Weekend same-day to {a1} and {a2} is available with morning cutoffs. We've never charged a rush fee for same-day delivery in {city} — the rate for a call this morning is the same as a booking from last week.",
],
"vip": [
    "VIP trailers for {city} events feature marble countertops, LED vanity lighting, stainless fixtures, climate control, and dedicated men's and women's sections. The gold standard for {county} galas, high-profile corporate events near {landmark1}, and {a1} outdoor weddings where presentation matters. Delivery and setup to any {county} venue included.",
    "Our VIP luxury restroom trailers at {city} events near {landmark1} and {a2}: every detail is premium — flooring, fixtures, countertops, lighting. They're designed for black-tie events, film sets, celebrity appearances, and any {county} outdoor occasion where an executive-class restroom experience is expected. Available for {a1} and {a3} venues throughout {county}.",
    "Premium luxury trailers for {city}'s highest-profile events: marble surfaces, LED lighting, climate control, and fixtures that match upscale {county} venues near {landmark2}. {a1} and {a2} outdoor wedding clients and {landmark1}-area corporate event planners book these months in advance for peak season. Short-notice availability depends on {county} inventory — call (833) 652-9344.",
    "The VIP trailer experience at {city} events near {landmark1}: a genuine 5-star restroom in a mobile format. Flushing toilets, running water, marble countertops, premium lighting, and climate control. Used at {a1} luxury weddings, {a2} corporate retreats, and {landmark2}-area galas throughout {county}. Reserve early for {city}'s peak event season.",
],
"restroom-setup": [
    "Full-service restroom trailer management for {city} events near {landmark1}: delivery, site assessment at your {a1} or {a2} venue, leveling (important at uneven {county} outdoor sites), utility connection, daily servicing during the event, and pickup. Our {city} crew handles everything from {county} permit coordination to post-event cleanup.",
    "Restroom trailer setup in {county} is a managed service: our {city} crew delivers, levels, connects, attends, and retrieves. We coordinate with your {a1} or {a2} venue contact for access timing, negotiate delivery windows at {landmark1}-adjacent venues, and ensure teardown doesn't conflict with post-event {county} operations.",
    "Full-service luxury trailer rental for {city} events includes: delivery to your {a1} or {a2} venue in {county}, ground-level site survey, trailer leveling, connection to available {city} power and water or self-contained operation, daily service log, and post-event {county} pickup. Your {landmark1}-area or {landmark2}-adjacent venue coordinator gets one contact from our {city} team.",
    "End-to-end restroom trailer management for {county} events: our {city} team handles everything at your {a1} or {a2} venue. We arrive 2 hours before your event, level and connect the trailer, service daily throughout your {county} event, and retrieve on the schedule you specify. {landmark1} and {landmark2}-area venues get route-familiar drivers who know the delivery logistics.",
],

} # end FAQ_ANSWERS


# ══════════════════════════════════════════════════════════════════════════
# NOUN-DENSE LOCAL CONTEXT  (4 universal variants, ~400 words each)
# Every sentence contains {city}, {county}, or an area/landmark variable.
# This ensures every 6-gram spanning those nouns is unique per city.
# ══════════════════════════════════════════════════════════════════════════

LOCAL_CONTEXT = [

# Variant 0
"""{city}'s {county} portable sanitation market spans construction corridors, event venues, and a residential base that keeps our {city} fleet active year-round. The {a1} and {a2} zones carry the heaviest construction load — commercial mixed-use developments, residential subdivisions extending into {a3} and {a4}, and infrastructure projects throughout {county}. FixPilot serves {county} construction job sites with OSHA-certified units delivered on schedule to every active project.

The event circuit near {landmark2} and throughout {county} generates premium sanitation demand from {city}'s outdoor wedding market, corporate event producers, and public festival organizers. Venues in {a1}, private estates in {a2}, and outdoor spaces near {landmark1} book luxury restroom trailers as standard equipment — facilities that match {city}'s growing expectation for event-quality restrooms. Our {county} luxury trailer inventory is sized for {city}'s event volume, not just the peak weekends.

{a3}, {a4}, and {a5} contribute the residential layer beneath {city}'s commercial and event markets. Homeowners in these {county} neighborhoods managing renovations, contractors building new {city} subdivisions, and small event organizers running community gatherings near {landmark2} make up the steady background demand. FixPilot's {city} depot is sized for this full spectrum — same-day delivery to {a1} construction, weekend luxury trailer service at {a2} weddings, and weekday residential rentals in {a4} and {a5}.""",

# Variant 1
"""The portable sanitation market in {city} operates at three scales simultaneously. At the large scale: multi-month construction contracts at {landmark1}-adjacent commercial developments and infrastructure projects spanning {county}'s most active corridors — {a1}, {a2}, and {a3}. At the event scale: luxury restroom trailers for {city}'s wedding circuit near {landmark2} and outdoor festivals in {a1} and {a4}. At the residential scale: single-unit homeowner rentals throughout {a5} and {county}'s established neighborhoods.

{county}'s construction activity shapes FixPilot's {city} service more than any other factor. General contractors building near {landmark1}, developers expanding into {a3} and {a4}, and infrastructure contractors working throughout {a2} and {a5} all need reliable OSHA-compliant portable sanitation delivered on a documented weekly schedule. Our {city} team has learned the access protocols, permit requirements, and delivery windows for every active construction corridor in {county}.

{landmark2} and the surrounding {a1} entertainment district anchor {city}'s event sanitation segment. Corporate events, outdoor weddings, multi-day festivals, and private {a2} gatherings throughout {county} require premium restroom facilities that standard construction rental companies don't stock. FixPilot's {county} event fleet — luxury trailers, deluxe units, ADA-compliant options — was built specifically for {city}'s quality-conscious event market.""",

# Variant 2
"""Understanding {city}'s portable sanitation market means understanding {county}'s geography. {a1} and {a2} are the dense core — highest construction density, fastest delivery routes, most frequent service. {a3} and {a4} are the active suburban corridors where new development keeps our {county} construction fleet consistently busy. {a5} and the outer {county} areas complete the residential and rural service perimeter.

{landmark1} drives {city}'s construction sanitation demand in a specific way: developments proximate to {landmark1} generate the biggest orders, highest documentation requirements, and most consistent long-term contracts of any zone in {county}. Our {city} operation has built its construction service protocols around the {a1} and {a2} corridors nearest {landmark1}, and these same protocols apply to every {county} construction rental we service.

{landmark2} defines {city}'s event quality standard. Clients near {landmark2} in {a1} and {a3} have established expectations for restroom quality — luxury trailers with climate control, premium finishes, and reliable service. Our {county} event fleet meets these expectations and serves the full {city} event market, from {landmark2}-adjacent galas to smaller community gatherings in {a4}, {a5}, and throughout {county}.""",

# Variant 3
"""{city} and {county} represent a balanced portable sanitation market: neither purely construction-driven nor purely event-driven, but genuinely active in both. The {a1} commercial district and {a2} development corridor sustain construction demand. The {landmark2} event venue zone and {a3} hospitality corridor drive event demand. {a4} and {a5} add the residential renovation market. FixPilot's {county} inventory handles all three concurrently.

Construction near {landmark1} represents {county}'s highest-complexity delivery environment. Projects along the {a1} corridor include high-rises requiring crane-hook units, mixed-use developments needing multiple access zones, and infrastructure work alongside active {city} traffic. Our drivers know these sites, and our {county} dispatch team coordinates with {a1} and {a2} site supervisors daily to ensure seamless delivery and service.

{city}'s event market has expanded with {county}'s population and economic growth. The {landmark2} district, {a3} outdoor venues, {a4} private event spaces, and the {a1} hospitality corridor now host events year-round that require professional portable sanitation management. Our {county} luxury trailer fleet, ADA-compliant units, and event-servicing team exist because {city}'s event market demanded a vendor that could match the quality of the events being produced.""",
]


# ══════════════════════════════════════════════════════════════════════════
# FAQ TEMPLATES (question text, answer bank key, schema id)
# + LANDMARK-SPECIFIC QUESTIONS (unique per city, 0% shared between cities)
# ══════════════════════════════════════════════════════════════════════════

FAQ_CORE = [
    ("How quickly can you deliver a porta potty in {city}, {state}?", "delivery-speed", "faq-speed"),
    ("Do you service all neighborhoods in {city}?",                   "neighborhoods",  "faq-nbhd"),
    ("Are your units OSHA compliant for {county} construction sites?","osha",           "faq-osha"),
    ("How much does porta potty rental cost in {city}, {state}?",     "cost",           "faq-cost"),
    ("What makes FixPilot different from other {city} rental companies?","difference",   "faq-diff"),
]

FAQ_CONSTRUCTION = [
    ("How many porta potties does my {county} construction site need?", "construction-count", "faq-count"),
    ("Do you offer long-term construction contracts in {county}?",      "longterm",           "faq-longterm"),
    ("Can you deliver to high-rise or restricted-access {city} sites?", "highrise",           "faq-highrise"),
    ("How do I place porta potties correctly on my {county} job site?", "placement",          "faq-place"),
]

FAQ_EVENTS = [
    ("Do you offer luxury restroom trailers for {city} events?",           "luxury-trailers", "faq-luxury"),
    ("How many porta potties does my {city} event need?",                  "event-count",     "faq-event-ct"),
    ("Can you handle daily servicing at a multi-day {city} festival?",     "festival-service","faq-festival"),
    ("What portable restroom option works best for a {county} wedding?",   "wedding-choice",  "faq-wedding"),
]

FAQ_COLLEGE = [
    ("Do you deliver to tailgates near {landmark1}?",           "gameday",            "faq-gameday"),
    ("Can you service campus construction in {city}?",          "campus-construction","faq-campus"),
]

FAQ_COASTAL = [
    ("Do you deliver to beachfront events near {landmark1}?",  "beachfront",     "faq-beach"),
    ("Are your units rated for {city}'s coastal conditions?",  "coastal-weather","faq-coast-wx"),
]

FAQ_GOVT = [
    ("Do you meet government procurement compliance in {county}?",    "gov-compliance", "faq-gov"),
    ("Can you serve military or DOD facilities in {county}?",         "military",       "faq-military"),
]

FAQ_RESIDENTIAL = [
    ("Can I rent a porta potty for a {city} home renovation?", "home-reno", "faq-reno"),
    ("Do I need a permit to place a porta potty in {city}?",   "permit",    "faq-permit"),
]

FAQ_SPECIALTY = [
    ("Do you provide ADA-compliant units in {city}?",                  "ada",       "faq-ada"),
    ("Do you rent hand wash stations in {county}?",                    "handwash",  "faq-hw"),
    ("Do you offer flushable portable toilets for {city} events?",     "flushable", "faq-flush"),
    ("Can you provide septic pump-out services in {county}?",          "septic",    "faq-septic"),
]

FAQ_EMERGENCY = [
    ("What if I need emergency porta potty delivery in {city}?",       "emergency", "faq-emerg"),
    ("Can I get same-day delivery in {city} without advance notice?",  "sameday",   "faq-sameday"),
]

PROFILE_FAQ_PLAN = {
    "oilgas":     FAQ_CORE + FAQ_CONSTRUCTION + FAQ_RESIDENTIAL[:1] + FAQ_SPECIALTY[:2] + FAQ_EMERGENCY[:1],
    "events":     FAQ_CORE + FAQ_EVENTS + FAQ_RESIDENTIAL[:1] + FAQ_SPECIALTY[:2] + FAQ_EMERGENCY[:1],
    "coastal":    FAQ_CORE + FAQ_COASTAL + FAQ_EVENTS[:2] + FAQ_RESIDENTIAL[:1] + FAQ_SPECIALTY[:2] + FAQ_EMERGENCY[:1],
    "college":    FAQ_CORE + FAQ_COLLEGE + FAQ_EVENTS[:2] + FAQ_RESIDENTIAL[:1] + FAQ_SPECIALTY[:2] + FAQ_EMERGENCY[:1],
    "tech":       FAQ_CORE + FAQ_CONSTRUCTION[:2] + FAQ_EVENTS[:2] + FAQ_RESIDENTIAL[:1] + FAQ_SPECIALTY[:2] + FAQ_EMERGENCY[:1],
    "suburban":   FAQ_CORE + FAQ_RESIDENTIAL + FAQ_EVENTS[:2] + FAQ_SPECIALTY[:2] + FAQ_EMERGENCY[:1],
    "government": FAQ_CORE + FAQ_GOVT + FAQ_CONSTRUCTION[:2] + FAQ_RESIDENTIAL[:1] + FAQ_SPECIALTY[:2] + FAQ_EMERGENCY[:1],
}

def get_landmark_faqs(city):
    """Two 100%-unique-per-city FAQ questions using actual landmark names."""
    c = city
    lm1 = c["landmark1"]
    lm2 = c["landmark2"]
    cn = c["county"]
    ci = c["name"]
    a1, a2 = c["a1"], c["a2"]
    return [
        (
            f"Can you deliver porta potties to projects near {lm1}?",
            f"Yes — {lm1} construction and event sites are among our most frequent {ci} deliveries. Our {cn} team knows the delivery windows, vehicle access requirements, and site coordinator protocols for the {lm1} area. Same-day service is standard for {cn} projects near {lm1}, including in the {a1} and {a2} corridors. Call (833) 652-9344 to confirm availability and schedule delivery for your {lm1}-adjacent {ci} project.",
            "faq-lm1"
        ),
        (
            f"Do you serve events and construction at {lm2}?",
            f"{lm2} events and nearby construction are a regular part of our {ci} service calendar. We've provided porta potties and luxury restroom trailers for {lm2}-area projects ranging from small private gatherings to large public events drawing thousands throughout {cn}. For construction near {lm2} in {a1} or {a2}, we coordinate delivery timing with your site supervisor. Call (833) 652-9344 for a {ci}-specific quote.",
            "faq-lm2"
        ),
    ]


# ══════════════════════════════════════════════════════════════════════════
# BUILDERS
# ══════════════════════════════════════════════════════════════════════════

def build_faq_schema(city, faqs, landmark_faqs):
    slug = city["slug"]
    entries = []
    all_faqs = faqs + [(None, None, None, q, a, fid) for q, a, fid in landmark_faqs]

    for i, item in enumerate(faqs):
        q_tmpl, ans_key, fid = item
        q = fmt(q_tmpl, city)
        variants = FAQ_ANSWERS.get(ans_key, ["We serve {city} — call (833) 652-9344."])
        a = fmt(pick(variants, slug, offset=i), city)
        entries.append(
            '        {\n'
            '          "@type": "Question",\n'
            f'          "@id": "https://fixpilotportapottyrentals.com/porta-potty-rental-{slug}/#{fid}",\n'
            f'          "name": {json.dumps(q)},\n'
            '          "acceptedAnswer": {"@type": "Answer", "text": ' + json.dumps(a) + '}\n'
            '        }'
        )
    for q, a, fid in landmark_faqs:
        entries.append(
            '        {\n'
            '          "@type": "Question",\n'
            f'          "@id": "https://fixpilotportapottyrentals.com/porta-potty-rental-{slug}/#{fid}",\n'
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


def build_faq_html(city, faqs, landmark_faqs):
    slug = city["slug"]
    items = ""
    i = 0
    for q_tmpl, ans_key, fid in faqs:
        q = fmt(q_tmpl, city)
        variants = FAQ_ANSWERS.get(ans_key, ["We serve {city} — call (833) 652-9344."])
        a = fmt(pick(variants, slug, offset=i), city)
        i += 1
        items += (
            f'\n                <div id="{fid}" class="border border-gray-100 rounded-xl p-6 shadow-sm">\n'
            f'                    <h3 class="font-semibold text-lg text-gray-800 mb-2">{i}. {q}</h3>\n'
            f'                    <p class="text-gray-600 text-sm">{a}</p>\n'
            f'                </div>'
        )
    for q, a, fid in landmark_faqs:
        i += 1
        items += (
            f'\n                <div id="{fid}" class="border border-gray-100 rounded-xl p-6 shadow-sm">\n'
            f'                    <h3 class="font-semibold text-lg text-gray-800 mb-2">{i}. {q}</h3>\n'
            f'                    <p class="text-gray-600 text-sm">{a}</p>\n'
            f'                </div>'
        )
    return (
        f'    <section id="faq" class="py-20 bg-white">\n'
        f'        <div class="container mx-auto px-4">\n'
        f'            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 text-center">{city["name"]} Porta Potty Rental — Frequently Asked Questions</h2>\n'
        f'            <p class="text-gray-600 max-w-2xl mx-auto text-lg text-center mb-12">Real answers for {city["name"]} residents, contractors, and event planners. Can\'t find yours? Call (833) 652-9344 anytime.</p>\n'
        f'            <div class="space-y-6 max-w-4xl mx-auto">{items}\n'
        f'            </div>\n'
        f'        </div>\n'
        f'    </section>'
    )


def build_local_context_section(city):
    slug = city["slug"]
    variant = pick(LOCAL_CONTEXT, slug, offset=5)
    body = fmt(variant, city)
    paras = [p.strip() for p in body.split('\n\n') if p.strip()]
    paras_html = ''.join(
        f'<p class="text-gray-700 leading-relaxed mb-5 text-base">{p}</p>\n'
        for p in paras
    )
    return (
        f'<section class="py-16 bg-white border-t border-gray-100" id="local-market">\n'
        f'  <div class="container mx-auto px-4 max-w-4xl">\n'
        f'    <h2 class="text-3xl md:text-4xl font-extrabold text-brand-900 mb-6">'
        f'Porta Potty Rental in {city["name"]}, {city["state"]} — {city["county"]} Service Area</h2>\n'
        f'    {paras_html}'
        f'  </div>\n'
        f'</section>'
    )


# ══════════════════════════════════════════════════════════════════════════
# PAGE PATCHER
# ══════════════════════════════════════════════════════════════════════════

def patch_page(html, city):
    slug = city["slug"]
    profile = city["profile"]
    faqs = PROFILE_FAQ_PLAN.get(profile, PROFILE_FAQ_PLAN["suburban"])
    landmark_faqs = get_landmark_faqs(city)

    # 1. Replace FAQPage schema
    new_schema = build_faq_schema(city, faqs, landmark_faqs)
    _ns = new_schema
    html = re.sub(
        r'<script type="application/ld\+json">\s*\{\s*"@context"\s*:\s*"https://schema\.org",\s*"@type"\s*:\s*"FAQPage".*?</script>',
        lambda m: _ns,
        html, flags=re.DOTALL
    )

    # 2. Replace FAQ HTML section
    new_faq_html = build_faq_html(city, faqs, landmark_faqs)
    _nf = new_faq_html
    html = re.sub(
        r'<section id="faq"[^>]*>.*?</section>',
        lambda m: _nf,
        html, flags=re.DOTALL
    )

    # 3. Inject/replace Local Market Context section
    local_ctx = build_local_context_section(city)
    _lc = local_ctx
    if 'id="local-market"' in html:
        html = re.sub(
            r'<section[^>]*id="local-market".*?</section>',
            lambda m: _lc,
            html, flags=re.DOTALL, count=1
        )
    else:
        html = re.sub(
            r'(<section id="related-cities")',
            lambda m: _lc + '\n' + m.group(1),
            html, count=1
        )

    return html


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    base = Path(".")
    dirs = sorted(p for p in base.iterdir()
                  if p.is_dir() and p.name.startswith("porta-potty-rental-"))
    updated = skipped = 0
    for d in dirs:
        slug = d.name[len("porta-potty-rental-"):]
        page = d / "index.html"
        if not page.exists():
            continue
        city = get_city_data(slug)
        if city is None:
            skipped += 1
            continue
        html = page.read_text(encoding="utf-8")
        patched = patch_page(html, city)
        if patched != html:
            page.write_text(patched, encoding="utf-8")
            print(f"  OK   {slug} ({city['profile']})")
            updated += 1
        else:
            print(f"  NOOP {slug}")
            skipped += 1
    print(f"\nDone. Updated: {updated}  Skipped: {skipped}")

if __name__ == "__main__":
    main()
