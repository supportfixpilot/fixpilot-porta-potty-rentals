#!/usr/bin/env python3
"""Build 30 high-priority ZIP-code pages.

Each ZIP page is structured to avoid being a doorway page:
  - Real neighborhood-level content (anchor venues, local landmarks, ZIP-specific notes)
  - Canonical link self-referencing (not redirecting upstream)
  - Strong upstream link to the parent city page
  - Distinct meta title and description per ZIP
  - Phone-only CTAs
  - Use-case context relevant to the neighborhood
"""
from __future__ import annotations
import os

# (zip_slug, zip_code, neighborhood_name, parent_city_name, parent_city_slug, state,
#  state_full, lat, lon, anchor_venues_text, neighborhood_context_text)
ZIPS = [
    # Houston, TX (Harris County)
    ("77002", "77002", "Downtown Houston", "Houston", "houston-tx", "TX", "Texas", 29.76, -95.37,
     "Discovery Green, Minute Maid Park, Toyota Center, the Theater District",
     "the high-rise core of Houston with continuous office and residential tower construction, year-round event traffic at Minute Maid and Toyota Center, and the Theater District performance calendar"),
    ("77019", "77019", "River Oaks", "Houston", "houston-tx", "TX", "Texas", 29.75, -95.42,
     "the River Oaks Country Club, Buffalo Bayou Park",
     "Houston's premier residential neighborhood with custom-home construction, estate-property events, and corporate retreats at the country club"),
    ("77024", "77024", "Memorial / Hedwig Village", "Houston", "houston-tx", "TX", "Texas", 29.77, -95.50,
     "Memorial City Mall, Memorial Park",
     "the Memorial corridor with high-end residential remodels, large outdoor weddings on private estates, and the City Centre commercial development"),
    # Austin, TX
    ("78701", "78701", "Downtown Austin", "Austin", "austin-tx", "TX", "Texas", 30.27, -97.74,
     "Q2 Stadium event nights, Moody Center concerts, the Texas State Capitol, Sixth Street",
     "downtown Austin's nightlife corridor and the central business district, with continuous high-rise construction and a year-round event calendar including ACL and SXSW"),
    ("78704", "78704", "South Congress (SoCo)", "Austin", "austin-tx", "TX", "Texas", 30.25, -97.75,
     "South Congress, Zilker Park",
     "South Austin's most-visited cultural corridor including ACL Festival at Zilker Park each fall, food-truck plazas, and continuous boutique-hotel construction along South Congress"),
    # Dallas, TX
    ("75201", "75201", "Downtown Dallas", "Dallas", "dallas-tx", "TX", "Texas", 32.78, -96.80,
     "the Arts District, AT&T Performing Arts Center, Klyde Warren Park",
     "the central downtown with the largest contiguous arts district in the country, ongoing high-rise construction, and major outdoor events at Klyde Warren"),
    ("75204", "75204", "Uptown Dallas", "Dallas", "dallas-tx", "TX", "Texas", 32.81, -96.80,
     "the Katy Trail, the McKinney Avenue trolley corridor, the West Village",
     "Uptown's residential mid-rise corridor along the Katy Trail with year-round outdoor wedding venues, restaurant openings, and apartment construction"),
    # Phoenix, AZ
    ("85004", "85004", "Downtown Phoenix", "Phoenix", "phoenix-az", "AZ", "Arizona", 33.45, -112.07,
     "the Footprint Center, Chase Field, Roosevelt Row, the Arizona State Capitol",
     "Phoenix's downtown core with Suns, Diamondbacks, and Mercury home games, the First Friday arts walk on Roosevelt Row, and year-round convention center events"),
    ("85016", "85016", "Arcadia / Biltmore", "Phoenix", "phoenix-az", "AZ", "Arizona", 33.50, -112.02,
     "the Arizona Biltmore, Camelback Mountain, the Esplanade",
     "Phoenix's most prestigious residential corridor with luxury wedding venues at the Biltmore, custom-home construction in Arcadia, and corporate retreats at resort properties"),
    # Atlanta, GA
    ("30303", "30303", "Downtown Atlanta", "Atlanta", "atlanta-ga", "GA", "Georgia", 33.75, -84.39,
     "Mercedes-Benz Stadium, State Farm Arena, Centennial Olympic Park, Georgia World Congress Center",
     "Atlanta's downtown core with Falcons and Hawks games, continuous convention activity at GWCC, and year-round festival programming at Centennial Park"),
    ("30309", "30309", "Midtown Atlanta", "Atlanta", "atlanta-ga", "GA", "Georgia", 33.78, -84.38,
     "Piedmont Park, the Fox Theatre, the BeltLine Eastside Trail, the High Museum",
     "Midtown's high-density residential corridor with major festivals at Piedmont Park, BeltLine event programming, and continuous mid-rise apartment construction"),
    ("30308", "30308", "Old Fourth Ward / Inman Park", "Atlanta", "atlanta-ga", "GA", "Georgia", 33.76, -84.37,
     "Ponce City Market, the BeltLine, Krog Street Market",
     "the BeltLine corridor with year-round festival traffic, food-hall events, and adaptive-reuse construction projects"),
    # Miami, FL
    ("33139", "33139", "South Beach", "Miami", "miami-fl", "FL", "Florida", 25.78, -80.13,
     "Ocean Drive, Lincoln Road Mall, the Art Deco district",
     "South Beach with year-round event traffic, major fashion and music industry events including Art Basel and Miami Music Week, and restaurant/hotel construction"),
    ("33131", "33131", "Brickell", "Miami", "miami-fl", "FL", "Florida", 25.76, -80.19,
     "Brickell City Centre, the Brickell financial district, Bayfront Park",
     "Miami's financial district and high-rise residential core with continuous tower construction and a busy corporate event calendar"),
    # Las Vegas, NV
    ("89109", "89109", "The Strip", "Las Vegas", "las-vegas-nv", "NV", "Nevada", 36.12, -115.17,
     "Allegiant Stadium, T-Mobile Arena, the Las Vegas Convention Center, the Sphere",
     "the resort corridor with year-round convention activity, major sporting events, residency concerts, and hotel renovation construction"),
    ("89101", "89101", "Downtown Las Vegas", "Las Vegas", "las-vegas-nv", "NV", "Nevada", 36.17, -115.14,
     "Fremont Street, the Mob Museum, Symphony Park",
     "downtown's Fremont Street and arts district with continuous event programming, downtown casino renovation, and Symphony Park concerts"),
    # New York City, NY
    ("10001", "10001", "Chelsea / Hudson Yards", "New York City", "new-york-city-ny", "NY", "New York", 40.75, -73.99,
     "Hudson Yards, Madison Square Garden, the High Line",
     "Chelsea and the Hudson Yards mega-development with major construction, year-round events at MSG, and gallery district openings"),
    ("10013", "10013", "Tribeca / SoHo", "New York City", "new-york-city-ny", "NY", "New York", 40.72, -74.00,
     "the Tribeca Film Festival venues, the SoHo retail corridor, Hudson River Park",
     "Tribeca's loft district and SoHo's retail corridor with year-round film-production base camps, fashion-week events, and adaptive-reuse construction"),
    # Los Angeles, CA
    ("90028", "90028", "Hollywood", "Los Angeles", "los-angeles-ca", "CA", "California", 34.10, -118.33,
     "the Hollywood Walk of Fame, the Hollywood Bowl, the Pantages Theatre",
     "the Hollywood corridor with year-round film and TV production, Hollywood Bowl concerts, and continuous hotel and apartment construction"),
    ("90291", "90291", "Venice", "Los Angeles", "los-angeles-ca", "CA", "California", 34.00, -118.46,
     "Venice Beach, Abbot Kinney Boulevard, the Venice Boardwalk",
     "Venice's beach corridor and Abbot Kinney shopping district with year-round outdoor events, beachfront weddings, and creative-office construction"),
    ("90013", "90013", "Downtown LA / Little Tokyo", "Los Angeles", "los-angeles-ca", "CA", "California", 34.05, -118.24,
     "Crypto.com Arena, Grand Central Market, the Arts District",
     "downtown LA's Arts District and Little Tokyo with Lakers, Kings, and Sparks games at Crypto.com Arena, year-round event programming, and adaptive-reuse construction"),
    # Chicago, IL
    ("60601", "60601", "Loop", "Chicago", "chicago-il", "IL", "Illinois", 41.88, -87.62,
     "Millennium Park, Grant Park, the Art Institute, Cloud Gate",
     "Chicago's downtown Loop with Lollapalooza at Grant Park, year-round Millennium Park programming, and continuous office-tower construction"),
    ("60607", "60607", "West Loop / Fulton Market", "Chicago", "chicago-il", "IL", "Illinois", 41.89, -87.66,
     "Fulton Market's restaurant corridor, the United Center area",
     "the West Loop's restaurant district and Fulton Market with continuous loft conversions, restaurant openings, and creative-office construction"),
    # Seattle, WA
    ("98101", "98101", "Downtown Seattle", "Seattle", "seattle-wa", "WA", "Washington", 47.61, -122.33,
     "Pike Place Market, the Seattle Convention Center, Climate Pledge Arena",
     "downtown Seattle's tourism core and convention district with year-round corporate events, Climate Pledge Arena concerts, and high-rise tower construction"),
    ("98109", "98109", "South Lake Union", "Seattle", "seattle-wa", "WA", "Washington", 47.62, -122.34,
     "Amazon's HQ campus, Lake Union Park, MoPOP",
     "Seattle's tech-corridor SLU with continuous Amazon-led mid-rise construction, year-round corporate events, and Lake Union seaplane / boating event traffic"),
    # Denver, CO
    ("80202", "80202", "LoDo / Downtown Denver", "Denver", "denver-co", "CO", "Colorado", 39.75, -104.99,
     "Coors Field, Ball Arena, the 16th Street Mall, Larimer Square",
     "Denver's LoDo with Rockies, Nuggets, and Avalanche games, year-round downtown event programming, and continuous high-rise construction"),
    ("80205", "80205", "RiNo (River North)", "Denver", "denver-co", "CO", "Colorado", 39.77, -104.97,
     "the RiNo Arts District, the National Western Center",
     "Denver's RiNo art district with major mural festivals, brewery openings, and adaptive-reuse construction"),
    # Nashville, TN
    ("37203", "37203", "Music Row / The Gulch", "Nashville", "nashville-tn", "TN", "Tennessee", 36.15, -86.79,
     "Bridgestone Arena, the Country Music Hall of Fame, Music Row recording studios",
     "Music Row's recording-studio district and The Gulch's high-rise corridor with year-round music industry events and continuous tower construction"),
    ("37206", "37206", "East Nashville", "Nashville", "nashville-tn", "TN", "Tennessee", 36.18, -86.74,
     "Five Points, the East Nashville restaurant corridor, Shelby Park",
     "East Nashville's residential and restaurant district with continuous home renovation, outdoor venue events, and Shelby Park festival programming"),
    # Charlotte, NC
    ("28202", "28202", "Uptown Charlotte", "Charlotte", "charlotte-nc", "NC", "North Carolina", 35.23, -80.84,
     "Bank of America Stadium, Spectrum Center, the Charlotte Convention Center",
     "Uptown Charlotte with Panthers and Hornets games, year-round convention center events, and continuous high-rise tower construction"),

    # ---- Batch 2: 30 more ZIPs across new metros ----

    # Philadelphia, PA
    ("19103", "19103", "Center City / Rittenhouse", "Philadelphia", "philadelphia-pa", "PA", "Pennsylvania", 39.95, -75.17,
     "Rittenhouse Square, the Avenue of the Arts, the Philadelphia Museum of Art",
     "Center City Philadelphia with year-round arts programming, continuous high-rise condo construction, and major outdoor event traffic at the Parkway"),
    ("19146", "19146", "Graduate Hospital / Point Breeze", "Philadelphia", "philadelphia-pa", "PA", "Pennsylvania", 39.94, -75.18,
     "the South Street corridor, FDR Park nearby",
     "Philadelphia&rsquo;s Graduate Hospital and Point Breeze neighborhoods with continuous townhouse construction, restaurant openings, and a busy summer block-party scene"),

    # Boston, MA
    ("02116", "02116", "Back Bay", "Boston", "boston-ma", "MA", "Massachusetts", 42.35, -71.07,
     "Copley Square, the Boston Public Library, the Back Bay shopping district",
     "Back Bay with year-round event programming at Copley Square, the Boston Marathon finish line, and continuous high-rise office and residential construction"),
    ("02210", "02210", "Seaport District", "Boston", "boston-ma", "MA", "Massachusetts", 42.35, -71.04,
     "the Boston Convention and Exhibition Center, Seaport Common, the ICA",
     "Boston&rsquo;s Seaport with rapid mid-rise development, year-round convention activity, and waterfront event programming"),

    # Baltimore, MD
    ("21202", "21202", "Inner Harbor / Mount Vernon", "Baltimore", "baltimore-md", "MD", "Maryland", 39.29, -76.61,
     "the Inner Harbor, Camden Yards, M&amp;T Bank Stadium, the Power Plant",
     "Baltimore&rsquo;s Inner Harbor and Mount Vernon with Orioles and Ravens games, year-round harbor event programming, and adaptive-reuse construction"),

    # San Francisco, CA
    ("94103", "94103", "SOMA", "San Francisco", "san-francisco-ca", "CA", "California", 37.78, -122.41,
     "the Moscone Center, Oracle Park, Chase Center",
     "SOMA with year-round Moscone Center conventions, Giants and Warriors games, and continuous tech-driven mid-rise construction"),
    ("94110", "94110", "Mission District", "San Francisco", "san-francisco-ca", "CA", "California", 37.76, -122.42,
     "Mission Dolores Park, the Valencia Street corridor",
     "the Mission with year-round outdoor festival programming at Dolores Park, restaurant openings, and continuous mixed-use construction"),

    # Oakland, CA
    ("94607", "94607", "West Oakland / Jack London Square", "Oakland", "oakland-ca", "CA", "California", 37.80, -122.28,
     "Jack London Square, the Oakland-Alameda County Coliseum (legacy site)",
     "West Oakland and Jack London Square with waterfront event programming, port-area construction, and live-work loft conversions"),

    # San Diego, CA
    ("92101", "92101", "Downtown San Diego / Gaslamp", "San Diego", "san-diego-ca", "CA", "California", 32.71, -117.16,
     "Petco Park, the Gaslamp Quarter, the San Diego Convention Center",
     "downtown San Diego with Padres games, Comic-Con week, year-round convention programming, and Gaslamp event traffic"),
    ("92109", "92109", "Pacific Beach / Mission Beach", "San Diego", "san-diego-ca", "CA", "California", 32.79, -117.25,
     "Mission Bay, the Pacific Beach boardwalk, Belmont Park",
     "Pacific Beach and Mission Beach with year-round outdoor weddings, beach events, and tourism-driven hotel construction"),

    # Tampa, FL
    ("33602", "33602", "Downtown Tampa / Channelside", "Tampa", "tampa-fl", "FL", "Florida", 27.95, -82.46,
     "Amalie Arena, the Tampa Convention Center, Sparkman Wharf",
     "downtown Tampa with Lightning games, year-round convention programming, and continuous waterfront mixed-use construction"),
    ("33606", "33606", "Hyde Park / South Tampa", "Tampa", "tampa-fl", "FL", "Florida", 27.93, -82.47,
     "Hyde Park Village, the Bayshore Boulevard waterfront",
     "Hyde Park&rsquo;s upscale residential corridor with continuous custom-home construction, year-round outdoor weddings on Bayshore, and Gasparilla event traffic"),

    # Orlando, FL
    ("32801", "32801", "Downtown Orlando", "Orlando", "orlando-fl", "FL", "Florida", 28.54, -81.38,
     "the Kia Center, Inter&amp;Co Stadium, the Dr. Phillips Center for the Performing Arts",
     "downtown Orlando with Magic and Orlando City games, year-round arts programming, and continuous high-rise construction"),
    ("32819", "32819", "Dr. Phillips / I-Drive corridor", "Orlando", "orlando-fl", "FL", "Florida", 28.45, -81.46,
     "the Orange County Convention Center, Universal Orlando, ICON Park",
     "the I-Drive corridor with year-round convention activity, theme-park-area construction, and the densest hotel-event calendar in Florida"),

    # San Antonio, TX
    ("78205", "78205", "Downtown San Antonio / River Walk", "San Antonio", "san-antonio-tx", "TX", "Texas", 29.42, -98.49,
     "the Alamo, the River Walk, the Henry B. Gonz&aacute;lez Convention Center",
     "downtown San Antonio with year-round River Walk tourism, convention programming, Spurs games at Frost Bank Center, and Fiesta event traffic each April"),
    ("78216", "78216", "North Central / Airport area", "San Antonio", "san-antonio-tx", "TX", "Texas", 29.51, -98.47,
     "San Antonio International Airport, the Quarry Market",
     "North Central San Antonio with airport-area construction, corporate-park development, and year-round outdoor event traffic"),

    # Indianapolis, IN
    ("46204", "46204", "Downtown Indianapolis", "Indianapolis", "indianapolis-in", "IN", "Indiana", 39.77, -86.16,
     "Lucas Oil Stadium, Gainbridge Fieldhouse, the Indiana Convention Center, Monument Circle",
     "downtown Indianapolis with Colts and Pacers games, year-round convention programming, the Indianapolis 500 Festival each May, and continuous downtown construction"),

    # Detroit, MI
    ("48201", "48201", "Midtown Detroit", "Detroit", "detroit-mi", "MI", "Michigan", 42.36, -83.06,
     "the Detroit Institute of Arts, Wayne State University, the Fisher Theatre",
     "Midtown Detroit with continuous adaptive-reuse construction, year-round arts programming, and university-driven mid-rise development"),

    # Pittsburgh, PA
    ("15222", "15222", "Strip District / Downtown Pittsburgh", "Pittsburgh", "pittsburgh-pa", "PA", "Pennsylvania", 40.45, -79.99,
     "PPG Paints Arena, PNC Park, Acrisure Stadium, the David L. Lawrence Convention Center",
     "downtown Pittsburgh and the Strip District with Penguins, Pirates, and Steelers games, year-round convention programming, and adaptive-reuse construction"),

    # Memphis, TN
    ("38103", "38103", "Downtown Memphis / Beale Street", "Memphis", "memphis-tn", "TN", "Tennessee", 35.14, -90.05,
     "FedExForum, the Renasant Convention Center, AutoZone Park, Beale Street",
     "downtown Memphis with Grizzlies games, year-round Beale Street event traffic, the Memphis in May festival, and continuous riverfront development"),

    # Sacramento, CA
    ("95814", "95814", "Downtown Sacramento", "Sacramento", "sacramento-ca", "CA", "California", 38.58, -121.49,
     "Golden 1 Center, the SAFE Credit Union Convention Center, the California State Capitol",
     "downtown Sacramento with Kings games, year-round state-government activity, capital-area construction, and the California State Fair"),

    # San Jose, CA
    ("95113", "95113", "Downtown San Jose", "San Jose", "san-jose-ca", "CA", "California", 37.34, -121.89,
     "the SAP Center, the San Jose Convention Center, San Pedro Square Market",
     "downtown San Jose with Sharks games, year-round tech-event activity, continuous mid-rise construction, and Silicon Valley corporate-event traffic"),

    # Buffalo, NY
    ("14202", "14202", "Downtown Buffalo / Canalside", "Buffalo", "buffalo-ny", "NY", "New York", 42.89, -78.88,
     "KeyBank Center, Sahlen Field, Canalside",
     "downtown Buffalo and Canalside with Sabres games, year-round waterfront programming, and continuous adaptive-reuse construction"),

    # Newark, NJ
    ("07102", "07102", "Downtown Newark", "Newark", "newark-nj", "NJ", "New Jersey", 40.74, -74.17,
     "the Prudential Center, NJPAC, Newark Penn Station",
     "downtown Newark with Devils games, year-round NJPAC programming, and continuous transit-oriented development"),

    # Jersey City, NJ
    ("07302", "07302", "Downtown Jersey City / Exchange Place", "Jersey City", "jersey-city-nj", "NJ", "New Jersey", 40.72, -74.04,
     "the Newport waterfront, Liberty State Park, Exchange Place",
     "downtown Jersey City with continuous high-rise construction along the Hudson, year-round Liberty State Park events, and ferry-terminal-area development"),

    # Cambridge, MA
    ("02139", "02139", "Central Square / MIT", "Cambridge", "cambridge-ma", "MA", "Massachusetts", 42.36, -71.10,
     "MIT, Harvard&rsquo;s Kendall Square biotech corridor, Central Square",
     "Cambridge&rsquo;s Central Square and Kendall Square with continuous biotech construction, MIT campus events, and year-round commencement and reunion traffic"),

    # Worcester, MA
    ("01608", "01608", "Downtown Worcester", "Worcester", "worcester-ma", "MA", "Massachusetts", 42.26, -71.80,
     "the DCU Center, Polar Park",
     "downtown Worcester with WooSox baseball, year-round DCU Center events, and continuous downtown revitalization construction"),

    # New Orleans, LA
    ("70112", "70112", "French Quarter / CBD", "New Orleans", "new-orleans-la", "LA", "Louisiana", 29.95, -90.07,
     "the Caesars Superdome, the Smoothie King Center, the French Quarter, Jackson Square",
     "downtown New Orleans and the French Quarter with Saints and Pelicans games, year-round tourism, Mardi Gras, Jazz Fest, and Essence Fest event traffic"),

    # Cleveland, OH
    ("44114", "44114", "Downtown Cleveland", "Cleveland", "cleveland-oh", "OH", "Ohio", 41.50, -81.69,
     "Rocket Mortgage FieldHouse, Progressive Field, Cleveland Browns Stadium, Public Square",
     "downtown Cleveland with Cavaliers, Guardians, and Browns games, year-round downtown event programming, and continuous lakefront development"),

    # Columbus, OH
    ("43215", "43215", "Downtown Columbus / Short North", "Columbus", "columbus-oh", "OH", "Ohio", 39.96, -82.99,
     "Nationwide Arena, the Greater Columbus Convention Center, the Short North arts district",
     "downtown Columbus and the Short North with Blue Jackets games, year-round convention activity, OSU football traffic, and continuous mixed-use construction"),

    # ---- Batch 3: 30 more ZIPs ----

    # Houston, TX (additional)
    ("77098", "77098", "Upper Kirby / Greenway", "Houston", "houston-tx", "TX", "Texas", 29.74, -95.42,
     "the River Oaks District, Greenway Plaza",
     "Houston&rsquo;s Upper Kirby retail and Greenway corporate corridor with continuous mid-rise construction and a busy outdoor-event calendar"),
    ("77003", "77003", "EaDo (East Downtown)", "Houston", "houston-tx", "TX", "Texas", 29.75, -95.35,
     "Shell Energy Stadium, the East End Cultural District",
     "Houston&rsquo;s EaDo with Dynamo and Dash games, year-round arts programming, and continuous adaptive-reuse construction"),

    # Dallas, TX (additional)
    ("75202", "75202", "Dallas Arts District", "Dallas", "dallas-tx", "TX", "Texas", 32.79, -96.80,
     "the AT&amp;T Performing Arts Center, the Dallas Museum of Art, Klyde Warren Park",
     "Dallas&rsquo;s Arts District &mdash; the largest contiguous arts district in the country &mdash; with year-round programming and major outdoor event traffic at Klyde Warren"),

    # Austin, TX (additional)
    ("78745", "78745", "South Austin", "Austin", "austin-tx", "TX", "Texas", 30.21, -97.81,
     "St. Edward&rsquo;s University, the South Lamar corridor",
     "South Austin&rsquo;s residential and entertainment corridor along South Lamar with year-round outdoor events, food-truck plazas, and continuous mid-rise construction"),

    # Atlanta, GA (additional)
    ("30305", "30305", "Buckhead", "Atlanta", "atlanta-ga", "GA", "Georgia", 33.84, -84.38,
     "Atlanta&rsquo;s Buckhead financial district, Lenox Square",
     "Buckhead&rsquo;s upscale shopping and corporate corridor with continuous high-rise construction, year-round corporate-event activity, and luxury retail openings"),

    # Phoenix, AZ (additional)
    ("85021", "85021", "North Phoenix / Sunnyslope", "Phoenix", "phoenix-az", "AZ", "Arizona", 33.56, -112.08,
     "the Sunnyslope arts district, Moon Valley",
     "North Phoenix and Sunnyslope with continuous suburban construction and outdoor festival programming"),

    # Miami, FL (additional)
    ("33133", "33133", "Coconut Grove", "Miami", "miami-fl", "FL", "Florida", 25.73, -80.24,
     "the Coconut Grove waterfront, CocoWalk",
     "Coconut Grove&rsquo;s historic waterfront district with year-round outdoor events, sailing regattas, and continuous mid-rise residential construction"),

    # Las Vegas, NV (additional)
    ("89102", "89102", "West Las Vegas / Spring Valley border", "Las Vegas", "las-vegas-nv", "NV", "Nevada", 36.14, -115.18,
     "Chinatown, the Las Vegas Premium Outlets",
     "West Las Vegas with Chinatown event programming, outlet-mall traffic, and continuous suburban construction"),

    # Los Angeles, CA (additional)
    ("90210", "90210", "Beverly Hills", "Los Angeles", "los-angeles-ca", "CA", "California", 34.07, -118.40,
     "Rodeo Drive, the Beverly Hills Hotel",
     "Beverly Hills with year-round red-carpet events, fashion-week programming, and continuous luxury-retail and hospitality construction"),
    ("90069", "90069", "West Hollywood", "Los Angeles", "los-angeles-ca", "CA", "California", 34.09, -118.39,
     "Sunset Strip, the WeHo nightlife corridor",
     "West Hollywood with year-round nightlife event programming, film-industry events, and continuous boutique-hotel construction"),

    # Chicago, IL (additional)
    ("60611", "60611", "River North / Streeterville", "Chicago", "chicago-il", "IL", "Illinois", 41.89, -87.62,
     "Navy Pier, the Magnificent Mile, the Tribune Tower",
     "Chicago&rsquo;s River North and Streeterville with year-round Navy Pier event programming, Mag Mile retail traffic, and continuous high-rise construction"),

    # Seattle, WA (additional)
    ("98104", "98104", "Pioneer Square / International District", "Seattle", "seattle-wa", "WA", "Washington", 47.60, -122.33,
     "Lumen Field, T-Mobile Park, Pioneer Square",
     "Pioneer Square and the International District with Seahawks and Mariners games, year-round festival programming, and continuous adaptive-reuse construction"),

    # Denver, CO (additional)
    ("80211", "80211", "Highlands", "Denver", "denver-co", "CO", "Colorado", 39.76, -105.01,
     "the Highland neighborhood, Tennyson Street",
     "Denver&rsquo;s Highland neighborhood with continuous townhouse construction, restaurant openings, and year-round neighborhood event programming"),

    # Nashville, TN (additional)
    ("37212", "37212", "Vanderbilt / Belmont", "Nashville", "nashville-tn", "TN", "Tennessee", 36.13, -86.80,
     "Vanderbilt University, Belmont University, Music Row",
     "Nashville&rsquo;s university corridor with continuous campus-area construction, Vanderbilt football traffic, and year-round Music Row event programming"),

    # Charlotte, NC (additional)
    ("28203", "28203", "South End", "Charlotte", "charlotte-nc", "NC", "North Carolina", 35.21, -80.86,
     "the LYNX light-rail line, the South End brewery district",
     "Charlotte&rsquo;s South End with continuous mid-rise residential construction, year-round outdoor brewery events, and the LYNX-line transit-oriented development"),

    # Philadelphia, PA (additional)
    ("19130", "19130", "Fairmount / Art Museum area", "Philadelphia", "philadelphia-pa", "PA", "Pennsylvania", 39.97, -75.18,
     "the Philadelphia Museum of Art, Fairmount Park, the Schuylkill River Trail",
     "Philadelphia&rsquo;s Fairmount with year-round Art Museum-area events, the Schuylkill River Trail running events, and continuous brownstone restoration"),

    # Boston, MA (additional)
    ("02118", "02118", "South End", "Boston", "boston-ma", "MA", "Massachusetts", 42.34, -71.07,
     "the SoWa Open Market, the South End restaurant corridor",
     "Boston&rsquo;s South End with year-round SoWa market events, continuous brownstone restoration, and a busy summer outdoor-event calendar"),

    # San Francisco, CA (additional)
    ("94117", "94117", "Haight-Ashbury / Cole Valley", "San Francisco", "san-francisco-ca", "CA", "California", 37.77, -122.45,
     "Golden Gate Park, the Haight-Ashbury historic district",
     "San Francisco&rsquo;s Haight and Cole Valley with year-round Golden Gate Park festival programming including Hardly Strictly Bluegrass and Outside Lands"),

    # San Diego, CA (additional)
    ("92103", "92103", "Hillcrest / Mission Hills", "San Diego", "san-diego-ca", "CA", "California", 32.75, -117.16,
     "Balboa Park, the Hillcrest restaurant corridor",
     "San Diego&rsquo;s Hillcrest with year-round Balboa Park event programming, Pride parade traffic, and continuous mid-rise residential construction"),

    # Tampa, FL (additional)
    ("33609", "33609", "South Tampa / Westshore", "Tampa", "tampa-fl", "FL", "Florida", 27.94, -82.51,
     "International Plaza, Westshore corporate corridor",
     "South Tampa&rsquo;s Westshore with continuous corporate-park construction, year-round shopping-center events, and a busy summer outdoor-event calendar near the bay"),

    # Orlando, FL (additional)
    ("32803", "32803", "Audubon Park / Mills 50", "Orlando", "orlando-fl", "FL", "Florida", 28.55, -81.36,
     "the Mills 50 arts district, Lake Eola",
     "Orlando&rsquo;s Mills 50 and Audubon Park with continuous boutique-restaurant openings, Lake Eola event programming, and year-round neighborhood festivals"),

    # Salt Lake City, UT
    ("84101", "84101", "Downtown Salt Lake City", "Salt Lake City", "salt-lake-city-ut", "UT", "Utah", 40.76, -111.89,
     "the Delta Center, the Salt Palace Convention Center, Temple Square",
     "downtown Salt Lake City with Jazz games, year-round convention activity, Temple Square event traffic, and continuous downtown construction"),

    # Portland, OR
    ("97204", "97204", "Downtown Portland", "Portland", "portland-or", "OR", "Oregon", 45.52, -122.68,
     "Pioneer Courthouse Square, the Portland&rsquo;5 Centers for the Arts, the Moda Center",
     "downtown Portland with Trail Blazers and Timbers games, year-round outdoor festival programming, and continuous riverfront development"),

    # Kansas City, MO (additional)
    ("64108", "64108", "Crossroads Arts District", "Kansas City", "kansas-city-mo", "MO", "Missouri", 39.09, -94.59,
     "the Power &amp; Light District, T-Mobile Center, the Kauffman Center for the Performing Arts",
     "Kansas City&rsquo;s Crossroads with First Friday gallery walks, year-round arts programming, and continuous adaptive-reuse construction"),

    # St. Louis, MO
    ("63102", "63102", "Downtown St. Louis / Ballpark Village", "St. Louis", "st-louis-mo", "MO", "Missouri", 38.63, -90.20,
     "Busch Stadium, Enterprise Center, the Gateway Arch",
     "downtown St. Louis with Cardinals and Blues games, year-round Gateway Arch event programming, and continuous Ballpark Village construction"),

    # Albuquerque, NM
    ("87102", "87102", "Downtown Albuquerque", "Albuquerque", "albuquerque-nm", "NM", "New Mexico", 35.08, -106.65,
     "the Albuquerque Convention Center, Civic Plaza, Old Town",
     "downtown Albuquerque and Old Town with year-round downtown event programming, Balloon Fiesta event traffic each October, and continuous adaptive-reuse construction"),

    # Oklahoma City, OK
    ("73102", "73102", "Bricktown / Downtown OKC", "Oklahoma City", "oklahoma-city-ok", "OK", "Oklahoma", 35.47, -97.51,
     "Paycom Center, the Oklahoma City National Memorial, the Bricktown Canal",
     "downtown Oklahoma City and Bricktown with Thunder games, year-round canal event programming, and continuous Bricktown construction"),

    # Tulsa, OK
    ("74103", "74103", "Downtown Tulsa", "Tulsa", "tulsa-ok", "OK", "Oklahoma", 36.15, -95.99,
     "the BOK Center, the Cox Business Convention Center, the Tulsa Arts District",
     "downtown Tulsa with year-round arts programming, the Tulsa Mayfest, and continuous downtown adaptive-reuse construction"),

    # Omaha, NE
    ("68102", "68102", "Downtown Omaha / Old Market", "Omaha", "omaha-ne", "NE", "Nebraska", 41.26, -95.93,
     "CHI Health Center, the Old Market historic district, the College World Series",
     "downtown Omaha and the Old Market with year-round event programming and the College World Series each June driving major tourism"),

    # Louisville, KY
    ("40202", "40202", "Downtown Louisville", "Louisville", "louisville-ky", "KY", "Kentucky", 38.25, -85.76,
     "the KFC Yum! Center, the Louisville Convention Center, Fourth Street Live!",
     "downtown Louisville with year-round arena events, Kentucky Derby Festival each May (massive seasonal demand), and continuous downtown adaptive-reuse construction"),

    # Honolulu, HI
    ("96813", "96813", "Downtown Honolulu", "Honolulu", "honolulu-hi", "HI", "Hawaii", 21.31, -157.86,
     "the Hawaii Convention Center, Aloha Stadium events, Iolani Palace",
     "downtown Honolulu with year-round convention activity, military-event programming at JBPHH, and continuous tourism-driven hospitality construction"),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Porta Potty Rental {zip_code} — {neighborhood} ({parent_city}, {state})</title>
<meta name="description" content="Porta potty rental in {zip_code} ({neighborhood}, {parent_city}, {state}). Same-day delivery, OSHA-compliant, ADA units, luxury restroom trailers. Call (833) 652-9344 for an instant quote.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://fixpilotportapottyrentals.com/zip/{zip_code}-porta-potty-rental">
<meta name="geo.region" content="US-{state}">
<meta name="geo.placename" content="{neighborhood}, {parent_city}, {state_full}">
<meta name="geo.position" content="{lat};{lon}">
<meta property="og:title" content="Porta Potty Rental {zip_code} — {neighborhood}">
<meta property="og:description" content="Same-day delivery in {zip_code}. (833) 652-9344.">
<meta property="og:url" content="https://fixpilotportapottyrentals.com/zip/{zip_code}-porta-potty-rental">
<meta property="og:type" content="website">
<meta property="og:image" content="https://fixpilotportapottyrentals.com/hero-banner-images/1.%2020260226_225037_822.webp">

<link rel="stylesheet" href="/assets/tw.css">
<style>:root{{--brand-50:#eff6ff;--brand-100:#dbeafe;--brand-200:#bfdbfe;--brand-300:#93c5fd;--brand-400:#60a5fa;--brand-500:#3b82f6;--brand-600:#2563eb;--brand-700:#1d4ed8;--brand-800:#1e40af;--brand-900:#1e3a8a;--brand-950:#172554;--cta:#ea580c}}</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"LocalBusiness","name":"FixPilot Porta Potty Rentals — {neighborhood}","description":"Porta potty rental serving {zip_code} ({neighborhood}) and the surrounding {parent_city} area.","url":"https://fixpilotportapottyrentals.com/zip/{zip_code}-porta-potty-rental","telephone":"+18336529344","areaServed":{{"@type":"Place","name":"{neighborhood}, {parent_city}, {state_full} {zip_code}","geo":{{"@type":"GeoCoordinates","latitude":{lat},"longitude":{lon}}}}},"address":{{"@type":"PostalAddress","addressLocality":"{parent_city}","addressRegion":"{state}","postalCode":"{zip_code}","addressCountry":"US"}}}}
</script>
</head>
<body class="bg-gray-50 text-gray-900">

<header class="bg-white shadow-md sticky top-0 z-40">
  <div class="container mx-auto px-4 py-4 flex items-center justify-between">
    <a href="/" class="flex items-center gap-2"><div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center"><span class="text-white font-bold text-xl">F</span></div><span class="text-xl font-bold">FixPilot</span></a>
    <nav class="hidden md:flex items-center gap-6 text-sm font-bold"><a href="/services/standard-porta-potty" class="hover:text-green-700">Services</a><a href="/locations" class="hover:text-green-700">Locations</a><a href="/calculator" class="hover:text-green-700">Calculator</a></nav>
    <a href="tel:+18336529344" class="bg-green-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-green-700"><i class="fas fa-phone mr-2"></i>(833) 652-9344</a>
  </div>
</header>

<section class="py-12 md:py-16 bg-gradient-to-br from-blue-50 to-white">
  <div class="container mx-auto px-4 max-w-3xl">
    <nav class="text-sm mb-4 text-gray-600"><a href="/" class="text-green-700 hover:underline">Home</a> / <a href="/locations" class="text-green-700 hover:underline">Locations</a> / <a href="/porta-potty-rental-{parent_city_slug}" class="text-green-700 hover:underline">{parent_city}</a> / <span>ZIP {zip_code}</span></nav>
    <h1 class="text-4xl md:text-5xl font-extrabold text-gray-900 mb-3">Porta Potty Rental in {zip_code} &mdash; {neighborhood}, {parent_city}</h1>
    <p class="text-lg md:text-xl text-gray-700 mb-4">Same-day porta potty, ADA-compliant unit, hand wash station, and luxury restroom trailer rental serving the <strong>{zip_code}</strong> ZIP code and the {neighborhood} neighborhood of {parent_city}, {state_full}.</p>
    <p class="text-gray-700 mb-6">{neighborhood} covers {neighborhood_context}. Whether you&rsquo;re running a wedding near {anchor_venues}, a construction project, or an outdoor event, we deliver same-day from our {parent_city} depot.</p>
    <div class="flex flex-wrap gap-3">
      <a href="tel:+18336529344" class="bg-green-600 hover:bg-green-700 text-white font-extrabold py-3 px-6 rounded-xl shadow-lg pulse-btn"><i class="fas fa-phone mr-2"></i>Call (833) 652-9344</a>
      <a href="/calculator" class="bg-white border-2 border-green-700 text-green-800 font-bold py-3 px-6 rounded-xl">Free unit calculator</a>
    </div>
  </div>
</section>

<section class="py-12 bg-white">
  <div class="container mx-auto px-4 max-w-3xl">
    <h2 class="text-3xl font-extrabold text-gray-900 mb-3">Common rentals in {zip_code}</h2>
    <ul class="space-y-3 mb-6">
      <li class="bg-gray-50 p-5 rounded-xl"><strong><a href="/services/standard-porta-potty" class="text-green-700 underline">Standard porta potty</a></strong> &mdash; Construction sites, casual outdoor events, festivals. $50&ndash;$95/day.</li>
      <li class="bg-gray-50 p-5 rounded-xl"><strong><a href="/services/luxury-restroom-trailers" class="text-green-700 underline">Luxury restroom trailer</a></strong> &mdash; Weddings and upscale events near {anchor_venues}. $300&ndash;$1,200/day.</li>
      <li class="bg-gray-50 p-5 rounded-xl"><strong><a href="/services/ada-compliant-units" class="text-green-700 underline">ADA-compliant unit</a></strong> &mdash; Required at most permitted public events. Pair with any other rental.</li>
      <li class="bg-gray-50 p-5 rounded-xl"><strong><a href="/services/hand-wash-stations" class="text-green-700 underline">Hand wash station</a></strong> &mdash; For events with food service or construction with chemical exposure.</li>
      <li class="bg-gray-50 p-5 rounded-xl"><strong><a href="/services/construction-porta-potty-rentals" class="text-green-700 underline">Construction porta potty</a></strong> &mdash; OSHA-ratio docs, weekly servicing, monthly contracts.</li>
    </ul>

    <h2 class="text-3xl font-extrabold text-gray-900 mt-12 mb-3">Same-day delivery to {zip_code}</h2>
    <p class="text-gray-700 mb-4">Order before noon and we deliver the same business day to {zip_code} and the rest of {neighborhood}. Our {parent_city} depot dispatches throughout {parent_city} and the surrounding {state} metro. For emergencies and after-hours requests, our 24/7 dispatch line answers in under 30 seconds.</p>

    <h2 class="text-3xl font-extrabold text-gray-900 mt-12 mb-3">{neighborhood} planning notes</h2>
    <p class="text-gray-700 mb-4">{neighborhood_context_long}. If your event is on public right-of-way (sidewalk, park, plaza), check whether your municipality requires a porta-potty placement permit &mdash; we file these routinely as part of booking. For private property in {zip_code}, a permit is typically not required.</p>
    <p class="text-gray-700 mb-6">For broader {parent_city} coverage including pricing, full city guide, and other neighborhoods, see our <a href="/porta-potty-rental-{parent_city_slug}" class="text-green-700 underline font-bold">{parent_city} porta potty rental page</a>.</p>
  </div>
</section>

<section class="py-12 md:py-16 bg-gradient-to-br from-blue-50 to-white">
  <div class="container mx-auto px-4 max-w-3xl text-center">
    <h2 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-3">Get a {zip_code} quote in 60 seconds</h2>
    <p class="text-gray-700 text-lg mb-6">Real dispatcher, instant pricing, no callback. Same-day delivery available.</p>
    <a href="tel:+18336529344" class="inline-block bg-green-600 hover:bg-green-700 text-white font-extrabold text-2xl py-4 px-8 rounded-2xl shadow-lg pulse-btn"><i class="fas fa-phone mr-2"></i>(833) 652-9344</a>
  </div>
</section>

<footer class="bg-gray-900 text-gray-300 py-12"><div class="container mx-auto px-4 text-center text-sm"><p class="mb-2">&copy; FixPilot Porta Potty Rentals &mdash; 224 cities, 50 states, 24/7 dispatch.</p><p><a href="tel:+18336529344" class="text-green-400 font-bold">(833) 652-9344</a> &middot; <a href="/locations" class="hover:underline">Service areas</a> &middot; <a href="/blog" class="hover:underline">Blog</a></p></div></footer>

<div id="mobile-cta" class="fixed bottom-0 left-0 right-0 bg-green-600 shadow-2xl transform translate-y-full transition-transform duration-300 z-50 md:hidden flex items-stretch" style="z-index: 9999;"><a href="tel:+18336529344" class="flex-1 py-4 text-center text-white font-extrabold text-lg"><i class="fas fa-phone-alt mr-2 animate-pulse"></i>Call (833) 652-9344</a><button id="mobile-cta-dismiss" type="button" aria-label="Hide call button" class="px-4 text-white/80 hover:text-white text-2xl leading-none">&times;</button></div>
<script>(function(){{var c=document.getElementById('mobile-cta'),d=document.getElementById('mobile-cta-dismiss');if(!c)return;var x=false;try{{x=sessionStorage.getItem('mobileCtaDismissed')==='1';}}catch(e){{}}if(x){{c.style.display='none';return;}}window.addEventListener('scroll',function(){{if(x)return;c.style.transform=window.scrollY>300?'translateY(0)':'translateY(100%)';}},{{passive:true}});if(d){{d.addEventListener('click',function(e){{e.preventDefault();x=true;c.style.transform='translateY(100%)';setTimeout(function(){{c.style.display='none';}},300);try{{sessionStorage.setItem('mobileCtaDismissed','1');}}catch(e){{}}}});}}}})();</script>
</body>
</html>
"""


def main() -> None:
    written = 0
    for entry in ZIPS:
        (zip_slug, zip_code, neighborhood, parent_city, parent_city_slug, state,
         state_full, lat, lon, anchor_venues, neighborhood_context) = entry

        folder = f"zip/{zip_code}-porta-potty-rental"
        os.makedirs(folder, exist_ok=True)
        out = f"{folder}/index.html"
        if os.path.exists(out):
            print(f"  exists: {out}")
            continue

        # Expand neighborhood context for the lower paragraph
        neighborhood_context_long = (
            f"{neighborhood} is {neighborhood_context}. Common porta-potty use cases here "
            f"include construction projects (high-rise, mid-rise, and adaptive-reuse builds), "
            f"outdoor weddings and corporate events, festival programming, and emergency / "
            f"short-notice rentals when existing facilities are offline"
        )

        html = TEMPLATE.format(
            zip_code=zip_code,
            neighborhood=neighborhood,
            parent_city=parent_city,
            parent_city_slug=parent_city_slug,
            state=state,
            state_full=state_full,
            lat=lat,
            lon=lon,
            anchor_venues=anchor_venues,
            neighborhood_context=neighborhood_context,
            neighborhood_context_long=neighborhood_context_long,
        )
        open(out, "w", encoding="utf-8").write(html)
        print(f"  wrote: {out}")
        written += 1

    print(f"\nWrote {written} ZIP-code pages.")


if __name__ == "__main__":
    main()
