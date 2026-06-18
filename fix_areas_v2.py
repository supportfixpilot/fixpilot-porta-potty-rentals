#!/usr/bin/env python3
"""Comprehensive fix for template leftover areas in city pages."""

import re
from pathlib import Path

CITY_DATA = {
    "houston-tx": {
        "name": "Houston",
        "state": "TX",
        "county": "Harris County",
        "areas": [
            {"name": "Downtown Houston", "desc": "Perfect for construction near Discovery Green and events at Minute Maid Park."},
            {"name": "Galleria", "desc": "Luxury restroom trailers for upscale weddings and events near The Galleria."},
            {"name": "Medical Center", "desc": "Serving Texas Medical Center and all hospital facilities."},
            {"name": "The Heights", "desc": "Event services for this historic neighborhood with Victorian architecture."},
            {"name": "Midtown", "desc": "Quick delivery to Houston's growing arts and entertainment district."},
            {"name": "Montrose", "desc": "Perfect for gallery openings, restaurants, and cultural events."},
            {"name": "River Oaks", "desc": "Premium sanitation services for luxury events in Houston's premier neighborhood."},
            {"name": "Sugar Land", "desc": "Serving Sugar Land Town Center and all Fort Bend County locations."},
            {"name": "Pearland", "desc": "Fast delivery to Pearland and southern Harris County."},
            {"name": "Katy", "desc": "Serving Katy ISD construction and community events."},
        ]
    },
    "phoenix-az": {
        "name": "Phoenix",
        "state": "AZ",
        "county": "Maricopa County",
        "areas": [
            {"name": "Scottsdale", "desc": "Luxury restroom trailers for Scottsdale resorts and events."},
            {"name": "Mesa", "desc": "Serving Mesa Convention Center and Apache Junction."},
            {"name": "Tempe", "desc": "Perfect for ASU events and Tempe Town Lake activities."},
            {"name": "Gilbert", "desc": "Family-friendly sanitation for Gilbert parks and community events."},
            {"name": "Chandler", "desc": "Serving Chandler Fashion Center and downtown Chandler."},
            {"name": "Glendale", "desc": "Quick delivery to State Farm Stadium and Gila River Arena."},
            {"name": "Peoria", "desc": "Serving Peoria sports complexes and Spring Training venues."},
            {"name": "Surprise", "desc": "Perfect for Surprise Stadium and Surprise Recreation Campus."},
            {"name": "Arcadia", "desc": "Premium services for Arcadia neighborhood and Camelback Mountain events."},
            {"name": "Desert Ridge", "desc": "Serving Desert Ridge Marketplace and JW Marriott Desert Ridge."},
        ]
    },
    "charlotte-nc": {
        "name": "Charlotte",
        "state": "NC",
        "county": "Mecklenburg County",
        "areas": [
            {"name": "South End", "desc": "Perfect for South End art walks and brewery events."},
            {"name": "Uptown", "desc": "Serving Charlotte's urban core, Bank of America Stadium, and Spectrum Center."},
            {"name": "NoDa", "desc": "Artistic sanitation for NoDa's galleries and music venues."},
            {"name": "Plaza Midwood", "desc": "Community events and neighborhood festivals in Plaza Midwood."},
            {"name": "Myers Park", "desc": "Luxury events and weddings in Charlotte's most prestigious neighborhood."},
            {"name": "Dilworth", "desc": "Quick delivery to Dilworth's parks and historic district."},
            {"name": "Ballantyne", "desc": "Serving Ballantyne Corporate Park and Ballantyne Village."},
            {"name": "University City", "desc": "UNC Charlotte events and University City partnerships."},
            {"name": "Lake Norman", "desc": "Lakefront events and Cornelius, Huntersville, and Davidson."},
            {"name": "Fort Mill", "desc": "Fast delivery to Fort Mill, Tega Cay, and Rock Hill."},
        ]
    },
    "fort-worth-tx": {
        "name": "Fort Worth",
        "state": "TX",
        "county": "Tarrant County",
        "areas": [
            {"name": "Downtown Fort Worth", "desc": "Perfect for Sundance Square events and cattle auctions."},
            {"name": "Stockyards", "desc": "Authentic western experiences near Fort Worth Stockyards National Historic District."},
            {"name": "Magnolia", "desc": "Serving the vibrant Magnolia District and Near Southside."},
            {"name": "TCU", "desc": "Amphitheater events and TCU campus construction."},
            {"name": "Sundance", "desc": "Premium services for Sundance Square Plaza events."},
            {"name": "Riverside", "desc": "Quick delivery to Fort Worth's riverside developments."},
            {"name": "North Fort Worth", "desc": "Serving AllianceTexas and Haslet construction projects."},
            {"name": "South Fort Worth", "desc": "Community events and Hulen Mall area."},
            {"name": "Benbrook", "desc": "Perfect for Benbrook Lake activities and community events."},
            {"name": "Haltom City", "desc": "Fast delivery to Haltom City and North Richland Hills."},
        ]
    },
    "the-woodlands-tx": {
        "name": "The Woodlands",
        "state": "TX",
        "county": "Montgomery County",
        "areas": [
            {"name": "Town Center", "desc": "Perfect for The Woodlands Mall and Cynthia Woods Pavilion events."},
            {"name": "Grogan's Mill", "desc": "Serving Grogan's Mill Village and neighborhood events."},
            {"name": "Panther Creek", "desc": "Quick delivery to Panther Creek Village and surrounding areas."},
            {"name": "Sterling Ridge", "desc": "Premium sanitation for Sterling Ridge events and construction."},
            {"name": "Cochran's Crossing", "desc": "Perfect for Cochran's Crossing neighborhood and schools."},
            {"name": "Indian Springs", "desc": "Serving Indian Springs Village and local parks."},
            {"name": "Alden Bridge", "desc": "Fast delivery to Alden Bridge community events."},
            {"name": "Creekside", "desc": "Perfect for Creekside Park Village and George Mitchell Preserve."},
            {"name": "Spring", "desc": "Serving Spring, TX and Klein area communities."},
            {"name": "Conroe", "desc": "Quick delivery to Conroe and Lake Conroe events."},
        ]
    },
    "baton-brouge-la": {
        "name": "Baton Rouge",
        "state": "LA",
        "county": "East Baton Rouge Parish",
        "areas": [
            {"name": "Downtown Baton Rouge", "desc": "Perfect for Louisiana State Capitol events and downtown festivals."},
            {"name": "LSU", "desc": "Quick delivery to Tiger Stadium and LSU campus construction."},
            {"name": "Southdowns", "desc": "Premium sanitation for Southdowns neighborhood events."},
            {"name": "Highland Road", "desc": "Serving Highland Road Park and community facilities."},
            {"name": "Perkins", "desc": "Perfect for Perkins Rowe shopping center and surrounding areas."},
            {"name": "Broadmoor", "desc": "Community events and Broadmoor neighborhood festivals."},
            {"name": "Sherwood Forest", "desc": "Quick delivery to Sherwood Forest and Garden District."},
            {"name": "Bocage", "desc": "Premium services for Bocage Shopping Center events."},
            {"name": "Mid City", "desc": "Serving Downtown Development District and Mid City."},
            {"name": "Webre", "desc": "Perfect for Webre area and Baton Rouge Airport vicinity."},
        ]
    },
    "boulder-co": {
        "name": "Boulder",
        "state": "CO",
        "county": "Boulder County",
        "areas": [
            {"name": "Downtown Boulder", "desc": "Perfect for Pearl Street Mall and Pearl Street concerts."},
            {"name": "Pearl Street", "desc": "Quick delivery to Pearl Street Farmers Market events."},
            {"name": "University Hill", "desc": "Serving CU Boulder campus and University Hill businesses."},
            {"name": "Mapleton Hill", "desc": "Historic neighborhoods and boulder Creek path events."},
            {"name": "Whittier", "desc": "Perfect for Whittier neighborhood and Eben G. Fine Park."},
            {"name": "Baseline", "desc": "Serving Baseline Reservoir and east Boulder areas."},
            {"name": "North Boulder", "desc": "Quick delivery to North Boulder and Foothills."},
            {"name": "South Boulder", "desc": "Perfect for South Boulder and Marshall Lake activities."},
            {"name": "Chautauqua", "desc": "Premium services for Chautauqua hiking and events."},
            {"name": "Eldorado Springs", "desc": "Fast delivery to Eldorado Canyon and springs."},
        ]
    },
    "bowling-green-ky": {
        "name": "Bowling Green",
        "state": "KY",
        "county": "Warren County",
        "areas": [
            {"name": "Downtown Bowling Green", "desc": "Perfect for The Trace and Fountain Square events."},
            {"name": "Schmidt", "desc": "Serving Schmidt development and surrounding areas."},
            {"name": "Cumberland Trace", "desc": "Quick delivery to Cumberland Trace and KY Exhibition Center."},
            {"name": "Rich Pond", "desc": "Perfect for Rich Pond neighborhood and community events."},
            {"name": "Plano", "desc": "Serving Plano community and local parks."},
            {"name": "Smiths Grove", "desc": "Fast delivery to Smiths Grove and Barren County."},
            {"name": "Woodburn", "desc": "Perfect for Woodburn and Western Kentucky University area."},
            {"name": "Oakland", "desc": "Premium sanitation for Oakland community events."},
            {"name": "Smiths", "desc": "Quick delivery to Smiths neighborhood and businesses."},
            {"name": "Alvaton", "desc": "Serving Alvaton and southern Warren County."},
        ]
    },
    "brooklyn-park-mn": {
        "name": "Brooklyn Park",
        "state": "MN",
        "county": "Hennepin County",
        "areas": [
            {"name": "Central Brooklyn Park", "desc": "Perfect for Brooklyn Center and North Hennepin College."},
            {"name": "North Brooklyn Park", "desc": "Quick delivery to North Brooklyn Park neighborhoods."},
            {"name": "South Brooklyn Park", "desc": "Serving South Brooklyn Park and Mississippi Crossing."},
            {"name": "East Brooklyn Park", "desc": "Perfect for East Brooklyn Park and Highway 610 corridor."},
            {"name": "West Brooklyn Park", "desc": "Premium services for West Brooklyn Park area."},
            {"name": "Edina", "desc": "Fast delivery to Edina and Southdale Center vicinity."},
            {"name": "Crystal", "desc": "Serving Crystal and Robbinsdale communities."},
            {"name": "Brooklyn Center", "desc": "Perfect for Brooklyn Center and Earle Brown Farm."},
            {"name": "Plymouth", "desc": "Quick delivery to Plymouth and Wayzata area."},
            {"name": "Champlin", "desc": "Premium services for Champlin and Hanthorne."},
        ]
    },
    "centennial-co": {
        "name": "Centennial",
        "state": "CO",
        "county": "Arapahoe County",
        "areas": [
            {"name": " DTC", "desc": "Perfect for Denver Tech Center and business park construction."},
            {"name": "Independence", "desc": "Quick delivery to Independence Plaza and surrounding areas."},
            {"name": "Willow Creek", "desc": "Serving Willow Creek neighborhood and parks."},
            {"name": "Cherry Creek", "desc": "Premium sanitation for Cherry Creek Shopping Center."},
            {"name": "Parker", "desc": "Fast delivery to Parker and Lincoln Meadows."},
            {"name": "Foxridge", "desc": "Perfect for Foxridge and Centennial center area."},
            {"name": "Highlands", "desc": "Serving Highlands at Pinehurst and surrounding neighborhoods."},
            {"name": "Silverbrook", "desc": "Quick delivery to Silverbrook and Walnut Hills."},
            {"name": "Louviers", "desc": "Premium services for Louviers and Dove Valley."},
            {"name": "Cottonwood", "desc": "Fast delivery to Cottonwood and Aspen Hills."},
        ]
    },
    "highlands-ranch-co": {
        "name": "Highlands Ranch",
        "state": "CO",
        "county": "Douglas County",
        "areas": [
            {"name": "North Highlands Ranch", "desc": "Perfect for C-470 corridor and HRCA recreation."},
            {"name": "East Highlands Ranch", "desc": "Quick delivery to East Highlands Ranch neighborhoods."},
            {"name": "South Highlands Ranch", "desc": "Serving South Highlands Ranch and Black Forest."},
            {"name": "West Highlands Ranch", "desc": "Premium sanitation for West Highlands Ranch."},
            {"name": "Westridge", "desc": "Perfect for Westridge and Back Country events."},
            {"name": "Southglenn", "desc": "Quick delivery to Southglenn Shopping Center."},
            {"name": "Cougar", "desc": "Serving Cougar area and Littleton莲社区."},
            {"name": "Eastridge", "desc": "Fast delivery to Eastridge and Falcon Creek."},
            {"name": "Ranch", "desc": "Perfect for Main Street Highlands Ranch events."},
            {"name": "Highlands", "desc": "Premium services for all Highlands Ranch villages."},
        ]
    },
    "hoover-al": {
        "name": "Hoover",
        "state": "AL",
        "county": "Jefferson County",
        "areas": [
            {"name": "The Preserve", "desc": "Perfect for The Preserve and Riverchase events."},
            {"name": "Ross Bridge", "desc": "Quick delivery to Ross Bridge and Hoover Metropolitan."},
            {"name": "Greystone", "desc": "Premium sanitation for Greystone Golf Club events."},
            {"name": "Riverchase", "desc": "Serving Riverchase Galleria and Patriot Park."},
            {"name": "Lake Cyrus", "desc": "Perfect for Lake Cyrus and Deer Valley area."},
            {"name": "Big Creek", "desc": "Quick delivery to Big Creek and Weatherly."},
            {"name": "Deer Valley", "desc": "Fast delivery to Deer Valley and Valleydale."},
            {"name": "Carmel", "desc": "Premium services for Carmel and Cahaba Heights."},
            {"name": "Inverness", "desc": "Serving Inverness and Shelby County."},
            {"name": "Cahaba Heights", "desc": "Quick delivery to Cahaba Heights and Mountain Brook."},
        ]
    },
    "huntsville-al": {
        "name": "Huntsville",
        "state": "AL",
        "county": "Madison County",
        "areas": [
            {"name": "Downtown Huntsville", "desc": "Perfect for Von Braun Center and courthouse square."},
            {"name": "Five Points", "desc": "Quick delivery to Five Points neighborhood events."},
            {"name": "Cliftons", "desc": "Serving Cliftons and campus area near UAH."},
            {"name": "Medical District", "desc": "Premium sanitation for Huntsville Hospital construction."},
            {"name": "Campus", "desc": "Fast delivery to Alabama A&M and Oakwood University."},
            {"name": "Merrill", "desc": "Perfect for Merrill and Redstone Arsenal vicinity."},
            {"name": "Lake Forest", "desc": "Quick delivery to Lake Forest and Whitesburg."},
            {"name": "Hampton Cove", "desc": "Premium services for Hampton Cove and Owens Cross Roads."},
            {"name": "Meridianville", "desc": "Fast delivery to Meridianville and Hazel Green."},
            {"name": "Madison", "desc": "Serving Madison, AL and Redstone Gateway."},
        ]
    },
    "independence-mo": {
        "name": "Independence",
        "state": "MO",
        "county": "Jackson County",
        "areas": [
            {"name": "Downtown Independence", "desc": "Perfect for Truman Historic District and Square events."},
            {"name": "Englewood", "desc": "Quick delivery to Englewood and Little Blue areas."},
            {"name": "River", "desc": "Serving Truman Road and river bottoms communities."},
            {"name": "Little Blue", "desc": "Premium sanitation for Little Blue and向外."},
            {"name": "Knoche", "desc": "Fast delivery to Knoche and Van Branch."},
            {"name": "Sugar Creek", "desc": "Perfect for Sugar Creek and Grain Valley."},
            {"name": "Lake Tapawingo", "desc": "Quick delivery to Lake Tapawingo and Blue Springs."},
            {"name": "Lee's Summit", "desc": "Premium services for Lee's Summit and Unity Village."},
            {"name": "Blue Springs", "desc": "Fast delivery to Blue Springs and Adams Dairy."},
            {"name": "Kansas City", "desc": "Serving Kansas City metro and Grandview."},
        ]
    },
    "kansas-city-mo": {
        "name": "Kansas City",
        "state": "MO",
        "county": "Jackson County",
        "areas": [
            {"name": "Downtown Kansas City", "desc": "Perfect for Power & Light District and Sprint Center."},
            {"name": "Crossroads", "desc": "Quick delivery to Crossroads Arts District."},
            {"name": "Westport", "desc": "Premium sanitation for Westport and Waldo."},
            {"name": "Plaza", "desc": "Fast delivery to Country Club Plaza and Loose Park."},
            {"name": "Brookside", "desc": "Perfect for Brookside Farmers Market and neighborhood."},
            {"name": "Waldo", "desc": "Quick delivery to Waldo and Brookside."},
            {"name": "Lee's Summit", "desc": "Serving Lee's Summit and Lake Lotawana."},
            {"name": "Independence", "desc": "Fast delivery to Independence and Truman Historic District."},
            {"name": "North Kansas City", "desc": "Premium services for North KC and Claycomo."},
            {"name": "Gladstone", "desc": "Quick delivery to Gladstone and Liberty."},
        ]
    },
    "lexington-ky": {
        "name": "Lexington",
        "state": "KY",
        "county": "Fayette County",
        "areas": [
            {"name": "Downtown Lexington", "desc": "Perfect for Rupp Arena and Cheapside Park."},
            {"name": "Chevy Chase", "desc": "Quick delivery to Chevy Chase and Pavilion."},
            {"name": "Southland", "desc": "Premium sanitation for Southland Drive events."},
            {"name": "Hamburg", "desc": "Fast delivery to Hamburg and Lexington Green."},
            {"name": "Palgrove", "desc": "Perfect for Palgrove and Tates Creek area."},
            {"name": "Beaumont", "desc": "Quick delivery to Beaumont and Masterson Station."},
            {"name": "Bryan Station", "desc": "Premium services for Bryan Station and Greendale."},
            {"name": "Tates Creek", "desc": "Fast delivery to Tates Creek and Lansdowne."},
            {"name": "Mount Tabor", "desc": "Serving Mount Tabor and Nicholasville Road area."},
            {"name": "Gardens", "desc": "Perfect for Gardens at Kentucky Horse Park."},
        ]
    },
    "mobile-al": {
        "name": "Mobile",
        "state": "AL",
        "county": "Mobile County",
        "areas": [
            {"name": "Downtown Mobile", "desc": "Perfect for Cathedral Square and Bienville Square."},
            {"name": "Midtown", "desc": "Quick delivery to Midtown and Oakleigh Garden District."},
            {"name": "Spring Hill", "desc": "Premium sanitation for Spring Hill College and area."},
            {"name": "West Mobile", "desc": "Fast delivery to West Mobile and University of South Alabama."},
            {"name": "Semmes", "desc": "Perfect for Semmes and west Mobile communities."},
            {"name": "Theodore", "desc": "Quick delivery to Theodore and Mobile Airport."},
            {"name": "Prichard", "desc": "Premium services for Prichard and Chickasaw."},
            {"name": "Chickasaw", "desc": "Fast delivery to Chickasaw and Satsuma."},
            {"name": "Tillmans", "desc": "Perfect for Tillmans Corner and Theodore."},
            {"name": "Cottage Hill", "desc": "Quick delivery to Cottage Hill and Forest Hill."},
        ]
    },
    "myrtle-beach-sc": {
        "name": "Myrtle Beach",
        "state": "SC",
        "county": "Horry County",
        "areas": [
            {"name": "Myrtle Beach", "desc": "Perfect for Broadway at the Beach and Beachwalk."},
            {"name": "Ocean Forest", "desc": "Quick delivery to Ocean Forest and Dunes area."},
            {"name": "Arcadian", "desc": "Premium sanitation for Arcadian Shores events."},
            {"name": "Briarcliffe", "desc": "Fast delivery to Briarcliffe Acres and Carolina Forest."},
            {"name": "North Myrtle Beach", "desc": "Perfect for Cherry Grove and Windy Hill Beach."},
            {"name": "Surfside", "desc": "Quick delivery to Surfside Beach and Garden City."},
            {"name": "Garden City", "desc": "Premium services for Garden City Beach."},
            {"name": "Murrells Inlet", "desc": "Fast delivery to Murrells Inlet and Pawleys Island."},
            {"name": "Conway", "desc": "Perfect for Conway and Horry Georgetown Tech."},
            {"name": "Loris", "desc": "Quick delivery to Loris and Aynor."},
        ]
    },
    "plymouth-ma": {
        "name": "Plymouth",
        "state": "MA",
        "county": "Plymouth County",
        "areas": [
            {"name": "Downtown Plymouth", "desc": "Perfect for waterfront and Plymouth Rock events."},
            {"name": "Waterfront", "desc": "Quick delivery to Plymouth Harbor and Mayflower II."},
            {"name": "The Pinehills", "desc": "Premium sanitation for Pinehills Golf Club."},
            {"name": "Plymouth Beach", "desc": "Fast delivery to Long Beach and Plymouth Beach."},
            {"name": "West Plymouth", "desc": "Perfect for West Plymouth and Manomet."},
            {"name": "North Plymouth", "desc": "Quick delivery to North Plymouth and Cedarville."},
            {"name": "South Plymouth", "desc": "Premium services for South Plymouth area."},
            {"name": "Manomet", "desc": "Fast delivery to Manomet and White Horse Beach."},
            {"name": "Sagamore Beach", "desc": "Perfect for Sagamore Beach and MA-3 corridor."},
            {"name": "Bourne", "desc": "Quick delivery to Bourne and Sagamore Bridge."},
        ]
    },
    "south-fulton-ga": {
        "name": "South Fulton",
        "state": "GA",
        "county": "Fulton County",
        "areas": [
            {"name": "College Park", "desc": "Perfect for College Park, airport, and Porsche event center."},
            {"name": "Union City", "desc": "Quick delivery to Union City and Welcome All Park."},
            {"name": "Fairburn", "desc": "Premium sanitation for Fairburn and Renaissance."},
            {"name": "Palmetto", "desc": "Fast delivery to Palmetto and Coweta County."},
            {"name": "Red Oak", "desc": "Perfect for Red Oak and Fort Gillem."},
            {"name": "Chattahoochee Hills", "desc": "Quick delivery to Serenbe and Chattahoochee Hills."},
            {"name": "East Point", "desc": "Premium services for East Point and MARTA."},
            {"name": "Forest Park", "desc": "Fast delivery to Forest Park and Lake Spivey."},
            {"name": "Jonesboro", "desc": "Perfect for Jonesboro and St. Francis area."},
            {"name": "Riverdale", "desc": "Quick delivery to Riverdale and Mount Zion."},
        ]
    },
    "wichita-ks": {
        "name": "Wichita",
        "state": "KS",
        "county": "Sedgwick County",
        "areas": [
            {"name": "Downtown Wichita", "desc": "Perfect for Old Town and Century II."},
            {"name": "Old Town", "desc": "Quick delivery to Old Town and Commerce Street."},
            {"name": "Delano", "desc": "Premium sanitation for Delano neighborhood."},
            {"name": "Riverside", "desc": "Fast delivery to Riverside and Arkansas River."},
            {"name": "North Riverside", "desc": "Perfect for North Riverside and Scribner."},
            {"name": "South Riverside", "desc": "Quick delivery to South Riverside and Cowtown."},
            {"name": "Matlock", "desc": "Premium services for Matlock and Lincoln Park."},
            {"name": "County Line", "desc": "Fast delivery to County Line and Goddard."},
            {"name": "Cowtown", "desc": "Perfect for Cowtown and Sedgwick County Zoo."},
            {"name": "Sunset", "desc": "Quick delivery to Sunset and Longview."},
        ]
    },
    "murfreesboro-tn": {
        "name": "Murfreesboro",
        "state": "TN",
        "county": "Rutherford County",
        "areas": [
            {"name": "Downtown Murfreesboro", "desc": "Perfect for Historic Square and MTSU campus."},
            {"name": "MTSU", "desc": "Quick delivery to Middle Tennessee State University."},
            {"name": "The Blvd", "desc": "Premium sanitation for The Boulevard and area."},
            {"name": "Barfield", "desc": "Fast delivery to Barfield Park and Veterans Park."},
            {"name": "North Murfreesboro", "desc": "Perfect for North Murfreesboro and Airport."},
            {"name": "South Murfreesboro", "desc": "Quick delivery to South Murfreesboro."},
            {"name": "Smyrna", "desc": "Premium services for Smyrna and La Vergne."},
            {"name": "La Vergne", "desc": "Fast delivery to La Vergne and Percy Priest."},
            {"name": "Walter Hill", "desc": "Perfect for Walter Hill and Stones River."},
            {"name": "Lascassas", "desc": "Quick delivery to Lascassas and Union Hall."},
        ]
    },
    "nashville-tn": {
        "name": "Nashville",
        "state": "TN",
        "county": "Davidson County",
        "areas": [
            {"name": "Downtown Nashville", "desc": "Perfect for Broadway and Bridgestone Arena."},
            {"name": "Germantown", "desc": "Quick delivery to Germantown and Bicentennial Mall."},
            {"name": "East Nashville", "desc": "Premium sanitation for East Nashville arts district."},
            {"name": "The Gulch", "desc": "Fast delivery to The Gulch and Music Row."},
            {"name": "12 South", "desc": "Perfect for 12 South and Sevier Park."},
            {"name": "Bellevue", "desc": "Quick delivery to Bellevue and Harpeth Valley."},
            {"name": "Antioch", "desc": "Premium services for Antioch and Cane Ridge."},
            {"name": "Madison", "desc": "Fast delivery to Madison and Goodlettsville."},
            {"name": "Hermitage", "desc": "Perfect for Hermitage and Donelson."},
            {"name": "Brentwood", "desc": "Quick delivery to Brentwood and Franklin."},
        ]
    },
}

def fix_city_areas(html, city_data):
    city_name = city_data["name"]
    state = city_data["state"]
    county = city_data["county"]
    areas = city_data["areas"]
    
    html = re.sub(
        r'(<section id="areas"[^>]*>.*?<h2[^>]*>)[^<]*Proudly Serving[^<]*',
        rf'\1Proudly Serving {city_name} and All of {county}',
        html,
        flags=re.DOTALL
    )
    
    html = re.sub(
        r'from the bustling streets of Downtown[^.]*',
        f'the thriving neighborhoods of {city_name} and the surrounding communities',
        html
    )
    
    areas_pattern = re.compile(
        r'<div class="grid sm:grid-cols-2 gap-4 mt-4">(.*?)</div>\s*(?=<h4|</section)',
        re.DOTALL
    )
    
    areas_html = ""
    for i, area in enumerate(areas):
        areas_html += f'''
                        <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
                            <h5 class="font-semibold text-gray-800 mb-1">{area["name"]}</h5>
                            <p class="text-sm text-gray-600">{area["desc"]}</p>
                        </div>'''
    
    areas_match = areas_pattern.search(html)
    if areas_match:
        html = html_pattern.sub(areas_pattern, f'<div class="grid sm:grid-cols-2 gap-4 mt-4">{areas_html}</div>', html)
    
    html = re.sub(
        r'<h4 class="font-bold text-brand-800 mb-3">Neighborhoods We Serve[^<]*',
        f'<h4 class="font-bold text-brand-800 mb-3">Neighborhoods We Serve in {city_name}:',
        html
    )
    
    return html

def main():
    fixed = 0
    for city_slug, city_data in CITY_DATA.items():
        html_file = Path(f"porta-potty-rental-{city_slug}/index.html")
        if not html_file.exists():
            print(f"Missing: {city_slug}")
            continue
        
        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        
        new_html = fix_city_areas(html, city_data)
        
        if new_html != html:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"Fixed: {city_slug}")
            fixed += 1
        else:
            print(f"No change: {city_slug}")
    
    print(f"\nTotal fixed: {fixed}")

if __name__ == "__main__":
    main()
