#!/usr/bin/env python3
"""Bulk-fix geo data on city pages flagged by audit_geo.py.

For each city in CITY_DATA, replaces in the page:
  - <meta name="geo.region|geo.placename|geo.position|ICBM" ...>
  - schema  addressLocality, addressRegion, postalCode, streetAddress
  - schema  geo.latitude, geo.longitude
  - schema  hasMap
  - schema  areaServed (full block — replaced with neighborhoods + nearby cities)
  - any leftover Atlanta neighborhood names in non-Atlanta pages
  - any leftover Peoria coords / Atlanta coords in coords fields

Conservative: only touches pages explicitly listed in CITY_DATA. Idempotent.
"""
from __future__ import annotations
import json
import os
import re

# Each entry: (state, state_full, county, lat, lon, zip, street, neighborhoods, nearby_cities, wiki_slug)
CITY_DATA: dict[str, dict] = {
    "porta-potty-rental-houston-tx": dict(
        name="Houston", state="TX", state_full="Texas", county="Harris County",
        lat=29.7604, lon=-95.3698, zip="77002", street="1001 Fannin St",
        neighborhoods=["Downtown Houston", "The Heights", "Midtown", "Montrose", "River Oaks",
                       "Galleria/Uptown", "Medical Center", "Energy Corridor", "Memorial",
                       "EaDo (East Downtown)"],
        nearby=["Pasadena", "Sugar Land", "Pearland", "Katy", "The Woodlands", "Spring", "Humble"],
        wiki="Houston",
    ),
    "porta-potty-rental-baton-brouge-la": dict(  # typo slug; will redirect later
        name="Baton Rouge", state="LA", state_full="Louisiana", county="East Baton Rouge Parish",
        lat=30.4515, lon=-91.1871, zip="70802", street="222 St Louis St",
        neighborhoods=["Downtown Baton Rouge", "Mid City", "Garden District", "Spanish Town",
                       "LSU Area", "Southdowns", "Highland Road", "Bocage", "Sherwood Forest",
                       "Old South Baton Rouge"],
        nearby=["Zachary", "Central", "Baker", "Denham Springs", "Gonzales", "Prairieville"],
        wiki="Baton_Rouge,_Louisiana",
    ),
    "porta-potty-rental-charlotte-nc": dict(
        name="Charlotte", state="NC", state_full="North Carolina", county="Mecklenburg County",
        lat=35.2271, lon=-80.8431, zip="28202", street="600 E 4th St",
        neighborhoods=["Uptown Charlotte", "South End", "NoDa", "Plaza Midwood", "Myers Park",
                       "Dilworth", "Ballantyne", "University City", "SouthPark", "Steele Creek"],
        nearby=["Concord", "Gastonia", "Huntersville", "Matthews", "Cornelius", "Mint Hill", "Pineville"],
        wiki="Charlotte,_North_Carolina",
    ),
    "porta-potty-rental-fort-worth-tx": dict(
        name="Fort Worth", state="TX", state_full="Texas", county="Tarrant County",
        lat=32.7555, lon=-97.3308, zip="76102", street="1000 Throckmorton St",
        neighborhoods=["Downtown Fort Worth", "Sundance Square", "Stockyards", "Cultural District",
                       "Magnolia Avenue", "Near Southside", "TCU/Westcliff", "Arlington Heights",
                       "Ridglea", "Westover Hills"],
        nearby=["Arlington", "Mansfield", "Bedford", "Hurst", "Euless", "Burleson", "Benbrook"],
        wiki="Fort_Worth,_Texas",
    ),
    "porta-potty-rental-the-woodlands-tx": dict(
        name="The Woodlands", state="TX", state_full="Texas", county="Montgomery County",
        lat=30.1658, lon=-95.4613, zip="77380", street="9950 Woodlands Pkwy",
        neighborhoods=["Town Center", "Grogan's Mill", "Panther Creek", "Cochran's Crossing",
                       "Indian Springs", "Sterling Ridge", "Alden Bridge", "Creekside Park",
                       "College Park", "Carlton Woods"],
        nearby=["Spring", "Conroe", "Tomball", "Magnolia", "Shenandoah", "Oak Ridge North"],
        wiki="The_Woodlands,_Texas",
    ),
    "porta-potty-rental-phoenix-az": dict(
        name="Phoenix", state="AZ", state_full="Arizona", county="Maricopa County",
        lat=33.4484, lon=-112.0740, zip="85004", street="200 W Washington St",
        neighborhoods=["Downtown Phoenix", "Arcadia", "Biltmore", "Camelback East", "Desert Ridge",
                       "Ahwatukee", "Sunnyslope", "North Phoenix", "South Mountain", "Maryvale"],
        nearby=["Scottsdale", "Tempe", "Mesa", "Glendale", "Chandler", "Gilbert", "Peoria", "Surprise"],
        wiki="Phoenix,_Arizona",
    ),
    "porta-potty-rental-nashville-tn": dict(
        name="Nashville", state="TN", state_full="Tennessee", county="Davidson County",
        lat=36.1627, lon=-86.7816, zip="37203", street="600 Charlotte Ave",
        neighborhoods=["Downtown Nashville", "The Gulch", "Germantown", "East Nashville",
                       "12 South", "Green Hills", "Belle Meade", "Berry Hill", "Sylvan Park",
                       "Sobro"],
        nearby=["Franklin", "Brentwood", "Hendersonville", "Murfreesboro", "Mount Juliet", "Goodlettsville"],
        wiki="Nashville,_Tennessee",
    ),
    "porta-potty-rental-murfreesboro-tn": dict(
        name="Murfreesboro", state="TN", state_full="Tennessee", county="Rutherford County",
        lat=35.8456, lon=-86.3903, zip="37130", street="111 W Vine St",
        neighborhoods=["Downtown Murfreesboro", "MTSU Area", "Blackman", "Stones River",
                       "The Avenue", "Cason Lane", "Northwest Murfreesboro", "Veterans Parkway",
                       "Indian Hills", "Bradyville Pike"],
        nearby=["Smyrna", "La Vergne", "Lebanon", "Eagleville", "Christiana", "Rockvale"],
        wiki="Murfreesboro,_Tennessee",
    ),
    "porta-potty-rental-las-vegas-nv": dict(
        name="Las Vegas", state="NV", state_full="Nevada", county="Clark County",
        lat=36.1716, lon=-115.1391, zip="89101", street="495 S Main St",
        neighborhoods=["The Strip", "Downtown Las Vegas", "Summerlin", "Spring Valley",
                       "Centennial Hills", "Sunrise Manor", "Paradise", "Henderson border",
                       "Chinatown", "Arts District"],
        nearby=["Henderson", "North Las Vegas", "Boulder City", "Pahrump", "Spring Valley"],
        wiki="Las_Vegas",
    ),
    "porta-potty-rental-north-las-vegas-nv": dict(
        name="North Las Vegas", state="NV", state_full="Nevada", county="Clark County",
        lat=36.1989, lon=-115.1175, zip="89030", street="2250 Las Vegas Blvd N",
        neighborhoods=["Aliante", "Eldorado", "Lone Mountain", "Sunrise Manor", "Cheyenne",
                       "Craig Ranch", "Tropical Parkway", "Centennial Hills border",
                       "Apex Industrial", "Nellis"],
        nearby=["Las Vegas", "Henderson", "Sunrise Manor", "Spring Valley", "Boulder City"],
        wiki="North_Las_Vegas,_Nevada",
    ),
    "porta-potty-rental-reno-nv": dict(
        name="Reno", state="NV", state_full="Nevada", county="Washoe County",
        lat=39.5296, lon=-119.8138, zip="89501", street="1 E 1st St",
        neighborhoods=["Downtown Reno", "Midtown", "Old Southwest", "Northwest Reno",
                       "Spanish Springs", "Hidden Valley", "Caughlin Ranch", "Damonte Ranch",
                       "Somersett", "Truckee Meadows"],
        nearby=["Sparks", "Carson City", "Truckee", "Fernley", "Sun Valley"],
        wiki="Reno,_Nevada",
    ),
    "porta-potty-rental-seattle-wa": dict(
        name="Seattle", state="WA", state_full="Washington", county="King County",
        lat=47.6062, lon=-122.3321, zip="98101", street="600 4th Ave",
        neighborhoods=["Downtown Seattle", "Capitol Hill", "Ballard", "Fremont", "Queen Anne",
                       "South Lake Union", "Belltown", "Wallingford", "West Seattle", "Columbia City"],
        nearby=["Bellevue", "Kirkland", "Redmond", "Renton", "Tukwila", "Shoreline", "Burien"],
        wiki="Seattle",
    ),
    "porta-potty-rental-spokane-wa": dict(
        name="Spokane", state="WA", state_full="Washington", county="Spokane County",
        lat=47.6588, lon=-117.4260, zip="99201", street="808 W Spokane Falls Blvd",
        neighborhoods=["Downtown Spokane", "Browne's Addition", "Kendall Yards", "South Hill",
                       "North Hill", "East Central", "Hillyard", "West Plains", "Five Mile Prairie",
                       "Logan Neighborhood"],
        nearby=["Spokane Valley", "Liberty Lake", "Cheney", "Airway Heights", "Mead", "Deer Park"],
        wiki="Spokane,_Washington",
    ),
    "porta-potty-rental-tacoma-wa": dict(
        name="Tacoma", state="WA", state_full="Washington", county="Pierce County",
        lat=47.2529, lon=-122.4443, zip="98402", street="747 Market St",
        neighborhoods=["Downtown Tacoma", "Stadium District", "Hilltop", "Proctor",
                       "North End", "Old Town", "Lincoln District", "South End", "South Tacoma",
                       "Eastside"],
        nearby=["Lakewood", "Puyallup", "Federal Way", "Gig Harbor", "University Place", "Fircrest"],
        wiki="Tacoma,_Washington",
    ),
    "porta-potty-rental-vancouver-wa": dict(
        name="Vancouver", state="WA", state_full="Washington", county="Clark County",
        lat=45.6387, lon=-122.6615, zip="98660", street="415 W 6th St",
        neighborhoods=["Downtown Vancouver", "Uptown Village", "Hazel Dell", "Salmon Creek",
                       "Cascade Park", "Fisher's Landing", "Felida", "Orchards", "Minnehaha",
                       "Hudson's Bay"],
        nearby=["Camas", "Washougal", "Ridgefield", "Battle Ground", "Portland (OR)", "La Center"],
        wiki="Vancouver,_Washington",
    ),
    "porta-potty-rental-baltimore-md": dict(
        name="Baltimore", state="MD", state_full="Maryland", county="Baltimore City",
        lat=39.2904, lon=-76.6122, zip="21201", street="100 N Holliday St",
        neighborhoods=["Inner Harbor", "Fells Point", "Federal Hill", "Canton", "Mount Vernon",
                       "Hampden", "Charles Village", "Roland Park", "Locust Point", "Patterson Park"],
        nearby=["Towson", "Dundalk", "Catonsville", "Essex", "Glen Burnie", "Pikesville", "Parkville"],
        wiki="Baltimore",
    ),
    "porta-potty-rental-ellicott-city-md": dict(
        name="Ellicott City", state="MD", state_full="Maryland", county="Howard County",
        lat=39.2673, lon=-76.7983, zip="21043", street="3430 Court House Dr",
        neighborhoods=["Historic Ellicott City", "Turf Valley", "Waverly Woods", "Dunloggin",
                       "Font Hill", "Centennial", "Burleigh Manor", "Saint John's Lane",
                       "Fulton Crossing", "Wheatfield"],
        nearby=["Columbia", "Catonsville", "Clarksville", "Marriottsville", "Elkridge", "Eldersburg"],
        wiki="Ellicott_City,_Maryland",
    ),
    "porta-potty-rental-waldorf-md": dict(
        name="Waldorf", state="MD", state_full="Maryland", county="Charles County",
        lat=38.6246, lon=-76.9296, zip="20601", street="200 Post Office Rd",
        neighborhoods=["St Charles", "Westlake", "Smallwood Village", "Pinefield", "Carrington",
                       "White Plains border", "Acton", "Berry Acres", "Stoddert", "Gleneagles"],
        nearby=["La Plata", "White Plains", "Bryans Road", "Indian Head", "Brandywine", "Accokeek"],
        wiki="Waldorf,_Maryland",
    ),
    "porta-potty-rental-boulder-co": dict(
        name="Boulder", state="CO", state_full="Colorado", county="Boulder County",
        lat=40.0150, lon=-105.2705, zip="80302", street="1777 Broadway",
        neighborhoods=["Downtown Boulder", "Pearl Street", "University Hill", "Mapleton Hill",
                       "Whittier", "Newlands", "North Boulder", "South Boulder", "Chautauqua",
                       "Gunbarrel"],
        nearby=["Longmont", "Lafayette", "Louisville", "Erie", "Superior", "Niwot", "Broomfield"],
        wiki="Boulder,_Colorado",
    ),
    "porta-potty-rental-centennial-co": dict(
        name="Centennial", state="CO", state_full="Colorado", county="Arapahoe County",
        lat=39.5807, lon=-104.8772, zip="80112", street="13133 E Arapahoe Rd",
        neighborhoods=["Willow Creek", "Walnut Hills", "Foxridge", "Cherry Knolls", "Heritage Greens",
                       "Smoky Hill", "Piney Creek", "Castlewood", "Homestead Farm", "DTC border"],
        nearby=["Englewood", "Greenwood Village", "Aurora", "Lone Tree", "Highlands Ranch", "Parker"],
        wiki="Centennial,_Colorado",
    ),
    "porta-potty-rental-highlands-ranch-co": dict(
        name="Highlands Ranch", state="CO", state_full="Colorado", county="Douglas County",
        lat=39.5539, lon=-104.9689, zip="80129", street="62 Plaza Dr",
        neighborhoods=["Westridge", "Eastridge", "Northridge", "Southridge", "BackCountry",
                       "Highland Heritage", "Town Center", "Highlands Walk", "Falcon Hills",
                       "Saddle Ranch"],
        nearby=["Lone Tree", "Castle Rock", "Centennial", "Littleton", "Parker", "Roxborough"],
        wiki="Highlands_Ranch,_Colorado",
    ),
    "porta-potty-rental-longmont-co": dict(
        name="Longmont", state="CO", state_full="Colorado", county="Boulder County",
        lat=40.1672, lon=-105.1019, zip="80501", street="350 Kimbark St",
        neighborhoods=["Old Town Longmont", "Prospect", "Mountain Brook", "Sunset",
                       "Quail Crossing", "Renaissance", "Grand View Meadows", "Twin Peaks",
                       "Loomiller", "West Grange"],
        nearby=["Boulder", "Niwot", "Erie", "Frederick", "Firestone", "Lyons", "Mead"],
        wiki="Longmont,_Colorado",
    ),
    "porta-potty-rental-bowling-green-ky": dict(
        name="Bowling Green", state="KY", state_full="Kentucky", county="Warren County",
        lat=36.9685, lon=-86.4808, zip="42101", street="1001 College St",
        neighborhoods=["Downtown Bowling Green", "WKU Area", "Cumberland Trace", "Hartland",
                       "Greystone", "Smiths Grove", "Hidden Cove", "Red Oak", "Plum Springs",
                       "Olde Stone"],
        nearby=["Smiths Grove", "Oakland", "Woodburn", "Plum Springs", "Plano", "Alvaton"],
        wiki="Bowling_Green,_Kentucky",
    ),
    "porta-potty-rental-lexington-ky": dict(
        name="Lexington", state="KY", state_full="Kentucky", county="Fayette County",
        lat=38.0406, lon=-84.5037, zip="40507", street="200 E Main St",
        neighborhoods=["Downtown Lexington", "Chevy Chase", "Hamburg", "Beaumont", "Tates Creek",
                       "Bryan Station", "Andover", "Palomar", "Squires Road", "Gardenside"],
        nearby=["Nicholasville", "Versailles", "Georgetown", "Winchester", "Richmond", "Frankfort"],
        wiki="Lexington,_Kentucky",
    ),
    "porta-potty-rental-brooklyn-park-mn": dict(
        name="Brooklyn Park", state="MN", state_full="Minnesota", county="Hennepin County",
        lat=45.0941, lon=-93.3563, zip="55443", street="5200 85th Ave N",
        neighborhoods=["Edinburgh", "Central Park", "Riverside", "Fair Oaks", "West River",
                       "Park Brook", "Northport", "Willow Lane", "Oak Grove", "Brookdale border"],
        nearby=["Maple Grove", "Brooklyn Center", "Plymouth", "Champlin", "Coon Rapids", "Crystal"],
        wiki="Brooklyn_Park,_Minnesota",
    ),
    "porta-potty-rental-madison-wi": dict(
        name="Madison", state="WI", state_full="Wisconsin", county="Dane County",
        lat=43.0731, lon=-89.4012, zip="53703", street="210 Martin Luther King Jr Blvd",
        neighborhoods=["Downtown Madison", "Capitol Square", "State Street", "Williamson-Marquette",
                       "Tenney-Lapham", "Dudgeon-Monroe", "Vilas", "Greenbush", "Sherman Triangle",
                       "Hill Farms"],
        nearby=["Middleton", "Fitchburg", "Sun Prairie", "Verona", "Stoughton", "Waunakee", "McFarland"],
        wiki="Madison,_Wisconsin",
    ),
    "porta-potty-rental-evansville-in": dict(
        name="Evansville", state="IN", state_full="Indiana", county="Vanderburgh County",
        lat=37.9716, lon=-87.5711, zip="47708", street="1 NW Martin Luther King Jr Blvd",
        neighborhoods=["Downtown Evansville", "Haynies Corner Arts District", "East Side",
                       "West Side", "North Side", "Lincolnshire", "Newburgh border", "Howell",
                       "Jacobsville", "Bayard Park"],
        nearby=["Newburgh", "Henderson (KY)", "Boonville", "Mount Vernon", "Princeton", "Owensville"],
        wiki="Evansville,_Indiana",
    ),
    "porta-potty-rental-indianapolis-in": dict(
        name="Indianapolis", state="IN", state_full="Indiana", county="Marion County",
        lat=39.7684, lon=-86.1581, zip="46204", street="200 E Washington St",
        neighborhoods=["Downtown Indianapolis", "Mass Ave", "Fountain Square", "Broad Ripple",
                       "Meridian-Kessler", "Irvington", "Speedway", "Fletcher Place", "Lockerbie",
                       "Cottage Home"],
        nearby=["Carmel", "Fishers", "Greenwood", "Plainfield", "Avon", "Noblesville", "Zionsville"],
        wiki="Indianapolis",
    ),
    "porta-potty-rental-south-bend-in": dict(
        name="South Bend", state="IN", state_full="Indiana", county="St. Joseph County",
        lat=41.6764, lon=-86.2520, zip="46601", street="227 W Jefferson Blvd",
        neighborhoods=["Downtown South Bend", "Notre Dame Area", "East Race", "Northeast",
                       "Southeast Park", "River Park", "Edison", "West Washington", "LaSalle Park",
                       "Harter Heights"],
        nearby=["Mishawaka", "Granger", "Niles (MI)", "Elkhart", "Goshen", "Osceola"],
        wiki="South_Bend,_Indiana",
    ),
    "porta-potty-rental-hoover-al": dict(
        name="Hoover", state="AL", state_full="Alabama", county="Jefferson County",
        lat=33.4054, lon=-86.8114, zip="35216", street="100 Municipal Dr",
        neighborhoods=["Riverchase", "Greystone", "The Preserve", "Ross Bridge", "Lake Cyrus",
                       "Trace Crossings", "Bluff Park", "Inverness", "Patton Creek", "Brookmoore"],
        nearby=["Birmingham", "Vestavia Hills", "Mountain Brook", "Pelham", "Helena", "Alabaster"],
        wiki="Hoover,_Alabama",
    ),
    "porta-potty-rental-huntsville-al": dict(
        name="Huntsville", state="AL", state_full="Alabama", county="Madison County",
        lat=34.7304, lon=-86.5861, zip="35801", street="308 Fountain Cir SW",
        neighborhoods=["Downtown Huntsville", "Five Points", "Twickenham", "Old Town",
                       "Medical District", "Hampton Cove", "Jones Valley", "Blossomwood",
                       "Big Cove", "Monte Sano"],
        nearby=["Madison", "Decatur", "Athens", "Meridianville", "Hazel Green", "Owens Cross Roads"],
        wiki="Huntsville,_Alabama",
    ),
    "porta-potty-rental-mobile-al": dict(
        name="Mobile", state="AL", state_full="Alabama", county="Mobile County",
        lat=30.6954, lon=-88.0399, zip="36602", street="205 Government St",
        neighborhoods=["Downtown Mobile", "Midtown", "Spring Hill", "West Mobile", "Tillmans Corner",
                       "Theodore", "Plateau", "Oakleigh Garden District", "Old Dauphin Way",
                       "Crichton"],
        nearby=["Saraland", "Prichard", "Chickasaw", "Daphne", "Spanish Fort", "Semmes", "Theodore"],
        wiki="Mobile,_Alabama",
    ),
    "porta-potty-rental-myrtle-beach-sc": dict(
        name="Myrtle Beach", state="SC", state_full="South Carolina", county="Horry County",
        lat=33.6891, lon=-78.8867, zip="29577", street="937 Broadway St",
        neighborhoods=["Downtown Myrtle Beach", "Ocean Forest", "Pine Lakes", "Market Common",
                       "Carolina Forest", "Withers Estate", "Dunes Club", "Arcadian Shores",
                       "Briarcliffe Acres", "Long Bay"],
        nearby=["North Myrtle Beach", "Surfside Beach", "Conway", "Garden City", "Murrells Inlet",
                "Pawleys Island"],
        wiki="Myrtle_Beach,_South_Carolina",
    ),
    "porta-potty-rental-plymouth-ma": dict(
        name="Plymouth", state="MA", state_full="Massachusetts", county="Plymouth County",
        lat=41.9584, lon=-70.6673, zip="02360", street="11 Lincoln St",
        neighborhoods=["Downtown Plymouth", "Plymouth Waterfront", "The Pinehills", "Manomet",
                       "White Horse Beach", "Cedarville", "North Plymouth", "Chiltonville",
                       "West Plymouth", "Saquish"],
        nearby=["Kingston", "Carver", "Plympton", "Sandwich", "Bourne", "Duxbury"],
        wiki="Plymouth,_Massachusetts",
    ),
    "porta-potty-rental-independence-mo": dict(
        name="Independence", state="MO", state_full="Missouri", county="Jackson County",
        lat=39.0911, lon=-94.4155, zip="64050", street="111 E Maple Ave",
        neighborhoods=["Independence Square", "Englewood", "Fairmount", "Maywood", "Stone Canyon",
                       "Hawthorne", "Crackerneck Creek", "Crysler Park", "Mt Washington",
                       "Atherton"],
        nearby=["Kansas City", "Blue Springs", "Sugar Creek", "Lee's Summit", "Raytown", "Buckner"],
        wiki="Independence,_Missouri",
    ),
    "porta-potty-rental-kansas-city-mo": dict(
        name="Kansas City", state="MO", state_full="Missouri", county="Jackson County",
        lat=39.0997, lon=-94.5786, zip="64106", street="414 E 12th St",
        neighborhoods=["Downtown Kansas City", "Crossroads", "Westport", "Country Club Plaza",
                       "Brookside", "Waldo", "River Market", "Power & Light District", "Northland",
                       "Hyde Park"],
        nearby=["Independence", "Lee's Summit", "North Kansas City", "Gladstone", "Liberty",
                "Overland Park (KS)", "Olathe (KS)"],
        wiki="Kansas_City,_Missouri",
    ),
    "porta-potty-rental-wichita-ks": dict(
        name="Wichita", state="KS", state_full="Kansas", county="Sedgwick County",
        lat=37.6872, lon=-97.3301, zip="67202", street="455 N Main St",
        neighborhoods=["Downtown Wichita", "Old Town", "Delano", "Riverside", "College Hill",
                       "Crown Heights", "Eastborough", "Crestview", "Sleepy Hollow",
                       "McAdams Park"],
        nearby=["Derby", "Andover", "Bel Aire", "Park City", "Maize", "Goddard", "Haysville"],
        wiki="Wichita,_Kansas",
    ),
    "porta-potty-rental-paradise-ca": dict(
        name="Paradise", state="CA", state_full="California", county="Butte County",
        lat=39.7596, lon=-121.6219, zip="95969", street="5555 Skyway",
        neighborhoods=["Downtown Paradise", "Magalia", "Old Magalia", "Upper Ridge", "Lower Ridge",
                       "Pearson Road", "Skyway", "Pentz Road", "Clark Road", "Honey Run"],
        nearby=["Magalia", "Chico", "Oroville", "Concow", "Yankee Hill", "Stirling City"],
        wiki="Paradise,_California",
    ),
    "porta-potty-rental-athens-ga": dict(
        name="Athens", state="GA", state_full="Georgia", county="Clarke County",
        lat=33.9519, lon=-83.3576, zip="30601", street="301 College Ave",
        neighborhoods=["Downtown Athens", "Five Points", "Normaltown", "Cobbham",
                       "Boulevard", "Westside Athens", "Eastside Athens", "Bishop Park",
                       "Pulaski Heights", "Beechwood"],
        nearby=["Watkinsville", "Winterville", "Bogart", "Statham", "Hull", "Bishop"],
        wiki="Athens,_Georgia",
    ),
    "porta-potty-rental-augusta-ga": dict(
        name="Augusta", state="GA", state_full="Georgia", county="Richmond County",
        lat=33.4735, lon=-82.0105, zip="30901", street="535 Telfair St",
        neighborhoods=["Downtown Augusta", "Summerville", "West Augusta", "South Augusta",
                       "Olde Town", "Harrisburg", "Sand Hills", "Forest Hills",
                       "Westside Augusta", "Hill District"],
        nearby=["North Augusta (SC)", "Martinez", "Evans", "Grovetown", "Hephzibah", "Aiken (SC)"],
        wiki="Augusta,_Georgia",
    ),
    "porta-potty-rental-macon-ga": dict(
        name="Macon", state="GA", state_full="Georgia", county="Bibb County",
        lat=32.8407, lon=-83.6324, zip="31201", street="700 Poplar St",
        neighborhoods=["Downtown Macon", "Ingleside", "Vineville", "Shirley Hills",
                       "Beall's Hill", "Pleasant Hill", "Lizella", "North Macon",
                       "South Macon", "East Macon"],
        nearby=["Warner Robins", "Forsyth", "Perry", "Centerville", "Byron", "Gray", "Bonaire"],
        wiki="Macon,_Georgia",
    ),
    "porta-potty-rental-savannah-ga": dict(
        name="Savannah", state="GA", state_full="Georgia", county="Chatham County",
        lat=32.0809, lon=-81.0912, zip="31401", street="2 E Bay St",
        neighborhoods=["Historic District", "Starland District", "Ardsley Park", "Thomas Square",
                       "Victorian District", "Midtown Savannah", "Southside", "Eastside",
                       "Ferguson Avenue", "Habersham Village"],
        nearby=["Pooler", "Tybee Island", "Wilmington Island", "Garden City", "Bloomingdale",
                "Port Wentworth", "Richmond Hill"],
        wiki="Savannah,_Georgia",
    ),
}


def patch_meta(html: str, key: str, attr: str, value: str) -> str:
    pattern = rf'(<meta\s+{attr}="{re.escape(key)}"\s+content=")[^"]*(")'
    return re.sub(pattern, lambda m: f"{m.group(1)}{value}{m.group(2)}", html, count=1)


def replace_area_served(html: str, neighborhoods: list[str], nearby: list[str], city: str, wiki: str) -> str:
    """Replace the entire areaServed array. Match the array conservatively."""
    pattern = re.compile(r'"areaServed"\s*:\s*\[(?:[^\[\]]|\[[^\]]*\])*\]', re.DOTALL)
    new_entries = [f'{{"@type": "City", "name": "{city}", "sameAs": "https://en.wikipedia.org/wiki/{wiki}"}}']
    for n in neighborhoods:
        new_entries.append(f'{{"@type": "Neighborhood", "name": "{n}"}}')
    for c in nearby:
        new_entries.append(f'{{"@type": "City", "name": "{c}"}}')
    new_block = '"areaServed": [\n        ' + ',\n        '.join(new_entries) + '\n      ]'
    return pattern.sub(new_block, html, count=1)


def fix_one(slug: str, data: dict) -> bool:
    path = f"{slug}/index.html"
    if not os.path.exists(path):
        print(f"  skip (missing): {path}")
        return False
    html = open(path, encoding="utf-8").read()
    orig = html

    # geo meta tags
    html = patch_meta(html, "geo.region", "name", f"US-{data['state']}")
    html = patch_meta(html, "geo.placename", "name", f"{data['name']}, {data['state_full']}")
    html = patch_meta(html, "geo.position", "name", f"{data['lat']};{data['lon']}")
    html = patch_meta(html, "ICBM", "name", f"{data['lat']}, {data['lon']}")

    # schema fields (one-shot regexes)
    html = re.sub(r'"addressLocality"\s*:\s*"[^"]*"',
                  f'"addressLocality": "{data["name"]}"', html, count=1)
    html = re.sub(r'"addressRegion"\s*:\s*"[A-Z]{2}"',
                  f'"addressRegion": "{data["state"]}"', html, count=1)
    html = re.sub(r'"postalCode"\s*:\s*"[0-9]{5}"',
                  f'"postalCode": "{data["zip"]}"', html, count=1)
    html = re.sub(r'"streetAddress"\s*:\s*"[^"]*"',
                  f'"streetAddress": "{data["street"]}"', html, count=1)
    html = re.sub(r'"latitude"\s*:\s*-?[0-9.]+',
                  f'"latitude": {data["lat"]}', html, count=1)
    html = re.sub(r'"longitude"\s*:\s*-?[0-9.]+',
                  f'"longitude": {data["lon"]}', html, count=1)

    # hasMap (handle both Google Maps + iframe-style URLs)
    qcity = data['name'].replace(' ', '+')
    html = re.sub(
        r'"hasMap"\s*:\s*"[^"]*"',
        f'"hasMap": "https://maps.google.com/maps?q={qcity}+{data["state"]}+{data["zip"]}"',
        html, count=1,
    )

    # areaServed array
    html = replace_area_served(html, data['neighborhoods'], data['nearby'], data['name'], data['wiki'])

    # Map iframe src (if present)
    html = re.sub(
        r'(<iframe[^>]+src=")[^"]*maps\.google\.com/maps\?q=[^"]*(")',
        rf'\1https://maps.google.com/maps?q={qcity}+{data["state"]}&t=&z=11&ie=UTF8&iwloc=&output=embed\2',
        html,
    )

    if html == orig:
        print(f"  unchanged: {path}")
        return False
    open(path, "w", encoding="utf-8").write(html)
    return True


def main() -> None:
    fixed = 0
    for slug, data in CITY_DATA.items():
        if fix_one(slug, data):
            print(f"  fixed: {slug}")
            fixed += 1
    print(f"\nFixed {fixed} city pages out of {len(CITY_DATA)} entries.")


if __name__ == "__main__":
    main()
