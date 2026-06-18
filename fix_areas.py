#!/usr/bin/env python3
"""Fix template leftover areas in city pages."""

import re
from pathlib import Path

CITY_AREAS = {
    "houston-tx": ["Downtown", "Galleria", "Medical Center", "The Heights", "Midtown", "Montrose", "River Oaks", "Sugar Land", "Pearland", "Katy"],
    "phoenix-az": ["Scottsdale", "Mesa", "Tempe", "Gilbert", "Chandler", "Glendale", "Peoria", "Surprise", "Arcadia", "Desert Ridge"],
    "charlotte-nc": ["South End", "Uptown", "NoDa", "Plaza Midwood", "Myers Park", "Dilworth", "Ballantyne", "University City", "Lake Norman", "Fort Mill"],
    "fort-worth-tx": ["Downtown", "Stockyards", "Magnolia", "TCU", "Sundance", "Riverside", "North Fort Worth", "South Fort Worth", "Benbrook", "Haltom City"],
    "the-woodlands-tx": ["Town Center", "Grogan's Mill", "Panther Creek", "Sterling Ridge", "Cochran's Crossing", "Indian Springs", "Alden Bridge", "Creekside", "Spring", "Conroe"],
    "athens-ga": ["Downtown", "Normaltown", "Five Points", "Bishop Park", "Georgia Square", "Prince Avenue", "Alps Road", "East Athens", "Oconee Hills", "Barnett Shoals"],
    "augusta-ga": ["Downtown", "Summerville", "North Augusta", "Aiken", "West Augusta", "South Augusta", "Riverwood", "Belair", "Martinez", "Evans"],
    "baton-brouge-la": ["Downtown", "LSU", "Southdowns", "Highland Road", "Perkins", "Broadmoor", "Crestworth", "Sherwood Forest", "Bocage", "East Baton Rouge"],
    "boulder-co": ["Downtown", "Pearl Street", "University Hill", "Mapleton Hill", "Whittier", "Baseline", "North Boulder", "South Boulder", "Chautauqua", "Eldorado Springs"],
    "bowling-green-ky": ["Downtown", "Schmidt", "Cumberland Trace", "Rich Pond", "Plano", "Smiths Grove", "Woodburn", "Oakland", "Smiths", "Alvaton"],
    "brooklyn-park-mn": ["Downtown", "North", "South", "East", "West", "Edina", "Crystal", "Brooklyn Center", "Plymouth", "Champlin"],
    "centennial-co": [" DTC", "Independence", "Willow Creek", "Cherry Creek", "Parker", "Foxridge", "Highlands", "Silverbrook", "Louviers", "Cottonwood"],
    "highlands-ranch-co": ["North", "East", "South", "West", "Westridge", "Southglenn", "Cougar", "Eastridge", "Ranch", "Highlands"],
    "hoover-al": ["The Preserve", "Ross Bridge", "Greystone", "Riverchase", "Lake Cyrus", "Big Creek", "Deer Valley", "Carmel", "Inverness", "Cahaba Heights"],
    "huntsville-al": ["Downtown", "Five Points", "Cliftons", "Medical District", "Campus", "Merrill", "Lake Forest", "Hampton Cove", "Meridianville", "Madison"],
    "independence-mo": ["Downtown", "Englewood", "River", "Little Blue", "Knoche", "Sugar Creek", "Lake Tapawingo", "Lee's Summit", "Blue Springs", "Kansas City"],
    "kansas-city-mo": ["Downtown", "Crossroads", "Westport", "Plaza", "Brookside", "Waldo", "Lee's Summit", "Independence", "North Kansas City", "Gladstone"],
    "lexington-ky": ["Downtown", "Chevy Chase", "Southland", "Hamburg", "Palgrove", "Beaumont", "Bryan Station", "Tates Creek", "Mount Tabor", "Gardens"],
    "macon-ga": ["Downtown", "Ingleside", "Villages at", "East Macon", "Warner Robins", "Milledgeville", "Bolingbroke", "Juliette", "Ocmulgee", "Talmage"],
    "mobile-al": ["Downtown", "Midtown", "Spring Hill", "West Mobile", "Semmes", "Theodore", "Prichard", "Chickasaw", "Tillmans", "Cottage Hill"],
    "myrtle-beach-sc": ["Downtown", "Myrtle Beach", "Ocean Forest", "Arcadian", "Briarcliffe", "North Myrtle", "Surfside", "Garden City", "Murrells Inlet", "Conway"],
    "plymouth-ma": ["Downtown", "Waterfront", "The Pinehills", "Plymouth Beach", "West Plymouth", "North Plymouth", "South Plymouth", "Manomet", "Sagamore Beach", "Bourne"],
    "savannah-ga": ["Downtown", "Historic District", "Savannah Victorian", "Starland", "Thomas Square", "Ardsley Park", "Wilmington Island", "Tybee Island", "Southside", "Pooler"],
    "south-fulton-ga": ["College Park", "Union City", "Fairburn", "Palmetto", "College Park", "Red Oak", "Chattahoochee Hills", "Atlanta", "East Point", "Forest Park"],
    "wichita-ks": ["Downtown", "Old Town", "Delano", "Riverside", "North Riverside", "South Riverside", "Matlock", "County Line", "Cowtown", "Sunset"],
}

def fix_areas(html, city, areas):
    if city not in CITY_AREAS:
        return html
    
    areas_str = '", "'.join(areas)
    areas_pattern = f'"{areas_str}"'
    
    atlanta_areas = ["Buckhead", "Peachtree Corners", "Alpharetta", "Smyrna", "Marietta", "Roswell", "Sandy Springs", "Decatur", "College Park", "East Point"]
    
    for area in atlanta_areas:
        html = re.sub(f'"{area}"', f'"AREA_PLACEHOLDER_{area}"', html)
    
    new_areas = '"' + '", "'.join(areas) + '"'
    html = re.sub(r'"AREA_PLACEHOLDER_[^"]+"', '', html)
    
    areas_match = re.search(r'"areas":\s*\[.*?\]', html, re.DOTALL)
    if areas_match:
        old_areas = areas_match.group(0)
        html = html.replace(old_areas, f'"areas": [{new_areas}]')
    
    return html

def main():
    fixed = 0
    for city, areas in CITY_AREAS.items():
        html_file = Path(f"porta-potty-rental-{city}/index.html")
        if not html_file.exists():
            print(f"Missing: {city}")
            continue
        
        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        
        new_html = fix_areas(html, city, areas)
        
        if new_html != html:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"Fixed: {city}")
            fixed += 1
        else:
            print(f"No change: {city}")
    
    print(f"\nTotal fixed: {fixed}")

if __name__ == "__main__":
    main()
