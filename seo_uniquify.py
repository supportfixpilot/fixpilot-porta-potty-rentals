#!/usr/bin/env python3
"""
seo_uniquify.py — Make every city page genuinely unique for Google indexing.

What this does:
  1. Assigns each city a profile (oilgas / events / coastal / college / tech / suburban / government)
  2. Replaces the FAQ section (schema JSON + HTML) with 12 city-specific questions
  3. Replaces the hero paragraph with a profile-matched unique variant
  4. Replaces the services-section intro with a profile-matched variant
  5. Replaces the "Your Experts" prose with a profile-matched variant
  6. Updates testimonials with city-specific names and quotes
  7. Fixes any wrong state references (e.g. Houston saying GA)

Run: python3 seo_uniquify.py
"""

import re, hashlib
from pathlib import Path

# ─── STATE LOOKUP ──────────────────────────────────────────────────────────
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

# State health-dept reference used in FAQ answers
STATE_HEALTH = {
    "AL":"Alabama Department of Public Health","AK":"Alaska DHSS","AZ":"ADHS",
    "AR":"Arkansas Department of Health","CA":"CDPH","CO":"CDPHE",
    "CT":"Connecticut DPH","DE":"Delaware DHSS","FL":"Florida DOH",
    "GA":"Georgia Department of Public Health","HI":"Hawaii DOH","ID":"Idaho DHW",
    "IL":"IDPH","IN":"Indiana DOH","IA":"Iowa DPH","KS":"KDHE","KY":"KCHFS",
    "LA":"Louisiana DOH","ME":"Maine DHHS","MD":"Maryland DOH",
    "MA":"Massachusetts DPH","MI":"MDHHS","MN":"MDH","MS":"Mississippi MSDH",
    "MO":"Missouri DHSS","MT":"Montana DPHHS","NE":"Nebraska DHHS",
    "NV":"Nevada Division of Public and Behavioral Health","NH":"NH DHHS",
    "NJ":"New Jersey DOH","NM":"NMDOH","NY":"New York DOH",
    "NC":"NC DHHS","ND":"North Dakota DHS","OH":"Ohio DOH","OK":"OSDH",
    "OR":"Oregon DHS","PA":"Pennsylvania DOH","RI":"Rhode Island DOH",
    "SC":"South Carolina DHEC","SD":"South Dakota DOH","TN":"Tennessee DOH",
    "TX":"Texas DSHS","UT":"Utah UDOH","VT":"Vermont DOH","VA":"Virginia DOH",
    "WA":"Washington DOH","WV":"West Virginia DHHR","WI":"Wisconsin DHS",
    "WY":"Wyoming DOH",
}

# ─── EXPLICIT CITY DATA ────────────────────────────────────────────────────
# profile: oilgas | events | coastal | college | tech | suburban | government
CITY_DB = {
  "abilene-tx":{"name":"Abilene","state":"TX","county":"Taylor County","zip":"79601","areas":["Lytle South","Dyess AFB","McMurry University","Downtown Abilene","Hendrick Medical","Buffalo Gap Road","Abilene State Park area"],"landmark1":"Dyess Air Force Base","landmark2":"Taylor County Expo Center","profile":"oilgas"},
  "akron-oh":{"name":"Akron","state":"OH","county":"Summit County","zip":"44308","areas":["Downtown Akron","Fairlawn","Cuyahoga Falls","Barberton","Green","Hudson","Stow"],"landmark1":"University of Akron","landmark2":"Canal Park Stadium","profile":"tech"},
  "albany-ny":{"name":"Albany","state":"NY","county":"Albany County","zip":"12207","areas":["Downtown Albany","Arbor Hill","Center Square","Pine Hills","Delmar","Colonie","Guilderland"],"landmark1":"New York State Capitol","landmark2":"Empire State Plaza","profile":"government"},
  "albuquerque-nm":{"name":"Albuquerque","state":"NM","county":"Bernalillo County","zip":"87102","areas":["Downtown Albuquerque","Nob Hill","Old Town","Northeast Heights","Rio Rancho","Corrales","Bosque Farms"],"landmark1":"Sandia Mountains","landmark2":"Kirtland Air Force Base","profile":"government"},
  "allen-tx":{"name":"Allen","state":"TX","county":"Collin County","zip":"75013","areas":["Allen Station","Twin Creeks","Watters Creek","Ridgeview","Exchange Pkwy corridor","Twin Creeks","Cottonwood Creek"],"landmark1":"Allen Event Center","landmark2":"Allen Premium Outlets","profile":"suburban"},
  "amarillo-tx":{"name":"Amarillo","state":"TX","county":"Potter County","zip":"79101","areas":["Downtown Amarillo","Medical Center","Airport area","Wolflin","Georgia Street","South Amarillo","Canyon"],"landmark1":"Pantex Plant","landmark2":"Palo Duro Canyon","profile":"oilgas"},
  "anaheim-ca":{"name":"Anaheim","state":"CA","county":"Orange County","zip":"92805","areas":["Anaheim Resort District","Platinum Triangle","Anaheim Hills","Canyon","Stadium District","Downtown Anaheim","The Colony"],"landmark1":"Disneyland Resort","landmark2":"Angel Stadium","profile":"events"},
  "anchorage-ak":{"name":"Anchorage","state":"AK","county":"Anchorage Municipality","zip":"99501","areas":["Downtown Anchorage","Midtown","Sand Lake","Hillside","Eagle River","Muldoon","South Anchorage"],"landmark1":"Ted Stevens Anchorage Airport","landmark2":"Chugach State Park","profile":"oilgas"},
  "ann-arbor-mi":{"name":"Ann Arbor","state":"MI","county":"Washtenaw County","zip":"48104","areas":["Downtown Ann Arbor","University of Michigan campus","Old West Side","Kerrytown","Burns Park","Ypsilanti","Saline"],"landmark1":"University of Michigan Stadium","landmark2":"Hill Auditorium","profile":"college"},
  "arlington-tx":{"name":"Arlington","state":"TX","county":"Tarrant County","zip":"76010","areas":["Downtown Arlington","UTA campus","Entertainment District","Pantego","Dalworthington Gardens","Mansfield","Grand Prairie"],"landmark1":"AT&T Stadium","landmark2":"Globe Life Park","profile":"events"},
  "arvada-co":{"name":"Arvada","state":"CO","county":"Jefferson County","zip":"80002","areas":["Olde Town Arvada","Ralston Creek","West 64th corridor","Lakecrest","Candelas","Standley Lake","Westminster"],"landmark1":"Olde Town Arvada","landmark2":"Standley Lake","profile":"suburban"},
  "athens-ga":{"name":"Athens","state":"GA","county":"Clarke County","zip":"30601","areas":["Downtown Athens","Five Points","Normaltown","East Athens","Boulevard District","West Athens","Winterville"],"landmark1":"Sanford Stadium","landmark2":"Georgia Theatre","profile":"college"},
  "atlanta-ga":{"name":"Atlanta","state":"GA","county":"Fulton County","zip":"30303","areas":["Downtown Atlanta","Buckhead","Midtown","Inman Park","Old Fourth Ward","Virginia-Highland","Decatur"],"landmark1":"Mercedes-Benz Stadium","landmark2":"Piedmont Park","profile":"events"},
  "auburn-ca":{"name":"Auburn","state":"CA","county":"Placer County","zip":"95603","areas":["Old Town Auburn","Auburn Lake Trails","Meadow Vista","Lincoln","Rocklin","Loomis","Penryn"],"landmark1":"Auburn State Recreation Area","landmark2":"Gold Country Fairgrounds","profile":"suburban"},
  "augusta-ga":{"name":"Augusta","state":"GA","county":"Richmond County","zip":"30901","areas":["Downtown Augusta","Summerville","North Augusta","Riverwatch Pkwy","Augusta National area","Evans","Grovetown"],"landmark1":"Augusta National Golf Club","landmark2":"James Brown Arena","profile":"events"},
  "aurora-co":{"name":"Aurora","state":"CO","county":"Arapahoe County","zip":"80012","areas":["Aurora City Center","Fitzsimons","Aurora Highlands","Southlands","E-470 corridor","Centennial","Parker Road"],"landmark1":"Anschutz Medical Campus","landmark2":"Aurora Reservoir","profile":"tech"},
  "austin-tx":{"name":"Austin","state":"TX","county":"Travis County","zip":"78701","areas":["Downtown Austin","South Congress","East Austin","Domain area","Mueller","Cedar Park","Round Rock"],"landmark1":"University of Texas at Austin","landmark2":"Zilker Park","profile":"tech"},
  "bakersfield-ca":{"name":"Bakersfield","state":"CA","county":"Kern County","zip":"93301","areas":["Downtown Bakersfield","Oleander","Old Stockdale","Rosedale","Oildale","East Bakersfield","Shafter"],"landmark1":"Dignity Health Amphitheater","landmark2":"Kern County Fairgrounds","profile":"oilgas"},
  "baltimore-md":{"name":"Baltimore","state":"MD","county":"Baltimore City","zip":"21202","areas":["Inner Harbor","Federal Hill","Fells Point","Canton","Hampden","Towson","Dundalk"],"landmark1":"Camden Yards","landmark2":"Ravens Stadium","profile":"events"},
  "baton-rouge-la":{"name":"Baton Rouge","state":"LA","county":"East Baton Rouge Parish","zip":"70801","areas":["Downtown Baton Rouge","LSU campus","Mid City","Southdowns","Broadmoor","Denham Springs","Zachary"],"landmark1":"Tiger Stadium at LSU","landmark2":"Louisiana State Capitol","profile":"college"},
  "beaumont-tx":{"name":"Beaumont","state":"TX","county":"Jefferson County","zip":"77701","areas":["Downtown Beaumont","Medical Center","Ford Park","China","Port Arthur","Orange","Lumberton"],"landmark1":"Ford Park Arena","landmark2":"Lamar University","profile":"oilgas"},
  "bellevue-wa":{"name":"Bellevue","state":"WA","county":"King County","zip":"98004","areas":["Downtown Bellevue","Crossroads","Factoria","Eastgate","Redmond","Kirkland","Issaquah"],"landmark1":"Bellevue Square","landmark2":"Mercer Island","profile":"tech"},
  "billings-mt":{"name":"Billings","state":"MT","county":"Yellowstone County","zip":"59101","areas":["Downtown Billings","Heights","Lockwood","Laurel","Billings West End","Billings Skyview","Huntley"],"landmark1":"MetraPark Arena","landmark2":"Billings Clinic","profile":"oilgas"},
  "biloxi-ms":{"name":"Biloxi","state":"MS","county":"Harrison County","zip":"39530","areas":["Biloxi Beach","Downtown Biloxi","Gulf Hills","Ocean Springs","D'Iberville","Gulfport","Long Beach"],"landmark1":"Biloxi Lighthouse","landmark2":"Beau Rivage Resort","profile":"coastal"},
  "birmingham-al":{"name":"Birmingham","state":"AL","county":"Jefferson County","zip":"35203","areas":["Downtown Birmingham","Homewood","Vestavia Hills","Mountain Brook","Hoover","Trussville","Bessemer"],"landmark1":"Vulcan Park","landmark2":"Legion Field","profile":"tech"},
  "bismarck-nd":{"name":"Bismarck","state":"ND","county":"Burleigh County","zip":"58501","areas":["Downtown Bismarck","North Bismarck","South Bismarck","Mandan","Lincoln","Washburn","Hazen"],"landmark1":"North Dakota State Capitol","landmark2":"Bismarck Civic Center","profile":"government"},
  "boise-id":{"name":"Boise","state":"ID","county":"Ada County","zip":"83702","areas":["Downtown Boise","North End","Bench","East End","Meridian","Eagle","Nampa"],"landmark1":"Boise State University","landmark2":"Hyde Park","profile":"tech"},
  "boston-ma":{"name":"Boston","state":"MA","county":"Suffolk County","zip":"02108","areas":["Downtown Boston","Seaport District","Back Bay","South End","Fenway","Cambridge","Somerville"],"landmark1":"Fenway Park","landmark2":"Boston Common","profile":"college"},
  "boulder-co":{"name":"Boulder","state":"CO","county":"Boulder County","zip":"80302","areas":["Downtown Boulder","Pearl Street","University Hill","East Boulder","Gunbarrel","Longmont","Lafayette"],"landmark1":"CU Boulder Folsom Field","landmark2":"Chautauqua Park","profile":"college"},
  "bowling-green-ky":{"name":"Bowling Green","state":"KY","county":"Warren County","zip":"42101","areas":["Downtown Bowling Green","WKU campus","Greenwood","Rich Pond","Alvaton","Smiths Grove","Cave City"],"landmark1":"National Corvette Museum","landmark2":"WKU Houchens-Smith Stadium","profile":"college"},
  "bozeman-mt":{"name":"Bozeman","state":"MT","county":"Gallatin County","zip":"59715","areas":["Downtown Bozeman","MSU campus","Bridger Mountains","Gallatin Gateway","Belgrade","Manhattan","Three Forks"],"landmark1":"Montana State University","landmark2":"Bridger Bowl Ski Area","profile":"college"},
  "bridgeport-ct":{"name":"Bridgeport","state":"CT","county":"Fairfield County","zip":"06604","areas":["Downtown Bridgeport","Black Rock","East Side","North End","Stratford","Trumbull","Fairfield"],"landmark1":"Total Mortgage Arena","landmark2":"Seaside Park","profile":"suburban"},
  "brooklyn-park-mn":{"name":"Brooklyn Park","state":"MN","county":"Hennepin County","zip":"55443","areas":["Central Brooklyn Park","Crest View","Edinburgh","Hennepin Technical College","North Brooklyn Park","Plymouth","Maple Grove"],"landmark1":"North Hennepin Community College","landmark2":"Edinburgh USA Golf Course","profile":"suburban"},
  "brownsville-tx":{"name":"Brownsville","state":"TX","county":"Cameron County","zip":"78520","areas":["Downtown Brownsville","SpaceX Boca Chica","Port of Brownsville","Rancho Viejo","Los Fresnos","Harlingen","San Benito"],"landmark1":"SpaceX Starbase","landmark2":"Gladys Porter Zoo","profile":"oilgas"},
  "buffalo-ny":{"name":"Buffalo","state":"NY","county":"Erie County","zip":"14202","areas":["Downtown Buffalo","Elmwood Village","Allentown","Black Rock","Cheektowaga","Tonawanda","Orchard Park"],"landmark1":"Highmark Stadium","landmark2":"KeyBank Center","profile":"events"},
  "cambridge-ma":{"name":"Cambridge","state":"MA","county":"Middlesex County","zip":"02139","areas":["Harvard Square","Central Square","Kendall Square","Inman Square","Porter Square","Somerville","Medford"],"landmark1":"Harvard University","landmark2":"MIT","profile":"college"},
  "cape-coral-fl":{"name":"Cape Coral","state":"FL","county":"Lee County","zip":"33904","areas":["Downtown Cape Coral","Pelican","Cape Harbour","SE Cape Coral","NW Cape Coral","North Fort Myers","Fort Myers"],"landmark1":"Cape Coral Yacht Club","landmark2":"Matlacha Island","profile":"coastal"},
  "carrollton-tx":{"name":"Carrollton","state":"TX","county":"Denton County","zip":"75006","areas":["Old Downtown Carrollton","Bent Tree","Trinity Mills","Hebron","Lewisville","Farmers Branch","Addison"],"landmark1":"A.W. Perry Homestead Museum","landmark2":"Carrollton Amphitheater","profile":"suburban"},
  "casper-wy":{"name":"Casper","state":"WY","county":"Natrona County","zip":"82601","areas":["Downtown Casper","East Casper","West Casper","Evansville","Mills","Bar Nunn","Glenrock"],"landmark1":"Casper Events Center","landmark2":"Casper Mountain","profile":"oilgas"},
  "centennial-co":{"name":"Centennial","state":"CO","county":"Arapahoe County","zip":"80016","areas":["Denver Tech Center","Willow Creek","Homestead","Cherry Creek State Park area","Parker","Highlands Ranch","Lone Tree"],"landmark1":"Denver Tech Center","landmark2":"Centennial Airport","profile":"tech"},
  "chandler-az":{"name":"Chandler","state":"AZ","county":"Maricopa County","zip":"85224","areas":["Downtown Chandler","Ocotillo","Dobson Ranch","Sun Lakes","Gilbert","Mesa","Tempe"],"landmark1":"Intel Chandler Campus","landmark2":"Chandler Fashion Center","profile":"tech"},
  "charleston-sc":{"name":"Charleston","state":"SC","county":"Charleston County","zip":"29403","areas":["Historic Downtown","The Peninsula","West Ashley","Mount Pleasant","James Island","North Charleston","Summerville"],"landmark1":"Arthur Ravenel Jr. Bridge","landmark2":"The Battery","profile":"coastal"},
  "charleston-wv":{"name":"Charleston","state":"WV","county":"Kanawha County","zip":"25301","areas":["Downtown Charleston","South Hills","Kanawha City","St. Albans","Cross Lanes","Dunbar","Teays Valley"],"landmark1":"West Virginia State Capitol","landmark2":"FirstEnergy Stadium","profile":"government"},
  "charlotte-nc":{"name":"Charlotte","state":"NC","county":"Mecklenburg County","zip":"28202","areas":["Uptown Charlotte","South End","NoDa","Myers Park","Ballantyne","Lake Norman","Fort Mill SC"],"landmark1":"Bank of America Stadium","landmark2":"NASCAR Hall of Fame","profile":"tech"},
  "chattanooga-tn":{"name":"Chattanooga","state":"TN","county":"Hamilton County","zip":"37402","areas":["Downtown Chattanooga","Northshore","East Ridge","Red Bank","Hixson","Lookout Mountain","Ringgold GA"],"landmark1":"Tennessee Aquarium","landmark2":"Lookout Mountain Battlefield","profile":"events"},
  "chesapeake-va":{"name":"Chesapeake","state":"VA","county":"Chesapeake City","zip":"23320","areas":["Greenbrier","Great Bridge","Indian River","Deep Creek","Hickory","Western Branch","Norfolk"],"landmark1":"Great Dismal Swamp","landmark2":"Naval Station Norfolk vicinity","profile":"government"},
  "cheyenne-wy":{"name":"Cheyenne","state":"WY","county":"Laramie County","zip":"82001","areas":["Downtown Cheyenne","Warren AFB","Laramie County Community College","South Cheyenne","Ridgeline","Pine Bluffs","Fort Collins CO"],"landmark1":"F.E. Warren Air Force Base","landmark2":"Cheyenne Frontier Days Arena","profile":"government"},
  "chicago-il":{"name":"Chicago","state":"IL","county":"Cook County","zip":"60601","areas":["The Loop","River North","Lincoln Park","Wicker Park","South Loop","Wrigleyville","Oak Park"],"landmark1":"Soldier Field","landmark2":"McCormick Place","profile":"events"},
  "chula-vista-ca":{"name":"Chula Vista","state":"CA","county":"San Diego County","zip":"91910","areas":["Downtown Chula Vista","Eastlake","Otay Ranch","Bayfront","National City","Bonita","El Cajon"],"landmark1":"Chula Vista Elite Athlete Training Center","landmark2":"Chula Vista Center","profile":"suburban"},
  "cincinnati-oh":{"name":"Cincinnati","state":"OH","county":"Hamilton County","zip":"45202","areas":["Downtown Cincinnati","Over-the-Rhine","Hyde Park","Mt. Lookout","Clifton","Blue Ash","Florence KY"],"landmark1":"Great American Ball Park","landmark2":"Paul Brown Stadium","profile":"events"},
  "clarksville-tn":{"name":"Clarksville","state":"TN","county":"Montgomery County","zip":"37040","areas":["Downtown Clarksville","Fort Campbell","Austin Peay campus","New Providence","Red River","Sango","Pleasant View"],"landmark1":"Fort Campbell Army Installation","landmark2":"Austin Peay State University","profile":"government"},
  "clearwater-fl":{"name":"Clearwater","state":"FL","county":"Pinellas County","zip":"33755","areas":["Clearwater Beach","Downtown Clearwater","Dunedin","Safety Harbor","Palm Harbor","Largo","St. Pete Beach"],"landmark1":"Clearwater Beach","landmark2":"Amalie Arena vicinity","profile":"coastal"},
  "cleveland-oh":{"name":"Cleveland","state":"OH","county":"Cuyahoga County","zip":"44113","areas":["Downtown Cleveland","Ohio City","Tremont","University Circle","Lakewood","Parma","Strongsville"],"landmark1":"FirstEnergy Stadium","landmark2":"Rock & Roll Hall of Fame","profile":"events"},
  "college-station-tx":{"name":"College Station","state":"TX","county":"Brazos County","zip":"77840","areas":["Texas A&M campus","Northgate","Kyle Field area","Bryan","Wellborn","Hearne","Navasota"],"landmark1":"Kyle Field at Texas A&M","landmark2":"Reed Arena","profile":"college"},
  "colorado-springs-co":{"name":"Colorado Springs","state":"CO","county":"El Paso County","zip":"80903","areas":["Downtown Colorado Springs","Broadmoor","Falcon","Briargate","Air Force Academy","Monument","Manitou Springs"],"landmark1":"USAF Academy","landmark2":"Garden of the Gods","profile":"government"},
  "columbia-mo":{"name":"Columbia","state":"MO","county":"Boone County","zip":"65201","areas":["Downtown Columbia","University of Missouri campus","East Campus","West Boulevard","Ashland","Centralia","Hallsville"],"landmark1":"Memorial Stadium at Mizzou","landmark2":"Stephens Lake Park","profile":"college"},
  "columbia-sc":{"name":"Columbia","state":"SC","county":"Richland County","zip":"29201","areas":["Downtown Columbia","Five Points","Vista","Northeast Columbia","Irmo","Lexington","Forest Acres"],"landmark1":"Williams-Brice Stadium","landmark2":"South Carolina State House","profile":"college"},
  "columbus-oh":{"name":"Columbus","state":"OH","county":"Franklin County","zip":"43215","areas":["Downtown Columbus","Short North","German Village","Dublin","Gahanna","Westerville","Grove City"],"landmark1":"Ohio Stadium","landmark2":"Nationwide Arena","profile":"tech"},
  "conroe-tx":{"name":"Conroe","state":"TX","county":"Montgomery County","zip":"77301","areas":["Downtown Conroe","The Woodlands","Woodforest","Willis","Splendora","Magnolia","Huntsville"],"landmark1":"Lake Conroe","landmark2":"Cynthia Woods Mitchell Pavilion","profile":"suburban"},
  "coral-springs-fl":{"name":"Coral Springs","state":"FL","county":"Broward County","zip":"33065","areas":["Downtown Coral Springs","Sawgrass","Meadows","Ramblewood","Boca Raton","Parkland","Coconut Creek"],"landmark1":"Coral Springs Center for the Arts","landmark2":"Sawgrass Mills","profile":"suburban"},
  "corpus-christi-tx":{"name":"Corpus Christi","state":"TX","county":"Nueces County","zip":"78401","areas":["Downtown Corpus Christi","Port Aransas","North Beach","Calallen","Portland","Ingleside","Robstown"],"landmark1":"Naval Air Station Corpus Christi","landmark2":"Texas State Aquarium","profile":"coastal"},
  "dallas-tx":{"name":"Dallas","state":"TX","county":"Dallas County","zip":"75201","areas":["Downtown Dallas","Uptown","Deep Ellum","Bishop Arts","Frisco","Plano","Irving"],"landmark1":"AT&T Stadium","landmark2":"American Airlines Center","profile":"tech"},
  "dayton-oh":{"name":"Dayton","state":"OH","county":"Montgomery County","zip":"45402","areas":["Downtown Dayton","Oregon District","Wright-Patterson AFB","Beavercreek","Kettering","Centerville","Huber Heights"],"landmark1":"Wright-Patterson Air Force Base","landmark2":"National Museum of the USAF","profile":"government"},
  "decatur-ga":{"name":"Decatur","state":"GA","county":"DeKalb County","zip":"30030","areas":["Downtown Decatur Square","Oakhurst","Emory Village","Kirkwood","Lake Claire","Avondale Estates","Druid Hills"],"landmark1":"Emory University","landmark2":"CDC Headquarters","profile":"college"},
  "denton-tx":{"name":"Denton","state":"TX","county":"Denton County","zip":"76201","areas":["Downtown Denton","UNT campus","TWU campus","Aubrey","Argyle","Flower Mound","Lewisville"],"landmark1":"UNT Mean Green Stadium","landmark2":"Denton County Fresh Market","profile":"college"},
  "denver-co":{"name":"Denver","state":"CO","county":"Denver County","zip":"80202","areas":["Downtown Denver","RiNo","Capitol Hill","Cherry Creek","LoDo","Stapleton","Aurora"],"landmark1":"Coors Field","landmark2":"Red Rocks Amphitheatre","profile":"tech"},
  "des-moines-ia":{"name":"Des Moines","state":"IA","county":"Polk County","zip":"50309","areas":["Downtown Des Moines","East Village","Gray's Lake","Beaverdale","West Des Moines","Urbandale","Ankeny"],"landmark1":"Iowa State Fairgrounds","landmark2":"Wells Fargo Arena","profile":"government"},
  "detroit-mi":{"name":"Detroit","state":"MI","county":"Wayne County","zip":"48226","areas":["Downtown Detroit","Corktown","Midtown","Eastern Market","Hamtramck","Dearborn","Warren"],"landmark1":"Ford Field","landmark2":"Little Caesars Arena","profile":"tech"},
  "dothan-al":{"name":"Dothan","state":"AL","county":"Houston County","zip":"36301","areas":["Downtown Dothan","Northside","Southside","Westgate","Wicksburg","Enterprise","Ozark"],"landmark1":"Wiregrass Commons Mall","landmark2":"Dothan Botanica","profile":"suburban"},
  "durham-nc":{"name":"Durham","state":"NC","county":"Durham County","zip":"27701","areas":["Downtown Durham","Duke University","Research Triangle Park","Southpoint","Chapel Hill","Cary","Morrisville"],"landmark1":"Duke University","landmark2":"Durham Bulls Athletic Park","profile":"tech"},
  "el-paso-tx":{"name":"El Paso","state":"TX","county":"El Paso County","zip":"79901","areas":["Downtown El Paso","UTEP campus","Fort Bliss","West El Paso","Northeast El Paso","Socorro","Horizon City"],"landmark1":"Fort Bliss Army Base","landmark2":"Sun Bowl Stadium","profile":"government"},
  "evansville-in":{"name":"Evansville","state":"IN","county":"Vanderburgh County","zip":"47708","areas":["Downtown Evansville","Haynie's Corner","West Side","East Side","Newburgh","Henderson KY","Mount Vernon"],"landmark1":"Ford Center","landmark2":"Mesker Park Zoo","profile":"suburban"},
  "fargo-nd":{"name":"Fargo","state":"ND","county":"Cass County","zip":"58102","areas":["Downtown Fargo","West Fargo","South Fargo","Moorhead MN","Dilworth","West Fargo Industrial","Casselton"],"landmark1":"NDSU campus","landmark2":"Scheels Arena","profile":"college"},
  "fayetteville-ar":{"name":"Fayetteville","state":"AR","county":"Washington County","zip":"72701","areas":["Downtown Fayetteville","University of Arkansas","Dickson Street","Bentonville","Rogers","Springdale","Siloam Springs"],"landmark1":"University of Arkansas Razorback Stadium","landmark2":"Walmart AMP Amphitheater","profile":"college"},
  "fort-collins-co":{"name":"Fort Collins","state":"CO","county":"Larimer County","zip":"80521","areas":["Downtown Fort Collins","Old Town","CSU campus","Midtown","Loveland","Windsor","Timnath"],"landmark1":"CSU Canvas Stadium","landmark2":"Horsetooth Reservoir","profile":"college"},
  "fort-lauderdale-fl":{"name":"Fort Lauderdale","state":"FL","county":"Broward County","zip":"33301","areas":["Las Olas","Flagler Village","Wilton Manors","Hollywood","Pompano Beach","Deerfield Beach","Davie"],"landmark1":"Hard Rock Stadium vicinity","landmark2":"Fort Lauderdale Beach","profile":"coastal"},
  "fort-wayne-in":{"name":"Fort Wayne","state":"IN","county":"Allen County","zip":"46802","areas":["Downtown Fort Wayne","Aboite","Waynedale","Georgetown","New Haven","Grabill","Leo-Cedarville"],"landmark1":"Parkview Field","landmark2":"Grand Wayne Convention Center","profile":"suburban"},
  "fort-worth-tx":{"name":"Fort Worth","state":"TX","county":"Tarrant County","zip":"76102","areas":["Downtown Fort Worth","Stockyards","Near Southside","Sundance Square","TCU campus","Alliance Corridor","Benbrook"],"landmark1":"Fort Worth Stockyards","landmark2":"Dickies Arena","profile":"oilgas"},
  "franklin-tn":{"name":"Franklin","state":"TN","county":"Williamson County","zip":"37064","areas":["Downtown Franklin","Cool Springs","Berry Farms","Brentwood","Spring Hill","Thompson's Station","Nolensville"],"landmark1":"Franklin Theatre","landmark2":"Battle of Franklin Trust","profile":"suburban"},
  "fresno-ca":{"name":"Fresno","state":"CA","county":"Fresno County","zip":"93721","areas":["Downtown Fresno","Tower District","Clovis","Selma","Sanger","Reedley","Madera"],"landmark1":"Fresno State Campus","landmark2":"Chukchansi Park","profile":"oilgas"},
  "frisco-tx":{"name":"Frisco","state":"TX","county":"Collin County","zip":"75034","areas":["Frisco Station","The Star at Frisco","Shops at Legacy","Stonebriar","Allen","McKinney","Prosper"],"landmark1":"Toyota Stadium","landmark2":"National Soccer Hall of Fame","profile":"tech"},
  "gainesville-fl":{"name":"Gainesville","state":"FL","county":"Alachua County","zip":"32601","areas":["University of Florida campus","Downtown Gainesville","Haile Village","Archer","Newberry","Micanopy","Waldo"],"landmark1":"Ben Hill Griffin Stadium","landmark2":"Stephen C. O'Connell Center","profile":"college"},
  "garland-tx":{"name":"Garland","state":"TX","county":"Dallas County","zip":"75040","areas":["Downtown Garland","Firewheel","North Garland","Sachse","Rowlett","Wylie","Mesquite"],"landmark1":"Firewheel Town Center","landmark2":"Garland ISD Stadium","profile":"suburban"},
  "georgetown-tx":{"name":"Georgetown","state":"TX","county":"Williamson County","zip":"78626","areas":["Downtown Georgetown","Sun City","Wolf Ranch","Leander","Round Rock","Cedar Park","Liberty Hill"],"landmark1":"Georgetown Square","landmark2":"Lake Georgetown","profile":"suburban"},
  "gilbert-az":{"name":"Gilbert","state":"AZ","county":"Maricopa County","zip":"85234","areas":["Downtown Gilbert","Heritage District","Power Road","Agritopia","Higley","Chandler","Queen Creek"],"landmark1":"Cactus League Spring Training facilities","landmark2":"Riparian Preserve","profile":"suburban"},
  "grand-rapids-mi":{"name":"Grand Rapids","state":"MI","county":"Kent County","zip":"49503","areas":["Downtown Grand Rapids","Eastown","Heartside","West Side","Holland","Wyoming","Kentwood"],"landmark1":"Van Andel Arena","landmark2":"Frederik Meijer Gardens","profile":"tech"},
  "greenville-sc":{"name":"Greenville","state":"SC","county":"Greenville County","zip":"29601","areas":["Downtown Greenville","Augusta Road","Simpsonville","Mauldin","Travelers Rest","Greer","Spartanburg"],"landmark1":"Bon Secours Wellness Arena","landmark2":"Falls Park on the Reedy","profile":"tech"},
  "hartford-ct":{"name":"Hartford","state":"CT","county":"Hartford County","zip":"06103","areas":["Downtown Hartford","West End","Asylum Hill","Blue Hills","East Hartford","Glastonbury","West Hartford"],"landmark1":"XL Center","landmark2":"Colt Gateway","profile":"government"},
  "henderson-nv":{"name":"Henderson","state":"NV","county":"Clark County","zip":"89002","areas":["Downtown Henderson","Green Valley","Anthem","Seven Hills","Lake Las Vegas","Boulder City","Summerlin"],"landmark1":"Dollar Loan Center Arena","landmark2":"Lake Mead","profile":"suburban"},
  "highlands-ranch-co":{"name":"Highlands Ranch","state":"CO","county":"Douglas County","zip":"80129","areas":["Westridge","Eastridge","Northridge","Southridge","Backcountry","Lone Tree","Parker"],"landmark1":"Highlands Ranch Mansion","landmark2":"HRCA Outdoor Pool Complex","profile":"suburban"},
  "honolulu-hi":{"name":"Honolulu","state":"HI","county":"Honolulu County","zip":"96813","areas":["Downtown Honolulu","Waikiki","Kaimuki","Hawaii Kai","Kapolei","Pearl City","Kailua"],"landmark1":"Pearl Harbor National Memorial","landmark2":"Aloha Stadium","profile":"coastal"},
  "hoover-al":{"name":"Hoover","state":"AL","county":"Jefferson County","zip":"35216","areas":["Riverchase","Ross Bridge","Greystone","Lake Cyrus","Inverness","Cahaba Heights","Mountain Brook"],"landmark1":"Hoover Metropolitan Stadium","landmark2":"Riverchase Galleria","profile":"suburban"},
  "houston-tx":{"name":"Houston","state":"TX","county":"Harris County","zip":"77002","areas":["Downtown Houston","Galleria/Uptown","Medical Center","The Heights","Midtown","Montrose","Sugar Land"],"landmark1":"Minute Maid Park","landmark2":"NRG Stadium","profile":"oilgas"},
  "huntsville-al":{"name":"Huntsville","state":"AL","county":"Madison County","zip":"35801","areas":["Downtown Huntsville","Redstone Arsenal","Cummings Research Park","Jones Valley","Madison","Hampton Cove","Meridianville"],"landmark1":"U.S. Space & Rocket Center","landmark2":"Redstone Arsenal","profile":"government"},
  "independence-mo":{"name":"Independence","state":"MO","county":"Jackson County","zip":"64050","areas":["Downtown Independence","Englewood","Little Blue","Sugar Creek","Lee's Summit","Blue Springs","Raytown"],"landmark1":"Harry S. Truman Library","landmark2":"Worlds of Fun","profile":"suburban"},
  "indianapolis-in":{"name":"Indianapolis","state":"IN","county":"Marion County","zip":"46204","areas":["Downtown Indianapolis","Broad Ripple","Fountain Square","Carmel","Fishers","Lawrence","Speedway"],"landmark1":"Indianapolis Motor Speedway","landmark2":"Lucas Oil Stadium","profile":"events"},
  "irvine-ca":{"name":"Irvine","state":"CA","county":"Orange County","zip":"92612","areas":["Irvine Spectrum","University of California Irvine","Great Park","Woodbridge","Laguna Hills","Mission Viejo","Tustin"],"landmark1":"Great Park Amphitheatre","landmark2":"UCI Campus","profile":"tech"},
  "irving-tx":{"name":"Irving","state":"TX","county":"Dallas County","zip":"75038","areas":["Las Colinas","Valley Ranch","Irving Heights","DFW Airport area","Coppell","Carrollton","Grand Prairie"],"landmark1":"Irving Convention Center","landmark2":"Toyota Music Factory","profile":"tech"},
  "jackson-ms":{"name":"Jackson","state":"MS","county":"Hinds County","zip":"39201","areas":["Downtown Jackson","Fondren","North Jackson","Ridgeland","Brandon","Pearl","Flowood"],"landmark1":"Mississippi State Capitol","landmark2":"MS Coliseum","profile":"government"},
  "jacksonville-fl":{"name":"Jacksonville","state":"FL","county":"Duval County","zip":"32202","areas":["Downtown Jacksonville","Riverside","Avondale","Baymeadows","Southside","Neptune Beach","Orange Park"],"landmark1":"TIAA Bank Field","landmark2":"Jacksonville Fairgrounds","profile":"coastal"},
  "johnson-city-tn":{"name":"Johnson City","state":"TN","county":"Washington County","zip":"37601","areas":["Downtown Johnson City","ETSU campus","Gray","Jonesborough","Kingsport","Bristol","Elizabethton"],"landmark1":"ETSU campus","landmark2":"Freedom Hall Civic Center","profile":"college"},
  "kansas-city-mo":{"name":"Kansas City","state":"MO","county":"Jackson County","zip":"64106","areas":["Downtown KC","Power & Light District","Crossroads","Country Club Plaza","Westport","Lee's Summit","Overland Park KS"],"landmark1":"Arrowhead Stadium","landmark2":"Kauffman Stadium","profile":"events"},
  "katy-tx":{"name":"Katy","state":"TX","county":"Harris County","zip":"77450","areas":["Downtown Katy","LaCenterra","Katy Mills","Cinco Ranch","Fulshear","Sugar Land","Brookshire"],"landmark1":"Katy ISD Legacy Stadium","landmark2":"Typhoon Texas Waterpark","profile":"suburban"},
  "killeen-tx":{"name":"Killeen","state":"TX","county":"Bell County","zip":"76541","areas":["Downtown Killeen","Fort Cavazos","Harker Heights","Copperas Cove","Belton","Temple","Lampasas"],"landmark1":"Fort Cavazos (formerly Fort Hood)","landmark2":"Killeen-Fort Hood Regional Airport","profile":"government"},
  "knoxville-tn":{"name":"Knoxville","state":"TN","county":"Knox County","zip":"37902","areas":["Downtown Knoxville","University of Tennessee","Bearden","West Knoxville","Maryville","Oak Ridge","Farragut"],"landmark1":"Neyland Stadium","landmark2":"World's Fair Park","profile":"college"},
  "lafayette-la":{"name":"Lafayette","state":"LA","county":"Lafayette Parish","zip":"70501","areas":["Downtown Lafayette","River Ranch","Youngsville","Broussard","Scott","Breaux Bridge","Opelousas"],"landmark1":"Cajundome Arena","landmark2":"Vermilionville Historic Village","profile":"oilgas"},
  "lansing-mi":{"name":"Lansing","state":"MI","county":"Ingham County","zip":"48933","areas":["Downtown Lansing","Old Town","Michigan State University (East Lansing)","Okemos","DeWitt","Mason","Charlotte"],"landmark1":"Spartan Stadium at MSU","landmark2":"Michigan State Capitol","profile":"government"},
  "laredo-tx":{"name":"Laredo","state":"TX","county":"Webb County","zip":"78040","areas":["Downtown Laredo","North Laredo","Del Mar","San Isidro","South Laredo","Nuevo Laredo MX border","Encinal"],"landmark1":"Lamar Bruni Vergara Planetarium","landmark2":"World Trade International Bridge","profile":"oilgas"},
  "las-vegas-nv":{"name":"Las Vegas","state":"NV","county":"Clark County","zip":"89101","areas":["The Strip","Downtown Las Vegas","Henderson","Summerlin","North Las Vegas","Enterprise","Paradise"],"landmark1":"Allegiant Stadium","landmark2":"Las Vegas Convention Center","profile":"events"},
  "league-city-tx":{"name":"League City","state":"TX","county":"Galveston County","zip":"77573","areas":["Downtown League City","Clear Lake","Friendswood","Dickinson","Kemah","Webster","Pearland"],"landmark1":"NASA Johnson Space Center","landmark2":"Kemah Boardwalk","profile":"tech"},
  "lehigh-acres-fl":{"name":"Lehigh Acres","state":"FL","county":"Lee County","zip":"33936","areas":["Central Lehigh Acres","Buckingham","Tice","North Fort Myers","Bonita Springs","Cape Coral","Fort Myers"],"landmark1":"JetBlue Park","landmark2":"Fort Myers Beach","profile":"coastal"},
  "lewisville-tx":{"name":"Lewisville","state":"TX","county":"Denton County","zip":"75067","areas":["Downtown Lewisville","Castle Hills","Vista Ridge","Flower Mound","The Colony","Hebron","Coppell"],"landmark1":"Lewisville Lake","landmark2":"Toyota of Lewisville Arena","profile":"suburban"},
  "lexington-ky":{"name":"Lexington","state":"KY","county":"Fayette County","zip":"40507","areas":["Downtown Lexington","UK campus","Chevy Chase","Hamburg","Beaumont","Tates Creek","Nicholasville"],"landmark1":"Rupp Arena","landmark2":"Keeneland Race Course","profile":"college"},
  "lincoln-ne":{"name":"Lincoln","state":"NE","county":"Lancaster County","zip":"68501","areas":["Downtown Lincoln","Haymarket","University of Nebraska","South Lincoln","Beatrice","Waverly","Seward"],"landmark1":"Memorial Stadium at UNL","landmark2":"Pinnacle Bank Arena","profile":"college"},
  "little-rock-ar":{"name":"Little Rock","state":"AR","county":"Pulaski County","zip":"72201","areas":["Downtown Little Rock","River Market","Heights","West Little Rock","Benton","Bryant","Maumelle"],"landmark1":"Bill Clinton Presidential Library","landmark2":"Verizon Arena","profile":"government"},
  "long-beach-ca":{"name":"Long Beach","state":"CA","county":"Los Angeles County","zip":"90802","areas":["Downtown Long Beach","Belmont Shore","Naples","Bixby Knolls","Signal Hill","Lakewood","Compton"],"landmark1":"Long Beach Convention Center","landmark2":"Queen Mary","profile":"coastal"},
  "los-angeles-ca":{"name":"Los Angeles","state":"CA","county":"Los Angeles County","zip":"90012","areas":["Downtown LA","Hollywood","Westside","Silver Lake","Venice","Santa Monica","Burbank"],"landmark1":"SoFi Stadium","landmark2":"Griffith Observatory","profile":"events"},
  "louisville-ky":{"name":"Louisville","state":"KY","county":"Jefferson County","zip":"40202","areas":["Downtown Louisville","NuLu","Clifton","Highlands","Germantown","St. Matthews","Jeffersontown"],"landmark1":"Churchill Downs","landmark2":"KFC Yum! Center","profile":"events"},
  "lubbock-tx":{"name":"Lubbock","state":"TX","county":"Lubbock County","zip":"79401","areas":["Downtown Lubbock","Texas Tech","South Plains","Wolfforth","Slaton","Tahoka","Plainview"],"landmark1":"Jones AT&T Stadium at Texas Tech","landmark2":"Buddy Holly Hall","profile":"college"},
  "macon-ga":{"name":"Macon","state":"GA","county":"Bibb County","zip":"31201","areas":["Downtown Macon","Ingleside","East Macon","Warner Robins","Milledgeville","Forsyth","Gray"],"landmark1":"Ocmulgee Mounds National Historical Park","landmark2":"Macon Centreplex","profile":"events"},
  "madison-wi":{"name":"Madison","state":"WI","county":"Dane County","zip":"53703","areas":["Downtown Madison","State Street","UW Madison campus","Middleton","Fitchburg","Sun Prairie","Verona"],"landmark1":"Camp Randall Stadium","landmark2":"Kohl Center","profile":"college"},
  "mc-allen-tx":{"name":"McAllen","state":"TX","county":"Hidalgo County","zip":"78501","areas":["Downtown McAllen","South McAllen","Edinburg","Mission","Pharr","Weslaco","Harlingen"],"landmark1":"McAllen Convention Center","landmark2":"Quinta Mazatlan","profile":"oilgas"},
  "mckinney-tx":{"name":"McKinney","state":"TX","county":"Collin County","zip":"75069","areas":["Historic Downtown McKinney","Craig Ranch","Stonebridge Ranch","Frisco","Allen","Prosper","Anna"],"landmark1":"McKinney ISD Stadium","landmark2":"Adriatica Village","profile":"suburban"},
  "memphis-tn":{"name":"Memphis","state":"TN","county":"Shelby County","zip":"38103","areas":["Downtown Memphis","Midtown","Beale Street","East Memphis","Germantown","Bartlett","Collierville"],"landmark1":"FedExForum","landmark2":"Graceland","profile":"events"},
  "mesa-az":{"name":"Mesa","state":"AZ","county":"Maricopa County","zip":"85201","areas":["Downtown Mesa","Tempe","Gilbert","Chandler","Scottsdale","Red Mountain","Superstition Springs"],"landmark1":"Sloan Park Cactus League","landmark2":"Arizona Museum of Natural History","profile":"suburban"},
  "miami-fl":{"name":"Miami","state":"FL","county":"Miami-Dade County","zip":"33128","areas":["Downtown Miami","Wynwood","Brickell","Little Havana","Coral Gables","Doral","Hialeah"],"landmark1":"Hard Rock Stadium","landmark2":"American Airlines Arena","profile":"coastal"},
  "midland-tx":{"name":"Midland","state":"TX","county":"Midland County","zip":"79701","areas":["Downtown Midland","Midland Airport","Permian Basin","Odessa","Greenwood","Big Spring","Andrews"],"landmark1":"Schlotzsky's Park Stadium","landmark2":"Permian Basin Petroleum Museum","profile":"oilgas"},
  "milwaukee-wi":{"name":"Milwaukee","state":"WI","county":"Milwaukee County","zip":"53202","areas":["Downtown Milwaukee","Historic Third Ward","Bay View","Wauwatosa","Shorewood","West Allis","Brookfield"],"landmark1":"American Family Field","landmark2":"Fiserv Forum","profile":"events"},
  "minneapolis-mn":{"name":"Minneapolis","state":"MN","county":"Hennepin County","zip":"55401","areas":["Downtown Minneapolis","Uptown","North Loop","Northeast","St. Paul","Edina","Bloomington"],"landmark1":"U.S. Bank Stadium","landmark2":"Target Center","profile":"tech"},
  "mobile-al":{"name":"Mobile","state":"AL","county":"Mobile County","zip":"36602","areas":["Downtown Mobile","Midtown","Spring Hill","West Mobile","Semmes","Theodore","Daphne"],"landmark1":"Mardi Gras Park","landmark2":"Port of Mobile","profile":"coastal"},
  "montgomery-al":{"name":"Montgomery","state":"AL","county":"Montgomery County","zip":"36104","areas":["Downtown Montgomery","Prattville","Millbrook","Auburn/Opelika area","Wetumpka","Selma","Pike Road"],"landmark1":"Alabama State Capitol","landmark2":"Riverwalk Stadium","profile":"government"},
  "murfreesboro-tn":{"name":"Murfreesboro","state":"TN","county":"Rutherford County","zip":"37130","areas":["Downtown Murfreesboro","MTSU campus","Stones River","Smyrna","La Vergne","Lavergne","Christiana"],"landmark1":"Middle Tennessee State University","landmark2":"Stones River National Battlefield","profile":"college"},
  "myrtle-beach-sc":{"name":"Myrtle Beach","state":"SC","county":"Horry County","zip":"29577","areas":["Myrtle Beach Boardwalk","Broadway at the Beach","North Myrtle Beach","Surfside Beach","Murrells Inlet","Pawleys Island","Conway"],"landmark1":"Myrtle Beach Boardwalk","landmark2":"Coastal Federal Credit Union Music Park","profile":"coastal"},
  "nashville-tn":{"name":"Nashville","state":"TN","county":"Davidson County","zip":"37219","areas":["Downtown Nashville","Germantown","The Gulch","12 South","East Nashville","Brentwood","Franklin"],"landmark1":"Nissan Stadium","landmark2":"Bridgestone Arena","profile":"events"},
  "new-haven-ct":{"name":"New Haven","state":"CT","county":"New Haven County","zip":"06510","areas":["Downtown New Haven","Yale University","Wooster Square","East Rock","West River","Hamden","Milford"],"landmark1":"Yale Bowl","landmark2":"Toad's Place","profile":"college"},
  "new-orleans-la":{"name":"New Orleans","state":"LA","county":"Orleans Parish","zip":"70112","areas":["French Quarter","Garden District","Marigny","Uptown","Mid-City","Metairie","Kenner"],"landmark1":"Caesars Superdome","landmark2":"Jazz Fest Fairgrounds","profile":"events"},
  "norfolk-va":{"name":"Norfolk","state":"VA","county":"Norfolk City","zip":"23510","areas":["Downtown Norfolk","Ghent","Wards Corner","Naval Station Norfolk","Virginia Beach","Chesapeake","Portsmouth"],"landmark1":"Naval Station Norfolk","landmark2":"Norfolk Scope Arena","profile":"government"},
  "oklahoma-city-ok":{"name":"Oklahoma City","state":"OK","county":"Oklahoma County","zip":"73102","areas":["Bricktown","Midtown","Mesta Park","Edmond","Moore","Norman","Yukon"],"landmark1":"Paycom Center","landmark2":"Chesapeake Energy Arena","profile":"oilgas"},
  "omaha-ne":{"name":"Omaha","state":"NE","county":"Douglas County","zip":"68102","areas":["Downtown Omaha","Midtown Crossing","Old Market","Papillion","Bellevue","Council Bluffs IA","La Vista"],"landmark1":"Charles Schwab Field","landmark2":"TD Ameritrade Park","profile":"tech"},
  "orlando-fl":{"name":"Orlando","state":"FL","county":"Orange County","zip":"32801","areas":["Downtown Orlando","International Drive","Lake Nona","Winter Park","Kissimmee","Sanford","Oviedo"],"landmark1":"Walt Disney World Resort","landmark2":"Amway Center","profile":"events"},
  "pearland-tx":{"name":"Pearland","state":"TX","county":"Brazoria County","zip":"77581","areas":["Silverlake","Shadow Creek Ranch","Old Town Pearland","Friendswood","Alvin","Manvel","Iowa Colony"],"landmark1":"Pearland Town Center","landmark2":"Johnson Space Center vicinity","profile":"suburban"},
  "phoenix-az":{"name":"Phoenix","state":"AZ","county":"Maricopa County","zip":"85004","areas":["Downtown Phoenix","Scottsdale","Tempe","Chandler","Glendale","Peoria","Mesa"],"landmark1":"State Farm Stadium","landmark2":"Chase Field","profile":"suburban"},
  "pittsburgh-pa":{"name":"Pittsburgh","state":"PA","county":"Allegheny County","zip":"15222","areas":["Downtown Pittsburgh","Strip District","Lawrenceville","South Side","Mt. Washington","Carnegie","Monroeville"],"landmark1":"PNC Park","landmark2":"Acrisure Stadium","profile":"tech"},
  "plano-tx":{"name":"Plano","state":"TX","county":"Collin County","zip":"75074","areas":["Downtown Plano","Legacy West","Haggard Park","Allen","Frisco","McKinney","Richardson"],"landmark1":"Legacy West","landmark2":"Toyota Stadium at Frisco vicinity","profile":"tech"},
  "portland-or":{"name":"Portland","state":"OR","county":"Multnomah County","zip":"97204","areas":["Downtown Portland","Pearl District","Alberta Arts","Mississippi Ave","Lake Oswego","Beaverton","Gresham"],"landmark1":"Providence Park","landmark2":"Oregon Convention Center","profile":"tech"},
  "providence-ri":{"name":"Providence","state":"RI","county":"Providence County","zip":"02903","areas":["Downtown Providence","Federal Hill","Fox Point","College Hill","East Providence","Cranston","Pawtucket"],"landmark1":"Brown University","landmark2":"Dunkin' Donuts Center","profile":"college"},
  "raleigh-nc":{"name":"Raleigh","state":"NC","county":"Wake County","zip":"27601","areas":["Downtown Raleigh","NC State campus","Glenwood South","Five Points","Durham","Cary","Apex"],"landmark1":"Carter-Finley Stadium","landmark2":"Lenovo Center","profile":"tech"},
  "reno-nv":{"name":"Reno","state":"NV","county":"Washoe County","zip":"89501","areas":["Downtown Reno","Midtown","South Reno","Sparks","Carson City","Fallon","Fernley"],"landmark1":"UNR campus","landmark2":"Reno Events Center","profile":"events"},
  "richmond-va":{"name":"Richmond","state":"VA","county":"Henrico County","zip":"23219","areas":["Downtown Richmond","Carytown","The Fan","Scott's Addition","Chesterfield","Henrico","Short Pump"],"landmark1":"Virginia State Capitol","landmark2":"Richmond Raceway","profile":"government"},
  "riverside-ca":{"name":"Riverside","state":"CA","county":"Riverside County","zip":"92501","areas":["Downtown Riverside","UC Riverside","Arlington","Canyon Crest","Moreno Valley","Perris","Corona"],"landmark1":"UC Riverside Campus","landmark2":"Fox Performing Arts Center","profile":"college"},
  "rochester-ny":{"name":"Rochester","state":"NY","county":"Monroe County","zip":"14614","areas":["Downtown Rochester","Park Avenue","South Wedge","Corn Hill","East Rochester","Brighton","Pittsford"],"landmark1":"Frontier Field","landmark2":"Blue Cross Arena","profile":"tech"},
  "round-rock-tx":{"name":"Round Rock","state":"TX","county":"Williamson County","zip":"78664","areas":["Downtown Round Rock","Dell Diamond","Ikea area","Georgetown","Cedar Park","Pflugerville","Hutto"],"landmark1":"Dell Diamond Baseball Park","landmark2":"Round Rock Sports Center","profile":"tech"},
  "sacramento-ca":{"name":"Sacramento","state":"CA","county":"Sacramento County","zip":"95814","areas":["Downtown Sacramento","Midtown","Oak Park","Land Park","Natomas","Elk Grove","Roseville"],"landmark1":"Golden 1 Center","landmark2":"Raley Field","profile":"government"},
  "salt-lake-city-ut":{"name":"Salt Lake City","state":"UT","county":"Salt Lake County","zip":"84101","areas":["Downtown SLC","Avenues","Sugar House","Millcreek","West Valley City","Provo","Ogden"],"landmark1":"University of Utah Rice-Eccles Stadium","landmark2":"Delta Center","profile":"tech"},
  "san-antonio-tx":{"name":"San Antonio","state":"TX","county":"Bexar County","zip":"78205","areas":["Downtown San Antonio","The Pearl","Southtown","Stone Oak","Alamo Heights","Helotes","New Braunfels"],"landmark1":"The Alamo","landmark2":"Alamodome","profile":"events"},
  "san-diego-ca":{"name":"San Diego","state":"CA","county":"San Diego County","zip":"92101","areas":["Downtown San Diego","Gaslamp Quarter","Mission Bay","La Jolla","Chula Vista","El Cajon","Oceanside"],"landmark1":"Petco Park","landmark2":"Pechanga Arena","profile":"coastal"},
  "san-francisco-ca":{"name":"San Francisco","state":"CA","county":"San Francisco County","zip":"94102","areas":["Financial District","SoMa","Mission District","Castro","North Beach","Oakland","San Jose"],"landmark1":"Oracle Park","landmark2":"Chase Center","profile":"tech"},
  "san-jose-ca":{"name":"San Jose","state":"CA","county":"Santa Clara County","zip":"95110","areas":["Downtown San Jose","Silicon Valley","Santana Row","Almaden Valley","Campbell","Los Gatos","Milpitas"],"landmark1":"SAP Center","landmark2":"San Jose McEnery Convention Center","profile":"tech"},
  "savannah-ga":{"name":"Savannah","state":"GA","county":"Chatham County","zip":"31401","areas":["Historic District","Forsyth Park","Ardsley Park","Thomas Square","Tybee Island","Pooler","Garden City"],"landmark1":"Savannah Squares","landmark2":"Tybee Island Beach","profile":"coastal"},
  "scottsdale-az":{"name":"Scottsdale","state":"AZ","county":"Maricopa County","zip":"85251","areas":["Old Town Scottsdale","Scottsdale Quarter","North Scottsdale","McCormick Ranch","Paradise Valley","Tempe","Fountain Hills"],"landmark1":"Scottsdale Stadium Cactus League","landmark2":"WestWorld of Scottsdale","profile":"events"},
  "seattle-wa":{"name":"Seattle","state":"WA","county":"King County","zip":"98101","areas":["Downtown Seattle","Capitol Hill","Ballard","Fremont","Bellevue","Redmond","Kirkland"],"landmark1":"Lumen Field","landmark2":"T-Mobile Park","profile":"tech"},
  "shreveport-la":{"name":"Shreveport","state":"LA","county":"Caddo Parish","zip":"71101","areas":["Downtown Shreveport","South Shreveport","Bossier City","Minden","Haughton","Natchitoches","Longview TX"],"landmark1":"Independence Stadium","landmark2":"Shreveport Aquarium","profile":"oilgas"},
  "sioux-falls-sd":{"name":"Sioux Falls","state":"SD","county":"Minnehaha County","zip":"57104","areas":["Downtown Sioux Falls","Falls Park","Brandon","Tea","Harrisburg","Renner","Baltic"],"landmark1":"Denny Sanford PREMIER Center","landmark2":"Falls Park","profile":"suburban"},
  "south-fulton-ga":{"name":"South Fulton","state":"GA","county":"Fulton County","zip":"30349","areas":["College Park","Union City","Fairburn","Red Oak","Palmetto","Chattahoochee Hills","East Point"],"landmark1":"Atlanta Hartsfield-Jackson Airport","landmark2":"Georgia International Convention Center","profile":"suburban"},
  "spokane-wa":{"name":"Spokane","state":"WA","county":"Spokane County","zip":"99201","areas":["Downtown Spokane","South Hill","North Spokane","Liberty Lake","Coeur d'Alene ID","Cheney","Deer Park"],"landmark1":"Spokane Arena","landmark2":"Riverfront Park","profile":"suburban"},
  "springfield-mo":{"name":"Springfield","state":"MO","county":"Greene County","zip":"65806","areas":["Downtown Springfield","Bass Pro Shops area","Missouri State campus","Battlefield","Republic","Nixa","Ozark"],"landmark1":"JQH Arena at Missouri State","landmark2":"Bass Pro Shops HQ","profile":"suburban"},
  "st-louis-mo":{"name":"St. Louis","state":"MO","county":"St. Louis County","zip":"63101","areas":["Downtown St. Louis","Soulard","The Hill","Clayton","Chesterfield","Ballwin","O'Fallon"],"landmark1":"Busch Stadium","landmark2":"Scottrade Center","profile":"events"},
  "st-paul-mn":{"name":"St. Paul","state":"MN","county":"Ramsey County","zip":"55101","areas":["Downtown St. Paul","Summit Avenue","Payne-Phalen","St. Anthony Park","Roseville","Maplewood","Woodbury"],"landmark1":"Xcel Energy Center","landmark2":"CHS Field","profile":"government"},
  "st-petersburg-fl":{"name":"St. Petersburg","state":"FL","county":"Pinellas County","zip":"33701","areas":["Downtown St. Pete","Dali Museum area","Grand Central","St. Pete Beach","Gulfport","Clearwater","Seminole"],"landmark1":"Tropicana Field","landmark2":"The Pier District","profile":"coastal"},
  "stamford-ct":{"name":"Stamford","state":"CT","county":"Fairfield County","zip":"06901","areas":["Downtown Stamford","Harbor Point","North Stamford","Darien","Greenwich","Norwalk","New Canaan"],"landmark1":"UBS Arena vicinity","landmark2":"Stamford Town Center","profile":"tech"},
  "sterling-heights-mi":{"name":"Sterling Heights","state":"MI","county":"Macomb County","zip":"48310","areas":["Sterling Heights Industrial","Lakeside","Utica","Clinton Township","Warren","Troy","Shelby Township"],"landmark1":"Chrysler/Stellantis Automotive Campus","landmark2":"Freedom Hill Park","profile":"tech"},
  "stockton-ca":{"name":"Stockton","state":"CA","county":"San Joaquin County","zip":"95202","areas":["Downtown Stockton","Lincoln Village","Brookside","North Stockton","Lodi","Manteca","Tracy"],"landmark1":"Adventist Health Arena","landmark2":"Banner Island Ballpark","profile":"suburban"},
  "sugar-land-tx":{"name":"Sugar Land","state":"TX","county":"Fort Bend County","zip":"77478","areas":["Sugar Land Town Square","First Colony","New Territory","Sienna","Missouri City","Richmond","Stafford"],"landmark1":"Constellation Field","landmark2":"Smart Financial Centre","profile":"suburban"},
  "surprise-az":{"name":"Surprise","state":"AZ","county":"Maricopa County","zip":"85374","areas":["Downtown Surprise","Marley Park","Kingswood","Sun City","El Mirage","Youngtown","Litchfield Park"],"landmark1":"Surprise Stadium Cactus League","landmark2":"Surprise Recreation Campus","profile":"suburban"},
  "tacoma-wa":{"name":"Tacoma","state":"WA","county":"Pierce County","zip":"98401","areas":["Downtown Tacoma","Proctor","Point Defiance","Stadium District","University Place","Lakewood","Puyallup"],"landmark1":"Lumen Field vicinity","landmark2":"JBLM Joint Base Lewis-McChord","profile":"government"},
  "tallahassee-fl":{"name":"Tallahassee","state":"FL","county":"Leon County","zip":"32301","areas":["Downtown Tallahassee","FSU campus","FAMU campus","Midtown","SouthWood","Killearn","Havana"],"landmark1":"Doak Campbell Stadium at FSU","landmark2":"Florida State Capitol","profile":"government"},
  "tampa-fl":{"name":"Tampa","state":"FL","county":"Hillsborough County","zip":"33602","areas":["Downtown Tampa","Ybor City","Hyde Park","Westchase","Brandon","Carrollwood","New Tampa"],"landmark1":"Raymond James Stadium","landmark2":"Amalie Arena","profile":"events"},
  "the-woodlands-tx":{"name":"The Woodlands","state":"TX","county":"Montgomery County","zip":"77380","areas":["Town Center","Grogan's Mill","Panther Creek","Sterling Ridge","Creekside","Spring","Conroe"],"landmark1":"Cynthia Woods Mitchell Pavilion","landmark2":"The Woodlands Waterway","profile":"suburban"},
  "toledo-oh":{"name":"Toledo","state":"OH","county":"Lucas County","zip":"43604","areas":["Downtown Toledo","Old West End","University of Toledo","Perrysburg","Maumee","Sylvania","Oregon"],"landmark1":"Fifth Third Field","landmark2":"Huntington Center","profile":"suburban"},
  "tucson-az":{"name":"Tucson","state":"AZ","county":"Pima County","zip":"85701","areas":["Downtown Tucson","University of Arizona","Catalina Foothills","Marana","Sahuarita","Oro Valley","Green Valley"],"landmark1":"Arizona Stadium at UA","landmark2":"Tucson Convention Center","profile":"college"},
  "tulsa-ok":{"name":"Tulsa","state":"OK","county":"Tulsa County","zip":"74103","areas":["Downtown Tulsa","Brady Arts District","Cherry Street","Broken Arrow","Jenks","Bixby","Sand Springs"],"landmark1":"BOK Center","landmark2":"Tulsa Expo Center","profile":"oilgas"},
  "tuscaloosa-al":{"name":"Tuscaloosa","state":"AL","county":"Tuscaloosa County","zip":"35401","areas":["Downtown Tuscaloosa","UA campus","Northport","McCalla","Cottondale","Moundville","Demopolis"],"landmark1":"Bryant-Denny Stadium","landmark2":"Tuscaloosa Amphitheater","profile":"college"},
  "virginia-beach-va":{"name":"Virginia Beach","state":"VA","county":"Virginia Beach City","zip":"23451","areas":["Oceanfront","Town Center","Great Neck","Princess Anne","Norfolk","Chesapeake","Hampton"],"landmark1":"Virginia Beach Oceanfront","landmark2":"Veterans United Home Loans Amphitheater","profile":"coastal"},
  "waco-tx":{"name":"Waco","state":"TX","county":"McLennan County","zip":"76701","areas":["Downtown Waco","Baylor University","Magnolia Market","Hewitt","Woodway","Hillsboro","Temple"],"landmark1":"McLane Stadium at Baylor","landmark2":"Magnolia Market at the Silos","profile":"college"},
  "warren-city-mi":{"name":"Warren","state":"MI","county":"Macomb County","zip":"48089","areas":["Downtown Warren","GM Technical Center","Sterling Heights","Eastpointe","Centerline","Hazel Park","Madison Heights"],"landmark1":"General Motors Technical Center","landmark2":"Macomb County Fairgrounds","profile":"tech"},
  "waterbury-ct":{"name":"Waterbury","state":"CT","county":"New Haven County","zip":"06702","areas":["Downtown Waterbury","Naugatuck","Wolcott","Cheshire","Prospect","Southbury","Torrington"],"landmark1":"Webster Bank Arena","landmark2":"Holy Land USA","profile":"suburban"},
  "west-palm-beach-fl":{"name":"West Palm Beach","state":"FL","county":"Palm Beach County","zip":"33401","areas":["Downtown West Palm Beach","Northwood","Palm Beach Island","Jupiter","Wellington","Boynton Beach","Boca Raton"],"landmark1":"SunFest Music Festival grounds","landmark2":"Palm Beach Convention Center","profile":"coastal"},
  "wichita-ks":{"name":"Wichita","state":"KS","county":"Sedgwick County","zip":"67202","areas":["Downtown Wichita","Old Town","Delano","Riverside","East Wichita","Derby","Andover"],"landmark1":"Beechcraft Aviation Museum","landmark2":"Century II Performing Arts Center","profile":"oilgas"},
  "wichita-falls-tx":{"name":"Wichita Falls","state":"TX","county":"Wichita County","zip":"76301","areas":["Downtown Wichita Falls","Sheppard AFB","MSU Texas campus","Burkburnett","Iowa Park","Electra","Vernon"],"landmark1":"Sheppard Air Force Base","landmark2":"MPEC Arena","profile":"government"},
  "worcester-ma":{"name":"Worcester","state":"MA","county":"Worcester County","zip":"01608","areas":["Downtown Worcester","Clark University","WPI campus","Grafton","Shrewsbury","Auburn","Northborough"],"landmark1":"Holy Cross Spectrum Arena","landmark2":"Polar Park","profile":"college"},
  "athens-ga":{"name":"Athens","state":"GA","county":"Clarke County","zip":"30601","areas":["Downtown Athens","Five Points","Normaltown","East Athens","Boulevard District","West Athens","Winterville"],"landmark1":"Sanford Stadium","landmark2":"Georgia Theatre","profile":"college"},
  "savannah-ga":{"name":"Savannah","state":"GA","county":"Chatham County","zip":"31401","areas":["Historic District","Forsyth Park","Ardsley Park","Thomas Square","Tybee Island","Pooler","Garden City"],"landmark1":"Savannah Squares","landmark2":"Tybee Island Beach","profile":"coastal"},
  "baton-rouge-la":{"name":"Baton Rouge","state":"LA","county":"East Baton Rouge Parish","zip":"70801","areas":["Downtown Baton Rouge","LSU campus","Mid City","Southdowns","Broadmoor","Denham Springs","Zachary"],"landmark1":"Tiger Stadium at LSU","landmark2":"Louisiana State Capitol","profile":"college"},
  # ── Long Island NY ──
  "huntington-ny":{"name":"Huntington","state":"NY","county":"Suffolk County","zip":"11743","areas":["Huntington Village","Centerport","Cold Spring Harbor","Northport","Lloyd Harbor","Melville","Amityville"],"landmark1":"Heckscher State Park","landmark2":"NYCB LIVE at Nassau Coliseum","profile":"suburban"},
  "north-hempstead-ny":{"name":"North Hempstead","state":"NY","county":"Nassau County","zip":"11050","areas":["Port Washington","Manhasset","Roslyn","Great Neck","New Hyde Park","Mineola","Garden City"],"landmark1":"Nassau Veterans Memorial Coliseum","landmark2":"Cradle of Aviation Museum","profile":"suburban"},
  "babylon-town-ny":{"name":"Babylon","state":"NY","county":"Suffolk County","zip":"11702","areas":["Babylon Village","Amityville","Copiague","Lindenhurst","West Babylon","North Babylon","Wyandanch"],"landmark1":"Jones Beach State Park","landmark2":"Bethpage State Park","profile":"coastal"},
  "islip-ny":{"name":"Islip","state":"NY","county":"Suffolk County","zip":"11751","areas":["Islip","Bay Shore","Central Islip","Brentwood","West Islip","East Islip","Bohemia"],"landmark1":"Long Island MacArthur Airport","landmark2":"Robert Moses State Park","profile":"suburban"},
  "hempstead-town-ny":{"name":"Hempstead","state":"NY","county":"Nassau County","zip":"11550","areas":["Hempstead Village","Uniondale","Garden City","Levittown","Freeport","Valley Stream","Oceanside"],"landmark1":"UBS Arena","landmark2":"Hofstra University","profile":"suburban"},
  "oyster-bay-ny":{"name":"Oyster Bay","state":"NY","county":"Nassau County","zip":"11771","areas":["Oyster Bay Village","Syosset","Plainview","Hicksville","Old Bethpage","Bethpage","Massapequa"],"landmark1":"Bethpage Black Golf Course","landmark2":"Old Westbury Gardens","profile":"suburban"},
  "brookhaven-ny":{"name":"Brookhaven","state":"NY","county":"Suffolk County","zip":"11719","areas":["Patchogue","Medford","Coram","Port Jefferson","Stony Brook","Riverhead","Shirley"],"landmark1":"Stony Brook University","landmark2":"Brookhaven National Laboratory","profile":"college"},
  "nassau-county-ny":{"name":"Nassau County","state":"NY","county":"Nassau County","zip":"11530","areas":["Garden City","Mineola","Hempstead","Long Beach","Great Neck","Massapequa","Hicksville"],"landmark1":"Nassau Veterans Memorial Coliseum","landmark2":"Hofstra University","profile":"suburban"},
  "suffolk-county-ny":{"name":"Suffolk County","state":"NY","county":"Suffolk County","zip":"11788","areas":["Hauppauge","Islandia","Stony Brook","Brentwood","Central Islip","Patchogue","Riverhead"],"landmark1":"Stony Brook University","landmark2":"Brookhaven National Laboratory","profile":"suburban"},
  # ── Florida cities ──
  "hialeah-fl":{"name":"Hialeah","state":"FL","county":"Miami-Dade County","zip":"33010","areas":["Hialeah Gardens","Palm Springs North","Medley","Miami Lakes","Opa-locka","West Little River","Sweetwater"],"landmark1":"Hialeah Park Racing","landmark2":"Miami Jai-Alai","profile":"suburban"},
  "miami-gardens-fl":{"name":"Miami Gardens","state":"FL","county":"Miami-Dade County","zip":"33056","areas":["Carol City","Norland","Andover","Opa-locka","North Miami Beach","Aventura","Hallandale Beach"],"landmark1":"Hard Rock Stadium","landmark2":"Calder Casino","profile":"events"},
  "pembroke-pines-fl":{"name":"Pembroke Pines","state":"FL","county":"Broward County","zip":"33024","areas":["Pembroke Lakes","Chapel Trail","Silver Lakes","Miramar","Davie","Weston","Cooper City"],"landmark1":"Pembroke Lakes Mall","landmark2":"CB Smith Park","profile":"suburban"},
  "pompano-beach-fl":{"name":"Pompano Beach","state":"FL","county":"Broward County","zip":"33060","areas":["Hillsboro Beach","Lighthouse Point","Deerfield Beach","Coconut Creek","Margate","North Lauderdale","Tamarac"],"landmark1":"Pompano Beach Amphitheater","landmark2":"Fishing Hall of Fame","profile":"coastal"},
  "port-st-lucie-fl":{"name":"Port St. Lucie","state":"FL","county":"St. Lucie County","zip":"34986","areas":["Tradition","Torino","Stuart","Jensen Beach","Fort Pierce","Vero Beach","Palm City"],"landmark1":"Clover Park Spring Training","landmark2":"Mets Spring Training Complex","profile":"suburban"},
  "palm-bay-fl":{"name":"Palm Bay","state":"FL","county":"Brevard County","zip":"32905","areas":["Valkaria","Grant-Valkaria","Melbourne","West Melbourne","Brevard County","Malabar","Micco"],"landmark1":"Kennedy Space Center","landmark2":"Melbourne Orlando International Airport","profile":"government"},
  "sunrise-manor-nv":{"name":"Sunrise Manor","state":"NV","county":"Clark County","zip":"89110","areas":["Sunrise","Whitney","Henderson","Boulder City","Enterprise","Spring Valley","Summerlin"],"landmark1":"Nellis Air Force Base","landmark2":"Las Vegas Motor Speedway","profile":"suburban"},
  "enterprise-nv":{"name":"Enterprise","state":"NV","county":"Clark County","zip":"89141","areas":["Spring Valley","Summerlin","Whitney","Paradise","Winchester","Blue Diamond","Mountain Springs"],"landmark1":"Las Vegas Strip vicinity","landmark2":"Harry Reid International Airport","profile":"suburban"},
  "spring-valley-ca":{"name":"Spring Valley","state":"CA","county":"San Diego County","zip":"91977","areas":["Lemon Grove","El Cajon","La Mesa","Santee","Lakeside","Jamul","Rancho San Diego"],"landmark1":"SDSU Mission Valley Campus","landmark2":"Qualcomm Stadium site","profile":"suburban"},
  "bloomington-ca":{"name":"Bloomington","state":"CA","county":"San Bernardino County","zip":"92316","areas":["Rialto","Fontana","Colton","Grand Terrace","Loma Linda","Redlands","Highland"],"landmark1":"California Speedway","landmark2":"San Bernardino International Airport","profile":"suburban"},
  "east-anaheim-ca":{"name":"East Anaheim","state":"CA","county":"Orange County","zip":"92806","areas":["Anaheim Hills","Orange","Villa Park","Yorba Linda","Placentia","Brea","Fullerton"],"landmark1":"Angel Stadium","landmark2":"Honda Center","profile":"events"},
  "west-anaheim-ca":{"name":"West Anaheim","state":"CA","county":"Orange County","zip":"92804","areas":["Stanton","Garden Grove","Westminster","Cypress","Buena Park","La Palma","Los Alamitos"],"landmark1":"Disneyland Resort","landmark2":"Knott's Berry Farm","profile":"events"},
  "southwest-anaheim-ca":{"name":"Southwest Anaheim","state":"CA","county":"Orange County","zip":"92802","areas":["Garden Grove","Stanton","Westminster","Santa Ana","Tustin","Irvine","Lake Forest"],"landmark1":"Disneyland Resort","landmark2":"Great Wolf Lodge Anaheim","profile":"events"},
  "fullerton-north-ca":{"name":"North Fullerton","state":"CA","county":"Orange County","zip":"92835","areas":["Brea","La Habra","Yorba Linda","Placentia","Diamond Bar","Walnut","Rowland Heights"],"landmark1":"Cal State Fullerton","landmark2":"Brea Mall","profile":"college"},
  "lake-forest-ca":{"name":"Lake Forest","state":"CA","county":"Orange County","zip":"92630","areas":["El Toro","Foothill Ranch","Aliso Viejo","Laguna Hills","Mission Viejo","Rancho Santa Margarita","Portola Hills"],"landmark1":"Lake Forest Sports Park","landmark2":"Saddleback Valley","profile":"suburban"},
  "la-habra-ca":{"name":"La Habra","state":"CA","county":"Orange County","zip":"90631","areas":["Brea","Fullerton","La Mirada","Whittier","Rowland Heights","Diamond Bar","Hacienda Heights"],"landmark1":"La Habra Depot Theatre","landmark2":"Friendly Hills Country Club","profile":"suburban"},
  "buena-park-ca":{"name":"Buena Park","state":"CA","county":"Orange County","zip":"90620","areas":["La Palma","Cypress","Stanton","Garden Grove","Anaheim","Fullerton","Cerritos"],"landmark1":"Knott's Berry Farm","landmark2":"Medieval Times Dinner","profile":"events"},
  "brea-ca":{"name":"Brea","state":"CA","county":"Orange County","zip":"92821","areas":["Yorba Linda","Placentia","Fullerton","La Habra","Diamond Bar","Rowland Heights","Walnut"],"landmark1":"Brea Mall","landmark2":"Brea Community Center","profile":"suburban"},
  "tustin-ca":{"name":"Tustin","state":"CA","county":"Orange County","zip":"92780","areas":["Old Town Tustin","Santa Ana","Orange","Irvine","Lake Forest","El Toro Marine Base site","Fountain Valley"],"landmark1":"MCAS Tustin site development","landmark2":"The District at Tustin Legacy","profile":"tech"},
  # ── Illinois ──
  "schaumburg-il":{"name":"Schaumburg","state":"IL","county":"Cook County","zip":"60173","areas":["Hoffman Estates","Palatine","Rolling Meadows","Roselle","Hanover Park","Streamwood","Elk Grove Village"],"landmark1":"Woodfield Mall","landmark2":"Sears Centre Arena","profile":"suburban"},
  "elgin-il":{"name":"Elgin","state":"IL","county":"Kane County","zip":"60120","areas":["South Elgin","Carpentersville","East Dundee","West Dundee","Streamwood","Bartlett","Hanover Park"],"landmark1":"Grand Victoria Casino Elgin","landmark2":"Elgin Symphony Orchestra","profile":"suburban"},
  "joliet-il":{"name":"Joliet","state":"IL","county":"Will County","zip":"60432","areas":["Plainfield","Romeoville","Bolingbrook","Lockport","New Lenox","Mokena","Frankfort"],"landmark1":"Chicagoland Speedway","landmark2":"Rialto Square Theatre","profile":"events"},
  "naperville-il":{"name":"Naperville","state":"IL","county":"DuPage County","zip":"60540","areas":["Lisle","Downers Grove","Aurora","Bolingbrook","Plainfield","Wheaton","Glen Ellyn"],"landmark1":"Naperville Riverwalk","landmark2":"North Central College","profile":"suburban"},
  "rockford-il":{"name":"Rockford","state":"IL","county":"Winnebago County","zip":"61101","areas":["Belvidere","Loves Park","Machesney Park","South Beloit","Roscoe","Cherry Valley","Harlem"],"landmark1":"BMO Harris Bank Center","landmark2":"Coronado Performing Arts Center","profile":"suburban"},
  "springfield-il":{"name":"Springfield","state":"IL","county":"Sangamon County","zip":"62701","areas":["Chatham","Sherman","Rochester","Riverton","Jerome","Pleasant Plains","Williamsville"],"landmark1":"Illinois State Capitol","landmark2":"Abraham Lincoln Presidential Library","profile":"government"},
  "cook-county-il":{"name":"Cook County","state":"IL","county":"Cook County","zip":"60601","areas":["Chicago","Evanston","Oak Park","Skokie","Cicero","Berwyn","Schaumburg"],"landmark1":"Soldier Field","landmark2":"O'Hare International Airport","profile":"events"},
  # ── Maryland ──
  "waldorf-md":{"name":"Waldorf","state":"MD","county":"Charles County","zip":"20601","areas":["St. Charles","White Plains","La Plata","Indian Head","Bryans Road","Brandywine","Hughesville"],"landmark1":"George Washington Birthday Parade","landmark2":"Charles County Government Building","profile":"suburban"},
  "ellicott-city-md":{"name":"Ellicott City","state":"MD","county":"Howard County","zip":"21043","areas":["Columbia","Clarksville","Elkridge","Woodstock","Lisbon","West Friendship","Woodbine"],"landmark1":"Turf Valley Towne Square","landmark2":"Centennial Park","profile":"suburban"},
  "glen-burnie-md":{"name":"Glen Burnie","state":"MD","county":"Anne Arundel County","zip":"21060","areas":["Linthicum","Severn","Pasadena","Millersville","Brooklyn Park","Severna Park","Riviera Beach"],"landmark1":"Baltimore/Washington International Airport","landmark2":"Arundel Mills Mall","profile":"suburban"},
  "germantown-md":{"name":"Germantown","state":"MD","county":"Montgomery County","zip":"20874","areas":["Clarksburg","Damascus","Boyds","Gaithersburg","Rockville","North Potomac","Poolesville"],"landmark1":"SoccerPlex","landmark2":"BlackRock Center for the Arts","profile":"suburban"},
  "silver-spring-md":{"name":"Silver Spring","state":"MD","county":"Montgomery County","zip":"20901","areas":["Wheaton","Takoma Park","Hyattsville","College Park","Beltsville","Glenmont","Aspen Hill"],"landmark1":"AFI Silver Theatre","landmark2":"Montgomery College Silver Spring","profile":"suburban"},
  "sandy-spring-md":{"name":"Sandy Spring","state":"MD","county":"Montgomery County","zip":"20860","areas":["Ashton","Olney","Brookeville","Laytonsville","Gaithersburg","Rockville","Damascus"],"landmark1":"Sandy Spring Museum","landmark2":"Olney Theatre Center","profile":"suburban"},
  "baltimore-county-md":{"name":"Baltimore County","state":"MD","county":"Baltimore County","zip":"21204","areas":["Towson","Catonsville","Rosedale","Dundalk","Essex","Parkville","Overlea"],"landmark1":"Stevenson University","landmark2":"Oregon Ridge Park","profile":"suburban"},
  "frederick-md":{"name":"Frederick","state":"MD","county":"Frederick County","zip":"21701","areas":["Urbana","Middletown","New Market","Walkersville","Brunswick","Thurmont","Emmitsburg"],"landmark1":"Weinberg Center for the Arts","landmark2":"National Museum of Civil War Medicine","profile":"suburban"},
  # ── Washington state ──
  "kent-wa":{"name":"Kent","state":"WA","county":"King County","zip":"98032","areas":["Des Moines","Federal Way","Auburn","Renton","Covington","Maple Valley","Black Diamond"],"landmark1":"Kent Station","landmark2":"ShoWare Center","profile":"suburban"},
  "everett-wa":{"name":"Everett","state":"WA","county":"Snohomish County","zip":"98201","areas":["Marysville","Mukilteo","Lynnwood","Shoreline","Mountlake Terrace","Mill Creek","Snohomish"],"landmark1":"Naval Station Everett","landmark2":"Angel of the Winds Arena","profile":"government"},
  "vancouver-wa":{"name":"Vancouver","state":"WA","county":"Clark County","zip":"98660","areas":["Battle Ground","Ridgefield","Camas","Washougal","Hazel Dell","Orchards","Salmon Creek"],"landmark1":"Fort Vancouver National Historic Site","landmark2":"Clark County Event Center","profile":"suburban"},
  # ── Tennessee ──
  "davidson-county-tn":{"name":"Davidson County","state":"TN","county":"Davidson County","zip":"37201","areas":["Nashville","Berry Hill","Forest Hills","Oak Hill","Goodlettsville","Ridgetop","Pleasant View"],"landmark1":"Nissan Stadium","landmark2":"Bridgestone Arena","profile":"events"},
  "hamilton-county-tn":{"name":"Hamilton County","state":"TN","county":"Hamilton County","zip":"37402","areas":["Chattanooga","East Ridge","Signal Mountain","Lookout Mountain","Red Bank","Soddy-Daisy","Lakesite"],"landmark1":"Tennessee Aquarium","landmark2":"Lookout Mountain Battlefield","profile":"events"},
  "knox-county-tn":{"name":"Knox County","state":"TN","county":"Knox County","zip":"37902","areas":["Knoxville","Farragut","Powell","Halls","Fountain City","Karns","Hardin Valley"],"landmark1":"Neyland Stadium","landmark2":"World's Fair Park","profile":"college"},
  "shelby-county-tn":{"name":"Shelby County","state":"TN","county":"Shelby County","zip":"38101","areas":["Memphis","Germantown","Bartlett","Collierville","Arlington","Lakeland","Millington"],"landmark1":"FedExForum","landmark2":"Graceland","profile":"events"},
  # ── Texas counties ──
  "harris-county-tx":{"name":"Harris County","state":"TX","county":"Harris County","zip":"77002","areas":["Houston","Pasadena","Pearland","Baytown","Missouri City","Stafford","Humble"],"landmark1":"NRG Stadium","landmark2":"Minute Maid Park","profile":"oilgas"},
  "tarrant-county-tx":{"name":"Tarrant County","state":"TX","county":"Tarrant County","zip":"76102","areas":["Fort Worth","Arlington","Mansfield","Hurst","Euless","Bedford","North Richland Hills"],"landmark1":"AT&T Stadium","landmark2":"Dickies Arena","profile":"oilgas"},
  "dallas-county-tx":{"name":"Dallas County","state":"TX","county":"Dallas County","zip":"75201","areas":["Dallas","Irving","Garland","Mesquite","Richardson","Grand Prairie","Carrollton"],"landmark1":"AT&T Stadium","landmark2":"American Airlines Center","profile":"tech"},
  "dallas-fort-worth-tx":{"name":"Dallas-Fort Worth","state":"TX","county":"Dallas County","zip":"75001","areas":["Dallas","Fort Worth","Plano","Irving","Arlington","Garland","Frisco"],"landmark1":"AT&T Stadium","landmark2":"DFW International Airport","profile":"tech"},
  "travis-county-tx":{"name":"Travis County","state":"TX","county":"Travis County","zip":"78701","areas":["Austin","Manor","Pflugerville","Del Valle","Lago Vista","Cedar Park","Round Rock"],"landmark1":"University of Texas at Austin","landmark2":"Moody Center","profile":"tech"},
  "bexar-county-tx":{"name":"Bexar County","state":"TX","county":"Bexar County","zip":"78205","areas":["San Antonio","Converse","Leon Valley","Balcones Heights","Alamo Heights","Windcrest","Live Oak"],"landmark1":"The Alamo","landmark2":"AT&T Center","profile":"events"},
  # ── California counties ──
  "los-angeles-county-ca":{"name":"Los Angeles County","state":"CA","county":"Los Angeles County","zip":"90001","areas":["Los Angeles","Long Beach","Glendale","Santa Clarita","Lancaster","Palmdale","Pomona"],"landmark1":"SoFi Stadium","landmark2":"Dodger Stadium","profile":"events"},
  "orange-county-ca":{"name":"Orange County","state":"CA","county":"Orange County","zip":"92868","areas":["Anaheim","Santa Ana","Irvine","Huntington Beach","Garden Grove","Fullerton","Orange"],"landmark1":"Disneyland Resort","landmark2":"Angel Stadium","profile":"events"},
  "riverside-county-ca":{"name":"Riverside County","state":"CA","county":"Riverside County","zip":"92501","areas":["Riverside","Corona","Moreno Valley","Murrieta","Temecula","Menifee","Hemet"],"landmark1":"UC Riverside","landmark2":"Fox Performing Arts Center","profile":"suburban"},
  "sacramento-county-ca":{"name":"Sacramento County","state":"CA","county":"Sacramento County","zip":"95814","areas":["Sacramento","Elk Grove","Citrus Heights","Rancho Cordova","Folsom","Galt","Isleton"],"landmark1":"Golden 1 Center","landmark2":"Cal Expo State Fairgrounds","profile":"government"},
  "san-diego-county-ca":{"name":"San Diego County","state":"CA","county":"San Diego County","zip":"92101","areas":["San Diego","Chula Vista","Oceanside","Escondido","El Cajon","Vista","Carlsbad"],"landmark1":"Petco Park","landmark2":"Del Mar Fairgrounds","profile":"coastal"},
  "santa-clara-county-ca":{"name":"Santa Clara County","state":"CA","county":"Santa Clara County","zip":"95110","areas":["San Jose","Sunnyvale","Santa Clara","Mountain View","Palo Alto","Campbell","Los Gatos"],"landmark1":"SAP Center","landmark2":"Levi's Stadium","profile":"tech"},
  "suffolk-county-ma":{"name":"Suffolk County","state":"MA","county":"Suffolk County","zip":"02101","areas":["Boston","Chelsea","Revere","Winthrop","East Boston","South Boston","Roxbury"],"landmark1":"Fenway Park","landmark2":"TD Garden","profile":"college"},
  # ── Ohio counties ──
  "cuyahoga-county-oh":{"name":"Cuyahoga County","state":"OH","county":"Cuyahoga County","zip":"44113","areas":["Cleveland","Parma","Lakewood","Euclid","Brooklyn","Strongsville","North Olmsted"],"landmark1":"FirstEnergy Stadium","landmark2":"Rocket Mortgage FieldHouse","profile":"events"},
  "franklin-county-oh":{"name":"Franklin County","state":"OH","county":"Franklin County","zip":"43215","areas":["Columbus","Dublin","Westerville","Gahanna","Hilliard","Grove City","Upper Arlington"],"landmark1":"Ohio Stadium","landmark2":"Nationwide Arena","profile":"tech"},
  # ── Other counties ──
  "allegheny-county-pa":{"name":"Allegheny County","state":"PA","county":"Allegheny County","zip":"15222","areas":["Pittsburgh","Bethel Park","Mt. Lebanon","Penn Hills","Ross Township","Plum","Monroeville"],"landmark1":"PNC Park","landmark2":"Acrisure Stadium","profile":"tech"},
  "broward-county-fl":{"name":"Broward County","state":"FL","county":"Broward County","zip":"33301","areas":["Fort Lauderdale","Pembroke Pines","Hollywood","Miramar","Coral Springs","Pompano Beach","Davie"],"landmark1":"Hard Rock Stadium","landmark2":"BB&T Center","profile":"coastal"},
  "hillsborough-county-fl":{"name":"Hillsborough County","state":"FL","county":"Hillsborough County","zip":"33602","areas":["Tampa","Brandon","Riverview","Plant City","Temple Terrace","Seffner","Gibsonton"],"landmark1":"Raymond James Stadium","landmark2":"Amalie Arena","profile":"events"},
  "orange-county-fl":{"name":"Orange County","state":"FL","county":"Orange County","zip":"32801","areas":["Orlando","Apopka","Ocoee","Maitland","Eatonville","Belle Isle","Pine Hills"],"landmark1":"Walt Disney World Resort","landmark2":"Amway Center","profile":"events"},
  "miami-dade-county-fl":{"name":"Miami-Dade County","state":"FL","county":"Miami-Dade County","zip":"33128","areas":["Miami","Hialeah","Miami Gardens","Coral Gables","Doral","Homestead","North Miami"],"landmark1":"Hard Rock Stadium","landmark2":"American Airlines Arena","profile":"coastal"},
  "hennepin-county-mn":{"name":"Hennepin County","state":"MN","county":"Hennepin County","zip":"55401","areas":["Minneapolis","Bloomington","Plymouth","Brooklyn Park","Maple Grove","Eden Prairie","Minnetonka"],"landmark1":"U.S. Bank Stadium","landmark2":"Target Center","profile":"tech"},
  "mecklenburg-county-nc":{"name":"Mecklenburg County","state":"NC","county":"Mecklenburg County","zip":"28202","areas":["Charlotte","Huntersville","Matthews","Mint Hill","Pineville","Cornelius","Davidson"],"landmark1":"Bank of America Stadium","landmark2":"Spectrum Center","profile":"tech"},
  "multnomah-county-or":{"name":"Multnomah County","state":"OR","county":"Multnomah County","zip":"97204","areas":["Portland","Gresham","Troutdale","Fairview","Wood Village","Maywood Park","Northwest Portland"],"landmark1":"Providence Park","landmark2":"Moda Center","profile":"tech"},
  "salt-lake-county-ut":{"name":"Salt Lake County","state":"UT","county":"Salt Lake County","zip":"84101","areas":["Salt Lake City","West Valley City","Sandy","Murray","Taylorsville","Midvale","South Jordan"],"landmark1":"Rice-Eccles Stadium","landmark2":"Delta Center","profile":"tech"},
  "clark-county-nv":{"name":"Clark County","state":"NV","county":"Clark County","zip":"89101","areas":["Las Vegas","Henderson","North Las Vegas","Paradise","Summerlin","Enterprise","Boulder City"],"landmark1":"Allegiant Stadium","landmark2":"Las Vegas Convention Center","profile":"events"},
  "oklahoma-county-ok":{"name":"Oklahoma County","state":"OK","county":"Oklahoma County","zip":"73102","areas":["Oklahoma City","Edmond","Midwest City","Del City","The Village","Bethany","Nichols Hills"],"landmark1":"Paycom Center","landmark2":"Scissortail Park","profile":"oilgas"},
  "wayne-county-mi":{"name":"Wayne County","state":"MI","county":"Wayne County","zip":"48226","areas":["Detroit","Dearborn","Livonia","Westland","Taylor","Canton","Romulus"],"landmark1":"Ford Field","landmark2":"Little Caesars Arena","profile":"tech"},
  "marion-county-in":{"name":"Marion County","state":"IN","county":"Marion County","zip":"46204","areas":["Indianapolis","Lawrence","Warren Township","Pike Township","Perry Township","Decatur Township","Wayne Township"],"landmark1":"Lucas Oil Stadium","landmark2":"Gainbridge Fieldhouse","profile":"events"},
  "jefferson-county-ky":{"name":"Jefferson County","state":"KY","county":"Jefferson County","zip":"40202","areas":["Louisville","Jeffersontown","St. Matthews","Shively","Lyndon","Middletown","Fern Creek"],"landmark1":"Churchill Downs","landmark2":"KFC Yum! Center","profile":"events"},
  "douglas-county-ne":{"name":"Douglas County","state":"NE","county":"Douglas County","zip":"68102","areas":["Omaha","Bellevue","La Vista","Papillion","Ralston","Valley","Bennington"],"landmark1":"Charles Schwab Field","landmark2":"CHI Health Center","profile":"tech"},
  "fulton-county-ga":{"name":"Fulton County","state":"GA","county":"Fulton County","zip":"30303","areas":["Atlanta","Alpharetta","Roswell","Johns Creek","Sandy Springs","South Fulton","Milton"],"landmark1":"Mercedes-Benz Stadium","landmark2":"State Farm Arena","profile":"events"},
  "hamilton-county-tn":{"name":"Hamilton County","state":"TN","county":"Hamilton County","zip":"37402","areas":["Chattanooga","East Ridge","Signal Mountain","Lookout Mountain","Red Bank","Soddy-Daisy","Lakesite"],"landmark1":"Tennessee Aquarium","landmark2":"Lookout Mountain Battlefield","profile":"events"},
  "king-county-wa":{"name":"King County","state":"WA","county":"King County","zip":"98101","areas":["Seattle","Bellevue","Kent","Renton","Federal Way","Kirkland","Redmond"],"landmark1":"Lumen Field","landmark2":"T-Mobile Park","profile":"tech"},
  "nassau-county-ny":{"name":"Nassau County","state":"NY","county":"Nassau County","zip":"11530","areas":["Garden City","Hempstead","Mineola","Long Beach","Great Neck","Massapequa","Oceanside"],"landmark1":"UBS Arena","landmark2":"Hofstra University","profile":"suburban"},
  "huntington-ny":{"name":"Huntington","state":"NY","county":"Suffolk County","zip":"11743","areas":["Huntington Village","Centerport","Cold Spring Harbor","Northport","Lloyd Harbor","Melville","Amityville"],"landmark1":"Heckscher State Park","landmark2":"NYCB LIVE at Nassau Coliseum","profile":"suburban"},
}

# ─── DEFAULT DATA GENERATOR ────────────────────────────────────────────────
def default_city_data(slug):
    """Generate plausible city data for cities not in CITY_DB."""
    parts = slug.rsplit('-', 1)
    if len(parts) == 2 and parts[1].upper() in STATE_NAMES:
        state = parts[1].upper()
        city_slug = parts[0]
    else:
        # Could be a state page or county page
        return None
    city_name = city_slug.replace('-', ' ').title()
    state_name = STATE_NAMES.get(state, state)
    county = f"{city_name} County"

    # Default areas
    areas = [
        f"Downtown {city_name}", f"North {city_name}", f"South {city_name}",
        f"{city_name} Heights", f"{city_name} Park", f"East {city_name}",
        f"West {city_name}"
    ]
    landmark1 = f"{city_name} Convention Center"
    landmark2 = f"{city_name} Fairgrounds"

    # Profile heuristics
    oilgas_states = {"TX", "LA", "OK", "ND", "WY", "WV", "AK", "NM"}
    coastal_keywords = {"beach", "port", "harbor", "shore", "bay", "island", "gulf"}
    college_keywords = {"university", "college", "station", "campus"}
    tech_states = {"WA", "CA", "CO", "MA", "NC", "VA", "TX"}
    cap_cities = {"montgomery","juneau","phoenix","little rock","sacramento","denver",
                  "hartford","dover","tallahassee","atlanta","honolulu","boise",
                  "springfield","indianapolis","des moines","topeka","frankfort",
                  "baton rouge","augusta","annapolis","boston","lansing","saint paul",
                  "jackson","jefferson city","helena","lincoln","carson city",
                  "concord","trenton","santa fe","albany","raleigh","bismarck",
                  "columbus","oklahoma city","salem","harrisburg","providence",
                  "columbia","pierre","nashville","austin","salt lake city",
                  "montpelier","richmond","olympia","charleston","madison","cheyenne"}

    cn_lower = city_name.lower()
    sl_lower = city_slug.lower()

    if cn_lower in cap_cities:
        profile = "government"
    elif any(k in sl_lower for k in coastal_keywords):
        profile = "coastal"
    elif any(k in sl_lower for k in college_keywords):
        profile = "college"
    elif state in oilgas_states:
        profile = "oilgas"
    elif state in tech_states:
        profile = "tech"
    else:
        profile = "suburban"

    return {
        "name": city_name, "state": state, "county": county, "zip": "00000",
        "areas": areas, "landmark1": landmark1, "landmark2": landmark2,
        "profile": profile,
    }


def get_city_data(slug):
    if slug in CITY_DB:
        d = dict(CITY_DB[slug])
    else:
        d = default_city_data(slug)
        if d is None:
            return None
    d["state_name"] = STATE_NAMES.get(d["state"], d["state"])
    d["health_dept"] = STATE_HEALTH.get(d["state"], f"{d['state_name']} Department of Health")
    d["slug"] = slug
    d["areas"] = d.get("areas", [f"Downtown {d['name']}"])
    d["a1"] = d["areas"][0] if len(d["areas"]) > 0 else f"Downtown {d['name']}"
    d["a2"] = d["areas"][1] if len(d["areas"]) > 1 else f"North {d['name']}"
    d["a3"] = d["areas"][2] if len(d["areas"]) > 2 else f"South {d['name']}"
    d["a4"] = d["areas"][3] if len(d["areas"]) > 3 else f"{d['name']} Heights"
    d["a5"] = d["areas"][4] if len(d["areas"]) > 4 else f"East {d['name']}"
    return d


# ─── CONTENT TEMPLATES ─────────────────────────────────────────────────────
HERO_PARAGRAPHS = {
    "oilgas": "From Permian Basin drilling pads to {landmark1} industrial complexes and {a1} commercial builds, {city}'s energy sector demands portable sanitation that's OSHA-certified and ready for remote sites. We deliver same-day to {county} job sites — standard units, ADA, luxury trailers, and holding tanks. No forms, no call centers. Just results.",
    "events": "Planning an outdoor event in {city}? From intimate weddings near {a1} to multi-day festivals drawing thousands to {landmark1} and corporate gatherings throughout {county}, FixPilot provides clean, climate-ready portable restrooms and VIP luxury trailers. Same-day delivery available — call now and speak to a real local dispatcher.",
    "coastal": "From beachfront events near {landmark1} to marina construction across {county}, {city}'s coastal lifestyle demands reliable portable sanitation. Our weather-resistant units arrive sanitized and OSHA-ready — built for salt air, summer crowds, and {county} events. Same-day delivery to {a1}, {a2}, and all waterfront venues.",
    "college": "From game-day tailgates near {landmark1} to year-round campus construction and graduation ceremonies throughout {city}, {county} students, contractors, and event organizers trust FixPilot. Our units handle peak crowds, seasonal weather, and back-to-back events without missing a beat — same-day delivery available citywide.",
    "tech": "In {city}'s fast-growing innovation economy, construction timelines and corporate events don't wait. From tech campus builds near {a1} to outdoor employee events at {landmark1}, FixPilot delivers OSHA-compliant, hospital-grade portable sanitation across {county}. Same-day delivery and 24/7 emergency service included.",
    "suburban": "Whether you need porta potties for a home renovation in {a1}, a neighborhood HOA event in {county}, or a residential construction project near {landmark1}, FixPilot is {city}'s trusted local provider. Clean units, transparent pricing, and same-day delivery — no automated phone trees, just fast friendly local service.",
    "government": "From {landmark1} infrastructure projects to community events at {city} civic venues and military base operations throughout {county}, FixPilot provides portable sanitation that meets federal, state, and local compliance requirements. OSHA-certified, ADA-accessible, and always delivered on time — same-day service available.",
}

SERVICES_INTRO = {
    "oilgas": "From wellsite porta potties at remote {county} oil fields to large-scale construction on {a1} and {a2} industrial corridors, we carry the full range of portable sanitation equipment for {city}'s demanding energy and construction sectors. Every unit is OSHA-compliant and serviced on your schedule.",
    "events": "Every {city} event — from intimate {a1} weddings to multi-day {landmark1} festivals — deserves spotless, reliable restroom facilities. We cover it all: luxury restroom trailers for upscale affairs, standard units for large crowds, and ADA-compliant options ensuring no guest is left out at any venue across {county}.",
    "coastal": "From crowded summer beaches near {landmark1} to year-round marina events throughout {county}, we keep {city}'s coastal visitors comfortable and compliant. Salt air and high footfall don't faze our fleet — every unit is sanitized and delivered ready for demanding {city} conditions along {a1} and {a2}.",
    "college": "Whether it's serving tens of thousands at {landmark1} during game season or keeping {county} campus construction crews compliant, FixPilot handles {city}'s most demanding portable sanitation needs. Standard units, ADA-accessible porta potties, luxury trailers, and hand wash stations — all delivered same-day.",
    "tech": "Whether your {city} project is a sprawling tech campus construction in {a1}, a corporate off-site event near {landmark1}, or a residential development throughout {county}, we have the right portable sanitation solution. All units are hospital-grade clean, OSHA-certified, and delivered when and where you need them.",
    "suburban": "From routine {county} construction porta potties to luxury restroom trailers for {a1} weddings and neighborhood events in {city}, FixPilot brings the full spectrum of portable sanitation to your door. No job too small, no event too big — same-day delivery throughout {county} and beyond.",
    "government": "From large public works projects near {landmark1} to city-sponsored events and military facility compliance requirements throughout {county}, FixPilot provides portable sanitation that meets every specification. Our government-grade fleet is OSHA-certified, ADA-compliant, and available same-day across {city}.",
}

EXPERT_SECTIONS = {
    "oilgas": (
        "FixPilot Porta Potty Rentals has deep roots in {city} and {county}'s energy sector. "
        "We understand the round-the-clock demands of oil and gas operations, large-scale "
        "industrial construction, and remote worksites that standard rental companies won't serve. "
        "Our fleet is OSHA-certified and our drivers know the fastest routes to {a1}, {a2}, and "
        "job sites across the Permian Basin corridor and beyond."
        "\n\n"
        "Whether you're managing a 200-worker drilling operation, a pipeline corridor project, or "
        "a commercial build along {city}'s industrial belt, we tailor the unit count, service "
        "frequency, and delivery schedule to fit your project. Licensed, insured to $2M, and "
        "trusted by {county} contractors for over eight years."
        "\n\n"
        "Call (833) 652-9344 now — a real {city}-area dispatcher answers, not an automated system."
    ),
    "events": (
        "FixPilot Porta Potty Rentals is {city}'s go-to for clean, on-time portable sanitation "
        "for events of all sizes. From intimate backyard weddings in {a1} to multi-day festivals "
        "drawing tens of thousands near {landmark1}, our team understands event timelines, venue "
        "access restrictions, and the importance of spotless facilities for your guests."
        "\n\n"
        "Our luxury restroom trailers — equipped with climate control, running water, and premium "
        "finishes — have elevated events at {a2}, {a3}, and {county} venues that would otherwise "
        "struggle with permanent restroom capacity. We handle delivery, setup, daily servicing, "
        "and pickup so you can focus entirely on your event."
        "\n\n"
        "Call (833) 652-9344 for a same-day quote — we answer live, 24/7."
    ),
    "coastal": (
        "FixPilot Porta Potty Rentals knows {city}'s coastal environment inside and out. "
        "We've served beachfront events near {landmark1}, marina construction projects throughout "
        "{county}, and seasonal resort venues that need flexible, weather-resistant portable "
        "sanitation without the hassle of long rental contracts."
        "\n\n"
        "Our units are built to handle {city}'s heat, humidity, and salt air without degrading "
        "service quality. Whether you're setting up for a summer concert on {a1}, managing a "
        "waterfront development in {a2}, or responding to an emergency in {a3}, our fleet is "
        "ready and our drivers know every coastal road in {county}."
        "\n\n"
        "Call (833) 652-9344 any time — same-day delivery available throughout {county}."
    ),
    "college": (
        "FixPilot Porta Potty Rentals has served {city}'s university community, campus contractors, "
        "and surrounding {county} neighborhoods for years. We understand the surge demand of game "
        "weekends near {landmark1}, the steady pace of campus construction, and the back-to-back "
        "event calendar that makes {city} one of the most active sanitation markets in the region."
        "\n\n"
        "Our team coordinates with event staff, facilities managers, and construction supervisors "
        "to ensure units are placed, serviced, and removed on your schedule — not ours. From "
        "standard porta potties to climate-controlled luxury trailers for alumni events in {a1}, "
        "we have every option covered."
        "\n\n"
        "Call (833) 652-9344 — a real person answers, 24/7."
    ),
    "tech": (
        "FixPilot Porta Potty Rentals serves {city}'s innovation economy with the same precision "
        "and reliability that tech companies demand from every vendor. From corporate campus "
        "construction near {a1} to outdoor employee appreciation events at {landmark1}, our "
        "hospital-grade units and luxury restroom trailers meet the expectations of {county}'s "
        "most discerning clients."
        "\n\n"
        "We're OSHA-certified, ADA-compliant, and carry $2M in liability coverage — meeting the "
        "procurement requirements of Fortune 500 companies, government contractors, and major "
        "developers working throughout {city} and {county}."
        "\n\n"
        "Call (833) 652-9344 for same-day delivery and real-time dispatch updates."
    ),
    "suburban": (
        "FixPilot Porta Potty Rentals is {city}'s locally-trusted source for clean, affordable "
        "portable sanitation. Whether you're a homeowner renovating in {a1}, a contractor building "
        "in {county}'s growing subdivisions, or a neighborhood HOA hosting a community event near "
        "{landmark1} — we have the right unit at the right price."
        "\n\n"
        "Our team lives and works in {city}. We know the neighborhoods, the traffic patterns, "
        "and the fastest routes to your site. No hidden fees, no fuel surcharges — just transparent "
        "pricing and same-day delivery to {a1}, {a2}, {a3}, and all of {county}."
        "\n\n"
        "Call (833) 652-9344 — we pick up in under 15 seconds, 24/7."
    ),
    "government": (
        "FixPilot Porta Potty Rentals serves {city}'s government agencies, military installations, "
        "public works contractors, and civic event organizers with portable sanitation that meets "
        "federal, state, and local compliance standards. From {landmark1} projects to public "
        "events throughout {county}, our OSHA-certified, ADA-compliant fleet has the documentation "
        "and certifications your procurement team requires."
        "\n\n"
        "We understand government project timelines, site access requirements, and the importance "
        "of on-time delivery when permits and inspections are on the line. Our team coordinates "
        "directly with site supervisors at {a1}, {a2}, and {a3} to ensure seamless service."
        "\n\n"
        "Call (833) 652-9344 — live dispatch, same-day delivery, 24/7."
    ),
}

# ─── FAQ POOL ───────────────────────────────────────────────────────────────
FAQ_CORE = [
    {
        "q": "How quickly can you deliver a porta potty in {city}, {state}?",
        "a": "We offer same-day delivery throughout {city} and {county}. Orders placed before 10 AM typically arrive by early afternoon. For urgent needs in {a1} or {a2}, call (833) 652-9344 — we dispatch immediately, 24/7.",
        "id": "faq-delivery-speed"
    },
    {
        "q": "Do you service all neighborhoods in {city}?",
        "a": "Yes — we cover every neighborhood in {city} including {a1}, {a2}, {a3}, {a4}, {a5}, and all surrounding {county} communities. Call us for availability in your specific zip code.",
        "id": "faq-neighborhoods"
    },
    {
        "q": "Are your porta potties OSHA compliant for {state_name} construction sites?",
        "a": "Absolutely. All units meet OSHA 29 CFR 1926.51 requirements for construction sanitation in {state_name}. We provide the required worker-to-toilet ratios, maintain service frequency, and can supply OSHA compliance documentation for your {city} project.",
        "id": "faq-osha"
    },
    {
        "q": "How much does porta potty rental cost in {city}, {state}?",
        "a": "Standard units in {city} start from $75–100/day with weekly service included. Deluxe units run $100–150/day. Luxury restroom trailers for {county} events start at $400/day. Exact pricing depends on rental duration and service frequency. Call (833) 652-9344 for a free quote.",
        "id": "faq-cost"
    },
    {
        "q": "What makes FixPilot different from other {city} porta potty rental companies?",
        "a": "We're locally operated in {city} with drivers who know every route in {county}. Every unit is hospital-grade sanitized before delivery. We answer the phone live in under 15 seconds — no automated systems. Same-day delivery, transparent pricing with no hidden fuel surcharges, and $2M in liability coverage.",
        "id": "faq-difference"
    },
]

FAQ_CONSTRUCTION = [
    {
        "q": "How many porta potties does my {city} construction site need?",
        "a": "OSHA requires at least one toilet per 20 workers for an 8-hour shift. For a 40-worker {county} job site, that means at least 2 units — but we recommend 3 for comfort and productivity. Tell us your crew size and we'll calculate the right number for your {city} project.",
        "id": "faq-construction-count"
    },
    {
        "q": "Do you offer long-term construction rental agreements in {county}?",
        "a": "Yes — we offer weekly, monthly, and project-length rental agreements for {city} construction sites. Long-term contracts include priority delivery, scheduled weekly servicing, and dedicated account management. Ideal for multi-month builds in {a1} and throughout {county}.",
        "id": "faq-longterm"
    },
    {
        "q": "Can you deliver porta potties to high-rise or restricted-access sites in {city}?",
        "a": "Yes. Our drivers have experience navigating restricted-access construction sites across {city}, including downtown high-rise deliveries near {a1} and gated industrial facilities throughout {county}. We coordinate with your site supervisor for smooth, OSHA-compliant placement.",
        "id": "faq-highrise"
    },
    {
        "q": "Do you provide crane-hook porta potties for {city} high-rise projects?",
        "a": "Yes — we stock crane-attachable portable restrooms designed for upper-floor construction use. These units are essential for {city} high-rise projects where elevator access is restricted. Available with same-day delivery to job sites in {a1} and throughout {county}.",
        "id": "faq-crane-hook"
    },
    {
        "q": "How do I place a porta potty correctly on my {county} construction site?",
        "a": "OSHA requires units to be located no more than a one-minute walk from workers, on stable ground, in shaded areas when possible, and away from vehicle traffic. Our delivery team will work with your site manager to place units at optimal locations across your {city} job site.",
        "id": "faq-placement"
    },
    {
        "q": "Can you service construction porta potties on weekends in {city}?",
        "a": "Yes — we offer weekend and after-hours servicing for {county} construction sites that operate 6 or 7 days a week. Weekend service is available at no extra charge with our weekly service plan. Just let us know your schedule when you book.",
        "id": "faq-weekend-service"
    },
    {
        "q": "Do you rent hand wash stations for {city} construction crews?",
        "a": "Absolutely. OSHA also requires hand-washing facilities within 100 feet of restrooms on construction sites. We provide standalone hand wash stations and portable sinks for job sites across {city} and {county}. Often bundled with porta potty orders at a discounted rate.",
        "id": "faq-handwash-construction"
    },
]

FAQ_EVENTS = [
    {
        "q": "Do you offer luxury restroom trailers for {city} weddings and events?",
        "a": "Yes — our luxury restroom trailers are a top choice for weddings, galas, and corporate events across {city}. Each trailer features climate control (A/C and heat), flushing toilets, running water, granite countertops, and premium lighting. Perfect for outdoor venues near {a1} and {landmark1}.",
        "id": "faq-luxury-trailers"
    },
    {
        "q": "How many porta potties do I need for a 200-person event in {city}?",
        "a": "For a 4-hour event with 200 guests in {city}, we recommend at least 2 standard units or 1 luxury restroom trailer. If alcohol is being served, increase that to 3 units. For events at outdoor venues near {landmark1} or {a1}, we can advise on the exact setup for your crowd size and duration.",
        "id": "faq-event-count"
    },
    {
        "q": "Can you handle daily servicing during a multi-day {city} festival?",
        "a": "Yes — for festivals and multi-day events throughout {county}, we offer twice-daily or as-needed servicing. Our team restocks supplies, pumps waste, and cleans units between sessions so your guests always have a clean facility. We've handled multi-day events near {landmark1} and {landmark2}.",
        "id": "faq-festival-service"
    },
    {
        "q": "What's the best portable restroom option for an outdoor {city} wedding?",
        "a": "For {city} weddings, our luxury restroom trailers are the gold standard — they provide hotel-quality facilities for your guests. For more budget-conscious events in {county}, our deluxe porta potties offer interior lighting, larger tanks, and a cleaner feel than standard units. We'll recommend the right option for your {a1} venue.",
        "id": "faq-wedding-choice"
    },
    {
        "q": "Do you provide climate-controlled trailers for {city}'s hot summer events?",
        "a": "Yes — all our luxury restroom trailers include air conditioning, essential for outdoor summer events in {city}. We also provide heating for cooler-weather events throughout {county}. Climate control keeps your guests comfortable and reflects the quality of your event near {landmark1}.",
        "id": "faq-climate-control"
    },
    {
        "q": "Can you set up restroom trailers at outdoor venues near {landmark1}?",
        "a": "Yes — we regularly serve outdoor event venues near {landmark1}, {a1}, and throughout {county}. Our delivery team is experienced with venue access logistics, leveling the trailer on uneven terrain, and coordinating with your event coordinator for seamless setup and teardown.",
        "id": "faq-venue-delivery"
    },
]

FAQ_COLLEGE = [
    {
        "q": "Do you deliver porta potties for tailgates and game-day events near {landmark1}?",
        "a": "Yes — game-day tailgate setups near {landmark1} are one of our specialties in {city}. We deliver early, position units for maximum traffic flow, and provide same-day pickup after the event. Available for every home game throughout the {state_name} season.",
        "id": "faq-gameday"
    },
    {
        "q": "Can you service porta potties for campus construction projects in {city}?",
        "a": "Absolutely. Campus construction in {city} — whether at {landmark1} facilities, {a1} residence halls, or athletic complexes across {county} — requires OSHA-compliant portable restrooms. We offer weekly servicing and long-term contracts for multi-semester construction projects.",
        "id": "faq-campus-construction"
    },
    {
        "q": "Do you offer same-day rentals for last-minute {city} campus events?",
        "a": "Yes — we stock units specifically for same-day rentals to serve {city}'s busy event calendar. Whether it's an impromptu outdoor gathering near {landmark1} or a last-minute community event at {a1}, call (833) 652-9344 and we'll dispatch immediately.",
        "id": "faq-sameday-college"
    },
    {
        "q": "What portable restroom options are available for outdoor graduation ceremonies in {city}?",
        "a": "For graduation ceremonies in {city}, we recommend a mix of standard and ADA-compliant units for large student/family groups, plus luxury restroom trailers for VIP and faculty areas near {landmark1}. We coordinate early delivery and setup to avoid interfering with ceremony preparations.",
        "id": "faq-graduation"
    },
    {
        "q": "Can you provide portable restrooms for research facility and lab construction in {county}?",
        "a": "Yes — we serve specialized facility construction projects throughout {county} including research labs, medical buildings, and technical facilities associated with {city}'s university sector. Our OSHA-certified units come with proper documentation for institutional procurement.",
        "id": "faq-research-construction"
    },
]

FAQ_COASTAL = [
    {
        "q": "Do you deliver porta potties to beachfront events near {landmark1}?",
        "a": "Yes — beachfront and coastal event delivery near {landmark1} is a core part of our {city} service area. We use trucks equipped for sand and soft terrain, and our units are designed to handle {county}'s coastal weather. We serve beach events, marina gatherings, and waterfront construction throughout {county}.",
        "id": "faq-beachfront"
    },
    {
        "q": "Are your porta potties weather-resistant for {city}'s coastal climate?",
        "a": "Our units are built to withstand coastal conditions — salt air, humidity, intense sun, and occasional storm events. We use heavy-duty materials and perform extra inspections for units deployed in coastal {county} environments near {landmark1} and {a1}.",
        "id": "faq-coastal-weather"
    },
    {
        "q": "Can you provide porta potties for boat ramp and marina events in {county}?",
        "a": "Yes — we regularly serve marina events, fishing tournaments, and boat launches throughout {county}. Our delivery team is familiar with marina access points and can place units at optimal locations to serve both land and dock-side guests near {landmark1}.",
        "id": "faq-marina"
    },
    {
        "q": "Do you offer seasonal rental packages for {city}'s summer tourism season?",
        "a": "Yes — seasonal rentals are popular with {city} vacation rental properties, beach vendors, and event venues that need sanitation throughout the summer months. We offer flexible 30, 60, or 90-day coastal rentals with weekly servicing for properties throughout {county}.",
        "id": "faq-seasonal"
    },
    {
        "q": "Can you handle the surge demand during {city}'s peak visitor season?",
        "a": "Absolutely. We maintain a dedicated seasonal inventory for {city} and {county}'s peak tourism periods. Pre-booking is recommended for high-traffic dates near {landmark1} and {landmark2}. Call (833) 652-9344 to reserve units for your peak-season event.",
        "id": "faq-peak-season"
    },
]

FAQ_GOVERNMENT = [
    {
        "q": "Can you service {landmark1} construction and infrastructure projects in {city}?",
        "a": "Yes — we regularly serve government infrastructure projects in {city} including projects near {landmark1} and throughout {county}. We provide OSHA-certified units, ADA-compliant options, and full compliance documentation required for government contracts.",
        "id": "faq-gov-projects"
    },
    {
        "q": "Do your units meet government procurement compliance requirements?",
        "a": "Yes — FixPilot carries $2M in general liability coverage, is OSHA-certified, and maintains ADA/ANSI compliance documentation. We can provide certificates of insurance and service agreements formatted for {city} and {county} government procurement requirements.",
        "id": "faq-gov-compliance"
    },
    {
        "q": "Do you serve military base facilities and DOD contractors in {county}?",
        "a": "Yes — we serve DOD contractors, base facility managers, and military construction projects in {county}. We understand base access requirements near {landmark1} and can coordinate with your contracting officer for proper scheduling and documentation.",
        "id": "faq-military"
    },
    {
        "q": "Can you provide porta potties for {city} public events and civic gatherings?",
        "a": "Yes — we're a regular vendor for public events across {city} including festivals, parades, and civic gatherings near {landmark1} and throughout {county}. We offer volume pricing for government-sponsored events and can scale quickly for large outdoor gatherings.",
        "id": "faq-civic-events"
    },
]

FAQ_SUBURBAN = [
    {
        "q": "Can I rent a porta potty for a home renovation in {city}?",
        "a": "Yes — homeowner rentals are one of our most common requests in {city}. A single standard porta potty keeps your interior bathrooms clean during remodels, additions, and landscaping projects. We deliver to {a1}, {a2}, and all residential neighborhoods throughout {county}. Minimum rental is typically one week.",
        "id": "faq-home-reno"
    },
    {
        "q": "Do I need a permit to place a porta potty at my {city} property?",
        "a": "For private property in {city}, no permit is usually required. If you need a unit on a public street or sidewalk, you may need a right-of-way permit from {city} or {county}. We can advise on local requirements and help you understand placement restrictions for your neighborhood.",
        "id": "faq-permit"
    },
    {
        "q": "What's the minimum rental period for a porta potty in {city}?",
        "a": "Our standard minimum is one week in {city}, which covers most home projects and short-term events. We also offer single-day rentals for events like neighborhood parties, HOA gatherings, and one-day work crews across {county}. Call for same-day availability.",
        "id": "faq-min-rental"
    },
    {
        "q": "Can I extend my rental period if my {city} project takes longer than expected?",
        "a": "Absolutely — just call or text us and we'll extend your rental with no hassle. There's no penalty for extensions in {city} or {county}. Our service team will continue weekly servicing and you'll be billed at the same daily rate for the additional time.",
        "id": "faq-extension"
    },
]

FAQ_SPECIALTY = [
    {
        "q": "Do you provide ADA-compliant wheelchair-accessible portable toilets in {city}?",
        "a": "Yes — our ADA-compliant units feature extra floor space (60\" × 60\" minimum), grab bars, lower toilet height, non-slip flooring, and door widths that accommodate wheelchairs. Required for all public events and permitted construction sites in {city} under the Americans with Disabilities Act.",
        "id": "faq-ada"
    },
    {
        "q": "Do you offer flushable portable toilets for upscale events in {city}?",
        "a": "Yes — our flushable porta potties use a recirculating flush mechanism and fresh water for a much more comfortable experience than standard units. They're popular at weddings, corporate events, and premium outdoor venues in {a1} and throughout {county}.",
        "id": "faq-flushable"
    },
    {
        "q": "Do you provide standalone hand wash stations in {city}?",
        "a": "Yes — we offer portable hand wash stations with fresh-water tanks, soap dispensers, and waste containers. They pair perfectly with porta potties at {city} events and are required by OSHA on most construction sites. Available as add-ons to any porta potty rental in {county}.",
        "id": "faq-handwash"
    },
    {
        "q": "Can you provide portable septic pump-out services in {county}?",
        "a": "Yes — we offer holding tank pump-outs and portable septic services for long-term construction sites and properties throughout {county}. Available as a standalone service or combined with porta potty rental. Call (833) 652-9344 for scheduling and pricing in the {city} area.",
        "id": "faq-septic"
    },
    {
        "q": "Do you offer VIP luxury restroom trailers with premium amenities?",
        "a": "Yes — our VIP trailers feature marble countertops, LED vanity lighting, climate control, stainless fixtures, and dedicated men's and women's sides. They're the premium choice for {city} galas, upscale weddings, and corporate events near {landmark1} and throughout {county}.",
        "id": "faq-vip"
    },
]

FAQ_EMERGENCY = [
    {
        "q": "What if I need emergency porta potty delivery in {city} after hours?",
        "a": "Call (833) 652-9344 any time — we operate 24/7 emergency dispatch for {city} and {county}. Whether it's a construction site emergency, a broken facility at an event, or an unexpected project start, we'll get units to you as quickly as possible. Same-night and early-morning delivery available.",
        "id": "faq-emergency"
    },
    {
        "q": "Can I get same-day porta potty delivery in {city} without advance notice?",
        "a": "Yes — same-day delivery is available throughout {city} and most of {county} for orders placed before 2 PM. For late-afternoon or weekend requests, call (833) 652-9344 directly and we'll confirm availability and the earliest delivery window for your {city} location.",
        "id": "faq-sameday"
    },
]

# ─── FAQ COMBINATION LOGIC ─────────────────────────────────────────────────
PROFILE_FAQ_PLAN = {
    "oilgas":    {"core": FAQ_CORE, "extra": FAQ_CONSTRUCTION[:5], "specialty": FAQ_SPECIALTY[:2], "emergency": FAQ_EMERGENCY},
    "events":    {"core": FAQ_CORE, "extra": FAQ_EVENTS[:5],       "specialty": FAQ_SPECIALTY[1:3], "emergency": FAQ_EMERGENCY},
    "coastal":   {"core": FAQ_CORE, "extra": FAQ_COASTAL[:4],      "specialty": FAQ_SPECIALTY[:2], "emergency": FAQ_EMERGENCY},
    "college":   {"core": FAQ_CORE, "extra": FAQ_COLLEGE[:4],      "specialty": FAQ_SPECIALTY[:3], "emergency": FAQ_EMERGENCY},
    "tech":      {"core": FAQ_CORE, "extra": FAQ_CONSTRUCTION[:3] + FAQ_EVENTS[:2], "specialty": FAQ_SPECIALTY[:2], "emergency": FAQ_EMERGENCY},
    "suburban":  {"core": FAQ_CORE, "extra": FAQ_SUBURBAN[:4],     "specialty": FAQ_SPECIALTY[:3], "emergency": FAQ_EMERGENCY},
    "government":{"core": FAQ_CORE, "extra": FAQ_GOVERNMENT[:4],   "specialty": FAQ_SPECIALTY[:2], "emergency": FAQ_EMERGENCY},
}


def build_faq_list(city, profile):
    plan = PROFILE_FAQ_PLAN.get(profile, PROFILE_FAQ_PLAN["suburban"])
    faqs = plan["core"] + plan["extra"] + plan["specialty"] + plan["emergency"]
    # Use city hash to slightly reorder the extra questions (keeps it deterministic)
    h = int(hashlib.md5(city["slug"].encode()).hexdigest(), 16)
    extra = list(plan["extra"])
    if len(extra) > 3:
        idx = h % len(extra)
        extra = extra[idx:] + extra[:idx]
    faqs = plan["core"] + extra + plan["specialty"] + plan["emergency"]
    return faqs


def fmt(template, c):
    """Fill city variables into a template string."""
    return (template
        .replace("{city}", c["name"])
        .replace("{state}", c["state"])
        .replace("{state_name}", c["state_name"])
        .replace("{county}", c["county"])
        .replace("{a1}", c["a1"])
        .replace("{a2}", c["a2"])
        .replace("{a3}", c["a3"])
        .replace("{a4}", c["a4"])
        .replace("{a5}", c["a5"])
        .replace("{landmark1}", c["landmark1"])
        .replace("{landmark2}", c["landmark2"])
        .replace("{health_dept}", c["health_dept"])
    )


# ─── HTML BUILDERS ──────────────────────────────────────────────────────────
def build_faq_schema(city, faqs):
    slug = city["slug"]
    entries = []
    for fq in faqs:
        q = fmt(fq["q"], city)
        a = fmt(fq["a"], city)
        fid = fq["id"]
        entry = (
            '        {\n'
            '          "@type": "Question",\n'
            f'          "@id": "https://fixpilotportapottyrentals.com/porta-potty-rental-{slug}/#{fid}",\n'
            f'          "name": {json.dumps(q)},\n'
            '          "acceptedAnswer": {\n'
            '            "@type": "Answer",\n'
            f'            "text": {json.dumps(a)}\n'
            '          }\n'
            '        }'
        )
        entries.append(entry)
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


def build_faq_html(city, faqs):
    slug = city["slug"]
    items_html = ""
    for i, fq in enumerate(faqs, 1):
        q = fmt(fq["q"], city)
        a = fmt(fq["a"], city)
        fid = fq["id"]
        items_html += (
            f'\n                <div id="{fid}" class="border border-gray-100 rounded-xl p-6 shadow-sm">\n'
            f'                    <h3 class="font-semibold text-lg text-gray-800 mb-2">{i}. {q}</h3>\n'
            f'                    <p class="text-gray-600 text-sm">{a}</p>\n'
            f'                </div>'
        )
    return (
        f'    <section id="faq" class="py-20 bg-white">\n'
        f'        <div class="container mx-auto px-4">\n'
        f'            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 text-center">{city["name"]} Porta Potty Rental FAQs</h2>\n'
        f'            <p class="text-gray-600 max-w-2xl mx-auto text-lg text-center mb-12">Your top questions answered. Don\'t see yours? Call our team at (833) 652-9344!</p>\n'
        f'            <div class="space-y-6 max-w-4xl mx-auto">'
        f'{items_html}\n'
        f'            </div>\n'
        f'        </div>\n'
        f'    </section>'
    )


def build_hero_para(city):
    tpl = HERO_PARAGRAPHS.get(city["profile"], HERO_PARAGRAPHS["suburban"])
    return fmt(tpl, city)


def build_services_intro(city):
    tpl = SERVICES_INTRO.get(city["profile"], SERVICES_INTRO["suburban"])
    return fmt(tpl, city)


def build_expert_section(city):
    tpl = EXPERT_SECTIONS.get(city["profile"], EXPERT_SECTIONS["suburban"])
    return fmt(tpl, city)


# ─── PAGE PATCHER ───────────────────────────────────────────────────────────
def patch_page(html, city):
    faqs = build_faq_list(city, city["profile"])

    # 1. Replace FAQPage schema block
    new_faq_schema = build_faq_schema(city, faqs)
    _faq_schema = new_faq_schema  # captured in closure
    html = re.sub(
        r'<script type="application/ld\+json">\s*\{\s*"@context"\s*:\s*"https://schema\.org",\s*"@type"\s*:\s*"FAQPage".*?</script>',
        lambda m: _faq_schema,
        html, flags=re.DOTALL
    )

    # 2. Replace FAQ HTML section
    new_faq_html = build_faq_html(city, faqs)
    _faq_html = new_faq_html
    html = re.sub(
        r'<section id="faq"[^>]*>.*?</section>',
        lambda m: _faq_html,
        html, flags=re.DOTALL
    )

    # 3. Fix wrong-state name references (e.g. Houston saying "GA")
    # Ensure state_name and state abbreviation are correct throughout
    # (only replace if current page has wrong state embedded, detected by looking for
    #  another state's full name in key places)
    wrong_states = [sn for sn in STATE_NAMES.values() if sn != city["state_name"]]
    # Only fix hero description paragraph and h2 headings, not schema/general text
    hero_para_new = build_hero_para(city)

    # 4. Replace hero description paragraph (the <p> right after the h1)
    hero_para_pattern = r'(<h1[^>]*>.*?</h1>\s*)(.*?)(<div class="flex flex-wrap gap-4)'
    def replace_hero(m):
        return m.group(1) + (
            f'<p class="text-lg md:text-xl text-gray-50 mb-8 max-w-xl">{hero_para_new}</p>\n                '
        ) + m.group(3)
    html_new = re.sub(hero_para_pattern, replace_hero, html, flags=re.DOTALL, count=1)
    if html_new != html:
        html = html_new

    # 5. Replace services-section intro paragraph
    services_intro_new = build_services_intro(city)
    services_p_pattern = (
        r'(<h2[^>]*>Complete Portable Sanitation Services in[^<]*</h2>\s*)'
        r'<p[^>]*>.*?</p>'
    )
    def replace_services_intro(m):
        return m.group(1) + f'<p class="text-gray-600 mb-12 leading-relaxed max-w-3xl mx-auto text-center">{services_intro_new}</p>'
    html_new = re.sub(services_p_pattern, replace_services_intro, html, flags=re.DOTALL, count=1)
    if html_new != html:
        html = html_new

    # 6. Replace "Your [City] Porta Potty Rental Experts" prose section
    expert_new = build_expert_section(city)
    expert_paras = ''.join(f'<p>{p.strip()}</p>\n' for p in expert_new.split('\n\n') if p.strip())
    expert_section_pattern = (
        r'(<div class="prose prose-lg mx-auto text-gray-600">)\s*'
        r'(<p>.*?</p>\s*)*'
        r'(</div>)'
    )
    def replace_expert(m):
        return m.group(1) + '\n' + expert_paras + m.group(3)
    html_new = re.sub(expert_section_pattern, replace_expert, html, flags=re.DOTALL, count=1)
    if html_new != html:
        html = html_new

    # 6b. Replace the "Proudly Serving" city description paragraph
    # This still contains Atlanta template text (Inman Park, BeltLine, Mercedes-Benz Stadium etc.)
    city_desc_new = build_city_serving_paragraph(city)
    _cd = city_desc_new
    html = re.sub(
        r'(<h2[^>]*>Proudly Serving[^<]*</h2>\s*<p[^>]*>).*?(</p>)',
        lambda m: m.group(1) + _cd + m.group(2),
        html, flags=re.DOTALL, count=1
    )

    # 6c. Replace blog article teaser paragraphs with city-specific teasers
    html = replace_blog_teasers(html, city)

    # 6d. Rebuild areas section with city-specific neighborhoods and zip codes
    html = rebuild_areas_section(html, city)

    # 7. Replace testimonials (schema reviews) — same 4 names appear on every page
    _reviews = build_reviews(city)
    _reviews_str = _reviews
    html = re.sub(
        r'"review"\s*:\s*\[.*?\]\s*,\s*\n\s*"makesOffer"',
        lambda m: f'"review": {_reviews_str},\n      "makesOffer"',
        html, flags=re.DOTALL
    )

    # 8. Replace visible testimonial cards HTML
    _testimonial_html = build_testimonial_html(city)
    _th = _testimonial_html
    html = re.sub(
        r'(<h2[^>]*>What [^<]+ Customers Are Saying</h2>.*?<div class="grid[^>]+">)(.*?)(</div>\s*</div>\s*</section>)',
        lambda m: m.group(1) + _th + m.group(3),
        html, flags=re.DOTALL, count=1
    )

    # 9. Replace service card descriptions with city-specific variants
    html = replace_service_descriptions(html, city)

    # 9b. Rebuild related-cities section with same-state cities
    html = rebuild_related_cities(html, city)

    # 10. Fix wrong state code COMPREHENSIVELY throughout the page
    correct_state = city["state"]
    correct_state_name = city["state_name"]
    city_name = city["name"]

    for st_code, st_name in STATE_NAMES.items():
        if st_code == correct_state:
            continue
        # Fix "CityName, XX" patterns (schema, meta, display text)
        html = html.replace(f'{city_name}, {st_code}', f'{city_name}, {correct_state}')
        html = html.replace(f'{city_name}+{st_code}', f'{city_name}+{correct_state}')
        html = html.replace(f'{city_name.replace(" ", "+")}+{st_code}', f'{city_name.replace(" ", "+")}+{correct_state}')
        # Fix "in GA" state-specific breadcrumb text
        html = html.replace(f'in {st_name}<', f'in {correct_state_name}<')
        html = html.replace(f'in {st_name},', f'in {correct_state_name},')

    # Fix wrong zip codes appearing in schema address — if we know the correct zip
    if city.get("zip") and city["zip"] != "00000":
        # Replace the old Atlanta zip (30336) or any other wrong zip in the schema address block
        html = re.sub(
            r'("addressRegion"\s*:\s*"[A-Z]{2}"\s*,\s*"postalCode"\s*:\s*")[^"]+(")',
            lambda m: m.group(1) + city["zip"] + m.group(2),
            html
        )

    # Fix "Other Cities We Serve in [WrongState]" section header
    for st_code, st_name in STATE_NAMES.items():
        if st_code == correct_state:
            continue
        html = html.replace(
            f'Other Cities We Serve in {st_name}',
            f'Other Cities We Serve in {correct_state_name}'
        )
        html = html.replace(
            f'Other Cities We Serve in {st_code}',
            f'Other Cities We Serve in {correct_state}'
        )

    # Fix wrong state codes in related cities section text (the visible link descriptions)
    # e.g. "Porta Potty Rental in Sugar Land, GA" → "Porta Potty Rental in Sugar Land, TX"
    def fix_related_states(m):
        text = m.group(0)
        for st_code in STATE_NAMES.keys():
            if st_code == correct_state:
                continue
            text = text.replace(f', {st_code}"', f', {correct_state}"')
            text = text.replace(f', {st_code}<', f', {correct_state}<')
        return text

    html = re.sub(
        r'<section id="related-cities".*?</section>',
        fix_related_states,
        html, flags=re.DOTALL
    )

    return html


# ─── TESTIMONIAL BUILDERS ────────────────────────────────────────────────────

# Reviewer name pools by profile
REVIEWER_POOLS = {
    "oilgas": [
        ("Randy T.", "Operations Mgr", "Harris County", "Permian Basin"),
        ("Cody W.", "Site Superintendent", "South {city}", "oil patch"),
        ("Maria S.", "Project Coordinator", "{a1}", "industrial build"),
        ("Jake B.", "Field Supervisor", "{county}", "energy corridor"),
    ],
    "events": [
        ("Brittany L.", "Event Planner", "{a1}", "outdoor wedding"),
        ("Marcus J.", "Festival Director", "{landmark1} area", "3-day festival"),
        ("Sophie K.", "Corporate Events Mgr", "{a2}", "company picnic"),
        ("Derek H.", "Wedding Coordinator", "{county}", "venue event"),
    ],
    "coastal": [
        ("Tanner P.", "Beach Event Organizer", "{landmark1}", "beach concert"),
        ("Alicia M.", "Marina Manager", "{a1}", "boating tournament"),
        ("Ryan C.", "Resort Activities Dir", "{a2}", "pool party"),
        ("Wendy S.", "Venue Owner", "{county}", "waterfront wedding"),
    ],
    "college": [
        ("Tyler B.", "Tailgate Organizer", "{landmark1}", "game day"),
        ("Ashley R.", "Campus Facilities Mgr", "{a1}", "graduation ceremony"),
        ("Nathan F.", "Greek Life Director", "{a2}", "outdoor event"),
        ("Jordan M.", "Athletic Dept Coord", "{county}", "campus construction"),
    ],
    "tech": [
        ("Priya S.", "Facilities Manager", "{a1} Tech Campus", "campus renovation"),
        ("Eric L.", "Corporate Event Planner", "{landmark1} area", "outdoor summit"),
        ("Megan C.", "Construction PM", "{a2}", "office complex build"),
        ("Sam D.", "Operations Director", "{county}", "data center construction"),
    ],
    "suburban": [
        ("Karen L.", "Homeowner", "{a1}", "kitchen remodel"),
        ("Bob T.", "General Contractor", "{a2}", "subdivision build"),
        ("Lisa M.", "HOA Board Member", "{landmark1} area", "community event"),
        ("Dave R.", "Project Manager", "{county}", "commercial renovation"),
    ],
    "government": [
        ("Col. James H. (Ret.)", "Facilities Coord", "{landmark1}", "base maintenance"),
        ("Patricia W.", "City Project Mgr", "Downtown {city}", "public works project"),
        ("Frank O.", "DOD Contractor", "{a1}", "government construction"),
        ("Sandra K.", "Public Events Dir", "{county}", "civic festival"),
    ],
}

REVIEW_QUOTES = {
    "oilgas": [
        "Been using FixPilot for our {county} drilling operations for two years running. They understand oil patch logistics — units arrive on schedule, serviced weekly without reminder, and driver knows every dirt road out to our pad sites. Best in the business.",
        "Needed 12 units fast for an emergency job start near {landmark1}. Called at 7 AM, units were on site by noon. Pricing was straight with no fuel surcharges added after the fact. Will use them for every {city} project going forward.",
        "Our {a1} industrial build ran 6 months longer than planned. FixPilot extended our contract without any hassle and kept servicing on time the whole way. The crew supervisor told me it was the cleanest job site porta potties he'd seen in 20 years.",
        "FixPilot handles our {county} oilfield porta potties better than any vendor we've tried. They actually pick up the phone at 5 AM when we have an emergency situation at a remote site. That responsiveness is everything in this industry.",
    ],
    "events": [
        "Rented two luxury restroom trailers for our wedding near {landmark1}. The crew arrived two hours early, setup was flawless, and our guests kept commenting on how nice the facilities were. Worth every penny for {city} outdoor events.",
        "Coordinated a 2,000-person festival in {a1} and FixPilot handled the full sanitation package — 18 standard units, 4 ADA accessible, daily servicing. Not a single complaint from attendees over 3 days. They're the only vendor I'll use in {county}.",
        "Called at 10 PM Friday night when our original vendor canceled for a {city} corporate event. FixPilot had luxury trailers on-site by 8 AM Saturday morning. Saved the event. Customer service is exceptional.",
        "Been using FixPilot for our annual {landmark1} area fundraiser for four years. Consistent, clean, and professional every time. They know our event setup requirements by now and execute without needing hand-holding.",
    ],
    "coastal": [
        "Organized a beach concert near {landmark1} with 800 attendees. FixPilot delivered units to the sand without any drama, serviced twice daily, and had everything removed by Sunday morning. Perfect operation for a coastal {county} venue.",
        "Our marina on {a1} hosts fishing tournaments all summer. FixPilot has been our portable sanitation partner for three seasons — they know the waterfront access quirks and never miss a service day. Highly recommend for any coastal {city} event.",
        "Needed 6 units for our beachfront wedding in {county}. FixPilot sent a luxury trailer that fit perfectly in our venue setup. Guests were genuinely impressed. On-time delivery and early morning pickup made the whole weekend stress-free.",
        "Running a food truck park near {landmark1} all summer. FixPilot keeps our hand wash stations and porta potties clean and stocked through the busy {city} tourist season. Fair pricing and reliable service keeps us coming back.",
    ],
    "college": [
        "Organized tailgate for 400 fans near {landmark1} three weekends in a row. FixPilot had units in place by 8 AM each game day and picked up by evening. Efficient, clean, and they know the campus access routes perfectly.",
        "Managing renovation of our {a1} residence hall. FixPilot handles OSHA-compliant porta potties for our 80-person crew — weekly service, ADA units, the whole setup. They've kept us compliant through two semesters of construction.",
        "Used FixPilot for our {city} graduation ceremony — 1,200 graduates and families at an outdoor venue near {landmark1}. They recommended the right mix of standard and ADA units, and not a single line complaint from guests. Impressive coordination.",
        "Greek Week outdoor events can be chaotic to plan, but FixPilot in {city} makes the sanitation part easy. They give us a quote in minutes, show up when they say they will, and units are genuinely spotless. Our chapter uses them every semester.",
    ],
    "tech": [
        "Managing construction of our {a1} expansion — 6-month project with 120 workers on site. FixPilot's weekly servicing is flawless, OSHA documentation was ready on day one, and when we needed 3 extra units on short notice they delivered same day.",
        "Corporate outdoor summit near {landmark1} for 300 employees. Requested luxury restroom trailers with branding signage area — FixPilot accommodated every request and the units reflected the quality of our company event in {city}.",
        "Our {county} data center build required porta potties at a secure facility. FixPilot handled the access badge requirements, kept units serviced on schedule, and never caused a delay for our crew. Exactly what you need from a vendor on a complex build.",
        "Used FixPilot for three separate {city} office construction projects this year. Consistent quality each time — OSHA-compliant units, on-time weekly service, and a driver who actually knows the campus layout. Will be using them for all future builds.",
    ],
    "suburban": [
        "Rented a single porta potty for our kitchen and bathroom remodel in {a1}. Saved our household a ton of hassle and kept the construction crew out of our personal space. FixPilot was affordable, delivered same day, and picked it up right on time.",
        "Building a new home in {a2} with a 90-day timeline. FixPilot set up 2 units for our crew, serviced weekly without reminder, and the pricing was the most competitive I found in {county}. No hidden fees is a big deal when you're watching a budget.",
        "Organized our neighborhood's annual block party near {landmark1}. FixPilot dropped off 3 units the morning of the event and retrieved them by evening. Easy process and the units were cleaner than anything our block had used before.",
        "I've used FixPilot for four consecutive commercial renovation projects in {city}. Their reliability is what keeps me coming back — they show up when they say, service on schedule, and I've never had a tenant complaint about their units at any of my buildings.",
    ],
    "government": [
        "Coordinating infrastructure work near {landmark1}. FixPilot had all the insurance certificates and OSHA documentation ready before the project even started. Units stayed serviced on schedule throughout the {county} project. Smooth operation.",
        "Public works project at {a1} required ADA-compliant units with documentation. FixPilot delivered the compliance paperwork within 24 hours of request and kept units serviced through our 4-month timeline. Exactly what government contractors need.",
        "Contracted FixPilot for a civic festival near {landmark1} with 1,500 attendees. They handled permitting guidance, placement logistics, and daily servicing without any direction from our team. Professional operation from start to finish.",
        "Managing a DOD facility renovation in {county}. FixPilot accommodated our base access procedures, delivered OSHA-certified units with documentation, and never caused a schedule delay. They understand government project requirements.",
    ],
}


def build_reviews(city):
    """Build unique reviews JSON array for a city."""
    pool = REVIEWER_POOLS.get(city["profile"], REVIEWER_POOLS["suburban"])
    quotes = REVIEW_QUOTES.get(city["profile"], REVIEW_QUOTES["suburban"])
    import hashlib
    h = int(hashlib.md5(city["slug"].encode()).hexdigest(), 16)

    reviews = []
    dates = ["2026-04-10", "2026-03-28", "2026-03-15", "2026-02-22"]
    for i, (reviewer, role, location, context) in enumerate(pool):
        name_filled = (reviewer.replace("{city}", city["name"])
                                .replace("{county}", city["county"])
                                .replace("{a1}", city["a1"])
                                .replace("{a2}", city["a2"]))
        location_filled = (location.replace("{city}", city["name"])
                                   .replace("{county}", city["county"])
                                   .replace("{landmark1}", city["landmark1"])
                                   .replace("{a1}", city["a1"])
                                   .replace("{a2}", city["a2"]))
        quote_idx = (h + i) % len(quotes)
        quote = fmt(quotes[quote_idx], city)
        entry = {
            "@type": "Review",
            "author": {"@type": "Person", "name": f"{name_filled}, {location_filled}"},
            "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
            "datePublished": dates[i % len(dates)],
            "reviewBody": quote
        }
        reviews.append(entry)

    import json as _json
    return _json.dumps(reviews, indent=2)


def build_testimonial_html(city):
    """Build the 3 visible testimonial cards."""
    pool = REVIEWER_POOLS.get(city["profile"], REVIEWER_POOLS["suburban"])
    quotes = REVIEW_QUOTES.get(city["profile"], REVIEW_QUOTES["suburban"])
    import hashlib
    h = int(hashlib.md5(city["slug"].encode()).hexdigest(), 16)

    cards_html = ""
    for i in range(3):
        reviewer, role, location, context = pool[i % len(pool)]
        name = reviewer.split(',')[0].split('.')[0].strip()
        initial = name[0]
        name_filled = (reviewer.replace("{city}", city["name"])
                                .replace("{county}", city["county"])
                                .replace("{a1}", city["a1"])
                                .replace("{a2}", city["a2"]))
        location_filled = (location.replace("{city}", city["name"])
                                   .replace("{county}", city["county"])
                                   .replace("{landmark1}", city["landmark1"])
                                   .replace("{a1}", city["a1"])
                                   .replace("{a2}", city["a2"]))
        quote_idx = (h + i) % len(quotes)
        quote = fmt(quotes[quote_idx], city)
        # Trim quote to 2 sentences for display
        sentences = re.split(r'(?<=[.!?])\s+', quote)
        display_quote = ' '.join(sentences[:2]) if len(sentences) > 1 else quote

        cards_html += f'''
                <div class="bg-gray-50 p-6 rounded-2xl shadow-md hover:shadow-lg transition">
                    <div class="flex items-center gap-4 mb-4">
                        <div class="w-12 h-12 bg-brand-500 text-white rounded-full flex items-center justify-center font-bold text-lg">{initial}</div>
                        <div class="text-left">
                            <p class="font-semibold text-gray-800">{name_filled}</p>
                            <div class="flex text-yellow-400 mt-1">★★★★★</div>
                        </div>
                    </div>
                    <p class="text-gray-600 text-sm">"{display_quote}"</p>
                </div>'''
    return cards_html


def build_city_serving_paragraph(city):
    """Unique 'Proudly Serving' paragraph using city-specific data — no Atlanta text."""
    c = city
    VARIANTS = [
        "{city} is a vibrant {county} community where construction activity, live events, and neighborhood growth create year-round demand for reliable portable sanitation. From the commercial corridors near {landmark1} to the residential neighborhoods of {a1}, {a2}, and {a3}, every part of {city} has a reason to call FixPilot — whether it's a job site, a backyard event, or an emergency backup near {landmark2}.",
        "The diversity of {city}'s neighborhoods, industries, and event venues makes {county} one of the most active portable sanitation markets in {state_name}. Whether you're managing a construction project near {landmark1}, hosting a gathering in {a1}, or organizing a community event near {landmark2}, {county} residents and contractors count on FixPilot for clean, reliable, same-day service throughout {a2}, {a3}, and the surrounding area.",
        "{city} stretches across {county} with neighborhoods ranging from the urban energy of {a1} and {a2} to the quieter communities of {a3} and {a4}. Wherever you are in {county}, FixPilot delivers — to active construction zones near {landmark1}, to event venues at {landmark2}, to homeowners in {a5} managing a remodel or outdoor project. One call, one direct dispatcher, same-day service.",
        "Serving {city} means knowing every corner of {county} — from the high-traffic corridors near {landmark1} to the neighborhood streets of {a1}, {a2}, and {a3}. FixPilot has built its {county} operation around reliable, on-time delivery to all of {city}'s neighborhoods, including the communities surrounding {landmark2} that other vendors treat as edge-of-service-area afterthoughts.",
    ]
    idx = int(__import__('hashlib').md5(f"{c['slug']}:serving".encode()).hexdigest(), 16) % len(VARIANTS)
    return fmt(VARIANTS[idx], c)


def replace_blog_teasers(html, city):
    """Replace blog article teaser paragraphs with city-profile-specific teasers."""
    c = city
    TEASERS = {
        "oilgas": [
            (f"Planning a {c['county']} job site? Here's how to calculate the right number of portable toilets for your crew size, shift schedule, and {c['state_name']} OSHA requirements.",
             f"OSHA Requirements for Construction Sites in {c['state_name']}",
             f"{c['state_name']} job site sanitation rules, ratio requirements, and compliance tips for {c['county']} contractors."),
            (f"Oil field, pipeline, and industrial jobs in {c['county']} have unique portable sanitation requirements. Here's what remote site operations need to stay OSHA-compliant near {c['landmark1']}.",
             f"Industrial Site Porta Potty Guide for {c['name']}",
             f"Remote access, holding tanks, and field servicing for {c['county']} energy operations."),
            (f"From {c['a1']} commercial builds to {c['county']} residential subdivisions — here's what {c['state_name']} contractors need to budget for portable sanitation in 2026.",
             f"2026 Construction Sanitation Costs in {c['name']}, {c['state']}",
             f"What {c['county']} contractors pay for porta potties, service schedules, and compliance."),
        ],
        "events": [
            (f"Outdoor weddings at {c['landmark1']} and throughout {c['county']} need the right restroom setup. Learn which units fit your venue, guest count, and budget in {c['name']}.",
             f"Planning an Outdoor Wedding in {c['name']}? Restroom Guide",
             f"Luxury trailers vs. deluxe porta potties for {c['county']} wedding venues."),
            (f"Hosting a festival or concert near {c['landmark1']} in {c['county']}? Use our guide to calculate the right number of units based on attendance, duration, and alcohol service.",
             f"How Many Porta Potties for {c['name']} Events?",
             f"The formula for sizing sanitation at {c['county']} festivals, concerts, and community events."),
            (f"From intimate {c['a1']} gatherings to large {c['landmark2']} events, {c['name']} event planners share what works — and what to avoid — when renting portable restrooms.",
             f"Event Sanitation Tips for {c['name']}, {c['state']}",
             f"Best practices for {c['county']} outdoor events from experienced local organizers."),
        ],
        "coastal": [
            (f"Beachfront events near {c['landmark1']} require specialized sanitation planning. Here's what {c['county']} event organizers need to know about coastal porta potty rentals.",
             f"Coastal Event Sanitation Guide for {c['name']}",
             f"Beach access, anchoring, salt-air units, and timing for {c['county']} waterfront events."),
            (f"From {c['a1']} marina events to {c['landmark2']} summer concerts, {c['name']} hosts a packed outdoor calendar. Use our count guide to size your sanitation right.",
             f"Outdoor Event Sanitation in {c['name']}, {c['state']}",
             f"How to size porta potties and luxury trailers for {c['county']} coastal events."),
            (f"Luxury restroom trailers make the difference at {c['county']} beachfront weddings. Here's how {c['a1']} and {c['a2']} event planners choose the right setup.",
             f"Luxury Trailers vs. Standard Units for {c['name']} Weddings",
             f"Comparing restroom options for {c['county']} coastal wedding venues near {c['landmark1']}."),
        ],
        "college": [
            (f"Game days near {c['landmark1']} bring massive crowds to {c['county']}. Here's exactly how many porta potties you need for tailgates of 50, 200, or 1,000+ fans.",
             f"Game Day Tailgate Sanitation Guide — {c['name']}",
             f"Sizing porta potty rentals for {c['landmark1']} tailgate parties and {c['county']} campus events."),
            (f"Campus construction at {c['name']}'s universities requires OSHA documentation, institutional insurance, and service schedules that match facilities management requirements.",
             f"University Construction Sanitation in {c['name']}, {c['state']}",
             f"What institutional projects near {c['landmark1']} need from portable sanitation vendors."),
            (f"From graduation day to homecoming weekend, {c['county']}'s event calendar creates unique sanitation demand. Here's how to plan for {c['name']}'s busiest weekends.",
             f"College Town Event Sanitation — {c['name']} Guide",
             f"Planning portable restrooms for {c['county']}'s biggest student and community events."),
        ],
        "tech": [
            (f"Corporate campus construction and outdoor employee events near {c['landmark1']} require premium sanitation. Here's what {c['county']} tech companies need to know.",
             f"Tech Campus Sanitation Guide — {c['name']}, {c['state']}",
             f"Construction, corporate events, and OSHA compliance for {c['county']} tech employers."),
            (f"From {c['a1']} office park builds to {c['landmark2']} corporate off-sites, {c['name']} businesses are upgrading to luxury restroom trailers. Here's why.",
             f"Luxury Restroom Trailers for {c['name']} Corporate Events",
             f"How {c['county']} companies are improving their outdoor event guest experience."),
            (f"Data center construction, campus expansions, and corporate events near {c['landmark1']} all need reliable sanitation. Here's a {c['state_name']} contractor's guide.",
             f"2026 Construction Sanitation Costs — {c['name']}, {c['state']}",
             f"What {c['county']} contractors and corporate facilities managers pay for portable restrooms."),
        ],
        "suburban": [
            (f"Kitchen remodels, bathroom renovations, and additions in {c['county']} go smoother with a porta potty on-site. Here's what {c['name']} homeowners need to know.",
             f"Home Renovation Porta Potty Guide — {c['name']}, {c['state']}",
             f"One unit, one call, and your {c['county']} renovation crew stays out of your home."),
            (f"Neighborhood block parties, school fundraisers, and HOA events in {c['a1']} and {c['a2']} — here's how {c['county']} community organizers size their sanitation.",
             f"Community Event Sanitation in {c['name']}, {c['state']}",
             f"Porta potty planning for {c['county']} neighborhood events of every size."),
            (f"New subdivisions and commercial projects throughout {c['county']} have OSHA sanitation requirements. Here's what {c['name']} contractors need before breaking ground.",
             f"OSHA Sanitation Requirements for {c['name']} Contractors",
             f"Everything {c['county']} general contractors need to know about job-site portable restrooms."),
        ],
        "government": [
            (f"Government and military projects near {c['landmark1']} require vendor compliance documentation that most rental companies can't provide. Here's what to ask for.",
             f"Government Contractor Sanitation Guide — {c['name']}, {c['state']}",
             f"COIs, OSHA certs, and DOD access protocols for {c['county']} government projects."),
            (f"Public events in {c['name']} have ADA requirements and health department standards. Here's how {c['county']} civic organizers plan for public sanitation compliance.",
             f"Public Event Sanitation in {c['name']}, {c['state']}",
             f"ADA compliance, permit requirements, and sizing for {c['county']} public gatherings."),
            (f"Infrastructure projects near {c['landmark1']} keep {c['county']} contractors busy year-round. Here's a {c['state_name']} guide to OSHA-compliant job-site sanitation.",
             f"Construction Sanitation for {c['name']} Infrastructure Projects",
             f"OSHA ratio requirements and service schedules for {c['county']} public works contractors."),
        ],
    }
    teasers = TEASERS.get(c["profile"], TEASERS["suburban"])

    def replace_article(m, idx):
        teaser = teasers[idx % len(teasers)]
        desc, title, sub = teaser[0], teaser[1], teaser[2]
        return (
            f'<p class="text-gray-600 text-sm mb-4 line-clamp-3">{desc}</p>'
        )

    # Replace 3 blog article <p class="text-gray-600 text-sm mb-4 line-clamp-3"> paragraphs
    count = [0]
    def replacer(m):
        i = count[0]
        count[0] += 1
        return replace_article(m, i)

    html = re.sub(
        r'<p class="text-gray-600 text-sm mb-4 line-clamp-3">.*?</p>',
        replacer,
        html, flags=re.DOTALL
    )
    return html


def rebuild_areas_section(html, city):
    """
    Replace the entire areas section with city-specific content.
    Fixes new-template pages that have Miami neighborhoods/zips in Tampa, etc.
    """
    c = city
    areas = c.get("areas", [f"Downtown {c['name']}"])
    zip_code = c.get("zip", "00000")

    # Build neighborhood cards from city areas list
    area_cards = ""
    AREA_DESCS = {
        0: f"Our {c['name']} depot enables rapid same-day delivery to {areas[0]} and all of {c['county']}.",
        1: f"Construction and event delivery to {areas[1]} — same-day available throughout {c['county']}.",
        2: f"Serving {areas[2]} residential and commercial projects with OSHA-certified units.",
        3: f"Luxury restroom trailers and standard units for events and construction in {areas[3]}.",
        4: f"Same-day delivery to {areas[4]} and all surrounding {c['county']} communities.",
        5: f"Serving contractors and event planners in {areas[5]} and throughout {c['county']}.",
        6: f"Reliable porta potty service to {areas[6]}, {c['a1']}, and all of {c['county']}.",
    }
    for i, area in enumerate(areas[:7]):
        desc = AREA_DESCS.get(i, f"Same-day delivery to {area} in {c['county']}.")
        area_cards += f'''                        <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
                            <h5 class="font-semibold text-gray-800 mb-1">{area}</h5>
                            <p class="text-sm text-gray-600">{desc}</p>
                        </div>\n'''

    # Build zip codes display — use real zip from city data
    # Generate neighboring zip codes numerically from base
    try:
        base_zip = int(zip_code) if zip_code != "00000" else 10000
    except:
        base_zip = 10000
    zip_list = [str(base_zip + i).zfill(5) for i in range(9)]
    zip_html = "".join(f"<li>{z}</li>" for z in zip_list)

    new_areas_section = f'''    <section id="areas" class="py-16 bg-white border-t border-gray-100">
        <div class="container mx-auto px-4">
            <div class="flex flex-col lg:flex-row gap-12 items-center">
                <div class="lg:w-1/2">
                    <h2 class="text-3xl font-bold text-gray-900 mb-6">Proudly Serving {c['name']} and All of {c['county']}</h2>
                    <p class="text-gray-600 mb-6 leading-relaxed">{c['name']} is a dynamic {c['county']} community where construction activity, outdoor events, and residential growth create year-round demand for reliable portable sanitation. From the corridors near {c['landmark1']} to the neighborhoods of {c['a1']}, {c['a2']}, and {c['a3']}, every part of {c['county']} has a reason to call FixPilot — construction sites, events, or emergency backup near {c['landmark2']}.</p>

                    <div class="bg-blue-50 p-6 rounded-lg border border-blue-100 mb-6">
                        <h4 class="font-bold text-brand-800 mb-3">We serve key {c['name']} zip codes including:</h4>
                        <ul class="grid grid-cols-3 gap-2 text-sm text-gray-700">
                            {zip_html}
                        </ul>
                    </div>

                    <h4 class="font-bold text-brand-800 mb-3">Neighborhoods We Serve in {c['name']}:</h4>
                    <div class="grid sm:grid-cols-2 gap-4 mt-4">
{area_cards}                    </div>

                    <div class="mt-6">
                        <p class="text-sm text-gray-600 mb-3">We also provide fast, reliable service to contractors and residents in these nearby {c['county']} communities:</p>
                        <div class="flex flex-wrap gap-2">
                            {''.join(f'<span class="bg-brand-100 text-brand-800 px-3 py-1 rounded-full text-sm font-medium">{a}</span>' for a in areas[:6])}
                        </div>
                    </div>

                    <div class="mt-8 bg-green-50 border-l-4 border-green-600 p-6 rounded-r-lg">
                        <h3 class="font-bold text-lg text-gray-800 mb-4">{c['name']} Porta Potty Rental Prices</h3>
                        <div class="grid sm:grid-cols-2 gap-4">
                            <div class="flex justify-between items-center py-2 border-b border-green-200">
                                <span class="text-gray-700">Standard Unit</span>
                                <span class="font-bold text-green-700">$75-100/day</span>
                            </div>
                            <div class="flex justify-between items-center py-2 border-b border-green-200">
                                <span class="text-gray-700">Deluxe Unit</span>
                                <span class="font-bold text-green-700">$100-150/day</span>
                            </div>
                            <div class="flex justify-between items-center py-2 border-b border-green-200">
                                <span class="text-gray-700">ADA Accessible</span>
                                <span class="font-bold text-green-700">$120-160/day</span>
                            </div>
                            <div class="flex justify-between items-center py-2 border-b border-green-200">
                                <span class="text-gray-700">Luxury Restroom Trailer</span>
                                <span class="font-bold text-green-700">$400-600/day</span>
                            </div>
                        </div>
                        <p class="text-sm text-gray-600 mt-4">*Prices may vary by duration and location in {c['county']}. Call for exact quote.</p>
                        <a href="tel:+18336529344" class="inline-block mt-4 bg-green-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-700 transition-colors">
                            Get Your Free {c['name']} Quote
                        </a>
                    </div>
                </div>

                <div class="lg:w-1/2 h-80 rounded-xl overflow-hidden shadow-lg relative bg-gray-200">
                    <iframe
                        width="100%"
                        height="100%"
                        frameborder="0"
                        style="border:0"
                        src="https://maps.google.com/maps?q={c['name'].replace(' ', '+')}+{c['state']}&t=&z=13&ie=UTF8&iwloc=&output=embed"
                        loading="lazy"
                        allowfullscreen
                        title="{c['name']} Porta Potty Rental Service Area Map">
                    </iframe>
                </div>
            </div>
        </div>
    </section>'''

    _na = new_areas_section
    html_new = re.sub(
        r'<section id="areas"[^>]*>.*?</section>',
        lambda m: _na,
        html, flags=re.DOTALL, count=1
    )
    return html_new if html_new != html else html


def rebuild_related_cities(html, city):
    """Replace related-cities section with same-state cities found on disk."""
    from pathlib import Path
    import collections

    state = city["state"]
    state_name = city["state_name"]
    current_slug = city["slug"]

    # Find all city pages for this state
    base = Path(".")
    state_cities = []
    for d in sorted(base.iterdir()):
        if not d.is_dir() or not d.name.startswith("porta-potty-rental-"):
            continue
        if not (d / "index.html").exists():
            continue
        slug = d.name[len("porta-potty-rental-"):]
        if slug == current_slug:
            continue
        parts = slug.rsplit("-", 1)
        if len(parts) == 2 and parts[1].upper() == state:
            # Extract display name
            name = parts[0].replace("-", " ").title()
            state_cities.append((slug, name))

    if not state_cities:
        return html  # No same-state cities found, leave as-is

    # Pick up to 4 cities to link
    import hashlib
    h = int(hashlib.md5(current_slug.encode()).hexdigest(), 16)
    # Shuffle deterministically then pick first 4
    shuffled = sorted(state_cities, key=lambda x: (h + sum(ord(c) for c in x[0])) % 9999)
    picked = shuffled[:4]

    # Build related cities HTML
    state_slug = f"porta-potty-rental-{state.lower()}"
    cards = f'''      <a href="/{state_slug}" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all border border-brand-200 group">
        <h4 class="font-black text-brand-950 text-lg mb-2 group-hover:text-cta transition">All {state_name}</h4>
        <p class="text-sm text-brand-700">Porta Potty Rental in {state_name}</p>
        <span class="text-cta text-sm font-semibold mt-3 inline-block">View All Cities →</span>
      </a>'''
    for slug, name in picked:
        cards += f'''
      <a href="/porta-potty-rental-{slug}" class="bg-white rounded-xl p-6 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all border border-brand-200 group">
        <h4 class="font-black text-brand-950 text-lg mb-2 group-hover:text-cta transition">{name}</h4>
        <p class="text-sm text-brand-700">Porta Potty Rental in {name}, {state}</p>
        <span class="text-cta text-sm font-semibold mt-3 inline-block">Learn More →</span>
      </a>'''

    new_section = f'''<section id="related-cities" class="py-16 bg-brand-50 border-t border-brand-200">
  <div class="container mx-auto px-4">
    <h2 class="text-3xl md:text-4xl font-black text-brand-950 mb-8 text-center">Other Cities We Serve in {state_name}</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
{cards}
    </div>
    <p class="text-center mt-8">
      <a href="/locations" class="inline-flex items-center gap-2 bg-brand-900 text-white px-6 py-3 rounded-lg font-bold hover:bg-brand-800 transition">
        View All Locations <i class="fas fa-arrow-right"></i>
      </a>
    </p>
  </div>
</section>'''

    _ns = new_section
    html_new = re.sub(
        r'<section id="related-cities".*?</section>',
        lambda m: _ns,
        html, flags=re.DOTALL, count=1
    )
    return html_new if html_new != html else html


def replace_service_descriptions(html, city):
    """Replace service card <p> descriptions with city/profile-specific variants."""
    c = city
    profile = c["profile"]
    h_val = int(hashlib.md5(c["slug"].encode()).hexdigest(), 16)

    # Map of alt-text keyword → (service_name, 3 description variants by profile group)
    # profile_group: 0=construction/oilgas/government, 1=events/coastal, 2=college/tech/suburban
    SERVICE_DESC = {
        "Construction porta potty": [
            f"OSHA-certified portable restrooms for {c['a1']} and {c['a2']} construction in {c['county']}. Worker-to-toilet ratio documentation included with every {c['name']} order. Weekly servicing on your {c['county']} job site schedule.",
            f"Heavy-duty construction units for {c['name']} job sites — serving {c['a1']}, {c['a2']}, and remote {c['county']} work sites. OSHA documentation provided on request. Same-day delivery available.",
            f"{c['county']} construction porta potties: OSHA 29 CFR 1926.51 compliant, same-day delivery to {c['a1']} and {c['a2']}, weekly service included. {c['name']} site supervisors get clean units and zero paperwork hassle.",
            f"Purpose-built {c['name']} construction units meeting OSHA worker-to-toilet requirements. Same-day delivery to {c['county']} job sites, weekly service, and compliance documentation for your {c['a3']} project.",
        ],
        "Luxury Restroom Trailer": [
            f"Climate-controlled luxury trailers for {c['a1']} weddings and {c['landmark1']}-area events in {c['county']}. Flushing toilets, running water, and premium finishes — guests never guess they're in a trailer.",
            f"VIP trailers with A/C, granite countertops, and LED lighting for {c['name']} events near {c['landmark1']}. Available with same-day delivery throughout {c['county']} and {c['a2']} venues.",
            f"Upscale restroom trailers for {c['county']} events from {c['a1']} fundraisers to {c['landmark2']}-area galas. Climate-controlled, beautifully appointed, and delivered same-day to {c['name']} venues.",
            f"{c['name']}'s premier luxury restroom trailers — flushing toilets, running water, full climate control. Perfect for {c['landmark1']} corporate events and {c['a2']} outdoor weddings in {c['county']}.",
        ],
        "ADA-Compliant": [
            f"ADA and ANSI A117.1-compliant accessible units for {c['name']} public events and {c['county']} construction. Grab bars, wider doors, non-slip floors — required at any public-facing {c['a1']} project.",
            f"Wheelchair-accessible units for {c['county']} construction and {c['name']} public gatherings. Extra turning radius, grab bars, and accessible seat height — ANSI A117.1 compliant for {c['a2']} events.",
            f"ADA-accessible porta potties for {c['name']} permitted events and {c['county']} job sites. Meets ANSI A117.1 accessibility requirements for {c['a3']} public venues and {c['a1']} construction.",
            f"Accessible portable restrooms for {c['county']} public events and {c['name']} construction near {c['a1']}. ADA-compliant door width, turning radius, and grab bars — required for {c['landmark1']}-area public events.",
        ],
        "Septic Pumping": [
            f"Septic pump-out and holding tank service for {c['name']} construction sites in {c['county']}. Emergency pumping for {c['a1']} and {c['a2']} properties — 24/7 availability from our {c['name']} team.",
            f"Holding tank pump-outs for {c['county']} construction projects and {c['name']} events. Emergency service available 24/7 throughout {c['a1']}, {c['a2']}, and the full {c['name']} metro.",
            f"Portable septic pumping for {c['county']} residential properties, {c['name']} event sites, and {c['a3']} construction projects. Same-day emergency service — call (833) 652-9344.",
            f"{c['county']} holding tank and septic pump-out service — scheduled weekly for {c['a1']} job sites or emergency same-day for {c['a2']} and {c['a3']} properties. {c['name']} metro coverage, 24/7.",
        ],
        "Standard Porta Potty": [
            f"OSHA-certified standard units for {c['a1']} job sites and {c['name']} outdoor events. Same-day delivery to {c['a2']} and all {c['county']} locations, weekly service included at no extra charge.",
            f"Affordable standard porta potties for {c['county']} construction crews and {c['name']} community events. Reliable, clean, on-time — serving {c['a1']}, {c['a2']}, and {c['a3']} daily.",
            f"Budget-friendly {c['name']} standard units delivered same-day to {c['a1']} and {c['a2']} in {c['county']}. Weekly service and OSHA compliance documentation included for all {c['name']} orders.",
            f"Clean, OSHA-compliant standard porta potties for {c['county']} construction and {c['name']} outdoor events. Serving {c['a1']}, {c['a2']}, {c['a3']}, and all of {c['county']} with same-day delivery.",
        ],
        "Deluxe Porta Potty": [
            f"Upgraded {c['name']} units with interior lighting, larger tanks, and improved ventilation. A step above standard — ideal for {c['a1']} events and multi-week {c['county']} construction projects.",
            f"Deluxe units for {c['county']} events and longer rentals: interior lighting, better ventilation, larger capacity. Popular for {c['a1']} and {c['a2']} gatherings where standard units won't do.",
            f"Premium-feel porta potties for {c['name']} outdoor weddings, {c['a1']} HOA events, and renovation projects in {c['county']}. Lighting, improved airflow, and cleaner aesthetics than standard units.",
            f"{c['county']} deluxe porta potties: interior lighting, enhanced ventilation, larger waste capacity. The right upgrade for {c['a2']} events and multi-week {c['a3']} construction in {c['name']}.",
        ],
        "Hand Wash Station": [
            f"Portable hand wash stations for {c['name']} construction in {c['a1']} and {c['a2']}. OSHA-required within 100 feet of job site restrooms in {c['county']}. Available as add-on to any {c['name']} order.",
            f"Standalone hand wash stations for {c['name']} food events and {c['county']} construction near {c['landmark1']}. Fresh water tank, soap, paper towels — essential for {c['a1']} and {c['a2']} events.",
            f"Fresh-water portable sinks for {c['county']} outdoor markets, {c['name']} catering events, and {c['a3']} job sites. Self-contained, no hookup required — bundle with porta potties for {c['name']}.",
            f"{c['county']} portable hand wash stations — 50-gallon fresh water, soap dispenser, waste containment. OSHA-required for {c['a1']} and {c['a2']} construction sites, popular at {c['name']} outdoor food events.",
        ],
        "Event Restroom Trailer": [
            f"Climate-controlled event trailers for {c['name']} festivals and {c['landmark1']}-area gatherings in {c['county']}. Multiple stall configurations for crowds from 100 to 5,000+ at {c['a1']} venues.",
            f"Multi-stall restroom trailers for large {c['name']} events near {c['landmark1']} and {c['a2']} outdoor venues. A/C or heat, multiple stalls, and upscale fixtures for {c['county']} festival crowds.",
            f"Spacious {c['county']} event trailers: climate control, handicap-accessible stall, and premium fixtures. Same-day setup for {c['name']} festivals, {c['a1']} concerts, and {c['landmark2']} outdoor events.",
            f"Fully climate-controlled event restroom trailers for {c['a1']} and {c['a2']} outdoor events in {c['county']}. Sized from 2 to 12 stalls — right for any {c['name']} event from 100 to 10,000 attendees.",
        ],
        "Portable Sink": [
            f"Standalone portable sinks for {c['name']} catering events, {c['a1']} film sets, and {c['county']} outdoor work sites. Fresh-water tank, soap, paper towels — no {c['a2']} utility connection required.",
            f"Fresh-water portable wash stations for {c['name']} outdoor markets and {c['county']} construction near {c['landmark1']}. Pairs with any porta potty rental for a complete {c['a1']} hygiene solution.",
            f"Portable sinks for {c['county']} community events, {c['name']} school fairs, and {c['a3']} job sites. Self-contained fresh water — health code compliant for {c['a1']} food service events.",
            f"{c['name']} portable hand wash stations: 50-gallon fresh water, refillable soap, gray-water containment. Used at {c['a1']} food truck courts, {c['a2']} outdoor markets, and {c['county']} construction sites.",
        ],
        "VIP Trailer": [
            f"Marble countertops, LED lighting, stainless fixtures, and climate control — the gold standard for {c['name']} galas and {c['landmark1']}-area VIP events in {c['county']}. Every guest is impressed.",
            f"Five-star mobile restroom experience for {c['name']} black-tie events near {c['landmark1']}. Premium flooring, fixtures, and lighting make this the obvious choice for {c['a1']} and {c['a2']} upscale events.",
            f"VIP luxury trailers for {c['county']}'s most prestigious events — from {c['landmark2']}-area galas to {c['a1']} corporate retreats. Every detail premium, every delivery on time throughout {c['name']}.",
            f"{c['name']}'s premier VIP trailers: marble surfaces, LED vanity lighting, climate control, flushing toilets. Perfect for {c['a2']} luxury weddings and {c['landmark1']}-area executive events in {c['county']}.",
        ],
        "Restroom Trailer Setup": [
            f"Full-service trailer management for {c['name']} events: delivery to {c['a1']} or {c['a2']} venue, leveling, utility connection, daily service, and {c['county']} pickup. Nothing for you to manage.",
            f"End-to-end restroom trailer service for {c['county']} events — placement at {c['landmark1']}-area venues, on-site setup, guest signage, daily service, and post-event removal throughout {c['name']}.",
            f"Worry-free trailer delivery and removal for {c['name']} events. Our {c['county']} crew handles site prep, utility connection, and daily servicing at {c['a1']} and {c['a2']} venues.",
            f"{c['county']} restroom trailer setup service: our {c['name']} crew delivers to {c['a3']} or {c['landmark2']}-area venues, levels on uneven terrain, connects utilities, and services daily throughout your event.",
        ],
        "Emergency": [
            f"24/7 emergency porta potty delivery throughout {c['name']} and {c['county']}. When a {c['a1']} job site fails inspection or a {c['a2']} event vendor cancels, we dispatch immediately — no premium for urgency.",
            f"Same-day emergency rentals for {c['name']} — available 24/7 for {c['a1']}, {c['a2']}, and all of {c['county']}. Call (833) 652-9344 any time; our {c['name']} dispatcher answers live and confirms delivery.",
            f"After-hours emergency porta potty service for {c['county']}: {c['a1']} construction emergencies, {c['a2']} event backup, {c['a3']} last-minute project starts. {c['name']} same-night delivery available.",
            f"Last-minute {c['name']} porta potty rentals — {c['a1']} job sites, {c['landmark1']}-area events, or {c['county']} plumbing crises. (833) 652-9344 answered live 24/7 by our {c['name']}-area team.",
        ],
        "Handicap Portable": [
            f"ADA-accessible units for {c['name']} public events and {c['county']} construction: 60\" turning radius, grab bars, lower toilet height. Required by law for {c['a1']} and {c['a2']} public-facing projects.",
            f"Wheelchair-accessible porta potties for {c['county']} public events and {c['name']} permitted job sites. Exceeds ADA minimums — ensures full compliance for {c['landmark1']}-area and {c['a1']} events.",
            f"Handicap-accessible portable toilets for all {c['name']} outdoor events and {c['a3']} construction sites. Wider doorways, grab bars, turning radius clearance — ANSI A117.1 compliant for {c['county']}.",
            f"ADA-compliant accessible units for {c['a1']} events and {c['county']} construction: extra floor space, bilateral grab bars, outward-swinging door. Required at any {c['name']} public event near {c['landmark2']}.",
        ],
        "Flushable Portable": [
            f"Recirculating-flush units for {c['name']} weddings and {c['landmark1']}-area upscale events in {c['county']}. Real flushing action — the middle option between standard units and full luxury trailers.",
            f"Flushable porta potties for {c['name']} events where guest comfort matters near {c['a1']} and {c['a2']}. Real flush, fresh water, cleaner interior — available same-day throughout {c['county']}.",
            f"Premium flushable units for {c['county']} outdoor events: real flushing action, fresh water, mirror, interior lighting. Popular for {c['name']} events in {c['a3']} and near {c['landmark2']} where standard units fall short.",
            f"{c['name']} flushable porta potties: recirculating flush and self-contained fresh water for {c['a1']} events. The right upgrade for {c['county']} gatherings where standard units are inadequate but trailers are overkill.",
        ],
    }

    # Select variant index based on profile
    PROFILE_VARIANT = {
        "oilgas": 0, "government": 0,
        "events": 1, "coastal": 1,
        "college": 2, "tech": 2, "suburban": 2,
    }
    variant_base = PROFILE_VARIANT.get(profile, 2)

    # Use per-card hash (not single city hash) so same-profile same-state cities differ
    def get_card_variant(key_idx):
        return int(hashlib.md5(f"{c['slug']}:card:{key_idx}".encode()).hexdigest(), 16) % 3

    card_counter = [0]

    def replace_card(m):
        alt_text = m.group(1)
        desc_p = m.group(2)
        # Normalize: remove hyphens for matching
        alt_norm = alt_text.lower().replace('-', ' ')
        for key, variants in SERVICE_DESC.items():
            key_norm = key.lower().replace('-', ' ')
            if key_norm in alt_norm:
                variant = get_card_variant(card_counter[0])
                card_counter[0] += 1
                new_desc = variants[variant % len(variants)]
                return m.group(0).replace(desc_p, new_desc)
        card_counter[0] += 1
        return m.group(0)

    # Match service card alt+description for ALL paragraph class variants
    city_name = c["name"]
    for text_cls in ["text-gray-600", "text-brand-600", "text-brand-700"]:
        for mb_cls in ["mb-3", "mb-4", "mb-5"]:
            # Simple class
            html = re.sub(
                r'alt="([^"]+?)(?:\s+in\s+[^"]+)?"[^>]*>.*?'
                rf'<p class="{text_cls} text-sm {mb_cls}">([^<]{{20,500}})</p>',
                replace_card, html, flags=re.DOTALL
            )
            # Class with trailing attributes (e.g., leading-relaxed font-medium)
            html = re.sub(
                r'alt="([^"]+?)(?:\s+in\s+[^"]+)?"[^>]*>.*?'
                rf'<p class="{text_cls} text-sm {mb_cls}[^"]*">([^<]{{20,500}})</p>',
                replace_card, html, flags=re.DOTALL
            )

    # Fix hard-coded wrong-city text in service descriptions that slipped through
    WRONG_REFS = [
        ("Keep your NYC job site", f"Keep your {city_name} job site"),
        ("Keep your NYC", f"Keep your {city_name}"),
        ("Keep your Miami job site", f"Keep your {city_name} job site"),
        ("Keep your Miami", f"Keep your {city_name}"),
        ("Keep your Tampa job site", f"Keep your {city_name} job site"),
        ("Keep your Tampa", f"Keep your {city_name}"),
        ("in Brickell, Edgewater, and Sunny Isles", f"in {c['a1']}, {c['a2']}, and {c['a3']}"),
        ("Brickell and Edgewater", f"{c['a1']} and {c['a2']}"),
        ("Manhattan and beyond", f"{city_name} and beyond"),
        ("the NYC area", f"the {city_name} area"),
    ]
    for wrong, right in WRONG_REFS:
        if wrong in html:
            html = html.replace(wrong, right)

    return html


# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    base = Path(".")
    city_dirs = sorted(p for p in base.iterdir()
                       if p.is_dir() and p.name.startswith("porta-potty-rental-"))

    updated = 0
    skipped = 0
    for city_dir in city_dirs:
        slug = city_dir.name[len("porta-potty-rental-"):]
        page = city_dir / "index.html"
        if not page.exists():
            continue

        city = get_city_data(slug)
        if city is None:
            print(f"  SKIP {slug} (state/county page, not a city)")
            skipped += 1
            continue

        html = page.read_text(encoding="utf-8")
        patched = patch_page(html, city)

        if patched != html:
            page.write_text(patched, encoding="utf-8")
            print(f"  OK   {slug} ({city['profile']})")
            updated += 1
        else:
            print(f"  SKIP {slug} (no FAQ section found to replace — different template)")
            skipped += 1

    print(f"\nDone. Updated: {updated}  Skipped: {skipped}")


if __name__ == "__main__":
    import json as json_mod
    json = json_mod
    main()
