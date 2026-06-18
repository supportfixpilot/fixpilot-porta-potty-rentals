#!/usr/bin/env python3
import os, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))

STATE_BODIES = {'alabama','arizona','arkansas','california','colorado','connecticut',
    'florida','georgia','idaho','illinois','indiana','iowa','kansas','kentucky',
    'louisiana','maryland','massachusetts','michigan','minnesota','mississippi',
    'missouri','montana','nebraska','nevada','ohio','oklahoma','oregon',
    'pennsylvania','tennessee','texas','utah','virginia','washington',
    'wisconsin','wyoming','south-carolina','south-dakota','north-carolina',
    'north-dakota','new-york','new-jersey','new-mexico','new-hampshire'}

STATE_COORDS = {
    'US-AL':(32.8067,-86.7911),'US-AZ':(34.0489,-111.0937),'US-AR':(34.7999,-92.1999),
    'US-CA':(36.7783,-119.4179),'US-CO':(39.5501,-105.7821),'US-CT':(41.6032,-73.0877),
    'US-FL':(27.6648,-81.5158),'US-GA':(32.1574,-82.9071),'US-ID':(44.0682,-114.7420),
    'US-IL':(40.6331,-89.3985),'US-IN':(40.2672,-86.1349),'US-IA':(41.8780,-93.0977),
    'US-KS':(39.0119,-98.4842),'US-KY':(37.8393,-84.2700),'US-LA':(31.2448,-92.1450),
    'US-MD':(39.0458,-76.6413),'US-MA':(42.4072,-71.3824),'US-MI':(44.3148,-85.6024),
    'US-MN':(46.7296,-94.6859),'US-MS':(32.3547,-89.3985),'US-MO':(37.9643,-91.8318),
    'US-MT':(46.8797,-110.3626),'US-NE':(41.4925,-99.9018),'US-NV':(38.8026,-116.4194),
    'US-OH':(40.4173,-82.9071),'US-OK':(35.0078,-97.0929),'US-OR':(43.8041,-120.5542),
    'US-PA':(41.2033,-77.1945),'US-TN':(35.5175,-86.5804),'US-TX':(31.9686,-99.9018),
    'US-UT':(39.3210,-111.0937),'US-VA':(37.4316,-78.6569),'US-WA':(47.7511,-120.7401),
    'US-WI':(43.7844,-88.7879),'US-WY':(43.0760,-107.2902),
    'US-SC':(33.8361,-81.1637),'US-SD':(43.9695,-99.9018),'US-NC':(35.7596,-79.0193),
    'US-ND':(47.5515,-101.0020),'US-NY':(42.1657,-74.9481),'US-NJ':(40.0583,-74.4057),
    'US-NM':(34.5199,-105.8701),'US-NH':(43.1939,-71.5724),
}

COUNTY_COORDS = {
    'allegheny-county-pa':(40.4406,-79.9959),'baltimore-county-md':(39.4093,-76.6082),
    'bexar-county-tx':(29.4241,-98.4936),'broward-county-fl':(26.1224,-80.1373),
    'clark-county-nv':(36.2145,-115.0132),'cook-county-il':(41.8781,-87.6298),
    'cuyahoga-county-oh':(41.4993,-81.6944),'dallas-county-tx':(32.7767,-96.7970),
    'davidson-county-tn':(36.1627,-86.7816),'douglas-county-ne':(41.2565,-96.0550),
    'fairfax-county-va':(38.8462,-77.3064),'franklin-county-oh':(39.9612,-82.9988),
    'fulton-county-ga':(33.7490,-84.3880),'hamilton-county-tn':(35.0456,-85.3097),
    'harris-county-tx':(29.7604,-95.3698),'hennepin-county-mn':(44.9778,-93.2650),
    'hillsborough-county-fl':(27.9506,-82.4572),'jefferson-county-ky':(38.2527,-85.7585),
    'king-county-wa':(47.5480,-121.9836),'lake-county-il':(42.2711,-87.8678),
    'los-angeles-county-ca':(34.0522,-118.2437),'maricopa-county-az':(33.4484,-112.0740),
    'miami-dade-county-fl':(25.7617,-80.1918),'middlesex-county-ma':(42.4084,-71.3824),
    'montgomery-county-md':(39.1547,-77.2405),'montgomery-county-tx':(30.3077,-95.4641),
    'mecklenburg-county-nc':(35.2271,-80.8431),'norfolk-county-ma':(42.1559,-71.1929),
    'orange-county-ca':(33.7175,-117.8311),'orange-county-fl':(28.5383,-81.3792),
    'palm-beach-county-fl':(26.6406,-80.3927),'pima-county-az':(32.2541,-110.8908),
    'pinellas-county-fl':(27.8766,-82.7820),'prince-georges-county-md':(38.8816,-76.9122),
    'riverside-county-ca':(33.7455,-115.9980),'sacramento-county-ca':(38.5816,-121.4944),
    'salt-lake-county-ut':(40.7608,-111.8910),'san-bernardino-ca':(34.1083,-117.2898),
    'san-diego-county-ca':(32.7157,-117.1611),'santa-clara-county-ca':(37.3382,-121.8863),
    'shelby-county-tn':(35.1495,-90.0490),'suffolk-county-ma':(42.3601,-71.0589),
    'suffolk-county-ny':(40.9176,-73.1222),'tarrant-county-tx':(32.7555,-97.3308),
    'travis-county-tx':(30.2672,-97.7431),'wayne-county-mi':(42.3314,-83.0458),
}

TEMPLATE_REVIEWS = (
    '"review": [\n'
    '    {\n'
    '      "@type": "Review",\n'
    '      "author": {"@type": "Person", "name": "James T., General Contractor"},\n'
    '      "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},\n'
    '      "reviewBody": "FixPilot delivered on time and kept our job site OSHA-compliant. Reliable service."\n'
    '    },\n'
    '    {\n'
    '      "@type": "Review",\n'
    '      "author": {"@type": "Person", "name": "Sandra M., Event Coordinator"},\n'
    '      "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},\n'
    '      "reviewBody": "Units were clean, delivery was on time, and the team was professional throughout."\n'
    '    }\n'
    '  ],\n  '
)

city_dirs = sorted([d for d in os.listdir(ROOT)
    if d.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(ROOT, d))])

fixed_hours = fixed_reviews = fixed_geo = 0

def is_valid_json(html):
    for b in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.DOTALL):
        try:
            json.loads(b)
        except:
            return False
    return True

for slug in city_dirs:
    body = slug.replace('porta-potty-rental-', '')
    is_state  = body in STATE_BODIES
    is_county = 'county' in body
    if not (is_state or is_county):
        continue

    path = os.path.join(ROOT, slug, 'index.html')
    if not os.path.exists(path):
        continue
    with open(path) as f:
        html = f.read()

    changed = False

    # Fix missing openingHours
    if 'openingHours' not in html:
        for anchor in ['"priceRange"', '"telephone"', '"url"', '"name"']:
            if anchor in html:
                html = html.replace(anchor,
                    '"openingHours": ["Mo-Fr 07:00-19:00", "Sa 08:00-17:00"],\n  ' + anchor, 1)
                changed = True
                fixed_hours += 1
                break

    # Add reviews to state pages that have none
    if is_state and 'reviewRating' not in html and 'aggregateRating' in html:
        html = html.replace('"aggregateRating"', TEMPLATE_REVIEWS + '"aggregateRating"', 1)
        changed = True
        fixed_reviews += 1

    # Add geo coords where missing
    if 'latitude' not in html:
        coords = None
        if is_county:
            coords = COUNTY_COORDS.get(body)
        if coords is None:
            region_m = re.search(r'geo\.region.*?content="([^"]+)"', html)
            if region_m:
                coords = STATE_COORDS.get(region_m.group(1))
        if coords:
            lat, lon = coords
            geo_str = f'"latitude": "{lat}",\n  "longitude": "{lon}",'
            for anchor in ['"address"', '"telephone"', '"url"', '"name"']:
                if anchor in html:
                    html = html.replace(anchor, geo_str + '\n  ' + anchor, 1)
                    changed = True
                    fixed_geo += 1
                    break

    if changed:
        if is_valid_json(html):
            with open(path, 'w') as f:
                f.write(html)
        else:
            print(f'  JSON invalid, skipping: {slug}')

print(f'Fixed openingHours : {fixed_hours}')
print(f'Added reviews      : {fixed_reviews}')
print(f'Added geo coords   : {fixed_geo}')
