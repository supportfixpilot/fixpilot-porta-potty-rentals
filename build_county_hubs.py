#!/usr/bin/env python3
"""Build top-10 county hub pages.

Each county hub:
  - URL  /porta-potty-rental-{county-slug}/
  - lists cities in our network within that county + nearby counties' cities
  - includes county-specific notes (population, major employers, regulatory)

Reuses the state-hub layout pattern.
"""
from __future__ import annotations
import os

# (county_slug, county_full, state_code, state_full, lat, lon,
#  cities_in_county [(name, slug)], nearby_county_cities [(name, slug, county)])
COUNTIES = [
    ("harris-county-tx", "Harris County", "TX", "Texas", 29.86, -95.39,
     [("Houston", "houston-tx"), ("Pasadena", "pasadena-tx" )],
     [("The Woodlands", "the-woodlands-tx", "Montgomery County"),
      ("Sugar Land", "sugar-land-tx", "Fort Bend County"),
      ("Pearland", "pearland-tx", "Brazoria County"),
      ("League City", "league-city-tx", "Galveston County")],
     "Harris County is the most populous county in Texas (4.7M residents) and home to the Houston metro economy — energy, healthcare, the Texas Medical Center, NRG Stadium, the Port of Houston. We dispatch fleets daily to construction, energy, and event sites across the county."),

    ("dallas-county-tx", "Dallas County", "TX", "Texas", 32.78, -96.80,
     [("Dallas", "dallas-tx"), ("Garland", "garland-tx"), ("Irving", "irving-tx"),
      ("Mesquite", "mesquite-tx"), ("Carrollton", "carrollton-tx"),
      ("Grand Prairie", "grand-prairie-tx")],
     [("Plano", "plano-tx", "Collin County"),
      ("Frisco", "frisco-tx", "Collin County"),
      ("Fort Worth", "fort-worth-tx", "Tarrant County"),
      ("Arlington", "arlington-tx", "Tarrant County")],
     "Dallas County (~2.6M residents) anchors the eastern half of the DFW metroplex. Heavy commercial construction, a major event calendar, and one of the most active wedding markets in Texas. Our DFW fleet covers same-day delivery throughout the county."),

    ("tarrant-county-tx", "Tarrant County", "TX", "Texas", 32.76, -97.32,
     [("Fort Worth", "fort-worth-tx"), ("Arlington", "arlington-tx")],
     [("Dallas", "dallas-tx", "Dallas County"),
      ("Grand Prairie", "grand-prairie-tx", "Dallas County"),
      ("Mansfield", "mansfield-tx", "Tarrant County")],
     "Tarrant County (~2.1M residents) is the western half of DFW — Fort Worth, Arlington, the Stockyards, AT&T Stadium, Globe Life Field. Construction and event sanitation are our highest-volume use cases here."),

    ("travis-county-tx", "Travis County", "TX", "Texas", 30.27, -97.74,
     [("Austin", "austin-tx")],
     [("Round Rock", "round-rock-tx", "Williamson County"),
      ("Cedar Park", "cedar-park-tx", "Williamson County"),
      ("Pflugerville", "pflugerville-tx", "Travis County"),
      ("San Marcos", "san-marcos-tx", "Hays County")],
     "Travis County is Austin and the live-music capital of Texas. SXSW, ACL, F1 weekend, Q2 Stadium events drive massive seasonal sanitation demand. Pre-book during peak event windows for best pricing."),

    ("los-angeles-county-ca", "Los Angeles County", "CA", "California", 34.05, -118.24,
     [("Los Angeles", "los-angeles-ca"), ("Long Beach", "long-beach-ca"),
      ("Glendale", "glendale-ca"), ("Lakewood", "lakewood-ca")],
     [("Anaheim", "anaheim-ca", "Orange County"),
      ("Santa Ana", "santa-ana-ca", "Orange County"),
      ("Irvine", "irvine-ca", "Orange County"),
      ("Riverside", "riverside-ca", "Riverside County")],
     "Los Angeles County (~10M residents) is the largest county in the United States. Heavy film and TV production, year-round event calendar, large construction pipeline. Our LA county fleet handles honeywagons, talent restrooms, and standard units at the same pace."),

    ("maricopa-county-az", "Maricopa County", "AZ", "Arizona", 33.45, -112.07,
     [("Phoenix", "phoenix-az"), ("Mesa", "mesa-az"), ("Chandler", "chandler-az"),
      ("Scottsdale", "scottsdale-az"), ("Gilbert", "gilbert-az"), ("Tempe", "tempe-az"),
      ("Surprise", "surprise-az")],
     [("Tucson", "tucson-az", "Pima County")],
     "Maricopa County (~4.5M residents) is the Phoenix metro — desert summer events, year-round construction, Spring Training facilities, the Talking Stick Resort area. Heat-resistant supply standard April–October."),

    ("cook-county-il", "Cook County", "IL", "Illinois", 41.84, -87.68,
     [("Chicago", "chicago-il"), ("Schaumburg", "schaumburg-il"),
      ("Elgin", "elgin-il")],
     [("Naperville", "naperville-il", "DuPage County"),
      ("Joliet", "joliet-il", "Will County"),
      ("Rockford", "rockford-il", "Winnebago County")],
     "Cook County (~5M residents) covers Chicago and most of its inner suburbs. Lakefront events, year-round construction, Soldier Field, McCormick Place, festivals throughout summer. Winter operations include heated stations and antifreeze additives."),

    ("fulton-county-ga", "Fulton County", "GA", "Georgia", 33.75, -84.39,
     [("Atlanta", "atlanta-ga"), ("South Fulton", "south-fulton-ga")],
     [("Decatur", "decatur-ga", "DeKalb County"),
      ("Sandy Springs", "sandy-springs-ga", "Fulton County"),
      ("Roswell", "roswell-ga", "Fulton County")],
     "Fulton County is the heart of metro Atlanta — Mercedes-Benz Stadium, State Farm Arena, the BeltLine, Hartsfield-Jackson, the film and TV production hub. Twice-weekly servicing default for sites with 20+ workers due to humidity."),

    ("king-county-wa", "King County", "WA", "Washington", 47.61, -122.33,
     [("Seattle", "seattle-wa"), ("Bellevue", "bellevue-wa"),
      ("Kent", "kent-wa")],
     [("Tacoma", "tacoma-wa", "Pierce County"),
      ("Everett", "everett-wa", "Snohomish County")],
     "King County (~2.3M residents) is the Seattle metro — tech-driven construction, Lumen Field, T-Mobile Park, year-round events. Rainy-season placement uses mud mats; winter operations include heated hand wash stations."),

    ("clark-county-nv", "Clark County", "NV", "Nevada", 36.17, -115.14,
     [("Las Vegas", "las-vegas-nv"), ("Henderson", "henderson-nv"),
      ("North Las Vegas", "north-las-vegas-nv"), ("Paradise", "enterprise-nv"),
      ("Sunrise Manor", "sunrise-manor-nv"), ("Enterprise", "enterprise-nv")],
     [],
     "Clark County (~2.3M residents) covers Las Vegas, Henderson, and most of Nevada's metro population. Massive event calendar — conventions, concerts, sporting events at Allegiant Stadium and T-Mobile Arena. Heat-resistant supply standard May–September."),

    # ---- Batch 2: 15 additional county hubs ----

    ("bexar-county-tx", "Bexar County", "TX", "Texas", 29.42, -98.49,
     [("San Antonio", "san-antonio-tx")],
     [("Austin", "austin-tx", "Travis County"),
      ("Corpus Christi", "corpus-christi-tx", "Nueces County"),
      ("Laredo", "laredo-tx", "Webb County")],
     "Bexar County (~2M residents) is San Antonio and the surrounding metro — Spurs games, Fiesta San Antonio, Joint Base San Antonio, year-round tourism around the River Walk and Alamo. Construction and event sanitation are the highest-volume use cases."),

    ("orange-county-ca", "Orange County", "CA", "California", 33.72, -117.83,
     [("Anaheim", "anaheim-ca"), ("Santa Ana", "santa-ana-ca"),
      ("Irvine", "irvine-ca"), ("Tustin", "tustin-ca"),
      ("Brea", "brea-ca"), ("Buena Park", "buena-park-ca"),
      ("La Habra", "la-habra-ca"), ("Lake Forest", "lake-forest-ca"),
      ("East Anaheim", "east-anaheim-ca"), ("West Anaheim", "west-anaheim-ca"),
      ("Southwest Anaheim", "southwest-anaheim-ca"),
      ("North Fullerton", "fullerton-north-ca"), ("Fullerton", "fullerton-ca")],
     [("Los Angeles", "los-angeles-ca", "Los Angeles County"),
      ("Long Beach", "long-beach-ca", "Los Angeles County"),
      ("Riverside", "riverside-ca", "Riverside County")],
     "Orange County (~3.2M residents) covers Disneyland, Angel Stadium, and Honda Center, plus a deep wedding-and-event calendar in Newport Beach, Laguna, and the Anaheim resort district. We dispatch luxury restroom trailers, honeywagons for film, and standard units across the full county daily."),

    ("san-diego-county-ca", "San Diego County", "CA", "California", 32.72, -117.16,
     [("San Diego", "san-diego-ca"), ("Chula Vista", "chula-vista-ca"),
      ("Spring Valley", "spring-valley-ca")],
     [("Riverside", "riverside-ca", "Riverside County"),
      ("Anaheim", "anaheim-ca", "Orange County")],
     "San Diego County (~3.3M residents) — Petco Park, Pechanga Arena, year-round outdoor events, Comic-Con, Coronado weddings. Pacific climate keeps event season nearly year-round; our San Diego depot ships same-day across the metro."),

    ("santa-clara-county-ca", "Santa Clara County", "CA", "California", 37.34, -121.89,
     [("San Jose", "san-jose-ca")],
     [("San Francisco", "san-francisco-ca", "San Francisco County"),
      ("Oakland", "oakland-ca", "Alameda County"),
      ("Stockton", "stockton-ca", "San Joaquin County")],
     "Santa Clara County is the heart of Silicon Valley — corporate-campus construction, year-round tech-event calendar, Levi's Stadium, the SAP Center, and a deep wedding scene in the South Bay. Cal/OSHA-compliant ratios standard on construction quotes."),

    ("riverside-county-ca", "Riverside County", "CA", "California", 33.95, -117.40,
     [("Riverside", "riverside-ca"), ("Bloomington", "bloomington-ca")],
     [("San Bernardino", "san-bernardino-ca", "San Bernardino County"),
      ("Anaheim", "anaheim-ca", "Orange County"),
      ("San Diego", "san-diego-ca", "San Diego County")],
     "Riverside County (~2.5M residents) covers the Inland Empire — Coachella Valley music festivals, Palm Springs corporate events, Temecula wineries, and major distribution-center construction along the I-10 and I-15 corridors."),

    ("sacramento-county-ca", "Sacramento County", "CA", "California", 38.58, -121.49,
     [("Sacramento", "sacramento-ca")],
     [("Stockton", "stockton-ca", "San Joaquin County"),
      ("San Francisco", "san-francisco-ca", "San Francisco County")],
     "Sacramento County (~1.6M residents) covers California's capital region — Golden 1 Center events, state-government construction, the State Fair, and rapid suburban development in Folsom and Roseville. Cal/OSHA-compliant supply standard."),

    ("miami-dade-county-fl", "Miami-Dade County", "FL", "Florida", 25.76, -80.19,
     [("Miami", "miami-fl"), ("Hialeah", "hialeah-fl"),
      ("Miami Gardens", "miami-gardens-fl")],
     [("Fort Lauderdale", "fort-lauderdale-fl", "Broward County"),
      ("Pembroke Pines", "pembroke-pines-fl", "Broward County"),
      ("Pompano Beach", "pompano-beach-fl", "Broward County")],
     "Miami-Dade County (~2.7M residents) anchors South Florida — Hard Rock Stadium, Kaseya Center, Art Basel, Miami Beach event scene, and continuous high-rise construction. Hurricane tie-down kits standard June–November; same-day delivery across the county."),

    ("broward-county-fl", "Broward County", "FL", "Florida", 26.12, -80.14,
     [("Fort Lauderdale", "fort-lauderdale-fl"),
      ("Pembroke Pines", "pembroke-pines-fl"),
      ("Pompano Beach", "pompano-beach-fl"),
      ("Coral Springs", "coral-springs-fl")],
     [("Miami", "miami-fl", "Miami-Dade County"),
      ("Hialeah", "hialeah-fl", "Miami-Dade County")],
     "Broward County (~1.9M residents) covers Fort Lauderdale, Hollywood, and the Sawgrass-Mills/Coral Springs suburbs. Major boat-show calendar, Las Olas events, year-round wedding venues, and active hurricane-season pre-staging."),

    ("hillsborough-county-fl", "Hillsborough County", "FL", "Florida", 27.95, -82.46,
     [("Tampa", "tampa-fl")],
     [("Clearwater", "clearwater-fl", "Pinellas County"),
      ("St. Petersburg", "st-petersburg-fl", "Pinellas County"),
      ("Orlando", "orlando-fl", "Orange County FL")],
     "Hillsborough County (~1.5M residents) covers the Tampa metro — Raymond James Stadium, Amalie Arena, the Florida State Fair, port-of-Tampa industrial construction, and a busy outdoor-wedding calendar around the Bayshore and Hyde Park."),

    ("orange-county-fl", "Orange County", "FL", "Florida", 28.54, -81.38,
     [("Orlando", "orlando-fl")],
     [("Tampa", "tampa-fl", "Hillsborough County"),
      ("Lehigh Acres", "lehigh-acres-fl", "Lee County")],
     "Orange County (~1.4M residents) is the Orlando metro — theme-park-area construction, Orange County Convention Center events, the Florida Citrus Bowl, year-round corporate retreat calendar, and continuous suburban development in Lake Nona and Winter Garden."),

    ("davidson-county-tn", "Davidson County", "TN", "Tennessee", 36.16, -86.78,
     [("Nashville", "nashville-tn")],
     [("Murfreesboro", "murfreesboro-tn", "Rutherford County"),
      ("Franklin", "franklin-tn", "Williamson County"),
      ("Clarksville", "clarksville-tn", "Montgomery County")],
     "Davidson County is Nashville and the Music City metro — Nissan Stadium, Bridgestone Arena, the Country Music Hall of Fame, year-round bachelorette and wedding traffic, and a deep festival calendar (CMA Fest, Live on the Green). Saturday luxury-trailer demand peaks April–October; book early."),

    ("mecklenburg-county-nc", "Mecklenburg County", "NC", "North Carolina", 35.23, -80.84,
     [("Charlotte", "charlotte-nc")],
     [("Concord", "concord-nc", "Cabarrus County"),
      ("Gastonia", "gastonia-nc", "Gaston County")],
     "Mecklenburg County (~1.1M residents) is Charlotte and the Queen City metro — Bank of America Stadium, Spectrum Center, Charlotte Motor Speedway, year-round corporate-event calendar, and active uptown high-rise construction."),

    ("suffolk-county-ma", "Suffolk County", "MA", "Massachusetts", 42.36, -71.06,
     [("Boston", "boston-ma")],
     [("Cambridge", "cambridge-ma", "Middlesex County"),
      ("Worcester", "worcester-ma", "Worcester County"),
      ("Lowell", "lowell-ma", "Middlesex County")],
     "Suffolk County is Boston and the surrounding cities — Fenway Park, TD Garden, the Boston Marathon, year-round biotech and university construction, and a busy fall wedding season. Winter operations include heated hand-wash stations and antifreeze servicing."),

    ("marion-county-in", "Marion County", "IN", "Indiana", 39.77, -86.16,
     [("Indianapolis", "indianapolis-in")],
     [("Carmel", "carmel-in", "Hamilton County"),
      ("Fishers", "fishers-in", "Hamilton County")],
     "Marion County (~970K residents) covers the Indianapolis metro — Lucas Oil Stadium, Gainbridge Fieldhouse, the Indy 500 (Memorial Day weekend brings fleet-wide deployment), the Indianapolis 500 Festival, and year-round downtown construction."),

    ("nassau-county-ny", "Nassau County", "NY", "New York", 40.72, -73.59,
     [("Hempstead Town", "hempstead-town-ny"),
      ("North Hempstead", "north-hempstead-ny"),
      ("Oyster Bay", "oyster-bay-ny")],
     [("Brookhaven", "brookhaven-ny", "Suffolk County"),
      ("Babylon Town", "babylon-town-ny", "Suffolk County"),
      ("Islip", "islip-ny", "Suffolk County"),
      ("Long Island", "long-island-ny", "Long Island metro")],
     "Nassau County (~1.4M residents) covers the western half of Long Island — UBS Arena, Nassau Coliseum, Belmont Park, beach-club weddings on the South Shore, and continuous suburban construction. NYC DOT permits often required for sites near Queens border."),

    ("suffolk-county-ny", "Suffolk County", "NY", "New York", 40.84, -72.92,
     [("Brookhaven", "brookhaven-ny"),
      ("Babylon Town", "babylon-town-ny"),
      ("Islip", "islip-ny"),
      ("Long Island", "long-island-ny")],
     [("Hempstead Town", "hempstead-town-ny", "Nassau County"),
      ("North Hempstead", "north-hempstead-ny", "Nassau County"),
      ("Oyster Bay", "oyster-bay-ny", "Nassau County")],
     "Suffolk County (~1.5M residents) covers the eastern half of Long Island — Hamptons summer-event season, Montauk fishing tournaments, vineyards on the North Fork, and continuous beach-house and commercial construction. Pre-book luxury restroom trailers 60+ days for July–August Hamptons weddings."),

    # ---- Batch 3: 15 additional county hubs ----

    ("wayne-county-mi", "Wayne County", "MI", "Michigan", 42.36, -83.08,
     [("Detroit", "detroit-mi")],
     [("Warren", "warren-city-mi", "Macomb County"),
      ("Sterling Heights", "sterling-heights-mi", "Macomb County")],
     "Wayne County (~1.7M residents) covers Detroit and the surrounding inner suburbs — Ford Field, Comerica Park, Little Caesars Arena, year-round downtown Detroit construction, and major auto-industry plant operations."),

    ("allegheny-county-pa", "Allegheny County", "PA", "Pennsylvania", 40.45, -79.99,
     [],
     [("Pittsburgh ZIP 15222", "../zip/15222-porta-potty-rental", "Allegheny County core")],
     "Allegheny County (~1.2M residents) covers Pittsburgh and the Mon Valley — PNC Park, Acrisure Stadium, PPG Paints Arena, year-round downtown construction, and continuing adaptive-reuse projects across the riverfronts."),

    ("hennepin-county-mn", "Hennepin County", "MN", "Minnesota", 44.97, -93.27,
     [("Brooklyn Park", "brooklyn-park-mn"),
      ("Maple Grove", "maple-grove-mn"),
      ("Blaine", "blaine-mn"),
      ("Minneapolis", "minneapolis-mn")],
     [("St. Paul", "st-paul-mn", "Ramsey County"),
      ("Lakeville", "lakeville-mn", "Dakota County"),
      ("Woodbury", "woodbury-mn", "Washington County")],
     "Hennepin County (~1.3M residents) is the Minneapolis metro core — U.S. Bank Stadium, Target Center, Target Field, year-round downtown construction, and a deep summer-festival calendar at the Stone Arch Bridge and Lake Calhoun."),

    ("multnomah-county-or", "Multnomah County", "OR", "Oregon", 45.52, -122.68,
     [],
     [("Vancouver, WA", "vancouver-wa", "Clark County WA"),
      ("Beaverton", "beaverton-or", "Washington County OR")],
     "Multnomah County (~810K residents) is Portland and the surrounding inner east-side neighborhoods — Moda Center, Providence Park, year-round food-truck-pod and street-festival calendar, and continuous riverfront construction."),

    ("davidson-county-tn-2", "Davidson County", "TN", "Tennessee", 36.16, -86.78,
     [], [], ""),  # placeholder; already exists

    ("franklin-county-oh", "Franklin County", "OH", "Ohio", 39.96, -82.99,
     [],
     [("Columbus core", "../zip/43215-porta-potty-rental", "Franklin County")],
     "Franklin County (~1.3M residents) is the Columbus metro — Nationwide Arena, Lower.com Field, the Greater Columbus Convention Center, OSU football traffic, and continuous Short North mid-rise construction."),

    ("cuyahoga-county-oh", "Cuyahoga County", "OH", "Ohio", 41.50, -81.69,
     [],
     [("Cleveland core", "../zip/44114-porta-potty-rental", "Cuyahoga County")],
     "Cuyahoga County (~1.2M residents) is Cleveland and the inner suburbs — Cleveland Browns Stadium, Rocket Mortgage FieldHouse, Progressive Field, year-round downtown event programming, and continuous lakefront development."),

    ("hamilton-county-tn", "Hamilton County", "TN", "Tennessee", 35.05, -85.31,
     [("Chattanooga", "chattanooga-tn")],
     [("Knoxville", "knoxville-tn", "Knox County"),
      ("Nashville", "nashville-tn", "Davidson County")],
     "Hamilton County (~370K residents) covers Chattanooga and the surrounding Tennessee River valley — the Tennessee Aquarium, Chattanooga Riverbend Festival, year-round outdoor-event calendar, and continuous downtown adaptive-reuse construction."),

    ("knox-county-tn", "Knox County", "TN", "Tennessee", 35.96, -83.92,
     [("Knoxville", "knoxville-tn")],
     [("Chattanooga", "chattanooga-tn", "Hamilton County"),
      ("Nashville", "nashville-tn", "Davidson County")],
     "Knox County (~480K residents) is Knoxville — Neyland Stadium, Thompson-Boling Arena, year-round UT athletics traffic, the Sunsphere/World's Fair Park festival programming, and a deep summer outdoor-event scene."),

    ("shelby-county-tn", "Shelby County", "TN", "Tennessee", 35.14, -90.05,
     [("Memphis", "memphis-tn")],
     [("Nashville", "nashville-tn", "Davidson County"),
      ("Little Rock", "little-rock-ar", "Pulaski County AR")],
     "Shelby County (~930K residents) covers Memphis and the surrounding Mid-South — FedExForum, AutoZone Park, Memphis in May, the Beale Street Music Festival, and continuous downtown adaptive-reuse construction."),

    ("jefferson-county-ky", "Jefferson County", "KY", "Kentucky", 38.26, -85.76,
     [("Louisville", "louisville-ky")],
     [("Lexington", "lexington-ky", "Fayette County")],
     "Jefferson County (~770K residents) is Louisville — Churchill Downs, KFC Yum! Center, Lynn Family Stadium, the Kentucky Derby Festival each May (massive seasonal demand), and year-round downtown construction."),

    ("oklahoma-county-ok", "Oklahoma County", "OK", "Oklahoma", 35.47, -97.52,
     [],
     [("Tulsa", "tulsa-ok", "Tulsa County")],
     "Oklahoma County (~800K residents) is Oklahoma City and inner suburbs — Paycom Center, the Oklahoma City National Memorial, year-round downtown event programming, and continuous Bricktown construction."),

    ("douglas-county-ne", "Douglas County", "NE", "Nebraska", 41.26, -95.93,
     [],
     [("Lincoln", "lincoln-ne", "Lancaster County NE")],
     "Douglas County (~580K residents) is Omaha — CHI Health Center, Werner Park, the College World Series each June (massive baseball-tourism demand), and continuous Old Market and downtown construction."),

    ("salt-lake-county-ut", "Salt Lake County", "UT", "Utah", 40.76, -111.89,
     [],
     [("Provo", "provo-ut", "Utah County UT")],
     "Salt Lake County (~1.2M residents) is Salt Lake City and the Wasatch Front metro — Delta Center, Rice-Eccles Stadium, the Salt Palace Convention Center, year-round outdoor-recreation event calendar, and continuous Sugar House and downtown construction."),

    ("baltimore-county-md", "Baltimore County", "MD", "Maryland", 39.40, -76.62,
     [],
     [("Baltimore (city)", "baltimore-md", "Baltimore City"),
      ("Towson, MD", "towson-md", "Baltimore County core")],
     "Baltimore County (~850K residents) wraps around the city of Baltimore — Towson, Catonsville, Dundalk, Owings Mills. Major commercial construction along the I-695 corridor, Towson University events, and year-round suburban festival programming."),

    ("fairfax-county-va", "Fairfax County", "VA", "Virginia", 38.85, -77.30,
     [],
     [("Arlington, VA", "arlington-va", "Arlington County VA"),
      ("Washington, DC", "washington-dc", "District of Columbia")],
     "Fairfax County (~1.1M residents) covers most of Northern Virginia — Tysons Corner construction, Reston Town Center, federal-contractor corporate-campus development, and year-round civic event programming."),
]


def template(county_slug: str, county_name: str, state: str, state_full: str,
             lat: float, lon: float, cities_in: list, nearby: list,
             intro: str) -> str:
    canonical = f"https://fixpilotportapottyrentals.com/porta-potty-rental-{county_slug}"
    title = f"Porta Potty Rental {county_name}, {state} — {len(cities_in)} Cities · Same-Day Delivery"
    description = (
        f"Porta potty rental across {county_name}, {state_full}: "
        f"{len(cities_in)} cities served, same-day delivery, OSHA-compliant, "
        f"luxury restroom trailers, ADA units. Call (833) 652-9344."
    )

    in_county_cards = "\n".join(
        f'      <a href="/porta-potty-rental-{slug}" class="bg-white rounded-xl p-5 shadow-md hover:shadow-xl hover:-translate-y-0.5 transition-all border border-blue-200 block">\n'
        f'        <h3 class="font-extrabold text-blue-900 text-lg mb-1">{name}</h3>\n'
        f'        <p class="text-sm text-blue-700">Porta Potty Rental in {name}, {state}</p>\n'
        '        <span class="text-cta text-sm font-semibold mt-2 inline-block">View &rarr;</span>\n'
        '      </a>'
        for name, slug in cities_in
    )

    nearby_cards = "\n".join(
        f'      <a href="/porta-potty-rental-{slug}" class="bg-white rounded-xl p-4 shadow hover:shadow-lg transition border border-gray-200 block">\n'
        f'        <h3 class="font-extrabold text-gray-900 mb-1">{name}</h3>\n'
        f'        <p class="text-xs text-gray-600">{county_label}</p>\n'
        '      </a>'
        for name, slug, county_label in nearby
    ) if nearby else ""

    nearby_section = (
        f'''
<section class="py-12 md:py-16 bg-white">
  <div class="container mx-auto px-4 max-w-6xl">
    <h2 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2">Nearby cities (other counties)</h2>
    <p class="text-gray-600 mb-8">We also serve adjacent counties. Pick the closest depot for fastest delivery.</p>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
{nearby_cards}
    </div>
  </div>
</section>'''
        if nearby else ""
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta name="geo.region" content="US-{state}">
<meta name="geo.placename" content="{county_name}, {state_full}">
<meta name="geo.position" content="{lat};{lon}">
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
<style>:root{{--brand-50:#eff6ff;--brand-100:#dbeafe;--brand-200:#bfdbfe;--brand-300:#93c5fd;--brand-400:#60a5fa;--brand-500:#3b82f6;--brand-600:#2563eb;--brand-700:#1d4ed8;--brand-800:#1e40af;--brand-900:#1e3a8a;--brand-950:#172554;--cta:#ea580c}}</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Porta Potty Rental {county_name}",
  "description": "{description}",
  "url": "{canonical}",
  "isPartOf": {{"@type": "WebSite", "name": "FixPilot Porta Potty Rentals", "url": "https://fixpilotportapottyrentals.com"}},
  "breadcrumb": {{
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://fixpilotportapottyrentals.com/"}},
      {{"@type": "ListItem", "position": 2, "name": "Locations", "item": "https://fixpilotportapottyrentals.com/locations"}},
      {{"@type": "ListItem", "position": 3, "name": "{county_name}", "item": "{canonical}"}}
    ]
  }}
}}
</script>
</head>
<body class="bg-blue-50 text-gray-900">

<header class="bg-white shadow-md sticky top-0 z-40">
  <div class="container mx-auto px-4 py-4 flex items-center justify-between">
    <a href="/" class="flex items-center gap-2"><div class="w-10 h-10 bg-brand-600 rounded-lg flex items-center justify-center"><span class="text-white font-bold text-xl">F</span></div><span class="text-xl font-bold">FixPilot</span></a>
    <nav class="hidden md:flex items-center gap-6 text-sm font-bold">
      <a href="/locations" class="hover:text-brand-700">Locations</a>
      <a href="/services/standard-porta-potty" class="hover:text-brand-700">Services</a>
      <a href="/calculator" class="hover:text-brand-700">Calculator</a>
      <a href="/blog" class="hover:text-brand-700">Blog</a>
    </nav>
    <a href="tel:+18336529344" class="bg-cta text-white px-4 py-2 rounded-lg font-bold hover:bg-orange-700"><i class="fas fa-phone mr-2"></i>(833) 652-9344</a>
  </div>
</header>

<section class="py-12 md:py-16 bg-gradient-to-br from-blue-100 to-white">
  <div class="container mx-auto px-4 max-w-5xl">
    <nav class="text-sm mb-4 text-gray-600">
      <a href="/" class="text-brand-700 hover:underline">Home</a> /
      <a href="/locations" class="text-brand-700 hover:underline">Locations</a> /
      <span>{county_name}</span>
    </nav>
    <h1 class="text-4xl md:text-5xl font-extrabold text-blue-900 mb-3">Porta Potty Rental in {county_name}, {state_full}</h1>
    <p class="text-lg md:text-xl text-blue-800 mb-6">{intro}</p>
    <div class="flex flex-wrap gap-3">
      <a href="tel:+18336529344" class="bg-cta hover:bg-orange-700 text-white font-extrabold py-3 px-6 rounded-xl shadow-lg pulse-btn"><i class="fas fa-phone mr-2"></i>Call (833) 652-9344</a>
      <a href="/calculator" class="bg-white border-2 border-blue-700 text-blue-800 font-bold py-3 px-6 rounded-xl">Free unit calculator</a>
    </div>
  </div>
</section>

<section class="py-12 md:py-16 bg-white">
  <div class="container mx-auto px-4 max-w-6xl">
    <h2 class="text-3xl md:text-4xl font-extrabold text-blue-900 mb-2">Cities we serve in {county_name}</h2>
    <p class="text-blue-700 mb-8">Same-day delivery in metro core, next-day everywhere else.</p>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
{in_county_cards}
    </div>
  </div>
</section>
{nearby_section}

<section class="py-12 md:py-16 bg-blue-50">
  <div class="container mx-auto px-4 max-w-5xl">
    <h2 class="text-3xl md:text-4xl font-extrabold text-blue-900 mb-3">Common use cases in {county_name}</h2>
    <div class="grid md:grid-cols-2 gap-6">
      <a href="/services/construction-porta-potty-rentals" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-blue-200">
        <h3 class="font-extrabold text-blue-900 text-xl mb-2">Construction sites</h3>
        <p class="text-blue-700">OSHA-ratio documentation, weekly servicing logs, crane-hookable units for high-rise builds in the metro core.</p>
      </a>
      <a href="/services/luxury-restroom-trailers" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-blue-200">
        <h3 class="font-extrabold text-blue-900 text-xl mb-2">Weddings &amp; events</h3>
        <p class="text-blue-700">Climate-controlled luxury restroom trailers, optional attendants, pre-event walkthroughs.</p>
      </a>
      <a href="/services/festival-porta-potty-rental" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-blue-200">
        <h3 class="font-extrabold text-blue-900 text-xl mb-2">Festivals &amp; concerts</h3>
        <p class="text-blue-700">Multi-day overnight servicing, ADA at every cluster, hand wash stations near food vendors and bars.</p>
      </a>
      <a href="/services/film-set-porta-potty-rental" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition border border-blue-200">
        <h3 class="font-extrabold text-blue-900 text-xl mb-2">Film &amp; TV production</h3>
        <p class="text-blue-700">Honeywagons, talent restrooms, NDA-compliant crews, production billing terms.</p>
      </a>
    </div>
  </div>
</section>

<section class="py-12 md:py-16 bg-gradient-to-br from-blue-50 to-white">
  <div class="container mx-auto px-4 max-w-3xl text-center">
    <h2 class="text-3xl md:text-4xl font-extrabold text-blue-900 mb-3">Get a quote for {county_name} in 60 seconds</h2>
    <p class="text-blue-800 text-lg mb-6">No forms. Real dispatcher. Instant pricing.</p>
    <a href="tel:+18336529344" class="inline-block bg-cta hover:bg-orange-700 text-white font-extrabold text-2xl py-4 px-8 rounded-2xl shadow-xl pulse-btn"><i class="fas fa-phone mr-2"></i>(833) 652-9344</a>
  </div>
</section>

<footer class="bg-blue-950 text-blue-100 py-12 mt-8">
  <div class="container mx-auto px-4 text-center text-sm">
    <p class="mb-2">&copy; FixPilot Porta Potty Rentals &mdash; 224 cities, 50 states, 24/7 dispatch.</p>
    <p><a href="tel:+18336529344" class="text-cta font-bold">(833) 652-9344</a> &middot; <a href="/locations" class="hover:underline">All service areas</a> &middot; <a href="/blog" class="hover:underline">Blog</a></p>
  </div>
</footer>

<div id="mobile-cta" class="fixed bottom-0 left-0 right-0 bg-cta shadow-2xl transform translate-y-full transition-transform duration-300 z-50 md:hidden flex items-stretch" style="z-index: 9999;">
  <a href="tel:+18336529344" class="flex-1 py-4 text-center text-white font-extrabold text-lg"><i class="fas fa-phone-alt mr-2 animate-pulse"></i>Call (833) 652-9344</a>
  <button id="mobile-cta-dismiss" type="button" aria-label="Hide call button" class="px-4 text-white/80 hover:text-white text-2xl leading-none">&times;</button>
</div>
<script>
(function(){{var c=document.getElementById('mobile-cta'),d=document.getElementById('mobile-cta-dismiss');if(!c)return;var x=false;try{{x=sessionStorage.getItem('mobileCtaDismissed')==='1';}}catch(e){{}}if(x){{c.style.display='none';return;}}window.addEventListener('scroll',function(){{if(x)return;c.style.transform=window.scrollY>300?'translateY(0)':'translateY(100%)';}},{{passive:true}});if(d){{d.addEventListener('click',function(e){{e.preventDefault();x=true;c.style.transform='translateY(100%)';setTimeout(function(){{c.style.display='none';}},300);try{{sessionStorage.setItem('mobileCtaDismissed','1');}}catch(e){{}}}});}}}})();
</script>
</body>
</html>
'''


def main() -> None:
    written = 0
    for entry in COUNTIES:
        county_slug, county_name, state, state_full, lat, lon, cities_in, nearby, intro = entry
        folder = f"porta-potty-rental-{county_slug}"
        os.makedirs(folder, exist_ok=True)
        out = f"{folder}/index.html"
        if os.path.exists(out):
            print(f"  exists: {out}")
            continue
        html = template(county_slug, county_name, state, state_full, lat, lon,
                        cities_in, nearby, intro)
        open(out, "w", encoding="utf-8").write(html)
        print(f"  wrote: {out} ({len(cities_in)} cities)")
        written += 1
    print(f"\nWrote {written} county hub pages.")


if __name__ == "__main__":
    main()
