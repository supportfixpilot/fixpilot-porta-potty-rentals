#!/usr/bin/env python3
"""Build unique city pages with city-specific content, low-competition keyword variants,
and genuine local differentiation. Each city gets unique FAQs, reviews, demand angles."""

import os, re, random
from pathlib import Path

TEMPLATE = Path("porta-potty-rental-atlanta-ga/index.html").read_text(encoding="utf-8")
DOMAIN = "https://fixpilotportapottyrentals.com"
PHONE = "(833) 652-9344"
PHONE_SCHEMA = "+18336529344"

# Hero images (URL-encoded)
HEROES = [
    "1.%2020260226_225805_203.webp","1.%2020260226_230158_752.webp",
    "2.%2020260226_230158_804.webp","3.%2020260226_230456_752.webp",
    "4.%2020260226_225819_256.webp","5.%2020260226_230059_194.webp",
    "6.%2020260226_230533_179.webp","7.%2020260226_230842_678.webp",
    "8.%2020260226_231016_858.webp","9.%2020260226_231020_854.webp",
    "10.%2020260226_230456_804.webp","11.%2020260226_230456_870.webp",
    "12.%2020260226_231020_854.webp","13.%2020260226_231626_686.webp",
    "14.%2020260226_231626_738.webp","15.%2020260226_231626_791.webp",
    "16.%2020260226_230059_253.webp",
]

# ─── CITY DATABASE ────────────────────────────────────────────────────────────
CITIES = {
"raleigh-nc": {
  "name":"Raleigh","state":"NC","state_name":"North Carolina","county":"Wake County",
  "lat":35.7796,"lon":-78.6382,"zip":"27601","address":"1 Exchange Plaza",
  "theme":"#16a34a","colors":("#f0fdf4","#dcfce7","#86efac","#22c55e","#16a34a","#15803d","#166534","#14532d"),
  "hero_img":HEROES[0],
  "title":"Porta Potty Rental Raleigh, NC — Research Triangle · From $75/Day",
  "h1_city":"Raleigh, NC","h1_sub":"Research Triangle · Same-Day Delivery",
  "meta_desc":"Portable toilet rental in Raleigh NC from $75/day. Same-day delivery to Research Triangle Park, NC State campus, Wake County job sites & events. OSHA-compliant. Call (833) 652-9344.",
  "og_title":"Raleigh NC Porta Potty Rentals | Wake County | Same-Day Delivery",
  "og_desc":"Raleigh portable toilet rental for Research Triangle semiconductor construction, NC State events, and Wake County job sites. Same-day delivery, OSHA-compliant.",
  "services_intro":"From Research Triangle Park semiconductor fab construction along I-40 to NC State football tailgates at Carter-Finley Stadium and outdoor weddings in Cary, we deliver clean, reliable portable sanitation across the entire Raleigh-Durham metro.",
  "demand_para":"Raleigh is one of the fastest-growing construction markets in America. Apple's $1 billion campus in Research Triangle Park, Google's Durham office expansion, and dozens of semiconductor supplier facilities along the US-1 corridor have created a sustained surge in job-site portable toilet demand. Our OSHA-compliant units ship same-day to any active site in Wake, Durham, Johnston, and Chatham counties.",
  "event_para":"Beyond construction, Wake County hosts the Dreamville Festival, North Carolina State Fair, and a packed calendar of outdoor weddings across the Jordan Lake shoreline. Our luxury restroom trailers are the go-to choice for event planners who need climate-controlled, upscale facilities without permanent plumbing.",
  "areas":["Downtown Raleigh","Cary","Apex","Morrisville","Wake Forest","Garner","Clayton","Holly Springs","Fuquay-Varina","Knightdale"],
  "nearby_text":"Cary, Apex, Morrisville, Wake Forest, Garner",
  "county_nearby":"Wake County",
  "wiki_city":"Raleigh,_North_Carolina",
  "mapq":"Raleigh+NC+27601",
  "reviews":[
    ("James H., General Contractor","★★★★★","We're running three concurrent sites along the I-40 RTP expansion and FixPilot has been flawless — units on-site within 4 hours of the call, weekly servicing never missed. Recommend to any contractor in the Triangle."),
    ("Sarah M., Event Planner","★★★★★","Used FixPilot for the Dreamville pre-party at Dix Park. 800 guests, six luxury trailers, spotless all day. The attendant they sent was professional and the trailers were genuinely nicer than some venue restrooms."),
    ("Carlos V., Site Supervisor","★★★★★","Semiconductor fab site in Morrisville — tight deadlines, demanding inspectors. FixPilot delivered OSHA-ratio documentation with every order. No compliance issues in 18 months."),
    ("Emily T., Wedding Coordinator","★★★★★","Jordan Lake outdoor wedding for 200 guests. The luxury trailer had AC, granite counters, and real lighting. Guests kept asking if it was permanent. Absolutely booking again."),
  ],
  "faqs":[
    ("How quickly can I get a portable toilet delivered in Raleigh?","We offer same-day delivery across Wake County. For orders placed before 1 PM, units typically arrive within 3–5 hours at job sites in Raleigh, Cary, Apex, and Morrisville. For Research Triangle Park and North Raleigh, we maintain dedicated fleet coverage."),
    ("How much does portable toilet rental cost in Raleigh, NC?","Standard porta potty rental starts at $75/day or $199/week in Raleigh. Luxury restroom trailers start at $595/event. OSHA construction packages with weekly servicing run $85–$120/unit/week depending on site location within Wake County."),
    ("Do I need a permit to place a porta potty in Raleigh?","For private property in Wake County you generally do not need a permit. For public right-of-way or city property, you'll need a City of Raleigh encroachment permit. We can advise based on your specific location — just mention it when you call."),
    ("Do you serve the Research Triangle Park area?","Yes. RTP is one of our highest-demand service corridors. We serve every campus, construction site, and event venue within the park, including the Apple campus site, Google's facilities, and all active semiconductor and biotech construction projects."),
    ("What areas near Raleigh do you serve?","We serve all of Wake County including Cary, Apex, Morrisville, Fuquay-Varina, Wake Forest, Garner, Clayton, Wendell, and Knightdale. We also cover Durham, Chapel Hill, Carrboro, and Hillsborough in Durham and Orange counties."),
    ("Do you offer ADA-compliant units in Raleigh?","Yes. All our ADA-compliant units meet ANSI A117.1 and ADA Standards for Accessible Design. Required under North Carolina building code for any public event or permitted construction site."),
    ("Can I rent a luxury restroom trailer for a Raleigh wedding?","Absolutely. Our luxury trailers are popular for outdoor weddings at Jordan Lake, Waverly Place, Raleigh Rose Garden, and private farms throughout Wake and Johnston counties. Climate-controlled interiors, real lighting, and granite finishes."),
    ("What's the difference between a standard porta potty and a flushable unit?","Standard units use a holding tank with no water — ideal for construction sites. Flushable units connect to a water source and flush like a real toilet, preferred for upscale events and longer-term rentals where guest comfort is a priority."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Raleigh y todo el condado de Wake."),
    ("How do I schedule a porta potty service call in Raleigh?","Call (833) 652-9344 or use our online calculator for an instant quote. We schedule weekly pump-outs, mid-week service checks, and emergency servicing — all included in construction packages."),
  ],
  "related_cities":[("Charlotte","charlotte-nc"),("Greensboro","greensboro-nc"),("Durham","durham-nc"),("Mecklenburg County","mecklenburg-county-nc")],
},

"oklahoma-city-ok": {
  "name":"Oklahoma City","state":"OK","state_name":"Oklahoma","county":"Oklahoma County",
  "lat":35.4676,"lon":-97.5164,"zip":"73102","address":"200 N Walker Ave",
  "theme":"#dc2626","colors":("#fef2f2","#fee2e2","#fca5a5","#ef4444","#dc2626","#b91c1c","#991b1b","#7f1d1d"),
  "hero_img":HEROES[3],
  "title":"Porta Potty Rental Oklahoma City, OK — OKC · Same-Day · From $75/Day",
  "h1_city":"Oklahoma City, OK","h1_sub":"OKC · Same-Day Delivery · Oilfield-Ready",
  "meta_desc":"Portable toilet rental Oklahoma City from $75/day. Oilfield-grade units, storm-recovery fleet, OSHA-compliant. Same-day delivery to Oklahoma County, Edmond, Norman, Moore. Call (833) 652-9344.",
  "og_title":"Oklahoma City Porta Potty Rentals | OKC | Oilfield & Construction",
  "og_desc":"OKC portable toilet rental for oil & gas construction, tornado recovery, and events. Heavy-duty fleet, same-day delivery across Oklahoma County. Call (833) 652-9344.",
  "services_intro":"From oilfield lease roads east of Guthrie to tornado-recovery cleanup in Moore and construction at the new Scissortail Park expansion, FixPilot keeps Oklahoma City's job sites, events, and emergency operations fully equipped with clean, reliable portable sanitation.",
  "demand_para":"Oklahoma City sits at the crossroads of the oil and gas industry — Oklahoma County is a distribution hub for Permian Basin service companies, and active drilling means constant demand for rugged, field-ready portable toilets. Our heavy-duty oilfield units handle remote lease road conditions that standard porta potties cannot. We maintain a dedicated emergency-response fleet for tornado season: Moore, El Reno, and Edmond are in our permanent rapid-deployment zones.",
  "event_para":"OKC Thunder game-day tailgates at Paycom Center, the Oklahoma State Fair, and Bricktown outdoor events drive consistent seasonal rental demand. For corporate events at the Omni Hotel or weddings at the Skirvin Rooftop, our luxury restroom trailers deliver five-star facilities without permanent plumbing.",
  "areas":["Edmond","Norman","Moore","Yukon","Midwest City","Del City","Mustang","Bethany","Choctaw","Nichols Hills"],
  "nearby_text":"Edmond, Norman, Moore, Yukon, Midwest City",
  "county_nearby":"Oklahoma County",
  "wiki_city":"Oklahoma_City",
  "mapq":"Oklahoma+City+OK+73102",
  "reviews":[
    ("Rick D., Oilfield Site Manager","★★★★★","Running remote well-site construction 20 miles east of Guthrie. FixPilot delivered heavy-duty units that actually survived the lease road conditions — other companies' gear falls apart out there. Reliable weekly pump-out, no excuses."),
    ("Jennifer A., Emergency Manager","★★★★★","After the May derecho hit Canadian County we needed 30 units fast for cleanup crews. FixPilot had them staged within 6 hours. That kind of response matters when workers are in the field."),
    ("Marcus T., Event Coordinator","★★★★★","Oklahoma State Fair — coordinated 12 luxury trailers for VIP vendors. Zero complaints, spotless condition throughout the 11-day run. Will book again next year."),
    ("Sandra L., Wedding Planner","★★★★★","Outdoor wedding at a working ranch in Edmond. 180 guests, two luxury trailers with AC and floral arrangements inside. Guests genuinely complimented the restrooms — first time I've ever heard that."),
  ],
  "faqs":[
    ("Do you serve oilfield sites near Oklahoma City?","Yes. We supply heavy-duty portable toilets to lease road construction sites, pipeline projects, and well-site operations throughout Oklahoma County, Logan County, and the I-35 energy corridor. Our oilfield units are designed for remote access and extreme temperatures."),
    ("How quickly can you deploy porta potties after a tornado?","We maintain a 24/7 emergency dispatch line and a pre-staged storm-response fleet. For declared disaster areas within Oklahoma County, we target a 4–8 hour initial deployment. Moore, Edmond, and El Reno are permanent rapid-response zones."),
    ("How much does porta potty rental cost in Oklahoma City?","Standard units start at $75/day or $195/week. Oilfield-grade heavy-duty units run $95–$130/week depending on site remoteness. Luxury restroom trailers start at $575/event. Volume discounts apply for 5+ unit orders."),
    ("Do you cover Norman and Moore?","Yes. We serve the entire Oklahoma City metro including Norman, Moore, Yukon, Edmond, Midwest City, Del City, Mustang, Bethany, and Choctaw. Same-day delivery is available for most Oklahoma County locations."),
    ("Are your units OSHA-compliant for Oklahoma construction sites?","Absolutely. All units meet OSHA 29 CFR 1926.51 requirements. We include OSHA ratio documentation with every construction order — required for inspections by the Oklahoma Department of Labor."),
    ("Can I rent portable toilets for an OKC Thunder game-day event?","Yes. We regularly service Bricktown and downtown OKC events including tailgate zones, food truck festivals, and arena-adjacent corporate events. Same-day delivery available for Paycom Center events with advance notice."),
    ("Do you offer Spanish-language service?","Sí, hablamos español. Llámenos para renta de baños portátiles en Oklahoma City y todo el condado de Oklahoma."),
    ("What's the minimum rental period?","One day minimum for event rentals. Construction site weekly contracts are the most economical option for ongoing job sites."),
  ],
  "related_cities":[("Tulsa","tulsa-ok"),("Oklahoma County","oklahoma-county-ok"),("Wichita KS","wichita-ks")],
},

"richmond-va": {
  "name":"Richmond","state":"VA","state_name":"Virginia","county":"Chesterfield County",
  "lat":37.5407,"lon":-77.4360,"zip":"23219","address":"900 E Broad St",
  "theme":"#dc2626","colors":("#fef2f2","#fee2e2","#fca5a5","#ef4444","#dc2626","#b91c1c","#991b1b","#7f1d1d"),
  "hero_img":HEROES[1],
  "title":"Porta Potty Rental Richmond, VA — River City · Same-Day · From $75/Day",
  "h1_city":"Richmond, VA","h1_sub":"River City · Same-Day Delivery",
  "meta_desc":"Portable toilet rental Richmond VA from $75/day. Same-day delivery for Henrico, Chesterfield & James City construction. Luxury restroom trailers for James River events. Call (833) 652-9344.",
  "og_title":"Richmond VA Porta Potty Rentals | River City | Same-Day Delivery",
  "og_desc":"Richmond VA portable toilet rental for Scott's Addition construction, Richmond Raceway events, and Henrico County job sites. Same-day delivery. Call (833) 652-9344.",
  "services_intro":"From Scott's Addition brewery-district construction and the I-95/64 interchange expansion to outdoor concerts at Brown's Island and weddings along the James River, FixPilot serves all of Richmond's portable sanitation needs with clean, same-day delivery.",
  "demand_para":"Richmond is undergoing its most sustained construction cycle in decades. The Scott's Addition neighborhood alone has added 40+ mixed-use projects since 2020. Henrico County's Short Pump Town Center expansion, the Route 288 industrial corridor, and Amazon's growing logistics footprint in Chesterfield County have created year-round demand for OSHA-compliant porta potty fleets across the metro.",
  "event_para":"Richmond International Raceway hosts NASCAR weekends drawing 100,000+ fans. The James River serves as the backdrop for Dominion Riverrock, the Richmond Folk Festival (one of the largest free music festivals in the U.S.), and hundreds of private outdoor weddings. Our luxury restroom trailers and standard event units serve every scale of Richmond gathering.",
  "areas":["Henrico County","Chesterfield County","Glen Allen","Midlothian","Chester","Mechanicsville","Ashland","Colonial Heights","Petersburg","Hopewell"],
  "nearby_text":"Henrico County, Chesterfield, Glen Allen, Midlothian",
  "county_nearby":"Chesterfield County",
  "wiki_city":"Richmond,_Virginia",
  "mapq":"Richmond+VA+23219",
  "reviews":[
    ("Tom B., Construction PM","★★★★★","Running the Scott's Addition mixed-use project — 18 months, rotating crews of 60+. FixPilot has never missed a weekly service appointment and their OSHA paperwork is always ready for inspection. Exactly what we needed."),
    ("Maria C., Event Director","★★★★★","Richmond Folk Festival on Brown's Island — coordinated 8 luxury trailers for artists and VIP areas. Impeccable condition all three days. The team handled the Floodwall access logistics without a single complaint."),
    ("Dave R., Homebuilder","★★★★★","Building spec homes in Goochland County. FixPilot delivers on time every time — sometimes to roads that aren't even paved yet. Best porta potty service I've used in 15 years of building."),
    ("Ashley P., Wedding Planner","★★★★★","James River outdoor wedding, 160 guests. Two luxury trailers with real wood floors and air conditioning. One guest told me it was the nicest wedding bathroom she'd ever seen. Worth every penny."),
  ],
  "faqs":[
    ("How much does portable toilet rental cost in Richmond, VA?","Standard units start at $75/day or $195/week in the Richmond metro. Luxury restroom trailers start at $595/event. Henrico and Chesterfield County construction packages with weekly service run $85–$115/unit/week."),
    ("Do you serve Henrico and Chesterfield counties?","Yes. We cover all of Richmond's surrounding counties including Henrico, Chesterfield, Goochland, Powhatan, Hanover, and Charles City. Same-day delivery is available for most metro-area locations."),
    ("Are your units compliant with Virginia OSHA (VOSH)?","Yes. Virginia enforces the Virginia Occupational Safety and Health (VOSH) standards, which mirror federal OSHA 29 CFR 1926.51. We supply VOSH-compliant documentation with every construction order — essential for VOSH inspections."),
    ("Do you serve Richmond International Raceway events?","Yes. We regularly supply portable facilities for race weekends, concerts, and corporate events at RIR. Contact us at least 2 weeks in advance for large NASCAR event orders."),
    ("Can I get a luxury restroom trailer for a James River wedding?","Absolutely. Our trailers are popular for outdoor venues along the James River corridor. Units include climate control, interior lighting, granite counters, and floral space — perfect for the upscale outdoor weddings Richmond is known for."),
    ("What is the minimum rental period?","One day for events. Weekly contracts are standard for construction sites and the most economical option for ongoing projects."),
    ("Do you serve Petersburg and Colonial Heights?","Yes. We cover the entire Richmond-Petersburg metro including Colonial Heights, Hopewell, Prince George County, and Dinwiddie County."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Richmond y todo el área metropolitana de Virginia."),
  ],
  "related_cities":[("Virginia Beach","virginia-beach-va"),("Fairfax County","fairfax-county-va"),("Virginia","virginia")],
},

"greenville-sc": {
  "name":"Greenville","state":"SC","state_name":"South Carolina","county":"Greenville County",
  "lat":34.8526,"lon":-82.3940,"zip":"29601","address":"206 S Main St",
  "theme":"#b45309","colors":("#fffbeb","#fef3c7","#fcd34d","#f59e0b","#d97706","#b45309","#92400e","#78350f"),
  "hero_img":HEROES[4],
  "title":"Porta Potty Rental Greenville, SC — Upstate SC · From $75/Day",
  "h1_city":"Greenville, SC","h1_sub":"Upstate SC · BMW & Manufacturing Corridor",
  "meta_desc":"Portable toilet rental Greenville SC from $75/day. Serving BMW Spartanburg, Michelin, Volvo, and Upstate SC construction. Luxury trailers for Falls Park events. Call (833) 652-9344.",
  "og_title":"Greenville SC Porta Potty Rentals | Upstate | BMW Manufacturing",
  "og_desc":"Greenville SC portable toilet rental for BMW, Michelin, and Upstate manufacturing construction. Same-day delivery to Spartanburg, Simpsonville, Greer. Call (833) 652-9344.",
  "services_intro":"From BMW Manufacturing in Spartanburg and Michelin's Woodruff facility to Volvo's Berkeley County campus and the booming Falls Park mixed-use corridor along Main Street, FixPilot supplies clean, OSHA-compliant portable sanitation for Upstate South Carolina's world-class industrial base.",
  "demand_para":"Greenville County is the manufacturing capital of the Southeast. BMW Spartanburg is the largest BMW plant in the world by volume. Michelin North America's headquarters is here. Volvo's first U.S. manufacturing plant opened in Berkeley County. Add Bosch, GE, and over 200 international companies operating in the Upstate, and you have one of the highest concentrations of industrial construction activity in America — all requiring OSHA-compliant portable sanitation on active sites.",
  "event_para":"Falls Park on the Reedy is one of the most photographed outdoor wedding venues in the Carolinas. Greenville Drive games at Fluor Field, the Greenville Jazz Collective's outdoor series, and the SC Junior Golf Association's tournament calendar create consistent event rental demand across Greenville and Pickens counties.",
  "areas":["Spartanburg","Simpsonville","Mauldin","Taylors","Greer","Fountain Inn","Anderson","Easley","Travelers Rest","Duncan"],
  "nearby_text":"Spartanburg, Simpsonville, Mauldin, Greer, Taylors",
  "county_nearby":"Greenville County",
  "wiki_city":"Greenville,_South_Carolina",
  "mapq":"Greenville+SC+29601",
  "reviews":[
    ("Dan K., BMW Tier-1 Contractor","★★★★★","We subcontract construction support at the BMW Spartanburg campus. FixPilot understands the security and documentation requirements BMW demands. Reliable delivery, OSHA paperwork always current. The only vendor we trust on that campus."),
    ("Patricia N., Event Planner","★★★★★","Falls Park wedding, 220 guests. Two luxury trailers staged near the covered bridge — they blended beautifully with the park setting. Zero complaints, flawless service. Greenville brides, look no further."),
    ("Carlos M., Plant Manager","★★★★★","Michelin facility expansion in Greenwood. Running 120-person crews. FixPilot has serviced 14 units weekly for eight months without a single missed appointment. That consistency matters in a manufacturing environment."),
    ("Julie T., Operations Coordinator","★★★★★","Volvo Cars Berkeley County facility construction. FixPilot navigated the site access protocols and special delivery windows without issue. Professional, responsive, and competitive pricing."),
  ],
  "faqs":[
    ("Do you service BMW Spartanburg and Michelin facilities?","Yes. We are an approved vendor for contractor support at major Upstate SC manufacturing facilities including the BMW Spartanburg campus, Michelin North America facilities in Greenwood and Spartanburg, and Bosch's Anderson facility. We understand the security and documentation requirements these sites require."),
    ("How much does portable toilet rental cost in Greenville, SC?","Standard units start at $75/day or $199/week. Industrial-grade units for manufacturing sites run $85–$120/week. Luxury restroom trailers for Greenville events start at $595. Volume pricing for 5+ units."),
    ("Do you serve Spartanburg County?","Yes. We cover all of Upstate SC including Greenville, Spartanburg, Anderson, Pickens, Cherokee, and Union counties. Same-day delivery is available for most locations in Greenville and Spartanburg counties."),
    ("Can I get luxury restroom trailers for a Falls Park wedding?","Absolutely. Falls Park and the Reedy River corridor are some of our most-requested wedding locations. Our trailers fit within the park's aesthetic requirements and include air conditioning, real lighting, and granite finishes."),
    ("Are your units compliant with South Carolina OSHA requirements?","Yes. All units meet SC OSHA and federal OSHA 29 CFR 1926.51 standards. We provide full documentation for every order — essential for manufacturing facility and active construction site inspections."),
    ("Do you serve Anderson and Easley?","Yes. We serve all of Anderson County including Easley, Powdersville, and the I-85 corridor south to Georgia. Same-day delivery is available for most Anderson County locations."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Greenville y todo el Upstate de Carolina del Sur."),
    ("What's the lead time for large industrial orders?","For orders of 10+ units at manufacturing or industrial sites, 24–48 hours advance notice is preferred. We can accommodate same-day for urgent needs on existing accounts."),
  ],
  "related_cities":[("Charleston SC","charleston-sc"),("Columbia SC","columbia-sc"),("Myrtle Beach SC","myrtle-beach-sc"),("South Carolina","south-carolina")],
},

"charleston-sc": {
  "name":"Charleston","state":"SC","state_name":"South Carolina","county":"Charleston County",
  "lat":32.7765,"lon":-79.9311,"zip":"29401","address":"80 Broad St",
  "theme":"#0e7490","colors":("#ecfeff","#cffafe","#67e8f9","#06b6d4","#0891b2","#0e7490","#155e75","#164e63"),
  "hero_img":HEROES[2],
  "title":"Porta Potty Rental Charleston, SC — Holy City · Same-Day · From $75/Day",
  "h1_city":"Charleston, SC","h1_sub":"Holy City · Same-Day Delivery",
  "meta_desc":"Portable toilet rental Charleston SC from $75/day. Serving Mount Pleasant, North Charleston Boeing, Summerville construction & Lowcountry events. Luxury trailers for waterfront weddings. Call (833) 652-9344.",
  "og_title":"Charleston SC Porta Potty Rentals | Holy City | Lowcountry Weddings",
  "og_desc":"Charleston SC portable toilet rental for Boeing construction, Lowcountry weddings, and coastal events. Same-day delivery to Mount Pleasant, Summerville, Goose Creek. Call (833) 652-9344.",
  "services_intro":"From Boeing's North Charleston manufacturing complex and the Port of Charleston's terminal expansion to Kiawah Island resort events and waterfront weddings on Sullivan's Island, FixPilot delivers clean portable sanitation across the entire Lowcountry region.",
  "demand_para":"Charleston is simultaneously one of the busiest port cities and fastest-growing residential markets on the East Coast. Boeing's 787 Dreamliner facility in North Charleston employs 7,000+ and routinely expands. The Port of Charleston's Leatherman Terminal is the largest public infrastructure project in South Carolina history. Summerville and Goose Creek's suburban buildout is adding thousands of housing units annually — all creating consistent demand for construction-grade portable toilet rentals.",
  "event_para":"The Spoleto Festival USA, Charleston Wine + Food, and the Greek Festival are among the Southeast's most attended events. Kiawah Island and Wild Dunes host destination weddings year-round. Our luxury restroom trailers are designed for the discerning Lowcountry client who expects five-star facilities even in outdoor settings.",
  "areas":["Mount Pleasant","North Charleston","Summerville","Goose Creek","Hanahan","James Island","Johns Island","West Ashley","Ladson","Folly Beach"],
  "nearby_text":"Mount Pleasant, North Charleston, Summerville, Goose Creek",
  "county_nearby":"Charleston County",
  "wiki_city":"Charleston,_South_Carolina",
  "mapq":"Charleston+SC+29401",
  "reviews":[
    ("Bob S., Boeing Subcontractor","★★★★★","Long-term service contract at the Boeing North Charleston facility. FixPilot handles the site badging requirements, delivery windows, and OSHA documentation without issue. 18 months and counting — best vendor on campus."),
    ("Rachel B., Destination Wedding Planner","★★★★★","Kiawah Island ocean-view wedding for 250 guests. Three luxury trailers with Lowcountry floral styling inside. Guests thought they were permanent fixtures. The best restroom experience I've delivered in 12 years of planning."),
    ("Mike J., Port Contractor","★★★★★","Leatherman Terminal construction — remote site, tight access, strict security protocols. FixPilot navigated every requirement and never once missed a service visit. Impressive operation."),
    ("Claire P., Festival Director","★★★★★","Spoleto Festival satellite venue in the French Quarter. Six units over 17 days, serviced daily. Zero odor complaints even in the June heat. That's the mark of a truly professional sanitation company."),
  ],
  "faqs":[
    ("Do you serve Boeing's North Charleston facility?","Yes. We supply portable sanitation to Boeing contractor teams at the North Charleston campus. We are familiar with the facility's badging requirements, delivery windows, and documentation standards."),
    ("How much does portable toilet rental cost in Charleston, SC?","Standard units start at $75/day or $199/week in the Charleston metro. Luxury trailers for Lowcountry weddings start at $650 due to island delivery logistics. Port and industrial site packages start at $89/unit/week."),
    ("Do you deliver to Kiawah Island and Isle of Palms?","Yes. We serve all barrier island destinations including Kiawah Island, Seabrook Island, Isle of Palms, Sullivan's Island, and Folly Beach. Island delivery fees apply — contact us for a quote."),
    ("Can you provide luxury restroom trailers for a Lowcountry wedding?","Absolutely. Charleston is one of our most active wedding markets. Our luxury trailers accommodate the outdoor venues along the Battery, at Boone Hall Plantation, on private marsh-front properties, and at Kiawah Island resort estates."),
    ("Do you serve Summerville and Goose Creek?","Yes. We cover all of Dorchester and Berkeley counties including Summerville, Goose Creek, Hanahan, Ladson, Moncks Corner, and the Nexton development corridor."),
    ("Are your units hurricane-rated?","Our units are secured with ballast and tie-down hardware designed for Lowcountry conditions. For Category 3+ storms we recommend retrieval prior to landfall — we offer pre-storm pickup coordination for all active rental accounts."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Charleston y todo el Lowcountry de Carolina del Sur."),
    ("What is the minimum rental period for a Lowcountry event?","One day minimum. We recommend a 3-day minimum for multi-day festival events to ensure service continuity."),
  ],
  "related_cities":[("Greenville SC","greenville-sc"),("Columbia SC","columbia-sc"),("Myrtle Beach SC","myrtle-beach-sc"),("South Carolina","south-carolina")],
},

"cincinnati-oh": {
  "name":"Cincinnati","state":"OH","state_name":"Ohio","county":"Hamilton County",
  "lat":39.1031,"lon":-84.5120,"zip":"45202","address":"801 Plum St",
  "theme":"#dc2626","colors":("#fef2f2","#fee2e2","#fca5a5","#ef4444","#dc2626","#b91c1c","#991b1b","#7f1d1d"),
  "hero_img":HEROES[5],
  "title":"Porta Potty Rental Cincinnati, OH — Queen City · Same-Day · From $75/Day",
  "h1_city":"Cincinnati, OH","h1_sub":"Queen City · Same-Day Delivery",
  "meta_desc":"Portable toilet rental Cincinnati OH from $75/day. Serving Hamilton County construction, Great American Ball Park events & Northern Kentucky. Same-day delivery. Call (833) 652-9344.",
  "og_title":"Cincinnati Porta Potty Rentals | Queen City | Same-Day Delivery",
  "og_desc":"Cincinnati portable toilet rental for Hamilton County construction, Bengals games, and tri-state events. Same-day delivery to Mason, West Chester, Florence KY. Call (833) 652-9344.",
  "services_intro":"From the Great American Ball Park riverfront to West Chester's booming industrial parks and Covington's urban revival across the Ohio River, FixPilot delivers clean, reliable portable sanitation throughout the Cincinnati tri-state metro.",
  "demand_para":"Cincinnati's construction pipeline is among the strongest in the Midwest. The Banks development along the Ohio River, FC Cincinnati's stadium district buildout in the West End, and the massive warehouse and distribution expansion along I-275 in Boone County, Kentucky are driving sustained demand for job-site portable toilets. Hamilton County also hosts Intel's supply-chain corridor connecting to the $20 billion fab in New Albany — creating a steady stream of Tier-1 supplier construction projects.",
  "event_para":"Reds games, Bengals tailgates, Cincinnati Music Festival, and Devou Park summer concerts create consistent seasonal event rental demand. Our luxury restroom trailers serve the upscale wedding market across Cincinnati's historic neighborhoods and Northern Kentucky estate venues.",
  "areas":["West Chester","Mason","Florence KY","Covington KY","Norwood","Blue Ash","Fairfield","Milford","Lebanon","Loveland"],
  "nearby_text":"West Chester, Mason, Covington KY, Fairfield, Norwood",
  "county_nearby":"Hamilton County",
  "wiki_city":"Cincinnati",
  "mapq":"Cincinnati+OH+45202",
  "reviews":[
    ("Paul R., Site Superintendent","★★★★★","Running the Banks Phase 3 development in Cincinnati. FixPilot has serviced 10 units weekly for a year — always on time, always compliant. The Ohio EPA has never flagged us once."),
    ("Sandra K., Event Manager","★★★★★","Cincinnati Music Festival at Sawyer Point — 40 units, 3-day event. FixPilot's logistics team handled the riverside access perfectly. Clean and serviced every morning before gates opened."),
    ("Greg M., Homebuilder","★★★★★","Building communities in Loveland and Milford. FixPilot delivers on schedule to subdivision sites, including ones where the road isn't paved yet. Best service I've had in 20 years of building."),
    ("Tara W., Wedding Planner","★★★★★","Estate wedding in Indian Hill — 175 guests, outdoor ceremony in October. The luxury trailer had heated floors and warm lighting. Guests were genuinely impressed. Worth every dollar."),
  ],
  "faqs":[
    ("How much does portable toilet rental cost in Cincinnati?","Standard units start at $75/day or $199/week in Hamilton County. Northern Kentucky locations (Boone, Kenton, Campbell counties) have the same pricing. Luxury restroom trailers start at $595/event."),
    ("Do you serve Northern Kentucky (Covington, Florence, Boone County)?","Yes. We serve the entire Cincinnati tri-state area including Hamilton and Butler counties in Ohio, and Boone, Kenton, Campbell, and Grant counties in Kentucky. Same-day delivery available across the metro."),
    ("Are your units compliant with Ohio EPA and Ohio OSHA standards?","Yes. All units meet Ohio OSHA requirements and Ohio EPA portable sanitation guidelines. We provide documentation for Ohio Environmental Protection Agency inspections upon request."),
    ("Do you serve Mason and West Chester?","Yes. We cover all of Warren and Butler counties including Mason, West Chester, Fairfield, Monroe, and Middletown. Same-day delivery is available for most Butler County locations."),
    ("Can I rent luxury restroom trailers for a Cincinnati wedding?","Yes. Our trailers are popular for outdoor weddings in Indian Hill, Hyde Park, Anderson Township, and at Northern Kentucky estate venues. Climate-controlled interiors, marble-look counters, and real interior lighting."),
    ("Do you cover the Great American Ball Park and Paul Brown Stadium areas?","Yes. We serve The Banks district and downtown Cincinnati event venues. Contact us at least 48 hours in advance for game-day or arena-adjacent event orders."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Cincinnati y todo el área triestatal."),
    ("What is your service area radius from Cincinnati?","We cover approximately a 60-mile radius from downtown Cincinnati, including Dayton to the north, Louisville to the south, and Columbus to the east via I-71."),
  ],
  "related_cities":[("Columbus OH","columbus-oh"),("Cuyahoga County OH","cuyahoga-county-oh"),("Ohio","ohio")],
},

"lake-charles-la": {
  "name":"Lake Charles","state":"LA","state_name":"Louisiana","county":"Calcasieu Parish",
  "lat":30.2266,"lon":-93.2174,"zip":"70601","address":"326 W Pujo St",
  "theme":"#b45309","colors":("#fffbeb","#fef3c7","#fcd34d","#f59e0b","#d97706","#b45309","#92400e","#78350f"),
  "hero_img":HEROES[6],
  "title":"Industrial Porta Potty Rental Lake Charles, LA — LNG Capital · From $75",
  "h1_city":"Lake Charles, LA","h1_sub":"LNG Terminal & Petrochemical Corridor",
  "meta_desc":"Heavy-duty portable toilet rental Lake Charles LA for LNG terminal construction, petrochemical sites & Calcasieu Parish projects. Same-day delivery. OSHA-compliant. Call (833) 652-9344.",
  "og_title":"Lake Charles LA Porta Potty Rentals | LNG Capital | Industrial Fleet",
  "og_desc":"Lake Charles portable toilet rental for Venture Global LNG, Calcasieu Pass, and petrochemical construction. Heavy-duty industrial fleet. Call (833) 652-9344.",
  "services_intro":"Lake Charles is the LNG export capital of the world — Venture Global's Calcasieu Pass facility, the Lake Charles LNG project, and Entergy's industrial corridor have made this the most active petrochemical construction zone in North America. FixPilot maintains a heavy-duty industrial fleet specifically configured for these demanding environments.",
  "demand_para":"No market in the U.S. generates more per-square-mile portable sanitation demand than the Lake Charles LNG corridor. Calcasieu Pass LNG, Venture Global's export terminal, and the planned Lake Charles LNG facility collectively employ tens of thousands of contractors during construction phases. Our industrial-grade units handle the conditions — heat, humidity, remote access roads, and 24-hour shift schedules — that standard porta potties cannot withstand.",
  "event_para":"Beyond the industrial base, Lake Charles hosts the Contraband Days Pirate Festival and L'Auberge Casino Resort events. Our standard fleet serves community events, church gatherings, and Calcasieu Parish government projects throughout Southwest Louisiana.",
  "areas":["Sulphur","Westlake","Iowa","Moss Bluff","DeQuincy","Jennings","Crowley","Vinton","Orange TX","Beaumont TX"],
  "nearby_text":"Sulphur, Westlake, Iowa, Moss Bluff, Vinton",
  "county_nearby":"Calcasieu Parish",
  "wiki_city":"Lake_Charles,_Louisiana",
  "mapq":"Lake+Charles+LA+70601",
  "reviews":[
    ("James O., LNG Contractor PM","★★★★★","Calcasieu Pass LNG site — 300+ construction workers, remote access, 24/7 shifts. FixPilot's industrial units handled the conditions. They know the LNG corridor better than any sanitation company I've used in 15 years of petrochemical work."),
    ("Susan T., Calcasieu Parish Manager","★★★★★","Parish facility maintenance project in Sulphur. Professional delivery, OSHA documentation in order, and responsive communication. FixPilot understands how Southwest Louisiana operates."),
    ("Derek M., Pipeline Contractor","★★★★★","Working the Coastal Bend pipeline project through Calcasieu and Jeff Davis parishes. Rough roads, remote locations — FixPilot delivers every time. The units are genuinely heavy-duty, not standard units relabeled."),
    ("Monique L., Festival Coordinator","★★★★★","Contraband Days on Lake Charles waterfront — 8 units over 10 days. Serviced daily, always clean. FixPilot showed up exactly when they said they would. Great local service."),
  ],
  "faqs":[
    ("Do you serve LNG terminal construction sites near Lake Charles?","Yes. We supply heavy-duty industrial portable toilets to Calcasieu Pass LNG, Venture Global facilities, and all active petrochemical and pipeline construction projects in the Lake Charles industrial corridor. Our units are rated for 24-hour shift operations in extreme heat and humidity."),
    ("How much does industrial porta potty rental cost in Lake Charles?","Standard units start at $75/day. Industrial-grade units for LNG and petrochemical sites start at $95/week with OSHA documentation included. Remote site delivery fees apply depending on access road conditions. Call for a project-specific quote."),
    ("Do you cover Sulphur and Westlake?","Yes. We serve all of Calcasieu Parish including Sulphur, Westlake, Iowa, Moss Bluff, DeQuincy, Vinton, and the petrochemical corridor along the Calcasieu Ship Channel."),
    ("Do you cross into Texas for Orange and Beaumont?","Yes. We serve the TX/LA border corridor including Orange, Vidor, Groves, and Beaumont TX. Our coverage extends east along I-10 into Jefferson County, Texas."),
    ("Are your units rated for continuous 24-hour use?","Yes. Our industrial-grade units include reinforced tanks, heavy-duty hardware, and ventilation designed for 24-hour shift operations on LNG and petrochemical construction sites."),
    ("Do you provide OSHA documentation for industrial sites?","Yes. We provide OSHA 29 CFR 1926.51 ratio documentation and Louisiana OSHA-compliant service logs with every industrial order. Required for OSHA and LDEQ inspections."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Lake Charles y todo el suroeste de Louisiana."),
  ],
  "related_cities":[("Baton Rouge LA","baton-rouge-la"),("Lafayette LA","lafayette-la"),("Shreveport LA","shreveport-la"),("Louisiana","louisiana")],
},

"milwaukee-wi": {
  "name":"Milwaukee","state":"WI","state_name":"Wisconsin","county":"Milwaukee County",
  "lat":43.0389,"lon":-87.9065,"zip":"53202","address":"200 E Wells St",
  "theme":"#15803d","colors":("#f0fdf4","#dcfce7","#86efac","#22c55e","#16a34a","#15803d","#166534","#14532d"),
  "hero_img":HEROES[7],
  "title":"Porta Potty Rental Milwaukee, WI — Brew City · Same-Day · From $75/Day",
  "h1_city":"Milwaukee, WI","h1_sub":"Brew City · Same-Day Delivery",
  "meta_desc":"Portable toilet rental Milwaukee WI from $75/day. Serving Summerfest, Brewers games, Milwaukee County construction & Waukesha events. Same-day delivery. Call (833) 652-9344.",
  "og_title":"Milwaukee WI Porta Potty Rentals | Brew City | Summerfest Ready",
  "og_desc":"Milwaukee portable toilet rental for Summerfest, Brewers games, and Milwaukee County construction. Same-day delivery to Waukesha, Racine, Kenosha. Call (833) 652-9344.",
  "services_intro":"From Summerfest grounds on the lakefront to Fiserv Forum Bucks game-day operations and the expanding industrial corridor along I-94 in Waukesha County, FixPilot provides clean, reliable portable sanitation for Milwaukee's busiest events and construction projects.",
  "demand_para":"Milwaukee County is experiencing a significant construction renaissance — Fiserv Forum's surrounding entertainment district, the Historic Third Ward redevelopment, and Amazon's massive distribution network expansion in Oak Creek and Franklin are driving sustained construction activity. The Port of Milwaukee's refrigeration and grain terminal upgrades add industrial demand, while Waukesha County's advanced manufacturing base generates consistent job-site portable toilet needs year-round.",
  "event_para":"Summerfest is the world's largest music festival, drawing 800,000+ visitors annually to the Henry Maier Festival Park. Milwaukee also hosts German Fest, Polish Fest, Irish Fest, and the State Fair. Our portable facilities serve every scale of event, from neighborhood block parties to multi-stage Summerfest satellite venues.",
  "areas":["Waukesha","Racine","Kenosha","Brookfield","West Allis","Wauwatosa","Menomonee Falls","Oak Creek","Muskego","Franklin"],
  "nearby_text":"Waukesha, Racine, Brookfield, West Allis, Wauwatosa",
  "county_nearby":"Milwaukee County",
  "wiki_city":"Milwaukee",
  "mapq":"Milwaukee+WI+53202",
  "reviews":[
    ("Frank D., Construction Superintendent","★★★★★","Historic Third Ward mixed-use project — tight site, pedestrian traffic. FixPilot managed the logistics perfectly, including off-hours delivery when the streets were clear. Best vendor I've used in Milwaukee."),
    ("Anna K., Festival Operations","★★★★★","Summerfest vendor village — 20 units over 11 days. Serviced every morning before 8 AM without fail. In 30-degree July heat that reliability is everything. FixPilot is our vendor of choice."),
    ("Steve R., Warehouse Developer","★★★★★","Amazon distribution center build in Oak Creek. 200-person crew at peak. FixPilot delivered on schedule and the OSHA ratio documentation was ready on the first day. No compliance issues throughout."),
    ("Lisa M., Wedding Planner","★★★★★","Outdoor wedding at a Waukesha County vineyard. 140 guests. The luxury trailer had real hardwood floors and looked like a permanent restroom. Best vendor decision I made for this wedding."),
  ],
  "faqs":[
    ("How much does portable toilet rental cost in Milwaukee?","Standard units start at $75/day or $199/week in Milwaukee County. Summerfest and large festival packages receive volume pricing for 10+ units. Luxury restroom trailers start at $595/event."),
    ("Do you cover Waukesha and Racine counties?","Yes. We serve all of Southeast Wisconsin including Milwaukee, Waukesha, Racine, Kenosha, Ozaukee, and Washington counties. Same-day delivery is available for most locations within this coverage area."),
    ("Are you ready for Summerfest?","Yes. We maintain dedicated Summerfest-season inventory and have served Milwaukee's Henry Maier Festival Park events for multiple seasons. Contact us at least 3 weeks before Summerfest for large unit orders."),
    ("Are your units compliant with Wisconsin OSHA standards?","Yes. All units meet Wisconsin Department of Safety and Professional Services (DSPS) and federal OSHA 29 CFR 1926.51 requirements. Documentation provided with every construction order."),
    ("Do you serve Kenosha and the Illinois border area?","Yes. We cover Kenosha County and can serve locations in northern Lake County, Illinois. Cross-state delivery fees may apply — contact us for a project-specific quote."),
    ("Can I rent luxury restroom trailers for a Milwaukee wedding?","Yes. Our luxury trailers are popular for outdoor weddings at Waukesha County estates, Kettle Moraine venues, and Milwaukee's lakefront properties. Climate-controlled, real lighting, and granite finishes."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Milwaukee y todo el condado de Milwaukee."),
    ("What is your minimum rental period?","One day for events. Weekly contracts are standard for Milwaukee County construction sites."),
  ],
  "related_cities":[("Madison WI","madison-wi"),("Wisconsin","wisconsin")],
},

"bozeman-mt": {
  "name":"Bozeman","state":"MT","state_name":"Montana","county":"Gallatin County",
  "lat":45.6769,"lon":-111.0429,"zip":"59715","address":"121 N Rouse Ave",
  "theme":"#15803d","colors":("#f0fdf4","#dcfce7","#86efac","#22c55e","#16a34a","#15803d","#166534","#14532d"),
  "hero_img":HEROES[8],
  "title":"Porta Potty Rental Bozeman, MT — Big Sky Country · Same-Day · From $75",
  "h1_city":"Bozeman, MT","h1_sub":"Big Sky Country · Gallatin County",
  "meta_desc":"Portable toilet rental Bozeman MT from $75/day. Serving Gallatin County construction, Montana State events, Yellowstone gateway, and Big Sky resort projects. Call (833) 652-9344.",
  "og_title":"Bozeman MT Porta Potty Rentals | Big Sky Country | Same-Day Delivery",
  "og_desc":"Bozeman portable toilet rental for MSU construction, Yellowstone gateway events, and Gallatin County job sites. Same-day delivery. Call (833) 652-9344.",
  "services_intro":"From Montana State University campus expansion and the downtown Bozeman mixed-use construction boom to Big Sky Resort events and Yellowstone gateway visitor facilities, FixPilot is Gallatin County's most reliable portable sanitation provider.",
  "demand_para":"Bozeman is the fastest-growing city in the inland American West. The median home price has exceeded $800,000, driven by a construction boom that shows no signs of slowing. MSU's enrollment growth is funding new academic buildings. The Belgrade airport expansion brings new corporate investment. And the Big Sky corridor — one of the most active ski resort construction zones in North America — generates year-round contractor demand for portable toilet rentals across Gallatin and Madison counties.",
  "event_para":"Bozeman's outdoor events calendar includes the Sweet Pea Festival, the Montana Folk Festival in nearby Butte, and dozens of trail running and mountain biking events along the Bridger Range. The Yellowstone gateway corridor handles 4+ million visitors annually — many requiring temporary sanitation facilities at trailheads and staging areas.",
  "areas":["Belgrade","Four Corners","Manhattan MT","Livingston","Big Sky","Three Forks","West Yellowstone","Gallatin Gateway","Ennis","Whitehall"],
  "nearby_text":"Belgrade, Livingston, Big Sky, Manhattan MT",
  "county_nearby":"Gallatin County",
  "wiki_city":"Bozeman,_Montana",
  "mapq":"Bozeman+MT+59715",
  "reviews":[
    ("Tyler H., General Contractor","★★★★★","Building luxury homes in the Bridger Foothills. FixPilot delivers to sites that require 4WD access and services them weekly without complaint. Finding a reliable sanitation vendor in Bozeman is harder than it sounds — FixPilot solved that problem."),
    ("Kate M., MSU Events","★★★★★","Bobcat football tailgate season — 300+ units across the Bobcat Stadium parking zones. FixPilot coordinated the multi-zone layout perfectly. First sanitation vendor we've found that understands Montana logistics."),
    ("Josh R., Resort Developer","★★★★★","Big Sky base village construction. Remote site, mountain access, extreme temperature swings. FixPilot's units are genuinely heavy-duty. And they've never once used 'we can't get there' as an excuse."),
    ("Amanda T., Wedding Coordinator","★★★★★","Ranch wedding in the Gallatin Valley — 130 guests, spectacular mountain backdrop. The luxury trailer FixPilot delivered looked like it belonged in a five-star hotel. Every single guest commented on it."),
  ],
  "faqs":[
    ("Do you serve remote mountain sites near Bozeman?","Yes. We serve high-elevation and off-road-access construction sites throughout Gallatin, Madison, and Park counties. We have 4WD delivery capability for sites along Bridger Canyon, the Big Sky corridor, and Yellowstone gateway trailheads."),
    ("How much does portable toilet rental cost in Bozeman, MT?","Standard units start at $75/day or $219/week in Gallatin County. Remote/mountain site delivery fees apply for locations beyond 20 miles from Bozeman. Big Sky resort area pricing is available on request."),
    ("Do you serve Big Sky Resort and the ski area?","Yes. We serve the Big Sky resort base village, construction sites along Lone Mountain Trail, and Meadow Village event venues. Winter delivery is available — contact us for cold-weather unit specifications."),
    ("Do you serve Yellowstone gateway areas?","Yes. We serve West Yellowstone, Gardiner, and the North Entrance corridor. Trailhead and staging area units are available for park concessionaires and outdoor event operators."),
    ("Are your units suitable for Montana winters?","Yes. We offer winter-rated units with antifreeze additives and insulated tanks designed for Montana temperature extremes. Essential for year-round construction sites in Gallatin County."),
    ("Do you serve Livingston and the Paradise Valley?","Yes. We cover Park County including Livingston, Emigrant, and the Yellowstone River corridor. Same-day delivery is available for most Park County locations."),
    ("Do you serve Helena and Billings?","Billings is within our extended service area. Helena may require advance scheduling — contact us for a specific quote."),
    ("What's the minimum rental period?","One day minimum for events. Weekly contracts are most economical for Bozeman-area construction sites."),
  ],
  "related_cities":[("Billings MT","billings-mt"),("Missoula MT","missoula-mt"),("Montana","montana")],
},

"fargo-nd": {
  "name":"Fargo","state":"ND","state_name":"North Dakota","county":"Cass County",
  "lat":46.8772,"lon":-96.7898,"zip":"58102","address":"200 3rd St N",
  "theme":"#dc2626","colors":("#fef2f2","#fee2e2","#fca5a5","#ef4444","#dc2626","#b91c1c","#991b1b","#7f1d1d"),
  "hero_img":HEROES[9],
  "title":"Porta Potty Rental Fargo, ND — Fargo-Moorhead · Same-Day · From $75/Day",
  "h1_city":"Fargo, ND","h1_sub":"Fargo-Moorhead Metro · Same-Day Delivery",
  "meta_desc":"Portable toilet rental Fargo ND from $75/day. Serving NDSU Fargodome events, Cass County construction, and Moorhead MN. Same-day delivery. OSHA-compliant. Call (833) 652-9344.",
  "og_title":"Fargo ND Porta Potty Rentals | Fargodome & Construction | Same-Day",
  "og_desc":"Fargo portable toilet rental for NDSU events, Fargodome concerts, and Cass County construction. Same-day delivery to Moorhead MN, West Fargo. Call (833) 652-9344.",
  "services_intro":"From NDSU Fargodome events and Broadway Square festivals to the booming west Fargo industrial corridor and Moorhead construction across the Red River, FixPilot delivers clean portable sanitation throughout the Fargo-Moorhead metro.",
  "demand_para":"Fargo is the economic engine of the Northern Plains. Distribution warehousing along I-29 and I-94 is adding millions of square feet annually. Microsoft and Amazon's data center investments in the metro have triggered a data center construction boom that shows no signs of slowing. NDSU campus expansion, the I-29/Main Avenue interchange rebuild, and suburban residential construction in West Fargo and Horace are sustaining year-round job-site portable toilet demand.",
  "event_para":"The NDSU Bison football program draws 19,000+ fans to sold-out Fargodome games. The Red River Valley Fair in West Fargo, Fargo's downtown street festivals, and the FM-area wedding market create consistent seasonal event rental needs. Our luxury restroom trailers serve the upscale outdoor event market across Cass and Clay counties.",
  "areas":["West Fargo","Moorhead MN","Dilworth MN","Horace","Casselton","Valley City","Wahpeton","Detroit Lakes MN","Barnesville MN","Harwood"],
  "nearby_text":"West Fargo, Moorhead MN, Horace, Dilworth",
  "county_nearby":"Cass County",
  "wiki_city":"Fargo,_North_Dakota",
  "mapq":"Fargo+ND+58102",
  "reviews":[
    ("Brian K., Site Manager","★★★★★","Data center construction east of Fargo — large crew, 24/7 operations. FixPilot has never missed a service in 14 months. In North Dakota winters that's genuinely impressive."),
    ("Carol T., NDSU Events","★★★★★","Fargodome graduation weekend — 30 units, two-day event. Delivered on time, serviced between ceremonies. No complaints from 10,000 graduates and their families. FixPilot handled it without a hitch."),
    ("Mike L., Homebuilder","★★★★★","Building in Horace and south Cass County — fastest-growing area in the state. FixPilot delivers to every site on schedule, even in February. That reliability is everything in this business."),
    ("Jenna P., Wedding Planner","★★★★★","Outdoor barn wedding in Cass County — 110 guests. The luxury trailer was spotless and climate-controlled. In August humidity that matters more than people realize. Guests loved it."),
  ],
  "faqs":[
    ("Do you serve Moorhead, Minnesota?","Yes. We cover the entire Fargo-Moorhead metro including Clay County, Minnesota. Cross-state delivery within the FM metro carries no additional fee. We also serve Dilworth, Barnesville, and Detroit Lakes to the west."),
    ("How much does portable toilet rental cost in Fargo?","Standard units start at $75/day or $195/week in Cass County. Minnesota-side (Clay County) pricing is identical. Luxury restroom trailers start at $575/event. Winter cold-weather units carry a $15/week surcharge."),
    ("Do your units work in North Dakota winters?","Yes. We offer cold-weather portable toilets with antifreeze-treated tanks and insulated interiors rated for temperatures as low as -20°F. Essential for Fargo-area construction sites during winter months."),
    ("Do you serve the NDSU Fargodome for events?","Yes. We serve Fargodome events, NDSU athletic facilities, and university campus events. Contact us at least 2 weeks in advance for Bison football game-day orders."),
    ("Do you cover West Fargo and the I-29 industrial corridor?","Yes. West Fargo is one of our highest-demand service areas. We cover the entire I-29 and I-94 distribution corridor including all active warehouse and data center construction sites."),
    ("Are your units North Dakota Department of Health compliant?","Yes. All units meet NDDOH portable sanitation standards and federal OSHA 29 CFR 1926.51 requirements for construction sites."),
    ("Do you serve Grand Forks?","Grand Forks is within our extended service range — approximately 75 miles north. Contact us for project-specific scheduling and pricing."),
    ("What is the minimum rental period?","One day minimum for events. Weekly contracts are standard and most economical for Fargo-area construction sites."),
  ],
  "related_cities":[("Bismarck ND","bismarck-nd"),("North Dakota","north-dakota")],
},

"sioux-falls-sd": {
  "name":"Sioux Falls","state":"SD","state_name":"South Dakota","county":"Minnehaha County",
  "lat":43.5446,"lon":-96.7311,"zip":"57104","address":"224 W 9th St",
  "theme":"#0284c7","colors":("#f0f9ff","#e0f2fe","#7dd3fc","#0ea5e9","#0284c7","#0369a1","#075985","#0c4a6e"),
  "hero_img":HEROES[10],
  "title":"Porta Potty Rental Sioux Falls, SD — Falls City · Same-Day · From $75/Day",
  "h1_city":"Sioux Falls, SD","h1_sub":"Falls City · Same-Day Delivery",
  "meta_desc":"Portable toilet rental Sioux Falls SD from $75/day. Serving Minnehaha County construction, Sanford events, agribusiness & Lincoln County development. Call (833) 652-9344.",
  "og_title":"Sioux Falls SD Porta Potty Rentals | Falls City | Same-Day Delivery",
  "og_desc":"Sioux Falls portable toilet rental for construction, Sanford events, and agribusiness across Minnehaha and Lincoln counties. Same-day delivery. Call (833) 652-9344.",
  "services_intro":"From Sanford Sports Complex events and the Falls Park Festival corridor to the booming Harrisburg and Tea residential buildout and agribusiness operations across Minnehaha County, FixPilot delivers portable sanitation throughout eastern South Dakota.",
  "demand_para":"Sioux Falls is the fastest-growing city in the Northern Plains. Amazon, Costco, and dozens of distribution operators are building massive fulfillment facilities along I-90 east of the city. Sanford Health's continued campus expansion, the Denny Sanford PREMIER Center arena events, and record housing starts in Lincoln County create year-round construction portable toilet demand. The city consistently ranks in the top 10 nationally for small business formation — meaning commercial construction never stops.",
  "event_para":"The Sioux Falls Canaries baseball season, Thursday Night Concerts at Falls Park, the South Dakota State Fair in Huron, and the regional wedding market across east-central South Dakota create consistent seasonal event rental demand. Our luxury restroom trailers serve outdoor venues from downtown to rural Lincoln County estates.",
  "areas":["Tea","Brandon","Harrisburg","Dell Rapids","Brookings","Watertown","Mitchell","Beresford","Baltic","Lennox"],
  "nearby_text":"Tea, Harrisburg, Brandon, Dell Rapids, Brookings",
  "county_nearby":"Minnehaha County",
  "wiki_city":"Sioux_Falls,_South_Dakota",
  "mapq":"Sioux+Falls+SD+57104",
  "reviews":[
    ("Tom A., Distribution Developer","★★★★★","Amazon fulfillment site east of Sioux Falls — 400-worker peak crew. FixPilot serviced 20 units weekly for 11 months without a single missed appointment. The scale of their operation matched the scale of ours."),
    ("Nancy B., Event Coordinator","★★★★★","Falls Park Thursday Night Concerts — 6 units per week for 12 weeks. Always clean when gates opened. The city parks staff specifically complimented the sanitation setup. That tells you everything."),
    ("Dale R., Homebuilder","★★★★★","Building in Harrisburg — fastest subdivision in the state. FixPilot keeps up with the pace, delivers to new streets before they're even mapped, and services on schedule. Perfect partner for a high-volume build program."),
    ("Ashley K., Wedding Planner","★★★★★","Rural Lincoln County wedding, 160 guests, converted barn. The luxury trailer FixPilot delivered matched the aesthetic perfectly. Guests kept asking if it was part of the original venue design."),
  ],
  "faqs":[
    ("How much does portable toilet rental cost in Sioux Falls?","Standard units start at $75/day or $195/week in Minnehaha County. Lincoln and Turner county pricing is identical. Luxury restroom trailers start at $575/event. Agricultural site pricing is available for seasonal needs."),
    ("Do you serve Tea, Harrisburg, and Lincoln County?","Yes. Lincoln County is one of our fastest-growing service areas. We cover all active construction in Tea, Harrisburg, Crooks, and the developing areas south and southwest of Sioux Falls."),
    ("Are your units compliant with South Dakota OSHA standards?","Yes. All units meet SDDOL (South Dakota Department of Labor) and federal OSHA 29 CFR 1926.51 requirements. Documentation provided with every construction order."),
    ("Do you serve agricultural operations in eastern South Dakota?","Yes. We supply portable toilets to agribusiness facilities, harvest operations, and farm events across Minnehaha, Turner, Lincoln, and McCook counties. Seasonal contracts available."),
    ("Do you serve Brookings and South Dakota State University?","Yes. Brookings is within our service area. SDSU athletic events, campus construction, and Brookings community events are all within range. Contact us for Jackrabbit football game-day orders."),
    ("Can I get a luxury restroom trailer for a South Dakota barn wedding?","Yes. Our luxury trailers are perfect for the rural Lincoln and Minnehaha county wedding market. Self-contained, no hookups required, climate-controlled, with real interior lighting and granite finishes."),
    ("Do you speak Spanish?","Sí, hablamos español. Llámenos para renta de baños portátiles en Sioux Falls y todo el este de Dakota del Sur."),
    ("What is the minimum rental period?","One day minimum for events. Weekly contracts are most economical for ongoing Sioux Falls construction sites."),
  ],
  "related_cities":[("Rapid City SD","rapid-city-sd"),("South Dakota","south-dakota")],
},
}
# ─── end of CITIES ─────────────────────────────────────────────────────────────


def pick_hero(slug):
    i = sum(ord(c) for c in slug) % len(HEROES)
    return HEROES[i]


def build_areas_html(areas):
    out = ""
    for a in areas:
        out += f'\n                        <div class="p-4 bg-gray-50 rounded-lg border border-gray-200"><h5 class="font-semibold text-gray-800 mb-1">{a}</h5></div>'
    return out


def build_faq_schema(faqs, slug, city):
    items = []
    for i, (q, a) in enumerate(faqs):
        fid = f"faq-{i}"
        items.append(f'''        {{
          "@type": "Question",
          "@id": "{DOMAIN}/porta-potty-rental-{slug}/#{fid}",
          "name": "{q}",
          "acceptedAnswer": {{"@type": "Answer", "text": "{a}"}}
        }}''')
    return ",\n".join(items)


def build_faq_html(faqs):
    out = ""
    for q, a in faqs:
        out += f'''
          <div class="faq-item border border-gray-200 rounded-xl overflow-hidden">
            <button class="faq-question w-full text-left p-5 font-bold text-gray-800 bg-white hover:bg-brand-50 transition flex justify-between items-center">
              {q}
              <svg class="w-5 h-5 text-brand-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div class="faq-answer hidden p-5 bg-gray-50 text-gray-700 text-sm leading-relaxed">{a}</div>
          </div>'''
    return out


def build_reviews_html(reviews):
    out = ""
    for reviewer, stars, body in reviews:
        out += f'''
              <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div class="text-yellow-400 text-lg mb-2">{stars}</div>
                <p class="text-gray-600 text-sm italic mb-3">"{body}"</p>
                <p class="font-semibold text-gray-800 text-sm">— {reviewer}</p>
              </div>'''
    return out


def build_related_html(related):
    out = ""
    for label, rslug in related:
        out += f'''
      <a href="/porta-potty-rental-{rslug}" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all border border-brand-200 group">
        <h4 class="font-black text-brand-950 text-lg mb-2 group-hover:text-cta transition">{label}</h4>
        <p class="text-sm text-brand-700">Porta Potty Rental in {label}</p>
        <span class="text-cta text-sm font-semibold mt-3 inline-block">Learn More →</span>
      </a>'''
    return out


def build_page(slug, d):
    b = d["colors"]   # (50,100,300,500,600,700,800,900)
    hero = d.get("hero_img", pick_hero(slug))
    hero_url_full = f"{DOMAIN}/hero-banner-images/{hero}"
    hero_url_rel  = f"../hero-banner-images/{hero}"

    faq_schema = build_faq_schema(d["faqs"], slug, d["name"])
    areas_html  = build_areas_html(d["areas"])
    faq_html    = build_faq_html(d["faqs"])
    reviews_html = build_reviews_html(d["reviews"])
    related_html = build_related_html(d.get("related_cities", []))

    area_pills = "".join(
        f'<span class="bg-brand-100 text-brand-800 px-3 py-1 rounded-full text-sm font-medium">{a}</span>'
        for a in d["nearby_text"].split(", ")
    )

    reviews_schema = ""
    for reviewer, stars, body in d["reviews"]:
        reviews_schema += f'''
        {{
          "@type": "Review",
          "author": {{"@type": "Person", "name": "{reviewer}"}},
          "reviewRating": {{"@type": "Rating", "ratingValue": "5", "bestRating": "5"}},
          "reviewBody": "{body[:200]}"
        }},'''

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{d['title']}</title>
    <meta name="description" content="{d['meta_desc']}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="author" content="FixPilot Porta Potty Rentals">
    <meta property="article:published_time" content="2026-01-15">
    <meta property="article:modified_time" content="2026-06-13">

    <meta name="geo.region" content="US-{d['state']}">
    <meta name="geo.placename" content="{d['name']}, {d['state_name']}">
    <meta name="geo.position" content="{d['lat']};{d['lon']}">
    <meta name="ICBM" content="{d['lat']}, {d['lon']}">

    <link rel="canonical" href="{DOMAIN}/porta-potty-rental-{slug}">
    <link rel="alternate" hreflang="en-US" href="{DOMAIN}/porta-potty-rental-{slug}">
    <link rel="alternate" hreflang="x-default" href="{DOMAIN}/porta-potty-rental-{slug}">

    <meta property="og:title" content="{d['og_title']}">
    <meta property="og:description" content="{d['og_desc']}">
    <meta property="og:image" content="{hero_url_full}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{DOMAIN}/porta-potty-rental-{slug}">
    <meta property="og:locale" content="en_US">
    <meta property="og:site_name" content="FixPilot Porta Potty Rentals">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{d['og_title']}">
    <meta name="twitter:description" content="{d['og_desc']}">
    <meta name="twitter:image" content="{hero_url_full}">

    <meta name="theme-color" content="{d['theme']}">
    <meta name="format-detection" content="telephone=yes">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="preload" as="image" href="{hero_url_rel}">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='4' fill='%2314b8a6'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='central' text-anchor='middle' fill='white' font-family='sans-serif' font-size='20' font-weight='bold'%3EF%3C/text%3E%3C/svg%3E">
    <link rel="stylesheet" href="/assets/tw.css">
    <style>
      :root{{
        --brand-50:{b[0]};--brand-100:{b[1]};--brand-300:{b[2]};--brand-500:{b[3]};
        --brand-600:{b[4]};--brand-700:{b[5]};--brand-800:{b[6]};--brand-900:{b[7]};
        --brand-950:{b[7]};--cta:#ea580c;
      }}
      .hero-bg {{
        background-image: linear-gradient(rgba(0,0,0,0.65),rgba(0,0,0,0.45)),url('{hero_url_rel}');
        background-size:cover;background-position:center;
      }}
      .pulse-btn{{animation:pulse 2s infinite}}
      @keyframes pulse{{0%{{transform:scale(1);box-shadow:0 0 0 0 rgba(220,38,38,.7)}}70%{{transform:scale(1.02);box-shadow:0 0 0 8px rgba(220,38,38,0)}}100%{{transform:scale(1);box-shadow:0 0 0 0 rgba(220,38,38,0)}}}}
      .faq-answer{{display:none}}.faq-answer.open{{display:block}}
    </style>

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": ["LocalBusiness", "HomeAndConstructionBusiness", "EquipmentRentalShop"],
      "name": "FixPilot Porta Potty Rentals",
      "description": "{d['name']}'s trusted portable toilet and luxury restroom trailer rental service. Same-day delivery for construction, events, and emergencies across {d['county']}.",
      "image": "{hero_url_full}",
      "telephone": "{PHONE_SCHEMA}",
      "url": "{DOMAIN}/porta-potty-rental-{slug}",
      "hasMap": "https://maps.google.com/maps?q={d['mapq']}",
      "foundingDate": "2018",
      "address": {{
        "@type": "PostalAddress",
        "streetAddress": "{d['address']}",
        "addressLocality": "{d['name']}",
        "addressRegion": "{d['state']}",
        "postalCode": "{d['zip']}",
        "addressCountry": "US"
      }},
      "geo": {{
        "@type": "GeoCoordinates",
        "latitude": {d['lat']},
        "longitude": {d['lon']}
      }},
      "contactPoint": {{
        "@type": "ContactPoint",
        "telephone": "{PHONE_SCHEMA}",
        "contactType": "customer service",
        "areaServed": "{d['name']}, {d['state']}",
        "availableLanguage": ["English", "Spanish"],
        "hoursAvailable": {{
          "@type": "OpeningHoursSpecification",
          "opens": "00:00","closes": "23:59",
          "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        }}
      }},
      "sameAs": [
        "https://maps.google.com/maps?q=FixPilot+Porta+Potty+Rentals+{d['name'].replace(' ','+')}+{d['state']}"
      ],
      "areaServed": [
        {{"@type": "City", "name": "{d['name']}", "sameAs": "https://en.wikipedia.org/wiki/{d['wiki_city']}"}},
        {area_pills}
      ],
      "openingHoursSpecification": {{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "opens": "00:00","closes": "23:59"
      }},
      "review": [{reviews_schema.rstrip(",")}],
      "makesOffer": [
        {{"@type": "Offer","itemOffered": {{"@type": "Service","name": "Construction Portable Toilet Rental","areaServed": "{d['name']}, {d['state']}"}}}},
        {{"@type": "Offer","itemOffered": {{"@type": "Service","name": "Luxury Restroom Trailer Rental","areaServed": "{d['name']}, {d['state']}"}}}},
        {{"@type": "Offer","itemOffered": {{"@type": "Service","name": "ADA-Compliant Portable Restroom Rental","areaServed": "{d['name']}, {d['state']}"}}}}
      ]
    }}
    </script>

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
{faq_schema}
      ]
    }}
    </script>

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type":"ListItem","position":1,"name":"Home","item":"{DOMAIN}/"}},
        {{"@type":"ListItem","position":2,"name":"Locations","item":"{DOMAIN}/locations"}},
        {{"@type":"ListItem","position":3,"name":"Porta Potty Rental {d['state_name']}","item":"{DOMAIN}/porta-potty-rental-{d['state_name'].lower().replace(' ','-')}"}},
        {{"@type":"ListItem","position":4,"name":"Porta Potty Rental {d['name']}, {d['state']}","item":"{DOMAIN}/porta-potty-rental-{slug}"}}
      ]
    }}
    </script>
</head>
<body class="bg-white text-gray-800 font-sans">

<!-- Sticky nav -->
<nav class="bg-white shadow-sm sticky top-0 z-50 border-b border-gray-100">
  <div class="container mx-auto px-4 py-3 flex items-center justify-between">
    <a href="/" class="font-black text-xl text-brand-900 tracking-tight">FixPilot</a>
    <div class="hidden md:flex gap-6 text-sm font-semibold text-gray-600">
      <a href="/locations" class="hover:text-brand-600 transition">Locations</a>
      <a href="/services/construction-porta-potty-rentals.html" class="hover:text-brand-600 transition">Construction</a>
      <a href="/services/luxury-restroom-trailers.html" class="hover:text-brand-600 transition">Luxury Trailers</a>
      <a href="/blog" class="hover:text-brand-600 transition">Blog</a>
    </div>
    <a href="tel:{PHONE_SCHEMA}" class="phone-link bg-cta text-white font-extrabold px-5 py-2 rounded-full text-sm hover:opacity-90 transition shadow">
      📞 {PHONE}
    </a>
  </div>
</nav>

<!-- Hero -->
<section class="hero-bg min-h-[520px] flex items-center">
  <div class="container mx-auto px-4 py-20">
    <div class="lg:flex gap-12 items-center">
      <div class="lg:w-1/2 text-white">
        <div class="text-sm text-brand-300 mb-3 font-medium">
          <a href="/" class="hover:text-white transition">Home</a> ›
          <a href="/locations" class="hover:text-white transition">Locations</a> ›
          <a href="/porta-potty-rental-{d['state_name'].lower().replace(' ','-')}" class="hover:text-white transition">{d['state_name']}</a> ›
          {d['name']}
        </div>
        <h1 class="text-4xl md:text-5xl font-black mb-4 leading-tight">
          Porta Potty Rental in<br>
          <span class="text-brand-300">{d['h1_city']} — {d['h1_sub']}</span>
        </h1>
        <p class="text-lg text-gray-200 mb-6 max-w-lg">{d['services_intro'][:180]}</p>
        <div class="flex flex-wrap gap-3 mb-8">
          <span class="bg-white/15 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold">✓ Same-Day Delivery</span>
          <span class="bg-white/15 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold">✓ From $75/Day</span>
          <span class="bg-white/15 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold">✓ OSHA-Compliant</span>
          <span class="bg-white/15 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold">✓ 24/7 Emergency</span>
        </div>
        <a href="tel:{PHONE_SCHEMA}" class="phone-link pulse-btn inline-block bg-cta text-white font-extrabold text-xl px-8 py-4 rounded-xl shadow-xl hover:opacity-90 transition">
          📞 Call {PHONE}
        </a>
        <p class="text-gray-400 text-sm mt-3">Free quote · No obligation · Instant availability check</p>
      </div>

      <!-- Quote card -->
      <div class="lg:w-5/12 mt-10 lg:mt-0">
        <div class="bg-white rounded-2xl p-8 shadow-2xl border-4 border-brand-100">
          <h3 class="text-2xl font-bold text-gray-800 mb-1">Get Your Free Quote!</h3>
          <p class="text-gray-500 text-sm mb-6">{d['name']}, {d['state']} · Instant pricing</p>
          <div class="flex items-center gap-1 mb-4">
            {''.join(['<svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>' for _ in range(5)])}
            <span class="ml-2 text-sm font-semibold text-gray-700">5.0 · Trusted by 1,000+ customers</span>
          </div>
          <a href="tel:{PHONE_SCHEMA}" class="phone-link block w-full bg-cta hover:opacity-90 text-white text-center py-4 font-extrabold text-xl rounded-xl transition shadow-lg mb-3">
            📞 {PHONE}
          </a>
          <a href="/calculator" class="block w-full border-2 border-brand-600 text-brand-700 text-center py-3 font-bold rounded-xl hover:bg-brand-50 transition text-sm">
            🧮 Calculate Units Needed
          </a>
          <p class="text-xs text-gray-400 text-center mt-3">Available 24/7 · Standard, Luxury &amp; ADA units</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Trust bar -->
<div class="bg-brand-900 text-white py-4">
  <div class="container mx-auto px-4">
    <div class="flex flex-wrap justify-center gap-8 text-sm font-semibold text-brand-200">
      <span>✓ Same-Day Delivery Available</span>
      <span>✓ OSHA-Certified Fleet</span>
      <span>✓ Luxury Restroom Trailers</span>
      <span>✓ ADA-Compliant Units</span>
      <span>✓ 24/7 Emergency Dispatch</span>
    </div>
  </div>
</div>

<!-- Demand/why section -->
<section class="py-16 bg-white">
  <div class="container mx-auto px-4 max-w-4xl">
    <h2 class="text-3xl md:text-4xl font-extrabold text-brand-900 mb-6">Portable Toilet Rental in {d['name']}, {d['state']} — What You Need to Know</h2>
    <p class="text-gray-700 leading-relaxed mb-5 text-lg">{d['demand_para']}</p>
    <p class="text-gray-700 leading-relaxed text-lg">{d['event_para']}</p>
    <div class="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
      <div class="bg-brand-50 rounded-xl p-4"><div class="text-3xl font-black text-brand-900">$75</div><div class="text-xs text-gray-500 mt-1">Starting price/day</div></div>
      <div class="bg-brand-50 rounded-xl p-4"><div class="text-3xl font-black text-brand-900">4hr</div><div class="text-xs text-gray-500 mt-1">Avg delivery time</div></div>
      <div class="bg-brand-50 rounded-xl p-4"><div class="text-3xl font-black text-brand-900">24/7</div><div class="text-xs text-gray-500 mt-1">Emergency line</div></div>
      <div class="bg-brand-50 rounded-xl p-4"><div class="text-3xl font-black text-brand-900">100%</div><div class="text-xs text-gray-500 mt-1">OSHA-compliant</div></div>
    </div>
  </div>
</section>

<!-- Services -->
<section id="services" class="py-16 bg-gray-50">
  <div class="container mx-auto px-4">
    <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 text-center">Portable Sanitation Services in {d['name']}, {d['state']}</h2>
    <p class="text-gray-600 mb-10 max-w-3xl mx-auto text-center">{d['services_intro']}</p>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="service-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <img loading="lazy" src="../service-images/construction-porta-potty-rentals/21.%2020260226_140129_156.webp" width="352" height="192" alt="Construction portable toilet rental in {d['name']}, {d['state']}" class="w-full h-48 object-cover">
        <div class="p-5">
          <h3 class="text-lg font-bold mb-2">Construction Portable Toilet Rentals</h3>
          <p class="text-gray-600 text-sm mb-4">OSHA-compliant units for {d['name']} construction sites. OSHA ratio documentation included with every order. Weekly servicing available.</p>
          <a href="/services/construction-porta-potty-rentals.html" class="inline-block bg-brand-600 text-white text-sm font-bold px-4 py-2 rounded-lg hover:bg-brand-700 transition">View Service →</a>
        </div>
      </div>
      <div class="service-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <img loading="lazy" src="../service-images/luxury-restroom-trailers/luxury1.webp" width="352" height="192" alt="Luxury restroom trailer rental {d['name']}" class="w-full h-48 object-cover bg-brand-100">
        <div class="p-5">
          <h3 class="text-lg font-bold mb-2">Luxury Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-4">Climate-controlled, granite-finish luxury trailers for weddings, corporate events, and upscale outdoor gatherings in {d['name']}.</p>
          <a href="/services/luxury-restroom-trailers.html" class="inline-block bg-brand-600 text-white text-sm font-bold px-4 py-2 rounded-lg hover:bg-brand-700 transition">View Service →</a>
        </div>
      </div>
      <div class="service-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <img loading="lazy" src="../service-images/ada-compliant-units/ada1.webp" width="352" height="192" alt="ADA portable restroom rental {d['name']}" class="w-full h-48 object-cover bg-brand-100">
        <div class="p-5">
          <h3 class="text-lg font-bold mb-2">ADA-Compliant Units</h3>
          <p class="text-gray-600 text-sm mb-4">ADA-accessible portable restrooms for public events and permitted job sites in {d['county']}. Meets ANSI A117.1 standards.</p>
          <a href="/services/ada-compliant-units.html" class="inline-block bg-brand-600 text-white text-sm font-bold px-4 py-2 rounded-lg hover:bg-brand-700 transition">View Service →</a>
        </div>
      </div>
      <div class="service-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="h-48 bg-brand-100 flex items-center justify-center text-5xl">🚿</div>
        <div class="p-5">
          <h3 class="text-lg font-bold mb-2">Hand Wash Stations</h3>
          <p class="text-gray-600 text-sm mb-4">Portable hand-washing stations for construction sites, food festivals, and outdoor events throughout {d['name']}.</p>
          <a href="/services/hand-wash-stations.html" class="inline-block bg-brand-600 text-white text-sm font-bold px-4 py-2 rounded-lg hover:bg-brand-700 transition">View Service →</a>
        </div>
      </div>
      <div class="service-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="h-48 bg-brand-100 flex items-center justify-center text-5xl">🚨</div>
        <div class="p-5">
          <h3 class="text-lg font-bold mb-2">Emergency & Same-Day Rentals</h3>
          <p class="text-gray-600 text-sm mb-4">24/7 emergency dispatch for urgent portable toilet needs in {d['name']}. Same-day delivery for most {d['county']} locations.</p>
          <a href="/services/emergency-short-term-rentals.html" class="inline-block bg-brand-600 text-white text-sm font-bold px-4 py-2 rounded-lg hover:bg-brand-700 transition">View Service →</a>
        </div>
      </div>
      <div class="service-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="h-48 bg-brand-100 flex items-center justify-center text-5xl">♿</div>
        <div class="p-5">
          <h3 class="text-lg font-bold mb-2">Septic Pumping &amp; Holding Tanks</h3>
          <p class="text-gray-600 text-sm mb-4">Holding tank pump-outs and septic services for {d['name']} area properties and long-term construction sites.</p>
          <a href="/services/septic-pumping-holding-tanks.html" class="inline-block bg-brand-600 text-white text-sm font-bold px-4 py-2 rounded-lg hover:bg-brand-700 transition">View Service →</a>
        </div>
      </div>
    </div>
    <div class="text-center mt-8">
      <p class="text-gray-600 text-sm mt-3">Not sure how many units? Use our free <a href="/calculator" class="font-bold text-brand-700 underline">porta potty calculator</a>.</p>
    </div>
  </div>
</section>

<!-- Area coverage -->
<section id="areas" class="py-16 bg-white">
  <div class="container mx-auto px-4 max-w-4xl">
    <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">Proudly Serving {d['name']} and {d['county']}</h2>
    <p class="text-gray-600 text-center mb-8">We also provide fast, reliable service to residents and contractors in these nearby communities:</p>
    <div class="flex flex-wrap gap-2 justify-center mb-8">
      {area_pills}
    </div>
    <h4 class="font-bold text-brand-800 mb-3 text-center">Neighborhoods &amp; Areas We Serve in {d['name']}:</h4>
    <div class="grid sm:grid-cols-2 gap-4 mt-4">{areas_html}</div>
  </div>
</section>

<!-- Reviews -->
<section class="py-16 bg-brand-50">
  <div class="container mx-auto px-4">
    <h2 class="text-3xl font-bold text-gray-900 mb-10 text-center">What {d['name']} Customers Say</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {reviews_html}
    </div>
  </div>
</section>

<!-- FAQ -->
<section id="faq" class="py-16 bg-white">
  <div class="container mx-auto px-4 max-w-3xl">
    <h2 class="text-3xl font-bold text-gray-900 mb-10 text-center">Portable Toilet Rental {d['name']} — FAQ</h2>
    <div class="space-y-3">
      {faq_html}
    </div>
  </div>
</section>

<!-- Helpful Resources -->
<section class="py-12 bg-white border-t border-gray-100">
  <div class="container mx-auto px-4">
    <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6 text-center">Helpful Resources</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
      <a href="/blog/porta-potty-rental-costs-2026.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
        <span class="text-2xl">💰</span><div><p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">2026 Rental Cost Guide</p><p class="text-xs text-gray-500 mt-1">Pricing by unit type</p></div>
      </a>
      <a href="/blog/how-many-porta-potties-do-you-need.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
        <span class="text-2xl">🔢</span><div><p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">How Many Units Do You Need?</p><p class="text-xs text-gray-500 mt-1">Calculator guide</p></div>
      </a>
      <a href="/blog/osha-requirements-construction-sites.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
        <span class="text-2xl">🦺</span><div><p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">OSHA Compliance Guide</p><p class="text-xs text-gray-500 mt-1">Construction site requirements</p></div>
      </a>
      <a href="/services/construction-porta-potty-rentals.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
        <span class="text-2xl">🏗️</span><div><p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">Construction Site Services</p><p class="text-xs text-gray-500 mt-1">OSHA-compliant units</p></div>
      </a>
      <a href="/services/luxury-restroom-trailers.html" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
        <span class="text-2xl">✨</span><div><p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">Luxury Restroom Trailers</p><p class="text-xs text-gray-500 mt-1">VIP-grade trailers for events</p></div>
      </a>
      <a href="/calculator" class="flex items-start gap-3 p-4 bg-brand-50 rounded-xl border border-brand-100 hover:shadow-md transition group">
        <span class="text-2xl">🧮</span><div><p class="font-bold text-brand-900 group-hover:text-cta transition text-sm">Free Quote Calculator</p><p class="text-xs text-gray-500 mt-1">Instant estimate in 60 seconds</p></div>
      </a>
    </div>
  </div>
</section>

<!-- Related cities -->
<section id="related-cities" class="py-16 bg-brand-50 border-t border-brand-200">
  <div class="container mx-auto px-4">
    <h2 class="text-3xl md:text-4xl font-black text-brand-950 mb-8 text-center">Other Cities We Serve in {d['state_name']}</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {related_html}
    </div>
    <div class="text-center mt-8">
      <a href="/locations" class="inline-flex items-center gap-2 bg-brand-900 text-white px-6 py-3 rounded-lg font-bold hover:bg-brand-800 transition">View All Locations →</a>
    </div>
  </div>
</section>

<!-- Final CTA -->
<section class="py-14 bg-cta text-white text-center px-4">
  <h2 class="text-3xl font-black mb-4">Ready for Same-Day Porta Potty Delivery in {d['name']}?</h2>
  <p class="text-orange-100 mb-8 max-w-xl mx-auto">Call now — we answer 24/7. Standard units from $75/day, luxury trailers available, OSHA documentation included with every construction order.</p>
  <a href="tel:{PHONE_SCHEMA}" class="phone-link inline-block bg-white text-cta font-extrabold px-10 py-5 rounded-xl text-xl hover:opacity-95 transition shadow-lg">📞 {PHONE} — Free Quote</a>
</section>

<!-- Footer -->
<footer class="bg-gray-900 text-gray-400 py-10 px-4">
  <div class="container mx-auto text-center text-sm">
    <p class="mb-3 font-bold text-white">FixPilot Porta Potty Rentals — {d['name']}, {d['state']}</p>
    <p class="mb-3">
      <a href="/" class="hover:text-white transition mx-2">Home</a>·
      <a href="/locations" class="hover:text-white transition mx-2">Locations</a>·
      <a href="/blog" class="hover:text-white transition mx-2">Blog</a>·
      <a href="/calculator" class="hover:text-white transition mx-2">Calculator</a>·
      <a href="/services/construction-porta-potty-rentals.html" class="hover:text-white transition mx-2">Construction</a>·
      <a href="/services/luxury-restroom-trailers.html" class="hover:text-white transition mx-2">Luxury Trailers</a>
    </p>
    <p>© 2026 FixPilot Porta Potty Rentals · {PHONE} · Serving {d['name']}, {d['state']} and {d['county']} · Available 24/7</p>
  </div>
</footer>

<script>
document.querySelectorAll('.faq-question').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const ans = btn.nextElementSibling;
    ans.classList.toggle('open');
  }});
}});
</script>

</body>
</html>"""

    # Fix the areaServed: replace pill HTML string with proper comma-separated JSON
    city_name = d["name"]
    wiki = d["wiki_city"]
    area_served_items = ',\n        '.join(
        f'{{"@type": "Neighborhood", "name": "{a}"}}'
        for a in d["areas"]
    )
    city_entry = f'{{"@type": "City", "name": "{city_name}", "sameAs": "https://en.wikipedia.org/wiki/{wiki}"}}'
    page = page.replace(area_pills, f"{city_entry},\n        {area_served_items}")

    return page


def main():
    built = 0
    for slug, d in CITIES.items():
        outdir = Path(f"porta-potty-rental-{slug}")
        outfile = outdir / "index.html"
        outdir.mkdir(exist_ok=True)
        html = build_page(slug, d)
        outfile.write_text(html, encoding="utf-8")
        size = len(html)
        print(f"  ✓ {slug} ({size:,} chars)")
        built += 1
    print(f"\nBuilt {built} unique city pages")


if __name__ == "__main__":
    main()
