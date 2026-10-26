"""
build-directory.py — Generates the SkilledRoofer contractor directory.
Reads the cleaned CSV and outputs:
  - directory.html  (main hub with state grid)
  - directory/<state>.html  (one page per state with contractor cards)

Re-run whenever the CSV is updated.
"""

import csv
import os
import json
import html as html_mod
from collections import defaultdict

CSV_PATH = os.path.join(os.path.dirname(__file__),
                        '..', '..', '..', 'Desktop',
                        'claude-skilled-Roofer-template-CLEANED.csv')
OUT_DIR = os.path.dirname(__file__)

STATE_ABBR_TO_NAME = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

NAME_TO_ABBR = {v: k for k, v in STATE_ABBR_TO_NAME.items()}

# ── STATE-SPECIFIC CONTENT ──────────────────────────────────────────
# Each entry: climate, licensing, avg_cost, popular_materials
# This unique content differentiates each state page for Google indexing.

STATE_DATA = {
    'Alabama': {
        'climate': 'Alabama roofs face intense summer heat, high humidity, and severe thunderstorms with frequent hail. The Gulf Coast region is also in a hurricane zone, where wind-driven rain and flying debris cause major roof damage. Roofs in Alabama typically age faster due to year-round UV exposure and moisture.',
        'licensing': 'Alabama requires roofing contractors to hold a state license through the Alabama Licensing Board for General Contractors for projects over $50,000. Always verify your contractor\'s license number before signing a contract.',
        'avg_cost': 'The average roof replacement in Alabama costs $7,500 to $12,000 for a standard asphalt shingle roof on a 2,000 sq ft home.',
        'popular_materials': 'Asphalt shingles rated for high winds (130+ MPH) are the most popular choice. Metal roofing is gaining ground in coastal areas for its wind and corrosion resistance.',
    },
    'Alaska': {
        'climate': 'Alaska roofs endure extreme cold, heavy snow loads, and prolonged ice buildup. In Anchorage and Fairbanks, temperatures can drop below -40F, causing materials to contract and crack. Ice dams are a constant threat, and the short construction season limits when roofing work can be done.',
        'licensing': 'Alaska does not require a statewide roofing contractor license, but Anchorage, Fairbanks, and Juneau each have their own local licensing and permit requirements. Check with your municipality before hiring.',
        'avg_cost': 'Roof replacement in Alaska runs $12,000 to $22,000 due to high labor costs, material shipping expenses, and the short installation window.',
        'popular_materials': 'Standing seam metal roofing is the top choice for its ability to shed snow. Architectural shingles rated for cold climates and high winds are also widely used.',
    },
    'Arizona': {
        'climate': 'Arizona roofs take extreme UV punishment, with summer temperatures regularly exceeding 115F in Phoenix and Tucson. Thermal cycling between scorching days and cool nights causes materials to expand and contract constantly. Monsoon season from June through September brings sudden heavy rain, hail, and high winds.',
        'licensing': 'Arizona requires roofing contractors to hold an active license from the Arizona Registrar of Contractors (ROC). Operating without a license is a criminal offense in Arizona.',
        'avg_cost': 'The average roof replacement in Arizona costs $8,000 to $14,000 for asphalt shingles, though tile roofs run $15,000 to $30,000.',
        'popular_materials': 'Concrete and clay tile dominate the market for their heat resistance and longevity in desert climates. Lighter-colored asphalt shingles with cool-roof ratings and foam roofing for flat commercial buildings are also common.',
    },
    'Arkansas': {
        'climate': 'Arkansas sits in Tornado Alley and experiences severe spring thunderstorms with damaging hail and high winds. Summer heat and humidity accelerate shingle aging, while occasional ice storms in winter cause tree damage and ice dams in the northern part of the state.',
        'licensing': 'Arkansas requires roofing contractors to register with the Arkansas Contractors Licensing Board for projects over $2,000. Contractors must carry liability insurance and workers\' compensation coverage.',
        'avg_cost': 'Roof replacement in Arkansas averages $7,000 to $11,500 for a standard asphalt shingle roof.',
        'popular_materials': 'Impact-resistant asphalt shingles (Class 4 rated) are popular due to frequent hail. Many insurance companies offer premium discounts for impact-resistant roofing in Arkansas.',
    },
    'California': {
        'climate': 'California\'s roofing challenges vary dramatically by region. Coastal areas face salt air corrosion and marine layer moisture. Inland valleys deal with extreme heat exceeding 110F. Northern California gets heavy rain and occasional snow in the mountains. Wildfire risk is a growing concern statewide, with ember-resistant roofing now required in many areas.',
        'licensing': 'California has strict contractor licensing through the Contractors State License Board (CSLB). Roofing contractors must hold a C-39 Roofing license. Always verify at cslb.ca.gov before hiring.',
        'avg_cost': 'Roof replacement in California costs $10,000 to $20,000 for asphalt shingles, with coastal and Bay Area prices running 30-50% higher than the Central Valley.',
        'popular_materials': 'Cool-roof rated shingles and tiles that reflect solar heat are popular statewide. In fire zones, Class A fire-rated materials are required. Clay and concrete tile remain the signature California look, especially in Southern California.',
    },
    'Colorado': {
        'climate': 'Colorado is one of the toughest states on roofs. The Front Range corridor from Fort Collins to Colorado Springs gets pummeled by hailstorms every spring and summer. High altitude means stronger UV radiation that degrades shingles faster. Heavy snow loads in the mountains and rapid freeze-thaw cycles at all elevations cause constant stress.',
        'licensing': 'Colorado does not require a statewide roofing license, but many municipalities including Denver, Colorado Springs, and Aurora require local contractor licenses and permits for roof work.',
        'avg_cost': 'Roof replacement in Colorado averages $9,000 to $16,000 for asphalt shingles. Costs spike after major hailstorms when demand surges.',
        'popular_materials': 'Class 4 impact-resistant shingles (like GAF Armor Shield II and Owens Corning Duration STORM) are extremely popular because many Colorado insurers offer 20-30% premium discounts for impact-rated roofs.',
    },
    'Connecticut': {
        'climate': 'Connecticut roofs face the full range of New England weather - heavy snow loads, ice dams, nor\'easters with high winds, and hot humid summers. Coastal areas from Bridgeport to New London also deal with salt spray and the occasional hurricane or tropical storm remnant.',
        'licensing': 'Connecticut requires roofing contractors to register with the Department of Consumer Protection as a Home Improvement Contractor (HIC). A separate certificate is needed for new construction roofing.',
        'avg_cost': 'Roof replacement in Connecticut costs $10,000 to $18,000, with Fairfield County and shoreline towns running higher due to elevated labor and material costs.',
        'popular_materials': 'Architectural asphalt shingles dominate, with ice and water shield underlayment required along eaves. Cedar shakes remain popular for historic homes, and standing seam metal is growing for its snow-shedding ability.',
    },
    'Delaware': {
        'climate': 'Delaware\'s coastal Mid-Atlantic climate brings hot, humid summers and cold, wet winters. The state\'s low elevation and proximity to the Atlantic make it vulnerable to nor\'easters and hurricane remnants. Coastal Sussex County deals with salt air corrosion and occasional flooding that damages roof structures from below.',
        'licensing': 'Delaware does not require a statewide roofing contractor license, but all contractors must register with the Delaware Division of Revenue and carry proper insurance. New Castle County and some municipalities have additional permit requirements.',
        'avg_cost': 'Roof replacement in Delaware costs $8,500 to $14,000 for a standard asphalt shingle roof.',
        'popular_materials': 'Asphalt shingles rated for high winds are the most common choice. Metal roofing is increasingly popular in beach communities for salt air resistance.',
    },
    'Florida': {
        'climate': 'Florida is the most demanding state for roofing in America. Hurricane-force winds, intense UV radiation, year-round humidity, and torrential rain create the perfect storm for roof degradation. The Florida Building Code requires roofs in the High-Velocity Hurricane Zone (Miami-Dade and Broward) to meet the strictest wind standards in the nation.',
        'licensing': 'Florida requires roofing contractors to hold a state-certified or state-registered license through the Department of Business and Professional Regulation (DBPR). The licensing exam is one of the toughest in the country.',
        'avg_cost': 'Roof replacement in Florida costs $9,000 to $18,000 for asphalt shingles, with South Florida running significantly higher due to code requirements. Metal and tile roofs range from $15,000 to $35,000.',
        'popular_materials': 'Concrete and clay tile are the signature Florida roofing materials for their wind resistance and longevity. Metal roofing rated for 160+ MPH winds is growing fast. All shingles must meet Miami-Dade NOA standards in hurricane zones.',
    },
    'Georgia': {
        'climate': 'Georgia roofs deal with hot, humid summers that accelerate algae and moss growth on shingles. Severe thunderstorms with hail sweep through the Piedmont region regularly. The coastal areas around Savannah face hurricane risk, while North Georgia mountain areas get occasional ice and snow.',
        'licensing': 'Georgia requires roofing contractors to hold a license from the Georgia State Licensing Board for Residential and General Contractors. A Residential-Light Commercial license covers most roofing work.',
        'avg_cost': 'Roof replacement in Georgia averages $7,500 to $13,000 for asphalt shingles, with Metro Atlanta prices on the higher end.',
        'popular_materials': 'Algae-resistant asphalt shingles are strongly recommended due to the humid climate. Look for shingles with copper or zinc granules that prevent black streaking.',
    },
    'Hawaii': {
        'climate': 'Hawaii\'s tropical climate creates unique roofing challenges. Trade winds carry salt spray that corrodes metal fasteners and flashing. Heavy tropical rain on the windward sides of the islands and intense year-round UV exposure degrade materials faster. Hurricane season from June through November adds additional wind risk.',
        'licensing': 'Hawaii requires roofing contractors to be licensed by the Department of Commerce and Consumer Affairs (DCCA). A C-42 Roofing specialty license is required for roofing-only work.',
        'avg_cost': 'Roof replacement in Hawaii is among the most expensive in the nation at $15,000 to $30,000, driven by shipping costs for materials to the islands and high labor rates.',
        'popular_materials': 'Standing seam metal roofing with stainless steel or galvalume fasteners is ideal for salt air resistance. Concrete tile and asphalt shingles rated for high winds are also common. Avoid dissimilar metal combinations that accelerate galvanic corrosion.',
    },
    'Idaho': {
        'climate': 'Idaho roofs face heavy snow loads in the mountains and northern panhandle, with Boise experiencing hot, dry summers exceeding 100F. Rapid temperature swings between seasons stress roofing materials. Wildfire smoke and ash from summer fires can deposit corrosive residue on roof surfaces.',
        'licensing': 'Idaho requires roofing contractors to register with the Idaho Contractors Board. A Public Works license is needed for government projects. Local jurisdictions may have additional requirements.',
        'avg_cost': 'Roof replacement in Idaho costs $8,000 to $14,000 for asphalt shingles, with mountain resort communities running significantly higher.',
        'popular_materials': 'Metal roofing is very popular in mountain areas for snow shedding. Architectural asphalt shingles are the standard in the Treasure Valley. Fire-resistant materials are recommended in wildfire-prone areas.',
    },
    'Illinois': {
        'climate': 'Illinois roofs endure brutal winters with heavy snow, ice dams, and sub-zero temperatures, followed by hot, humid summers. The state sits at the edge of Tornado Alley, and spring thunderstorms bring damaging hail and high winds. The Chicago area adds lake-effect weather that dumps extra snow and ice on roofs.',
        'licensing': 'Illinois requires roofing contractors to be licensed by the Illinois Department of Financial and Professional Regulation. Chicago has its own additional contractor licensing requirements through the city.',
        'avg_cost': 'Roof replacement in Illinois costs $9,000 to $16,000. Chicago metro area prices run 20-30% higher than downstate.',
        'popular_materials': 'Heavy-weight architectural shingles that handle freeze-thaw cycles are the standard. Ice and water shield underlayment is essential along eaves. Impact-resistant shingles are increasingly popular in hail-prone central Illinois.',
    },
    'Indiana': {
        'climate': 'Indiana gets hit hard by spring and summer thunderstorms with frequent hail and tornado activity. Winters bring heavy snow and ice, especially in the northern part of the state near Lake Michigan. The humidity in summer promotes algae growth on shingle roofs.',
        'licensing': 'Indiana does not require a statewide roofing contractor license, but contractors must register with the Indiana Secretary of State and carry general liability insurance. Many cities including Indianapolis require local permits.',
        'avg_cost': 'Roof replacement in Indiana averages $7,500 to $12,500 for asphalt shingles.',
        'popular_materials': 'Impact-resistant asphalt shingles are popular in hail-prone areas. Standard architectural shingles with algae-resistant granules are the most common choice for the humid climate.',
    },
    'Iowa': {
        'climate': 'Iowa is in the heart of Tornado Alley and gets severe hailstorms every spring and summer. Winter brings heavy snow, ice storms, and sustained sub-zero temperatures that test every roofing material. Wind is a year-round factor across the open terrain.',
        'licensing': 'Iowa requires roofing contractors to register with the Iowa Division of Labor. Contractors must carry workers\' compensation insurance if they have employees and general liability insurance.',
        'avg_cost': 'Roof replacement in Iowa costs $7,000 to $12,000 for asphalt shingles.',
        'popular_materials': 'Class 4 impact-resistant shingles are highly recommended because of frequent hail. Many Iowa insurers offer discounts for impact-rated roofs. Metal roofing is growing in popularity on farmsteads and rural properties.',
    },
    'Kansas': {
        'climate': 'Kansas sits squarely in Tornado Alley and experiences some of the most destructive hailstorms in the nation. Straight-line winds exceeding 80 MPH sweep across the open prairie. Summer heat, winter ice storms, and constant UV exposure create a demanding environment for any roof.',
        'licensing': 'Kansas does not require a statewide roofing contractor license. However, most cities and counties require local business licenses and building permits for roof work. Always ask for proof of insurance.',
        'avg_cost': 'Roof replacement in Kansas averages $7,000 to $12,000 for asphalt shingles. Insurance claims for hail damage are among the highest per capita in the country.',
        'popular_materials': 'Impact-resistant Class 4 shingles are the smart choice for Kansas. Several Kansas insurers mandate or heavily incentivize impact-rated roofing after a claim.',
    },
    'Kentucky': {
        'climate': 'Kentucky experiences a mix of southern heat and humidity with cold, wet winters. Severe thunderstorms with hail and tornadoes hit the western part of the state regularly. The eastern mountains get heavier snow. High humidity promotes algae and moss growth on shingles statewide.',
        'licensing': 'Kentucky does not require a statewide roofing license, but contractors must carry general liability insurance. Louisville, Lexington, and other cities require local contractor licensing and building permits.',
        'avg_cost': 'Roof replacement in Kentucky costs $7,000 to $12,000 for asphalt shingles.',
        'popular_materials': 'Algae-resistant architectural shingles are the standard choice. Metal roofing is popular in rural eastern Kentucky for its longevity and low maintenance.',
    },
    'Louisiana': {
        'climate': 'Louisiana roofs face extreme conditions: hurricane-force winds, torrential rain, year-round humidity, and intense heat. The Gulf Coast is one of the highest-risk zones for hurricane damage in the country. Mold and algae growth are constant problems due to the subtropical climate.',
        'licensing': 'Louisiana requires roofing contractors to hold a license from the Louisiana State Licensing Board for Contractors for projects over $50,000. Contractors must pass an exam and demonstrate financial responsibility.',
        'avg_cost': 'Roof replacement in Louisiana costs $8,000 to $15,000 for asphalt shingles. Insurance costs are among the highest in the nation, making wind-rated materials a wise investment.',
        'popular_materials': 'Wind-rated asphalt shingles (130+ MPH) and metal roofing are essential in Louisiana. Standing seam metal is increasingly popular for its hurricane resistance. All roofing must meet Louisiana\'s enhanced building code for wind zones.',
    },
    'Maine': {
        'climate': 'Maine roofs face harsh, long winters with heavy snow loads, ice dams, and strong coastal winds. Nor\'easters bring combination snow-rain-wind events multiple times per season. The short construction season (May through October) means crews are in high demand.',
        'licensing': 'Maine does not require a statewide roofing contractor license, but contractors must register with the state and carry insurance. Local municipalities may require additional permits.',
        'avg_cost': 'Roof replacement in Maine costs $9,000 to $16,000 for asphalt shingles, with coastal and resort areas running higher.',
        'popular_materials': 'Architectural shingles rated for cold climates are the standard. Ice and water shield is critical along all eaves and valleys. Standing seam metal is popular for its ability to shed heavy snow loads.',
    },
    'Maryland': {
        'climate': 'Maryland roofs deal with hot, humid summers, cold winters with ice and snow, and the occasional hurricane remnant hitting the Chesapeake Bay and Eastern Shore regions. The combination of heat and humidity promotes algae growth on roof surfaces.',
        'licensing': 'Maryland requires roofing contractors to hold a Home Improvement Commission (MHIC) license. This is strictly enforced - hiring an unlicensed contractor can void your protections under the Maryland Home Improvement Guaranty Fund.',
        'avg_cost': 'Roof replacement in Maryland costs $9,000 to $16,000, with the DC suburbs and Annapolis area on the higher end.',
        'popular_materials': 'Algae-resistant architectural asphalt shingles are the most common choice. Slate roofing is traditional in historic areas like Baltimore and Annapolis. Metal roofing is growing on the Eastern Shore.',
    },
    'Massachusetts': {
        'climate': 'Massachusetts roofs endure heavy nor\'easters, ice dams, coastal wind, and hot humid summers. Cape Cod and the Islands face additional salt spray corrosion. The state\'s older housing stock means many roofs sit on structures not designed for modern snow loads or insulation standards.',
        'licensing': 'Massachusetts requires roofing contractors to register as Home Improvement Contractors (HIC) with the Office of Consumer Affairs. Boston and many other municipalities have additional contractor licensing requirements.',
        'avg_cost': 'Roof replacement in Massachusetts costs $10,000 to $18,000, with Greater Boston and Cape Cod among the most expensive areas in New England.',
        'popular_materials': 'Architectural asphalt shingles are the standard. Cedar shakes are common on Cape Cod and historic homes. Ice and water shield is required along eaves, valleys, and around penetrations per state code.',
    },
    'Michigan': {
        'climate': 'Michigan roofs face Lake-effect snow that can dump several feet in a single storm along the western and northern coasts. Heavy ice buildup, long freezing winters, and the freeze-thaw cycle are the primary enemies. Summer thunderstorms bring hail to the southern Lower Peninsula.',
        'licensing': 'Michigan requires residential roofing contractors to hold a Maintenance and Alteration license or a Residential Builder license from the Michigan Department of Licensing and Regulatory Affairs (LARA).',
        'avg_cost': 'Roof replacement in Michigan costs $8,000 to $14,000 for asphalt shingles.',
        'popular_materials': 'Heavy-weight architectural shingles rated for cold climates are the standard. Metal roofing is popular in the Upper Peninsula for snow shedding. Ice and water shield underlayment is essential throughout the state.',
    },
    'Minnesota': {
        'climate': 'Minnesota is one of the coldest states, with winter temperatures dropping to -30F and beyond. Heavy snow loads, severe ice dams, and a short construction season from May to October make roofing challenging. Summer thunderstorms bring hail, especially in the southern and western parts of the state.',
        'licensing': 'Minnesota requires roofing contractors to hold a Residential Contractor or Residential Roofer license from the Minnesota Department of Labor and Industry. Licensing requires passing an exam and carrying insurance.',
        'avg_cost': 'Roof replacement in Minnesota costs $9,000 to $15,000 for asphalt shingles. The short construction season concentrates demand and can push prices higher in summer.',
        'popular_materials': 'Cold-climate rated architectural shingles with superior ice dam protection are essential. Metal roofing is growing in popularity for its snow-shedding ability. Proper attic ventilation is critical to prevent ice dams.',
    },
    'Mississippi': {
        'climate': 'Mississippi roofs endure extreme heat, year-round humidity, and severe weather including tornadoes and Gulf Coast hurricanes. The southern part of the state is in the hurricane impact zone. High moisture levels promote rapid algae and moss growth on all roof surfaces.',
        'licensing': 'Mississippi requires roofing contractors to hold a license from the Mississippi State Board of Contractors for projects over $50,000 (residential) or $10,000 (commercial). Verify at msboc.us.',
        'avg_cost': 'Roof replacement in Mississippi averages $7,000 to $11,000 for asphalt shingles, among the lowest in the nation.',
        'popular_materials': 'Algae-resistant asphalt shingles rated for high winds are the top choice. Metal roofing is increasingly popular in coastal areas near Biloxi and Gulfport for hurricane resistance.',
    },
    'Missouri': {
        'climate': 'Missouri sits at the crossroads of severe weather. Tornadoes, hail, ice storms, and intense summer thunderstorms all hit the state regularly. The St. Louis and Kansas City metro areas are in high-risk hail zones. Winter ice storms in the Ozarks cause significant tree and roof damage.',
        'licensing': 'Missouri does not require a statewide roofing license, but St. Louis, Kansas City, Springfield, and other cities have their own contractor licensing and permit requirements.',
        'avg_cost': 'Roof replacement in Missouri costs $7,500 to $13,000 for asphalt shingles.',
        'popular_materials': 'Impact-resistant asphalt shingles are strongly recommended in the KC and STL metro areas due to frequent hail. Several Missouri insurers offer premium discounts for Class 4 rated roofs.',
    },
    'Montana': {
        'climate': 'Montana roofs endure harsh winters with heavy snow loads, extreme cold, and high winds. The western mountains get more snow while the eastern plains face wind-driven ice and temperature swings from -40F to 100F across seasons. Wildfire risk is increasing in forested areas.',
        'licensing': 'Montana does not require a statewide roofing contractor license, but contractors must register with the Montana Department of Labor and carry workers\' compensation insurance if they have employees.',
        'avg_cost': 'Roof replacement in Montana costs $9,000 to $15,000 for asphalt shingles, with ski resort areas running much higher.',
        'popular_materials': 'Standing seam metal roofing is extremely popular for its ability to shed snow and withstand high winds. Fire-resistant materials are recommended in wildfire-prone areas near national forests.',
    },
    'Nebraska': {
        'climate': 'Nebraska is in the heart of Hail Alley - the state gets more damaging hailstorms per square mile than almost anywhere in the country. Tornadoes, high winds across the open plains, and harsh winters with heavy snow and ice dams are constant threats to roofs.',
        'licensing': 'Nebraska requires roofing contractors to register with the Nebraska Department of Labor. Omaha, Lincoln, and other cities have their own licensing and permit requirements.',
        'avg_cost': 'Roof replacement in Nebraska costs $7,500 to $12,500 for asphalt shingles. Hail damage claims are among the most frequent in the nation.',
        'popular_materials': 'Class 4 impact-resistant shingles are practically standard in Nebraska due to the severe hail risk. Many insurers require or heavily incentivize impact-rated roofing.',
    },
    'Nevada': {
        'climate': 'Nevada roofs face extreme heat in Las Vegas and Reno with summer temperatures exceeding 115F. Intense UV radiation at high desert elevations degrades materials faster. The dry climate means less moisture damage, but thermal cycling between hot days and cool nights stresses materials constantly.',
        'licensing': 'Nevada requires roofing contractors to hold a license from the Nevada State Contractors Board (NSCB). A C-15 Roofing and Siding license is required for roofing work. Penalties for unlicensed work are severe.',
        'avg_cost': 'Roof replacement in Nevada costs $8,000 to $14,000 for asphalt shingles, with Las Vegas strip-adjacent areas and Reno running higher.',
        'popular_materials': 'Cool-roof rated shingles that reflect solar heat are essential for energy efficiency. Concrete tile is common in Las Vegas subdivisions. Flat roof systems (TPO, modified bitumen) are standard on commercial buildings.',
    },
    'New Hampshire': {
        'climate': 'New Hampshire roofs face severe New England winters with heavy snow, ice dams, and nor\'easters. The White Mountains region gets some of the highest snowfall in the Northeast. Coastal areas near Portsmouth deal with salt spray and high winds.',
        'licensing': 'New Hampshire does not require a statewide roofing contractor license, but contractors must register with the New Hampshire Secretary of State. Most municipalities require building permits for roof work.',
        'avg_cost': 'Roof replacement in New Hampshire costs $9,000 to $16,000 for asphalt shingles, with ski areas and the Seacoast running higher.',
        'popular_materials': 'Architectural asphalt shingles rated for cold climates are the standard. Standing seam metal is popular in the mountains. Ice and water shield is critical on all eaves and valleys.',
    },
    'New Jersey': {
        'climate': 'New Jersey roofs deal with hot, humid summers, cold winters with snow and ice, and powerful nor\'easters that bring high winds and flooding to the Shore area. Hurricane remnants occasionally track up the coast bringing damaging winds inland. Salt air corrosion affects roofs within several miles of the coast.',
        'licensing': 'New Jersey requires roofing contractors to register as Home Improvement Contractors (HIC) with the Division of Consumer Affairs. Contractors must carry liability insurance and provide a written contract for all work.',
        'avg_cost': 'Roof replacement in New Jersey costs $10,000 to $18,000, making it one of the more expensive states for roofing due to high labor costs and strict code requirements.',
        'popular_materials': 'Architectural asphalt shingles are the most common. Slate is traditional in many historic North Jersey communities. Cedar shakes are popular at the Shore despite higher maintenance requirements.',
    },
    'New Mexico': {
        'climate': 'New Mexico roofs face intense UV radiation at high elevations, extreme temperature swings between day and night, and occasional monsoon downpours that test drainage systems. In Albuquerque and Santa Fe, flat roofs must handle both desert sun and occasional heavy snow.',
        'licensing': 'New Mexico requires roofing contractors to hold a license from the New Mexico Regulation and Licensing Department, Construction Industries Division. License categories vary by project size.',
        'avg_cost': 'Roof replacement in New Mexico costs $7,500 to $13,000 for asphalt shingles. Flat roof systems on adobe-style homes may cost more.',
        'popular_materials': 'Flat roof systems (TPO, modified bitumen, built-up) are the traditional choice for the Southwest adobe style. Pitched roofs use cool-roof rated asphalt shingles or metal. Standing seam metal is growing for its durability in UV-intense conditions.',
    },
    'New York': {
        'climate': 'New York State spans dramatically different roofing climates - from heavy lake-effect snow in Buffalo and Syracuse to coastal hurricane risk on Long Island and the Hudson Valley. The Adirondacks get massive snowfall, while New York City roofs endure freeze-thaw cycles, wind tunnels between buildings, and aging infrastructure.',
        'licensing': 'New York requires roofing contractors to be licensed in most municipalities. New York City has strict DOB licensing. Westchester, Nassau, Suffolk, and other counties have their own licensing requirements. Always verify local requirements.',
        'avg_cost': 'Roof replacement in New York costs $10,000 to $20,000 for asphalt shingles, with NYC and Long Island running $15,000 to $30,000 due to access challenges and high labor costs.',
        'popular_materials': 'Architectural asphalt shingles are standard upstate. Flat roof systems dominate in NYC. Slate is traditional on historic homes. Standing seam metal is popular in the Adirondacks and Hudson Valley.',
    },
    'North Carolina': {
        'climate': 'North Carolina roofs face diverse challenges - hurricane-force winds and salt spray on the Outer Banks and coast, severe thunderstorms with hail in the Piedmont, and heavy snow in the Blue Ridge Mountains. The humid climate promotes algae and moss growth statewide.',
        'licensing': 'North Carolina requires roofing contractors to hold a license from the NC Licensing Board for General Contractors for projects over $30,000. A limited license covers smaller projects.',
        'avg_cost': 'Roof replacement in North Carolina costs $8,000 to $14,000 for asphalt shingles, with the Research Triangle and Charlotte metro areas at the higher end.',
        'popular_materials': 'Algae-resistant asphalt shingles rated for high winds are the standard. Metal roofing is increasingly popular in mountain and coastal areas. The Outer Banks requires hurricane-rated materials and enhanced fastening.',
    },
    'North Dakota': {
        'climate': 'North Dakota roofs endure some of the most extreme weather in the lower 48 - severe blizzards, sustained sub-zero temperatures, heavy snow loads, and a short construction season. Summer brings intense thunderstorms with large hail, especially in the eastern part of the state.',
        'licensing': 'North Dakota requires roofing contractors to be licensed by the North Dakota Secretary of State and hold a contractor license through the state. Local jurisdictions may have additional requirements.',
        'avg_cost': 'Roof replacement in North Dakota costs $8,000 to $14,000 for asphalt shingles.',
        'popular_materials': 'Impact-resistant asphalt shingles are strongly recommended due to frequent hail. Metal roofing is common on agricultural and rural properties. Proper ice and water shield is critical.',
    },
    'Ohio': {
        'climate': 'Ohio roofs face lake-effect snow in the northeast near Cleveland, severe thunderstorms with hail across the central and western parts of the state, and humid summers that promote algae growth. Freeze-thaw cycles from November through March are hard on all roofing materials.',
        'licensing': 'Ohio does not require a statewide roofing license, but many cities including Columbus, Cleveland, Cincinnati, and Akron require local contractor registration and building permits.',
        'avg_cost': 'Roof replacement in Ohio costs $7,500 to $13,000 for asphalt shingles.',
        'popular_materials': 'Architectural asphalt shingles with algae resistance are the most popular choice. Impact-resistant shingles are gaining ground in hail-prone western Ohio.',
    },
    'Oklahoma': {
        'climate': 'Oklahoma is ground zero for severe weather - the state leads the nation in tornadoes per capita and gets devastating hailstorms every spring. Straight-line winds exceeding 100 MPH are not uncommon. Summer heat exceeds 100F, and ice storms hit in winter.',
        'licensing': 'Oklahoma does not require a statewide roofing license, but contractors must register with the Oklahoma Construction Industries Board for projects over $50,000. Oklahoma City and Tulsa have local licensing requirements.',
        'avg_cost': 'Roof replacement in Oklahoma costs $7,000 to $12,000 for asphalt shingles. Insurance claims for hail and wind damage are among the highest in the nation.',
        'popular_materials': 'Impact-resistant Class 4 shingles are practically standard in Oklahoma. The state incentivizes impact-rated roofing through insurance premium reductions. Metal roofing is growing in popularity.',
    },
    'Oregon': {
        'climate': 'Western Oregon roofs endure months of continuous rain from October through May, creating ideal conditions for moss, algae, and moisture damage. The Willamette Valley is one of the wettest regions in the country. Eastern Oregon is dry but faces wildfire risk and extreme temperature swings.',
        'licensing': 'Oregon requires roofing contractors to be licensed with the Oregon Construction Contractors Board (CCB). Licensing requires a surety bond, insurance, and passing an exam.',
        'avg_cost': 'Roof replacement in Oregon costs $9,000 to $16,000 for asphalt shingles, with Portland metro at the higher end.',
        'popular_materials': 'Moss-resistant and algae-resistant shingles are essential in western Oregon. Standing seam metal is popular for its rain shedding. Cedar shakes are traditional but require significant maintenance in the wet climate.',
    },
    'Pennsylvania': {
        'climate': 'Pennsylvania roofs face cold, snowy winters in the west and Poconos, hot humid summers in Philadelphia, and everything in between. Lake-effect snow hits the Erie area hard. Ice dams are a common problem across the state, and severe thunderstorms bring hail to the central counties.',
        'licensing': 'Pennsylvania requires roofing contractors to register with the Attorney General\'s Home Improvement Registration program (PA Home Improvement Contractor Registration Act). Philadelphia has its own contractor licensing through L&I.',
        'avg_cost': 'Roof replacement in Pennsylvania costs $8,500 to $15,000 for asphalt shingles, with Philadelphia and Pittsburgh metro areas at the higher end.',
        'popular_materials': 'Architectural asphalt shingles are the standard. Slate roofing has deep roots in Pennsylvania - the Lehigh Valley has been a major slate producing region for over a century. Ice and water shield is essential along eaves.',
    },
    'Rhode Island': {
        'climate': 'Rhode Island roofs face powerful nor\'easters, coastal wind, salt spray, and humid summers. Despite its small size, the state gets significant weather - heavy snow, ice, and the occasional hurricane or tropical storm tracking up the coast.',
        'licensing': 'Rhode Island requires roofing contractors to register with the Rhode Island Contractors\' Registration and Licensing Board. All contractors must carry liability insurance and workers\' compensation.',
        'avg_cost': 'Roof replacement in Rhode Island costs $9,500 to $16,000 for asphalt shingles.',
        'popular_materials': 'Architectural asphalt shingles rated for high winds are the standard. Cedar shakes are traditional in coastal communities. Slate is common on historic homes in Providence and Newport.',
    },
    'South Carolina': {
        'climate': 'South Carolina roofs face intense heat, high humidity, and hurricane risk along the coast from Myrtle Beach to Hilton Head. Severe thunderstorms with hail hit the upstate region. The Lowcountry\'s combination of heat, moisture, and salt air is especially hard on roofing materials.',
        'licensing': 'South Carolina requires roofing contractors to hold a license from the SC Residential Builders Commission (residential) or the SC Contractors Licensing Board (commercial) for projects over $5,000.',
        'avg_cost': 'Roof replacement in South Carolina costs $7,500 to $13,000 for asphalt shingles, with Charleston and Hilton Head running higher.',
        'popular_materials': 'Algae-resistant and wind-rated asphalt shingles are the standard. Metal roofing is very popular in the Lowcountry and coastal areas for hurricane resistance and salt air durability.',
    },
    'South Dakota': {
        'climate': 'South Dakota roofs endure severe hailstorms, blizzards, and extreme temperature swings from -30F in winter to 100F+ in summer. The Black Hills get heavy snow while the eastern prairie is in prime hail territory. Wind is a year-round factor across the open landscape.',
        'licensing': 'South Dakota does not require a statewide roofing license, but Sioux Falls, Rapid City, and other municipalities require local business licenses and building permits for roof work.',
        'avg_cost': 'Roof replacement in South Dakota costs $7,500 to $13,000 for asphalt shingles.',
        'popular_materials': 'Impact-resistant asphalt shingles are the smart choice due to severe hail risk. Metal roofing is common on agricultural and rural buildings. Proper wind-rated fastening is critical.',
    },
    'Tennessee': {
        'climate': 'Tennessee roofs face a mix of severe thunderstorms with hail and tornadoes in the spring, hot and humid summers that promote algae growth, and occasional ice storms in winter. West Tennessee is in a higher tornado risk zone, while East Tennessee in the Smokies gets heavier snow.',
        'licensing': 'Tennessee requires roofing contractors to hold a license from the Tennessee Board for Licensing Contractors for projects over $25,000. Smaller projects may require a home improvement license.',
        'avg_cost': 'Roof replacement in Tennessee costs $7,000 to $12,500 for asphalt shingles, with Nashville metro prices trending higher due to rapid growth.',
        'popular_materials': 'Algae-resistant architectural asphalt shingles are the most popular choice. Metal roofing is growing in the rural and mountain areas of East Tennessee.',
    },
    'Texas': {
        'climate': 'Texas roofs face an extreme range of conditions depending on region. The Gulf Coast gets hurricanes, DFW and Central Texas get pummeled by severe hail, West Texas endures intense UV and desert heat, and the Panhandle sees ice storms and tornadoes. The DFW metroplex is one of the most hail-damaged regions in the country.',
        'licensing': 'Texas does not require a statewide roofing license, but most major cities including Houston, Dallas, San Antonio, and Austin require local contractor registration and building permits. Always verify insurance and ask for references.',
        'avg_cost': 'Roof replacement in Texas costs $8,000 to $15,000 for asphalt shingles. Insurance claim activity after hailstorms is massive - Texas leads the nation in hail-related insurance claims.',
        'popular_materials': 'Impact-resistant Class 4 asphalt shingles are strongly recommended, especially in DFW and Central Texas. Metal roofing is popular in the Hill Country and Gulf Coast for wind resistance. Concrete tile is common in South Texas.',
    },
    'Utah': {
        'climate': 'Utah roofs deal with heavy mountain snow in Park City and the Wasatch Front, intense UV at high elevation, and extreme dryness in the valleys. Temperature swings of 40-50 degrees in a single day are common. Summer thunderstorms bring occasional hail to the Wasatch Front.',
        'licensing': 'Utah requires roofing contractors to hold a license from the Utah Division of Occupational and Professional Licensing (DOPL). General contractors and specialty roofing contractors must pass an exam.',
        'avg_cost': 'Roof replacement in Utah costs $8,000 to $14,000 for asphalt shingles, with Park City and other ski areas running much higher.',
        'popular_materials': 'Metal roofing is popular in mountain areas for snow shedding. Architectural asphalt shingles are standard in the Wasatch Front valleys. Cool-roof options help with summer heat management.',
    },
    'Vermont': {
        'climate': 'Vermont roofs face harsh, long winters with heavy snow, ice dams, and bitter cold. The Green Mountains get significant snowfall, and the entire state is subject to freeze-thaw damage from November through April. The short construction season concentrates all roofing work into five months.',
        'licensing': 'Vermont does not require a statewide roofing contractor license, but all contractors must register with the Vermont Secretary of State. Many municipalities require building permits for roof replacements.',
        'avg_cost': 'Roof replacement in Vermont costs $9,000 to $16,000 for asphalt shingles, with ski resort areas running significantly higher.',
        'popular_materials': 'Standing seam metal roofing is very popular for its ability to shed snow. Slate is traditional on older Vermont homes. Architectural asphalt shingles with enhanced cold-weather performance are the budget standard.',
    },
    'Virginia': {
        'climate': 'Virginia roofs face diverse conditions - hurricane remnants and salt spray on the coast, severe thunderstorms in the Piedmont, and heavy snow in the Blue Ridge and Shenandoah Valley. The state\'s humidity promotes algae and moss growth, especially in the Tidewater region.',
        'licensing': 'Virginia requires roofing contractors to hold a license from the Virginia Department of Professional and Occupational Regulation (DPOR). A Class A license covers projects over $120,000; Class B covers $10,000 to $120,000.',
        'avg_cost': 'Roof replacement in Virginia costs $8,500 to $15,000 for asphalt shingles, with Northern Virginia and Hampton Roads at the higher end.',
        'popular_materials': 'Algae-resistant architectural asphalt shingles are the standard. Slate is traditional in historic areas. Metal roofing is growing in the Shenandoah Valley and mountain regions.',
    },
    'Washington': {
        'climate': 'Western Washington roofs endure 6-8 months of near-continuous rain, making moisture management the number one priority. Moss and algae growth is extremely aggressive. Eastern Washington is the opposite - hot, dry summers with wildfire risk and cold, snowy winters.',
        'licensing': 'Washington requires roofing contractors to be registered with the Washington State Department of Labor and Industries (L&I). Contractors must carry a surety bond, liability insurance, and workers\' compensation.',
        'avg_cost': 'Roof replacement in Washington costs $10,000 to $18,000 for asphalt shingles, with Seattle metro among the most expensive markets on the West Coast.',
        'popular_materials': 'Moss-resistant and algae-resistant shingles are essential west of the Cascades. Standing seam metal is popular for rain shedding. Cedar shakes are iconic but require constant maintenance in the wet climate.',
    },
    'West Virginia': {
        'climate': 'West Virginia\'s mountain terrain creates challenging roofing conditions - heavy snow at higher elevations, frequent freeze-thaw cycles, and steep roof pitches that complicate installation. Severe thunderstorms bring hail to the eastern panhandle. High humidity promotes moss and algae in the valleys.',
        'licensing': 'West Virginia requires roofing contractors to hold a license from the West Virginia Division of Labor, Contractor Licensing Board for projects over $2,500.',
        'avg_cost': 'Roof replacement in West Virginia costs $7,000 to $12,000 for asphalt shingles.',
        'popular_materials': 'Metal roofing is very popular for its snow-shedding ability on steep mountain roofs. Architectural asphalt shingles are the standard for residential homes in the valleys.',
    },
    'Wisconsin': {
        'climate': 'Wisconsin roofs endure brutal winters with heavy snow, sustained sub-zero temperatures, and severe ice dam formation. Lake-effect snow hits the eastern counties hard. Summer thunderstorms bring hail, and the freeze-thaw cycle from late fall through early spring is relentless.',
        'licensing': 'Wisconsin requires roofing contractors to hold a Dwelling Contractor credential from the Wisconsin Department of Safety and Professional Services (DSPS) for residential work.',
        'avg_cost': 'Roof replacement in Wisconsin costs $8,000 to $14,000 for asphalt shingles.',
        'popular_materials': 'Heavy-weight architectural shingles rated for extreme cold are the standard. Metal roofing is growing in popularity for snow shedding. Proper ice and water shield and attic ventilation are critical to prevent ice dams.',
    },
    'Wyoming': {
        'climate': 'Wyoming roofs face extreme wind - the state is one of the windiest in the nation, with gusts regularly exceeding 70 MPH. Add heavy snow, extreme cold, intense UV at high elevation, and severe hailstorms, and Wyoming is one of the toughest environments for any roof.',
        'licensing': 'Wyoming does not require a statewide roofing contractor license. However, most municipalities require business licenses and building permits for roof work.',
        'avg_cost': 'Roof replacement in Wyoming costs $9,000 to $15,000 for asphalt shingles, with resort areas like Jackson Hole running much higher.',
        'popular_materials': 'Metal roofing rated for extreme wind is the top choice. Any asphalt shingle used in Wyoming should be rated for 130+ MPH winds. Enhanced fastening patterns (6 nails per shingle minimum) are recommended statewide.',
    },
}


def slug(name):
    return name.lower().replace(' ', '-')


def stars_html(rating):
    """Return HTML for star display given a rating like 4.8."""
    if not rating:
        return ''
    try:
        r = float(rating)
    except ValueError:
        return ''
    full = int(r)
    half = 1 if r - full >= 0.3 else 0
    empty = 5 - full - half
    return '★' * full + ('½' if half else '') + '☆' * empty


def e(text):
    """HTML-escape."""
    return html_mod.escape(str(text)) if text else ''


def json_escape(text):
    """Escape text for safe embedding in JSON strings."""
    if not text:
        return ''
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def build_schema_local_business(items, state_name):
    """Build JSON-LD LocalBusiness schema for a list of contractors."""
    businesses = []
    for c in items:
        biz = {
            "@type": "RoofingContractor",
            "name": c['name'],
            "@context": "https://schema.org",
        }
        # Address
        addr = {"@type": "PostalAddress"}
        if c['address']:
            addr["streetAddress"] = c['address']
        if c['city']:
            addr["addressLocality"] = c['city']
        if c['state']:
            addr["addressRegion"] = c['state']
        if c['zip']:
            addr["postalCode"] = c['zip']
        addr["addressCountry"] = "US"
        biz["address"] = addr

        if c['phone']:
            digits = ''.join(ch for ch in c['phone'] if ch.isdigit())
            if digits.startswith('1') and len(digits) > 10:
                digits = digits[1:]
            biz["telephone"] = f"+1{digits}"

        if c['website']:
            url = c['website'] if c['website'].startswith('http') else 'https://' + c['website']
            biz["url"] = url

        if c['rating']:
            try:
                rating_val = float(c['rating'])
                agg = {
                    "@type": "AggregateRating",
                    "ratingValue": str(rating_val),
                    "bestRating": "5",
                }
                if c['reviews']:
                    agg["reviewCount"] = c['reviews']
                biz["aggregateRating"] = agg
            except ValueError:
                pass

        biz["areaServed"] = {
            "@type": "State",
            "name": state_name
        }
        businesses.append(biz)

    # Wrap in an ItemList
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Roofing Contractors in {state_name}",
        "numberOfItems": len(businesses),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": biz
            }
            for i, biz in enumerate(businesses)
        ]
    }
    return json.dumps(schema, indent=2)


def read_csv():
    contractors = defaultdict(list)
    total = 0
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state_abbr = row.get('state', '').strip().upper()
            if state_abbr not in STATE_ABBR_TO_NAME:
                continue
            state_name = STATE_ABBR_TO_NAME[state_abbr]
            contractors[state_name].append({
                'name': row.get('business_name', '').strip(),
                'address': row.get('street_address', '').strip(),
                'city': row.get('city', '').strip(),
                'state': state_abbr,
                'zip': row.get('zip', '').strip(),
                'phone': row.get('phone', '').strip(),
                'website': row.get('website', '').strip(),
                'rating': row.get('google_rating', '').strip(),
                'reviews': row.get('review_count', '').strip(),
            })
            total += 1
    return contractors, total


# ── GA4 ─────────────────────────────────────────────────────────────
GA4_SCRIPT = '''  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-71L37NKQDH"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-71L37NKQDH');
  </script>'''


# ── NAV ──────────────────────────────────────────────────────────────
def nav_html(active='directory', prefix=''):
    return f'''<nav class="nav">
  <div class="nav-inner">
    <a href="{prefix}index.html" class="nav-logo">
      <img src="{prefix}favicon.svg" alt="SR" width="32" height="32">
      <span class="nav-logo-text">Skilled<span>Roofer</span></span>
    </a>
    <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('open')" aria-label="Toggle menu">☰</button>
    <ul class="nav-links">
      <li><a href="{prefix}shingles.html">Shingles</a></li>
      <li><a href="{prefix}metal-roofing.html">Metal Roofing</a></li>
      <li><a href="{prefix}commercial.html">Commercial</a></li>
      <li><a href="{prefix}tools.html">Tools</a></li>
      <li><a href="{prefix}diy-projects.html">DIY Projects</a></li>
      <li><a href="{prefix}directory.html" class="active">Directory</a></li>
    </ul>
  </div>
</nav>'''


# ── FOOTER ───────────────────────────────────────────────────────────
def footer_html(prefix=''):
    return f'''<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <h3>Skilled<span>Roofer</span></h3>
      <p>Expert roofing material reviews and buying guides for professionals and homeowners.</p>
    </div>
    <div class="footer-col">
      <h4>Guides</h4>
      <ul>
        <li><a href="{prefix}shingles.html">Best Shingles</a></li>
        <li><a href="{prefix}metal-roofing.html">Metal Roofing</a></li>
        <li><a href="{prefix}metal-vs-shingles.html">Metal vs Shingles</a></li>
        <li><a href="{prefix}commercial.html">Commercial</a></li>
        <li><a href="{prefix}best-roofing-materials.html">Best Materials Compared</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>More</h4>
      <ul>
        <li><a href="{prefix}underlayment.html">Underlayment</a></li>
        <li><a href="{prefix}tools.html">Roofing Tools</a></li>
        <li><a href="{prefix}diy-projects.html">DIY Projects</a></li>
        <li><a href="{prefix}find-roofing-contractor.html">Find a Contractor</a></li>
        <li><a href="{prefix}directory.html">Contractor Directory</a></li>
        <li><a href="{prefix}privacy.html">Privacy Policy</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>&copy; 2026 SkilledRoofer.com - All rights reserved.</span>
    <span>As an Amazon Associate and affiliate partner, we earn from qualifying purchases.</span>
  </div>
</footer>'''


# ── GSAP SCRIPT ──────────────────────────────────────────────────────
GSAP_SCRIPT = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger);
  document.querySelectorAll('.animate-in').forEach((el, i) => {
    gsap.fromTo(el,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' },
        delay: i * 0.05
      }
    );
  });
</script>'''


# ── STATE PAGE ───────────────────────────────────────────────────────
def build_state_page(state_name, items):
    abbr = NAME_TO_ABBR[state_name]
    state_info = STATE_DATA.get(state_name, {})
    count = len(items)

    # Build contractor cards
    cards = []
    for c in items:
        rating_html = ''
        if c['rating']:
            star_display = stars_html(c['rating'])
            review_text = f'({e(c["reviews"])} review{"s" if c["reviews"] != "1" else ""})' if c['reviews'] else ''
            rating_html = (
                f'<div class="contractor-rating">'
                f'<span class="contractor-stars">{star_display}</span>'
                f'<span class="contractor-rating-num">{e(c["rating"])}</span>'
                f'<span class="contractor-reviews">{review_text}</span>'
                f'</div>'
            )

        addr_parts = []
        if c['address']:
            addr_parts.append(e(c['address']))
        city_state_zip = ', '.join(filter(None, [e(c['city']), e(c['state'])]))
        if c['zip']:
            city_state_zip += ' ' + e(c['zip'])
        if city_state_zip:
            addr_parts.append(city_state_zip)
        address_html = '<br>'.join(addr_parts)

        phone_html = ''
        if c['phone']:
            digits = ''.join(ch for ch in c['phone'] if ch.isdigit())
            if digits.startswith('1') and len(digits) > 10:
                digits = digits[1:]
            phone_html = f'<a href="tel:+1{digits}" class="contractor-phone">📞 {e(c["phone"])}</a>'

        website_html = ''
        if c['website']:
            url = c['website'] if c['website'].startswith('http') else 'https://' + c['website']
            website_html = f'<a href="{e(url)}" target="_blank" rel="noopener" class="contractor-website">🌐 Visit Website</a>'

        cards.append(f'''    <div class="contractor-card animate-in" data-name="{e(c['name']).lower()}" data-city="{e(c['city']).lower()}" data-zip="{e(c['zip'])}">
      {rating_html}
      <h3>{e(c['name'])}</h3>
      <div class="contractor-address">{address_html}</div>
      {phone_html}
      {website_html}
    </div>''')

    # JSON for search
    search_data = json.dumps([
        {'name': c['name'].lower(), 'city': c['city'].lower(), 'zip': c['zip']}
        for c in items
    ])

    # Build schema markup
    schema_json = build_schema_local_business(items, state_name)

    # State-specific content section
    climate_text = state_info.get('climate', '')
    licensing_text = state_info.get('licensing', '')
    avg_cost_text = state_info.get('avg_cost', '')
    materials_text = state_info.get('popular_materials', '')

    state_content = ''
    if climate_text:
        state_content = f'''
<div class="section" style="padding-bottom:0;">
  <div class="content-block animate-in">
    <h2>Roofing in {e(state_name)}: What You Need to Know</h2>
    <p>{climate_text}</p>
    <p>{licensing_text}</p>
  </div>
  <div class="content-block animate-in">
    <h3>Average Roof Replacement Cost in {e(state_name)}</h3>
    <p>{avg_cost_text} For a detailed breakdown by material type, see our <a href="../roof-replacement-cost.html">roof replacement cost guide</a>. Compare <a href="../shingles.html">asphalt shingles</a> and <a href="../metal-roofing.html">metal roofing</a> to choose the right material for your {e(state_name)} home.</p>
  </div>
  <div class="content-block animate-in">
    <h3>Popular Roofing Materials in {e(state_name)}</h3>
    <p>{materials_text} Need help choosing? Our <a href="../best-roofing-materials.html">complete materials comparison</a> covers every option. Make sure proper <a href="../underlayment.html">underlayment</a> is part of the job.</p>
  </div>
</div>
'''

    # Unique meta description
    meta_desc = f'Compare {count} roofing contractors in {e(state_name)} with ratings, reviews, and contact info. {avg_cost_text.split(".")[0] + "." if avg_cost_text else ""}'

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
{GA4_SCRIPT}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{count} Best Roofing Contractors in {e(state_name)} (2026)</title>
  <meta name="description" content="{e(meta_desc)}">
  <meta property="og:title" content="{count} Best Roofing Contractors in {e(state_name)} (2026)">
  <meta property="og:description" content="Compare {count} roofing contractors in {e(state_name)}. Ratings, reviews, and contact info.">
  <meta property="og:type" content="website">
  <meta property="og:image" content="https://skilledroofer.com/img/41.jpg">
  <meta property="og:url" content="https://skilledroofer.com/directory/{slug(state_name)}.html">
  <link rel="canonical" href="https://skilledroofer.com/directory/{slug(state_name)}.html">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css">
</head>
<body>

{nav_html('directory', '../')}

<!-- Page Header -->
<div class="page-header">
  <div class="page-header-content">
    <div class="hero-badge">Contractor Directory</div>
    <h1>{count} Best Roofing Contractors in <span class="highlight">{e(state_name)}</span></h1>
    <p>Compare {count} verified roofing contractors in {e(state_name)} with ratings, reviews, and contact information.</p>
  </div>
</div>
{state_content}
<div class="section">
  <div class="directory-search">
    <input type="text" id="contractorSearch" placeholder="Search by business name, city, or zip..." oninput="filterContractors()">
  </div>
  <div class="directory-count" id="contractorCount">Showing all <strong>{count}</strong> contractors in {e(state_name)}</div>

  <div class="contractor-grid" id="contractorGrid">
{chr(10).join(cards)}
  </div>
  <div class="no-results" id="noResults" style="display:none;">No contractors found matching your search.</div>
</div>

<div class="section" style="padding-top:0;">
  <div class="content-block animate-in">
    <h3>How to Choose a Roofing Contractor in {e(state_name)}</h3>
    <p>Before hiring, verify the contractor is properly licensed in {e(state_name)}, carries liability insurance and workers' compensation, and can provide recent local references. Get at least three written estimates and never pay more than 30% upfront. For a complete vetting checklist, read our <a href="../find-roofing-contractor.html">guide to finding a roofing contractor</a>.</p>
  </div>
  <a href="../directory.html" class="btn btn-outline">&#8592; Back to All States</a>
</div>

{footer_html('../')}

{GSAP_SCRIPT}
<script>
const searchData = {search_data};
function filterContractors() {{
  const q = document.getElementById('contractorSearch').value.toLowerCase().trim();
  const grid = document.getElementById('contractorGrid');
  const cards = grid.querySelectorAll('.contractor-card');
  let shown = 0;
  searchData.forEach((s, i) => {{
    const match = !q || s.name.includes(q) || s.city.includes(q) || s.zip.includes(q);
    cards[i].style.display = match ? '' : 'none';
    if (match) shown++;
  }});
  document.getElementById('contractorCount').innerHTML =
    'Showing <strong>' + shown + '</strong> contractor' + (shown !== 1 ? 's' : '') + ' in {e(state_name)}';
  document.getElementById('noResults').style.display = shown === 0 ? '' : 'none';
}}
</script>

<script type="application/ld+json">
{schema_json}
</script>

</body>
</html>'''
    return page


# ── MAIN ─────────────────────────────────────────────────────────────
def main():
    import sys
    skip_hub = '--states-only' in sys.argv

    print('Reading CSV...')
    contractors, total = read_csv()
    print(f'Found {total} contractors across {len(contractors)} states.')

    # Ensure directory/ folder exists
    dir_path = os.path.join(OUT_DIR, 'directory')
    os.makedirs(dir_path, exist_ok=True)

    if not skip_hub:
        print('Skipping hub page (use without --states-only to rebuild).')
        print('Hub page (directory.html) has been manually enhanced - not overwriting.')
    else:
        print('--states-only flag detected. Skipping hub page regeneration.')

    # Build state pages
    for state_name in sorted(contractors.keys()):
        items = contractors[state_name]
        page = build_state_page(state_name, items)
        page_path = os.path.join(dir_path, f'{slug(state_name)}.html')
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page)
        print(f'  {slug(state_name)}.html - {len(items)} contractors')

    print(f'\nDone! Generated {len(contractors)} state pages.')


if __name__ == '__main__':
    main()
