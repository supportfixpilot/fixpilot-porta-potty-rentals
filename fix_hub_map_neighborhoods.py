#!/usr/bin/env python3
"""
fix_hub_map_neighborhoods.py
- Adds a Google Maps iframe section before <footer> on state/county hub pages
- Adds containsPlace Neighborhood entries to the first schema block
"""
import os, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))

# State: (map query, zoom, [city labels for schema])
STATE_DATA = {
    'alabama':        ('Alabama',           6,  ['Birmingham','Montgomery','Huntsville','Mobile','Tuscaloosa']),
    'arizona':        ('Arizona',           6,  ['Phoenix','Tucson','Scottsdale','Mesa','Chandler']),
    'arkansas':       ('Arkansas',          6,  ['Little Rock','Fayetteville','Fort Smith','Springdale','Jonesboro']),
    'california':     ('California',        5,  ['Los Angeles','San Diego','San Jose','San Francisco','Fresno']),
    'colorado':       ('Colorado',          6,  ['Denver','Colorado Springs','Aurora','Fort Collins','Boulder']),
    'connecticut':    ('Connecticut',       7,  ['Bridgeport','New Haven','Hartford','Stamford','Waterbury']),
    'florida':        ('Florida',           6,  ['Jacksonville','Miami','Tampa','Orlando','St. Petersburg']),
    'georgia':        ('Georgia',           6,  ['Atlanta','Augusta','Columbus','Macon','Savannah']),
    'idaho':          ('Idaho',             6,  ['Boise','Meridian','Nampa','Idaho Falls','Pocatello']),
    'illinois':       ('Illinois',          6,  ['Chicago','Aurora','Joliet','Naperville','Rockford']),
    'indiana':        ('Indiana',           6,  ['Indianapolis','Fort Wayne','Evansville','South Bend','Carmel']),
    'iowa':           ('Iowa',              6,  ['Des Moines','Cedar Rapids','Davenport','Sioux City','Iowa City']),
    'kansas':         ('Kansas',            6,  ['Wichita','Overland Park','Kansas City','Topeka','Olathe']),
    'kentucky':       ('Kentucky',          6,  ['Louisville','Lexington','Bowling Green','Owensboro','Covington']),
    'louisiana':      ('Louisiana',         6,  ['New Orleans','Baton Rouge','Shreveport','Metairie','Lafayette']),
    'maryland':       ('Maryland',          7,  ['Baltimore','Columbia','Germantown','Silver Spring','Waldorf']),
    'massachusetts':  ('Massachusetts',     7,  ['Boston','Worcester','Springfield','Cambridge','Lowell']),
    'michigan':       ('Michigan',          6,  ['Detroit','Grand Rapids','Warren','Sterling Heights','Ann Arbor']),
    'minnesota':      ('Minnesota',         6,  ['Minneapolis','Saint Paul','Rochester','Duluth','Bloomington']),
    'mississippi':    ('Mississippi',       6,  ['Jackson','Gulfport','Southaven','Hattiesburg','Biloxi']),
    'missouri':       ('Missouri',          6,  ['Kansas City','St. Louis','Springfield','Columbia','Independence']),
    'montana':        ('Montana',           6,  ['Billings','Missoula','Great Falls','Bozeman','Butte']),
    'nebraska':       ('Nebraska',          6,  ['Omaha','Lincoln','Bellevue','Grand Island','Kearney']),
    'nevada':         ('Nevada',            6,  ['Las Vegas','Henderson','Reno','North Las Vegas','Sparks']),
    'ohio':           ('Ohio',              6,  ['Columbus','Cleveland','Cincinnati','Toledo','Akron']),
    'oklahoma':       ('Oklahoma',          6,  ['Oklahoma City','Tulsa','Norman','Broken Arrow','Edmond']),
    'oregon':         ('Oregon',            6,  ['Portland','Salem','Eugene','Gresham','Hillsboro']),
    'pennsylvania':   ('Pennsylvania',      6,  ['Philadelphia','Pittsburgh','Allentown','Erie','Reading']),
    'tennessee':      ('Tennessee',         6,  ['Nashville','Memphis','Knoxville','Chattanooga','Clarksville']),
    'texas':          ('Texas',             5,  ['Houston','San Antonio','Dallas','Austin','Fort Worth']),
    'utah':           ('Utah',              6,  ['Salt Lake City','West Valley City','Provo','West Jordan','Orem']),
    'virginia':       ('Virginia',          6,  ['Virginia Beach','Norfolk','Chesapeake','Richmond','Newport News']),
    'washington':     ('Washington+State',  6,  ['Seattle','Spokane','Tacoma','Vancouver','Bellevue']),
    'wisconsin':      ('Wisconsin',         6,  ['Milwaukee','Madison','Green Bay','Kenosha','Racine']),
    'wyoming':        ('Wyoming',           6,  ['Cheyenne','Casper','Laramie','Gillette','Rock Springs']),
    'south-carolina': ('South+Carolina',    6,  ['Columbia','Charleston','North Charleston','Mount Pleasant','Rock Hill']),
    'south-dakota':   ('South+Dakota',      6,  ['Sioux Falls','Rapid City','Aberdeen','Brookings','Watertown']),
    'north-carolina': ('North+Carolina',    6,  ['Charlotte','Raleigh','Greensboro','Durham','Winston-Salem']),
    'north-dakota':   ('North+Dakota',      6,  ['Fargo','Bismarck','Grand Forks','Minot','West Fargo']),
    'new-york':       ('New+York+State',    6,  ['New York City','Buffalo','Rochester','Yonkers','Syracuse']),
    'new-jersey':     ('New+Jersey',        7,  ['Newark','Jersey City','Paterson','Elizabeth','Edison']),
    'new-mexico':     ('New+Mexico',        6,  ['Albuquerque','Las Cruces','Rio Rancho','Santa Fe','Roswell']),
    'new-hampshire':  ('New+Hampshire',     7,  ['Manchester','Nashua','Concord','Derry','Dover']),
}

# County: (map query, zoom, [neighborhood labels])
COUNTY_DATA = {
    'allegheny-county-pa':      ('Allegheny+County+PA',      10, ['Pittsburgh','Mt. Lebanon','Bethel Park','McKeesport','Monroeville']),
    'baltimore-county-md':      ('Baltimore+County+MD',       10, ['Towson','Catonsville','Dundalk','Essex','Pikesville']),
    'bexar-county-tx':          ('Bexar+County+TX',           10, ['San Antonio','Converse','Universal City','Schertz','Live Oak']),
    'broward-county-fl':        ('Broward+County+FL',         10, ['Fort Lauderdale','Hollywood','Pembroke Pines','Miramar','Coral Springs']),
    'clark-county-nv':          ('Clark+County+NV',           10, ['Las Vegas','Henderson','North Las Vegas','Enterprise','Sunrise Manor']),
    'cook-county-il':           ('Cook+County+IL',            10, ['Chicago','Evanston','Skokie','Oak Park','Cicero']),
    'cuyahoga-county-oh':       ('Cuyahoga+County+OH',        10, ['Cleveland','Parma','Lakewood','Euclid','Strongsville']),
    'dallas-county-tx':         ('Dallas+County+TX',          10, ['Dallas','Irving','Garland','Grand Prairie','Mesquite']),
    'davidson-county-tn':       ('Davidson+County+TN',        10, ['Nashville','Antioch','Brentwood','Hermitage','Madison']),
    'douglas-county-ne':        ('Douglas+County+NE',         11, ['Omaha','Bellevue','Ralston','Papillion','La Vista']),
    'fairfax-county-va':        ('Fairfax+County+VA',         10, ['Fairfax','Reston','Herndon','McLean','Springfield']),
    'franklin-county-oh':       ('Franklin+County+OH',        10, ['Columbus','Dublin','Westerville','Gahanna','Grove City']),
    'fulton-county-ga':         ('Fulton+County+GA',          10, ['Atlanta','Sandy Springs','Alpharetta','Roswell','Johns Creek']),
    'hamilton-county-tn':       ('Hamilton+County+TN',        10, ['Chattanooga','East Ridge','Red Bank','Soddy-Daisy','Collegedale']),
    'harris-county-tx':         ('Harris+County+TX',           9, ['Houston','Pasadena','Baytown','Sugar Land','Pearland']),
    'hennepin-county-mn':       ('Hennepin+County+MN',        10, ['Minneapolis','Bloomington','Plymouth','Brooklyn Park','Maple Grove']),
    'hillsborough-county-fl':   ('Hillsborough+County+FL',    10, ['Tampa','Brandon','Riverview','Clearwater','Plant City']),
    'jefferson-county-ky':      ('Jefferson+County+KY',       10, ['Louisville','Jeffersontown','St. Matthews','Shively','Valley Station']),
    'king-county-wa':           ('King+County+WA',            10, ['Seattle','Bellevue','Kent','Renton','Federal Way']),
    'knox-county-tn':           ('Knox+County+TN',            10, ['Knoxville','Farragut','Powell','Halls','Fountain City']),
    'lake-county-il':           ('Lake+County+IL',            10, ['Waukegan','North Chicago','Round Lake','Gurnee','Libertyville']),
    'los-angeles-county-ca':    ('Los+Angeles+County+CA',      9, ['Los Angeles','Long Beach','Glendale','Santa Clarita','Pomona']),
    'maricopa-county-az':       ('Maricopa+County+AZ',         9, ['Phoenix','Scottsdale','Mesa','Tempe','Chandler']),
    'marion-county-in':         ('Marion+County+IN',          10, ['Indianapolis','Lawrence','Beech Grove','Speedway','Southport']),
    'mecklenburg-county-nc':    ('Mecklenburg+County+NC',     10, ['Charlotte','Matthews','Mint Hill','Huntersville','Pineville']),
    'miami-dade-county-fl':     ('Miami+Dade+County+FL',       9, ['Miami','Hialeah','Miami Gardens','Coral Gables','Homestead']),
    'middlesex-county-ma':      ('Middlesex+County+MA',       10, ['Lowell','Cambridge','Somerville','Newton','Waltham']),
    'montgomery-county-md':     ('Montgomery+County+MD',      10, ['Rockville','Silver Spring','Bethesda','Gaithersburg','Germantown']),
    'montgomery-county-tx':     ('Montgomery+County+TX',      10, ['The Woodlands','Conroe','Humble','Kingwood','Spring']),
    'norfolk-county-ma':        ('Norfolk+County+MA',         10, ['Quincy','Braintree','Dedham','Weymouth','Milton']),
    'orange-county-ca':         ('Orange+County+CA',           9, ['Anaheim','Santa Ana','Irvine','Huntington Beach','Garden Grove']),
    'orange-county-fl':         ('Orange+County+FL',          10, ['Orlando','Apopka','Ocoee','Winter Park','Maitland']),
    'palm-beach-county-fl':     ('Palm+Beach+County+FL',      10, ['West Palm Beach','Boca Raton','Delray Beach','Boynton Beach','Lake Worth']),
    'pima-county-az':           ('Pima+County+AZ',            10, ['Tucson','Marana','Oro Valley','Sahuarita','South Tucson']),
    'pinellas-county-fl':       ('Pinellas+County+FL',        10, ['St. Petersburg','Clearwater','Largo','Dunedin','Tarpon Springs']),
    'prince-georges-county-md': ('Prince+Georges+County+MD',  10, ['Bowie','Laurel','College Park','Greenbelt','Hyattsville']),
    'riverside-county-ca':      ('Riverside+County+CA',        9, ['Riverside','Moreno Valley','Corona','Temecula','Murrieta']),
    'sacramento-county-ca':     ('Sacramento+County+CA',      10, ['Sacramento','Elk Grove','Citrus Heights','Roseville','Folsom']),
    'salt-lake-county-ut':      ('Salt+Lake+County+UT',       10, ['Salt Lake City','West Valley City','Sandy','Taylorsville','Murray']),
    'san-bernardino-ca':        ('San+Bernardino+CA',         10, ['San Bernardino','Fontana','Rancho Cucamonga','Ontario','Victorville']),
    'san-diego-county-ca':      ('San+Diego+County+CA',        9, ['San Diego','Chula Vista','El Cajon','Oceanside','Escondido']),
    'santa-clara-county-ca':    ('Santa+Clara+County+CA',     10, ['San Jose','Sunnyvale','Santa Clara','Mountain View','Palo Alto']),
    'shelby-county-tn':         ('Shelby+County+TN',          10, ['Memphis','Germantown','Bartlett','Collierville','Arlington']),
    'suffolk-county-ma':        ('Suffolk+County+MA',         11, ['Boston','Revere','Chelsea','Winthrop','Hyde Park']),
    'suffolk-county-ny':        ('Suffolk+County+NY',         10, ['Huntington','Babylon','Islip','Smithtown','Brookhaven']),
    'tarrant-county-tx':        ('Tarrant+County+TX',          9, ['Fort Worth','Arlington','Grand Prairie','Mansfield','North Richland Hills']),
    'travis-county-tx':         ('Travis+County+TX',          10, ['Austin','Round Rock','Cedar Park','Pflugerville','Georgetown']),
    'wayne-county-mi':          ('Wayne+County+MI',           10, ['Detroit','Dearborn','Livonia','Westland','Sterling Heights']),
}

def make_map_section(query, zoom):
    return f'''
<!-- Service area map -->
<section class="py-10 bg-gray-50">
  <div class="container mx-auto px-4 max-w-5xl">
    <h2 class="text-2xl font-black text-brand-900 mb-4 text-center">Service Area Map</h2>
    <div class="rounded-xl overflow-hidden shadow-md" style="height:320px">
      <iframe
        width="100%" height="100%" frameborder="0" style="border:0"
        src="https://maps.google.com/maps?q={query}&t=&z={zoom}&ie=UTF8&iwloc=&output=embed"
        loading="lazy" allowfullscreen
        title="FixPilot Porta Potty Rental Service Area">
      </iframe>
    </div>
  </div>
</section>'''

def make_neighborhood_schema(places):
    entries = ',\n        '.join(
        f'{{"@type": "Neighborhood", "name": "{p}"}}' for p in places
    )
    return f'"containsPlace": [\n        {entries}\n      ],'

def is_valid(html):
    for b in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.DOTALL):
        try: json.loads(b)
        except: return False
    return True

city_dirs = sorted([d for d in os.listdir(ROOT)
    if d.startswith('porta-potty-rental-') and os.path.isdir(os.path.join(ROOT, d))])

fixed_map = fixed_nb = 0

for slug in city_dirs:
    body = slug.replace('porta-potty-rental-', '')
    data = STATE_DATA.get(body) or COUNTY_DATA.get(body)
    if not data:
        continue

    path = os.path.join(ROOT, slug, 'index.html')
    if not os.path.exists(path): continue
    with open(path) as f: html = f.read()

    query, zoom, places = data
    changed = False

    # 1. Add map embed before <footer>
    if 'maps.google.com/maps' not in html or 'output=embed' not in html:
        map_html = make_map_section(query, zoom)
        if '<footer' in html:
            html = html.replace('<footer', map_html + '\n<footer', 1)
        else:
            html = html + map_html
        fixed_map += 1
        changed = True

    # 2. Add containsPlace neighborhoods to first schema block
    if '"Neighborhood"' not in html and '"containsPlace"' not in html:
        nb_schema = make_neighborhood_schema(places)
        # Inject after "geo" block or after "latitude" field or after "openingHours"
        for anchor in ['"openingHours"', '"latitude"', '"priceRange"', '"telephone"', '"url"']:
            if anchor in html:
                # Find the line end of this anchor's value and inject after
                pat = re.compile(re.escape(anchor) + r'[^\n]+\n')
                m = pat.search(html)
                if m:
                    html = html[:m.end()] + '      ' + nb_schema + '\n' + html[m.end():]
                    fixed_nb += 1
                    changed = True
                    break

    if changed:
        if is_valid(html):
            with open(path, 'w') as f: f.write(html)
        else:
            print(f'  JSON invalid, skipping: {slug}')

print(f'Added map embeds     : {fixed_map}')
print(f'Added neighborhoods  : {fixed_nb}')
