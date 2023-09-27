import configparser
import logging
import textwrap
from datetime import datetime
from typing import Dict, List

import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


# pylint: disable=too-many-branches,line-too-long,C0302
# flake8: noqa


d_SectorSubsectorIndustry = {
    "All Sectors (except Funds)": "sic1=-1&sicl=100&sich=9999",
    "Agriculture, Forestry, Fish": "sic1=1&sic2=1&sicl=100&sich=199",
    "Agriculture, Forestry, Fish -> Crops": "sic1=1&sic2=1&sicl=100&sich=199",
    "Agriculture, Forestry, Fish -> Livestock & Animal Specialties": "sic1=1&sic2=2&sicl=200&sich=699",
    "Agriculture, Forestry, Fish -> Agriculture Services": "sic1=1&sic2=7&sicl=700&sich=799",
    "Agriculture, Forestry, Fish -> Forestry": "sic1=1&sic2=8&sicl=800&sich=899",
    "Agriculture, Forestry, Fish -> Fishing, Hunting & Trapping": "sic1=1&sic2=9&sicl=900&sich=999",
    "Mining": "sic1=10&sic2=0&sicl=1000&sich=1499",
    "Mining -> Metal Mining": "sic1=10&sic2=10&sic3=1000&sicl=1000&sich=1039",
    "Mining -> Metal Mining -> Gold & Silver Ores": "sic1=10&sic2=10&sic3=1040&sicl=1040&sich=1089",
    "Mining -> Metal Mining -> Miscellaneous Metal Ores": "sic1=10&sic2=10&sic3=1090&sicl=1090&sich=1219",
    "Mining -> Coal Mining": "sic1=10&sic2=12&sic3=0&sicl=1200&sich=1299",
    "Mining -> Coal Mining -> Bituminous Coal & Lignite Mining": "sic1=10&sic2=12&sic3=1220&sicl=1220&sich=1220",
    "Mining -> Coal Mining -> Bituminous Coal & Lignite Surfac": "sic1=10&sic2=12&sic3=1221&sicl=1221&sich=1310",
    "Mining -> Oil & Gas Extraction": "sic1=10&sic2=13&sic3=0&sicl=1300&sich=1399",
    "Mining -> Oil & Gas Extraction -> Crude Petroleum & Natural Gas": "sic1=10&sic2=13&sic3=1311&sicl=1311&sich=1380",
    "Mining -> Oil & Gas Extraction -> Drilling Oil & Gas Wells": "sic1=10&sic2=13&sic3=1381&sicl=1381&sich=1381",
    "Mining -> Oil & Gas Extraction -> Oil & Gas Field Exploration Serv": "sic1=10&sic2=13&sic3=1382&sicl=1382&sich=1388",
    "Mining -> Oil & Gas Extraction -> Oil & Gas Field Services": "sic1=10&sic2=13&sic3=1389&sicl=1389&sich=1399",
    "Mining -> Mining Non-metallic Minerals": "sic1=10&sic2=14&sicl=1400&sich=1519",
    "Construction": "sic1=15&sic2=0&sicl=1500&sich=1799",
    "Construction -> General Contractors & Builders": "sic1=15&sic2=15&sicl=1500&sich=1599",
    "Construction -> General Contractors & Builders -> Residential Bldg Contractors": "sic1=15&sic2=15&sic3=1520&sicl=1520&sich=1530",
    "Construction -> General Contractors & Builders -> Operative Builders": "sic1=15&sic2=15&sic3=1531&sicl=1531&sich=1539",
    "Construction -> General Contractors & Builders -> Nonresidential Bldg Contractors": "sic1=15&sic2=15&sic3=1540&sicl=1540&sich=1599",
    "Construction -> Heavy Construction": "sic1=15&sic2=16&sic3=0&sicl=1600&sich=1699",
    "Construction -> Heavy Construction -> Heavy Construction Non-Bldg Cont": "sic1=15&sic2=16&sic3=1600&sicl=1600&sich=1622",
    "Construction -> Heavy Construction -> Water, Sewer, Pipeline, Comm & P": "sic1=15&sic2=16&sic3=1623&sicl=1623&sich=1699",
    "Construction -> Special Trade Contractors": "sic1=15&sic2=17&sic3=0&sicl=1700&sich=1999",
    "Construction -> Special Trade Contractors -> Special Trade Contractors": "sic1=15&sic2=17&sic3=1700&sicl=1700&sich=1730",
    "Construction -> Special Trade Contractors -> Electrical Work": "sic1=15&sic2=17&sic3=1731&sicl=1731&sich=1999",
    "Manufacturing": "sic1=20&sic2=0&sicl=2000&sich=3999",
    "Manufacturing -> Food": "sic1=20&sic2=20&sic3=0&sicl=2000&sich=2099",
    "Manufacturing -> Food -> Food & Kindred Products": "sic1=20&sic2=20&sic3=2000&sicl=2000&sich=2010",
    "Manufacturing -> Food -> Meat Packing Plants": "sic1=20&sic2=20&sic3=2011&sicl=2011&sich=2012",
    "Manufacturing -> Food -> Sausage & Other Prepared Meat P": "sic1=20&sic2=20&sic3=2013&sicl=2013&sich=2014",
    "Manufacturing -> Food -> Poultry Slaughtering & Processing": "sic1=20&sic2=20&sic3=2015&sicl=2015&sich=2019",
    "Manufacturing -> Food -> Dairy Products": "sic1=20&sic2=20&sic3=2020&sicl=2020&sich=2023",
    "Manufacturing -> Food ->  Ice Cream & Froze Desserts": "sic1=20&sic2=20&sic3=2024&sicl=2024&sich=2029",
    "Manufacturing -> Food -> Canned, Frozen & Preserved Fruit": "sic1=20&sic2=20&sic3=2030&sicl=2030&sich=2032",
    "Manufacturing -> Food -> Canned, Fruits, Veg, Preserves": "sic1=20&sic2=20&sic3=2033&sicl=2033&sich=2039",
    "Manufacturing -> Food -> Grain Mill Products": "sic1=20&sic2=20&sic3=2040&sicl=2040&sich=2049",
    "Manufacturing -> Food ->  Bakery Products": "sic1=20&sic2=20&sic3=2050&sicl=2050&sich=2051",
    "Manufacturing -> Food -> Cookies & Crackers": "sic1=20&sic2=20&sic3=2052&sicl=2052&sich=2059",
    "Manufacturing -> Food -> Sugar & Confectionery Products": "sic1=20&sic2=20&sic3=2060&sicl=2060&sich=2069",
    "Manufacturing -> Food -> Fats & Oils": "sic1=20&sic2=20&sic3=2070&sicl=2070&sich=2079",
    "Manufacturing -> Food -> Beverages": "sic1=20&sic2=20&sic3=2080&sicl=2080&sich=2081",
    "Manufacturing -> Food -> Malt Beverages": "sic1=20&sic2=20&sic3=2082&sicl=2082&sich=2085",
    "Manufacturing -> Food -> Bottled & Canned Soft Drinks & C": "sic1=20&sic2=20&sic3=2086&sicl=2086&sich=2089",
    "Manufacturing -> Food -> Miscellaneous Food Preparations": "sic1=20&sic2=20&sic3=2090&sicl=2090&sich=2091",
    "Manufacturing -> Food -> Prepared Fresh or Frozen Fish &": "sic1=20&sic2=20&sic3=2092&sicl=2092&sich=2099",
    "Manufacturing -> Tobacco": "sic1=20&sic2=21&sic3=0&sicl=2100&sich=2199",
    "Manufacturing -> Tobacco -> Tobacco Products": "sic1=20&sic2=21&sic3=2100&sicl=2100&sich=2110",
    "Manufacturing -> Tobacco -> Cigarettes": "sic1=20&sic2=21&sic3=2111&sicl=2111&sich=2199",
    "Manufacturing -> Textile Mill Products": "sic1=20&sic2=22&sic3=0&sicl=2200&sich=2299",
    "Manufacturing -> Textile Mill Products -> Textile Mill Products": "sic1=20&sic2=22&sic3=2200&sicl=2200&sich=2210",
    "Manufacturing -> Textile Mill Products -> Broadwoven Fabric Mills, Cotton": "sic1=20&sic2=22&sic3=2211&sicl=2211&sich=2220",
    "Manufacturing -> Textile Mill Products -> Broadwoven Fabric Mills, Man Mad": "sic1=20&sic2=22&sic3=2221&sicl=2221&sich=2249",
    "Manufacturing -> Textile Mill Products -> Knitting Mills": "sic1=20&sic2=22&sic3=2250&sicl=2250&sich=2252",
    "Manufacturing -> Textile Mill Products -> Knit Outerwear Mills": "sic1=20&sic2=22&sic3=2253&sicl=2253&sich=2272",
    "Manufacturing -> Textile Mill Products -> Carpets & Rugs": "sic1=20&sic2=22&sic3=2273&sicl=2273&sich=2299",
    "Manufacturing -> Apparel": "sic1=20&sic2=23&sic3=0&sicl=2300&sich=2399",
    "Manufacturing -> Apparel -> Other Finished Prods of": "sic1=20&sic2=23&sic3=2300&sicl=2300&sich=2319",
    "Manufacturing -> Apparel -> Men’s & Boy’s Furnishings, Work Cl": "sic1=20&sic2=23&sic3=2320&sicl=2320&sich=2329",
    "Manufacturing -> Apparel -> Women’s, Misses’, & Juniors Oute": "sic1=20&sic2=23&sic3=2330&sicl=2330&sich=2339",
    "Manufacturing -> Apparel -> Women’s, Misses’, Children’s & l": "sic1=20&sic2=23&sic3=2340&sicl=2340&sich=2389",
    "Manufacturing -> Apparel -> Miscellaneous Fabric": "sic1=20&sic2=23&sic3=2390&sicl=2390&sich=2399",
    "Manufacturing -> Lumber": "sic1=20&sic2=24&sic3=0&sicl=2400&sich=2499",
    "Manufacturing -> Lumber -> Lumber & Wood Products (No Furni)": "sic1=20&sic2=24&sic3=2400&sicl=2400&sich=2420",
    "Manufacturing -> Lumber -> Sawmills & Planting Mills, Gener": "sic1=20&sic2=24&sic3=2421&sicl=2421&sich=2429",
    "Manufacturing -> Lumber -> Millwood, Veneer, Plywood & Str": "sic1=20&sic2=24&sic3=2430&sicl=2430&sich=2450",
    "Manufacturing -> Lumber -> Mobile Homes": "sic1=20&sic2=24&sic3=2451&sicl=2451&sich=2451",
    "Manufacturing -> Lumber -> Prefabricated Wood Buildings & Compo": "sic1=20&sic2=24&sic3=2452&sicl=2452&sich=2509",
    "Manufacturing -> Furniture": "sic1=20&sic2=25&sic3=0&sicl=2500&sich=2599",
    "Manufacturing -> Furniture -> Household Furniture": "sic1=20&sic2=25&sic3=2510&sicl=2510&sich=2510",
    "Manufacturing -> Furniture -> Wood Household Furniture, (no Up)": "sic1=20&sic2=25&sic3=2511&sicl=2511&sich=2519",
    "Manufacturing -> Furniture -> Office Furniture": "sic1=20&sic2=25&sic3=2520&sicl=2520&sich=2521",
    "Manufacturing -> Furniture -> Office Furniture (No Wood)": "sic1=20&sic2=25&sic3=2522&sicl=2522&sich=2530",
    "Manufacturing -> Furniture -> Public Bldg & Related Furniture": "sic1=20&sic2=25&sic3=2531&sicl=2531&sich=2539",
    "Manufacturing -> Furniture -> Partitions, Shelving, Lockers & O": "sic1=20&sic2=25&sic3=2540&sicl=2540&sich=2589",
    "Manufacturing -> Furniture -> Miscellaneous Furniture & Fixtures": "sic1=20&sic2=25&sic3=2590&sicl=2590&sich=2599",
    "Manufacturing -> Paper": "sic1=20&sic2=26&sic3=0&sicl=2600&sich=2699",
    "Manufacturing -> Paper -> Papers & Allied Products": "sic1=20&sic2=26&sic3=2600&sicl=2600&sich=2610",
    "Manufacturing -> Paper -> Pulp Mills": "sic1=20&sic2=26&sic3=2611&sicl=2611&sich=2620",
    "Manufacturing -> Paper -> Paper Mills": "sic1=20&sic2=26&sic3=2621&sicl=2621&sich=2630",
    "Manufacturing -> Paper -> Paperboard Mills": "sic1=20&sic2=26&sic3=2631&sicl=2631&sich=2649",
    "Manufacturing -> Paper -> Paperboard Containers & Boxes": "sic1=20&sic2=26&sic3=2650&sicl=2650&sich=2669",
    "Manufacturing -> Paper -> Converted Paper & Paperboard Pro": "sic1=20&sic2=26&sic3=2670&sicl=2670&sich=2672",
    "Manufacturing -> Paper -> Plastics, Foils & Coated Paper Ba": "sic1=20&sic2=26&sic3=2673&sicl=2673&sich=2710",
    "Manufacturing -> Printing & Publishing": "sic1=20&sic2=27&sic3=0&sicl=2700&sich=2799",
    "Manufacturing -> Printing & Publishing -> Newspapers: Publishing or Publishing and Printing": "sic1=20&sic2=27&sic3=2711&sicl=2711&sich=2720",
    "Manufacturing -> Printing & Publishing -> Periodicals: Publishing or Publishing and Printing": "sic1=20&sic2=27&sic3=2721&sicl=2721&sich=2730",
    "Manufacturing -> Printing & Publishing -> Books: Publishing or Publishing and Printing": "sic1=20&sic2=27&sic3=2731&sicl=2731&sich=2731",
    "Manufacturing -> Printing & Publishing -> Book Printing": "sic1=20&sic2=27&sic3=2732&sicl=2732&sich=2740",
    "Manufacturing -> Printing & Publishing -> Miscellaneous Publishing": "sic1=20&sic2=27&sic3=2741&sicl=2741&sich=2749",
    "Manufacturing -> Printing & Publishing -> Commercial Printing": "sic1=20&sic2=27&sic3=2750&sicl=2750&sich=2760",
    "Manufacturing -> Printing & Publishing -> Manifold Business Forms": "sic1=20&sic2=27&sic3=2761&sicl=2761&sich=2770",
    "Manufacturing -> Printing & Publishing -> Greeting Cards": "sic1=20&sic2=27&sic3=2771&sicl=2771&sich=2779",
    "Manufacturing -> Printing & Publishing -> Blankbooks, Looseleaf Binders &": "sic1=20&sic2=27&sic3=2780&sicl=2780&sich=2789",
    "Manufacturing -> Printing & Publishing ->Service Industries For The Print": "sic1=20&sic2=27&sic3=2790&sicl=2790&sich=2799",
    "Manufacturing -> Chemicals": "sic1=20&sic2=28&sic3=0&sicl=2800&sich=2899",
    "Manufacturing -> Chemicals -> Chemicals & Allied Products": "sic1=20&sic2=28&sic3=2800&sicl=2800&sich=2809",
    "Manufacturing -> Chemicals -> Industrial Inorganic Chemicals": "sic1=20&sic2=28&sic3=2810&sicl=2810&sich=2819",
    "Manufacturing -> Chemicals -> Plastic Material, Synth Resin/Ru": "sic1=20&sic2=28&sic3=2820&sicl=2820&sich=2820",
    "Manufacturing -> Chemicals -> Plastic Material, Synth Resins": "sic1=20&sic2=28&sic3=2821&sicl=2821&sich=2832",
    "Manufacturing -> Chemicals -> Medicinal Chemicals & Botanical": "sic1=20&sic2=28&sic3=2833&sicl=2833&sich=2833",
    "Manufacturing -> Chemicals -> Pharmaceutical Preparations": "sic1=20&sic2=28&sic3=2834&sicl=2834&sich=2834",
    "Manufacturing -> Chemicals -> In Vitro & In Vito Diagnostic Su": "sic1=20&sic2=28&sic3=2835&sicl=2835&sich=2835",
    "Manufacturing -> Chemicals -> Biological Products ,(No Diagnos": "sic1=20&sic2=28&sic3=2836&sicl=2836&sich=2839",
    "Manufacturing -> Chemicals -> Soap, Detergents, Cleaning, Perf": "sic1=20&sic2=28&sic3=2840&sicl=2840&sich=2841",
    "Manufacturing -> Chemicals -> Specialty Cleaning, Polishing &": "sic1=20&sic2=28&sic3=2842&sicl=2842&sich=2843",
    "Manufacturing -> Chemicals -> Perfumes, Cosmetics & Other Toil": "sic1=20&sic2=28&sic3=2844&sicl=2844&sich=2850",
    "Manufacturing -> Chemicals -> Paints, Varnishes, Lacquers, Ena": "sic1=20&sic2=28&sic3=2851&sicl=2851&sich=2859",
    "Manufacturing -> Chemicals -> Industrial Organic Chemicals": "sic1=20&sic2=28&sic3=2860&sicl=2860&sich=2869",
    "Manufacturing -> Chemicals ->Agriculture Chemicals": "sic1=20&sic2=28&sic3=2870&sicl=2870&sich=2889",
    "Manufacturing -> Chemicals -> Miscellaneous Chemical Products": "sic1=20&sic2=28&sic3=2890&sicl=2890&sich=2890",
    "Manufacturing -> Chemicals -> Adhesives & Sealants": "sic1=20&sic2=28&sic3=2891&sicl=2891&sich=2910",
    "Manufacturing -> Petroleum Refining": "sic1=20&sic2=29&sic3=0&sicl=2900&sich=2999",
    "Manufacturing -> Petroleum Refining -> Petroleum Refining": "sic1=20&sic2=29&sic3=2911&sicl=2911&sich=2949",
    "Manufacturing -> Petroleum Refining -> Asphalt Paving & Roofing Materia": "sic1=20&sic2=29&sic3=2950&sicl=2950&sich=2989",
    "Manufacturing -> Petroleum Refining -> Miscellaneous Products of Petrol": "sic1=20&sic2=29&sic3=2990&sicl=2990&sich=3010",
    "Manufacturing -> Rubber & Plastic": "sic1=20&sic2=30&sic3=0&sicl=3000&sich=3099",
    "Manufacturing -> Rubber & Plastic -> Tires & Inner Tubes": "sic1=20&sic2=30&sic3=3011&sicl=3011&sich=3020",
    "Manufacturing -> Rubber & Plastic -> Rubber & Plastics Footwear": "sic1=20&sic2=30&sic3=3021&sicl=3021&sich=3049",
    "Manufacturing -> Rubber & Plastic -> Gaskets & Packg & Sealg Devices &": "sic1=20&sic2=30&sic3=3050&sicl=3050&sich=3059",
    "Manufacturing -> Rubber & Plastic -> Fabricated Rubber Products": "sic1=20&sic2=30&sic3=3060&sicl=3060&sich=3079",
    "Manufacturing -> Rubber & Plastic -> Miscellaneous Plastics Products": "sic1=20&sic2=30&sic3=3080&sicl=3080&sich=3080",
    "Manufacturing -> Rubber & Plastic -> Unsupported Plastics Film & Shee": "sic1=20&sic2=30&sic3=3081&sicl=3081&sich=3085",
    "Manufacturing -> Rubber & Plastic -> Plastics Foam Products": "sic1=20&sic2=30&sic3=3086&sicl=3086&sich=3088",
    "Manufacturing -> Rubber & Plastic -> Plastics Products": "sic1=20&sic2=30&sic3=3089&sicl=3089&sich=3099",
    "Manufacturing -> Leather": "sic1=20&sic2=31&sic3=0&sicl=3100&sich=3199",
    "Manufacturing -> Leather -> Leather Products": "sic1=20&sic2=31&sic3=3100&sicl=3100&sich=3139",
    "Manufacturing -> Leather -> Footwear, (No Rubber)": "sic1=20&sic2=31&sic3=3140&sicl=3140&sich=3210",
    "Manufacturing -> Stone, Clay, Glass & Concrete": "sic1=20&sic2=32&sic3=0&sicl=3200&sich=3299",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Flat Glass": "sic1=20&sic2=32&sic3=3211&sicl=3211&sich=3219",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Glass & Glasswear, Pressed or Bl": "sic1=20&sic2=32&sic3=3220&sicl=3220&sich=3220",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Glass Containers": "sic1=20&sic2=32&sic3=3221&sicl=3221&sich=3230",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Glass Products Made of Purchase": "sic1=20&sic2=32&sic3=3231&sicl=3231&sich=3240",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Cements, Hydrallic": "sic1=20&sic2=32&sic3=3241&sicl=3241&sich=3249",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Structural Clay Products": "sic1=20&sic2=32&sic3=3250&sicl=3250&sich=3259",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Pottery & Related Products": "sic1=20&sic2=32&sic3=3260&sicl=3260&sich=3269",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Concreate, Gypsum & Plaster Production": "sic1=20&sic2=32&sic3=3270&sicl=3270&sich=3271",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Concrete Products, Except Block": "sic1=20&sic2=32&sic3=3272&sicl=3272&sich=3280",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Cut Stone & Stone Products": "sic1=20&sic2=32&sic3=3281&sicl=3281&sich=3289",
    "Manufacturing -> Stone, Clay, Glass & Concrete -> Abrasive, Asbestos & Misc Nonmet": "sic1=20&sic2=32&sic3=3290&sicl=3290&sich=3309",
    "Manufacturing -> Primary Metal": "sic1=20&sic2=33&sic3=0&sicl=3300&sich=3399",
    "Manufacturing -> Primary Metal -> Steel Works, Blast Furnaces & Ro": "sic1=20&sic2=33&sic3=3310&sicl=3310&sich=3311",
    "Manufacturing -> Primary Metal -> Steel Works, Blast Furnaces & R": "sic1=20&sic2=33&sic3=3312&sicl=3312&sich=3316",
    "Manufacturing -> Primary Metal -> Steel Pipe & Tubes": "sic1=20&sic2=33&sic3=3317&sicl=3317&sich=3319",
    "Manufacturing -> Primary Metal -> Iron & Steel Foundries": "sic1=20&sic2=33&sic3=3320&sicl=3320&sich=3329",
    "Manufacturing -> Primary Metal -> Primary Smelting & Refining of N": "sic1=20&sic2=33&sic3=3330&sicl=3330&sich=3333",
    "Manufacturing -> Primary Metal -> Primary Production of Aluminium": "sic1=20&sic2=33&sic3=3334&sicl=3334&sich=3340",
    "Manufacturing -> Primary Metal -> Secondary Smelting & Refining of": "sic1=20&sic2=33&sic3=3341&sicl=3341&sich=3349",
    "Manufacturing -> Primary Metal -> Rolling Drawing & Extruding of N": "sic1=20&sic2=33&sic3=3350&sicl=3350&sich=3356",
    "Manufacturing -> Primary Metal -> Drawing & Insulating of Non Ferro": "sic1=20&sic2=33&sic3=3357&sicl=3357&sich=3359",
    "Manufacturing -> Primary Metal -> Nonferrous Foundries (Castings)": "sic1=20&sic2=33&sic3=3360&sicl=3360&sich=3389",
    "Manufacturing -> Primary Metal -> Miscellaneous Primary Metal Prod": "sic1=20&sic2=33&sic3=3390&sicl=3390&sich=3410",
    "Manufacturing -> Fabricated Metal Products": "sic1=20&sic2=34&sic3=0&sicl=3400&sich=3499",
    "Manufacturing -> Fabricated Metal Products -> Metal Cans": "sic1=20&sic2=34&sic3=3411&sicl=3411&sich=3411",
    "Manufacturing -> Fabricated Metal Products -> Metal Shipping Barrels, Drums, K": "sic1=20&sic2=34&sic3=3412&sicl=3412&sich=3419",
    "Manufacturing -> Fabricated Metal Products -> Cutlery, Handtools & General Har": "sic1=20&sic2=34&sic3=3420&sicl=3420&sich=3429",
    "Manufacturing -> Fabricated Metal Products -> Hearing Equip, Except Elec & War": "sic1=20&sic2=34&sic3=3430&sicl=3430&sich=3432",
    "Manufacturing -> Fabricated Metal Products ->  Heating Equipment, Except Electr": "sic1=20&sic2=34&sic3=3433&sicl=3433&sich=3439",
    "Manufacturing -> Fabricated Metal Products -> Fabricated Structural Metal Prod": "sic1=20&sic2=34&sic3=3440&sicl=3440&sich=3441",
    "Manufacturing -> Fabricated Metal Products -> Metal Doors, Sash, Frames, Moldi": "sic1=20&sic2=34&sic3=3442&sicl=3442&sich=3442",
    "Manufacturing -> Fabricated Metal Products -> Fabricated Plate Work (Boiler Sh": "sic1=20&sic2=34&sic3=3443&sicl=3443&sich=3443",
    "Manufacturing -> Fabricated Metal Products -> Sheet Metal Work": "sic1=20&sic2=34&sic3=3444&sicl=3444&sich=3447",
    "Manufacturing -> Fabricated Metal Products -> Prefabricated Metal Buildings &": "sic1=20&sic2=34&sic3=3448&sicl=3448&sich=3450",
    "Manufacturing -> Fabricated Metal Products -> Screw Machine Products": "sic1=20&sic2=34&sic3=3451&sicl=3451&sich=3451",
    "Manufacturing -> Fabricated Metal Products -> Bolts, Nuts, Screws, Rivets & Wa": "sic1=20&sic2=34&sic3=3452&sicl=3452&sich=3459",
    "Manufacturing -> Fabricated Metal Products -> Metal Forgings & Stampings": "sic1=20&sic2=34&sic3=3460&sicl=3460&sich=3469",
    "Manufacturing -> Fabricated Metal Products -> Coating, Engraving & Allied Serv": "sic1=20&sic2=34&sic3=3470&sicl=3470&sich=3479",
    "Manufacturing -> Fabricated Metal Products -> Ordnance & Accessories, (No Vehi": "sic1=20&sic2=34&sic3=3480&sicl=3480&sich=3489",
    "Manufacturing -> Fabricated Metal Products -> Miscellaneous Fabricated Metal P": "sic1=20&sic2=34&sic3=3490&sicl=3490&sich=3509",
    "Manufacturing -> Ind Machinery & Computers": "sic1=20&sic2=35&sicl=3500&sich=3599",
    "Manufacturing -> Ind Machinery & Computers -> Engines & Turbines": "sic1=20&sic2=35&sic3=3510&sicl=3510&sich=3522",
    "Manufacturing -> Ind Machinery & Computers -> Farm Machinery & Equipment": "sic1=20&sic2=35&sic3=3523&sicl=3523&sich=3523",
    "Manufacturing -> Ind Machinery & Computers -> Lawn & Garden Tractors & Home La": "sic1=20&sic2=35&sic3=3524&sicl=3524&sich=3529",
    "Manufacturing -> Ind Machinery & Computers -> Construction, Mining & Materials": "sic1=20&sic2=35&sic3=3530&sicl=3530&sich=3530",
    "Manufacturing -> Ind Machinery & Computers -> Construction Machinery & Equip": "sic1=20&sic2=35&sic3=3531&sicl=3531&sich=3531",
    "Manufacturing -> Ind Machinery & Computers -> Mining Machinery & Equip (No Oil": "sic1=20&sic2=35&sic3=3532&sicl=3532&sich=3532",
    "Manufacturing -> Ind Machinery & Computers -> Oil & Gas Field Machinery & Equi": "sic1=20&sic2=35&sic3=3533&sicl=3533&sich=3536",
    "Manufacturing -> Ind Machinery & Computers -> Industrial Trucks, Tractors, Tra": "sic1=20&sic2=35&sic3=3537&sicl=3537&sich=3539",
    "Manufacturing -> Ind Machinery & Computers -> Metalworking Machinery & Equipment": "sic1=20&sic2=35&sic3=3540&sicl=3540&sich=3540",
    "Manufacturing -> Ind Machinery & Computers -> Machine Tools, Metal Cutting Typ": "sic1=20&sic2=35&sic3=3541&sicl=3541&sich=3549",
    "Manufacturing -> Ind Machinery & Computers -> Special Industry Machinery (No M": "sic1=20&sic2=35&sic3=3550&sicl=3550&sich=3554",
    "Manufacturing -> Ind Machinery & Computers -> Printing Trades Machinery & Equi": "sic1=20&sic2=35&sic3=3555&sicl=3555&sich=3558",
    "Manufacturing -> Ind Machinery & Computers -> Special Industry Machinery": "sic1=20&sic2=35&sic3=3559&sicl=3559&sich=3559",
    "Manufacturing -> Ind Machinery & Computers -> General Industrial Machinery & E": "sic1=20&sic2=35&sic3=3560&sicl=3560&sich=3560",
    "Manufacturing -> Ind Machinery & Computers -> Pumps & Pumping Equipment": "sic1=20&sic2=35&sic3=3561&sicl=3561&sich=3561",
    "Manufacturing -> Ind Machinery & Computers -> Ball & Roller Bearings": "sic1=20&sic2=35&sic3=3562&sicl=3562&sich=3563",
    "Manufacturing -> Ind Machinery & Computers -> Industrial & Commercial Fans & B": "sic1=20&sic2=35&sic3=3564&sicl=3564&sich=3566",
    "Manufacturing -> Ind Machinery & Computers -> Industrial Process Furnaces & Ov": "sic1=20&sic2=35&sic3=3567&sicl=3567&sich=3568",
    # "Manufacturing -> Ind Machinery & Computers -> General Industrial Machinery & E": "sic1=20&sic2=35&sic3=3569&sicl=3569&sich=3569",
    "Manufacturing -> Ind Machinery & Computers -> Computer & Office Equipment": "sic1=20&sic2=35&sic3=3570&sicl=3570&sich=3570",
    "Manufacturing -> Ind Machinery & Computers -> Electronic Computers": "sic1=20&sic2=35&sic3=3571&sicl=3571&sich=3571",
    "Manufacturing -> Ind Machinery & Computers -> Computer Storage Devices": "sic1=20&sic2=35&sic3=3572&sicl=3572&sich=3574",
    "Manufacturing -> Ind Machinery & Computers -> Computer Terminals": "sic1=20&sic2=35&sic3=3575&sicl=3575&sich=3575",
    "Manufacturing -> Ind Machinery & Computers -> Computer Communications Equipmen": "sic1=20&sic2=35&sic3=3576&sicl=3576&sich=3576",
    "Manufacturing -> Ind Machinery & Computers -> Computer Peripheral Equipment": "sic1=20&sic2=35&sic3=3577&sicl=3577&sich=3577",
    "Manufacturing -> Ind Machinery & Computers -> Calculating & Accounting Machine": "sic1=20&sic2=35&sic3=3578&sicl=3578&sich=3578",
    "Manufacturing -> Ind Machinery & Computers -> Office Machines": "sic1=20&sic2=35&sic3=3579&sicl=3579&sich=3579",
    "Manufacturing -> Ind Machinery & Computers -> Refrigeration & Service Industry": "sic1=20&sic2=35&sic3=3580&sicl=3580&sich=3584",
    "Manufacturing -> Ind Machinery & Computers -> Air-Cond & Warm Air Heating Equip": "sic1=20&sic2=35&sic3=3585&sicl=3585&sich=3589",
    "Manufacturing -> Ind Machinery & Computers -> Misc Industrial & Commercial Mac": "sic1=20&sic2=35&sic3=3590&sicl=3590&sich=3599",
    "Manufacturing -> Electronics": "sic1=20&sic2=36&sic3=0&sicl=3600&sich=3699",
    "Manufacturing -> Electronics -> Electronic & Other Electrical Eq": "sic1=20&sic2=36&sic3=3600&sicl=3600&sich=3611",
    "Manufacturing -> Electronics -> Power, Distribution & Specialty": "sic1=20&sic2=36&sic3=3612&sicl=3612&sich=3612",
    "Manufacturing -> Electronics -> Switchgear & Switchboard Apparat": "sic1=20&sic2=36&sic3=3613&sicl=3613&sich=3619",
    "Manufacturing -> Electronics -> Electrical Industrial Apparatus": "sic1=20&sic2=36&sic3=3620&sicl=3620&sich=3620",
    "Manufacturing -> Electronics -> Motors & Generators": "sic1=20&sic2=36&sic3=3621&sicl=3621&sich=3629",
    "Manufacturing -> Electronics -> Household Appliances": "sic1=20&sic2=36&sic3=3630&sicl=3630&sich=3633",
    "Manufacturing -> Electronics -> Electric Housewares & Fans": "sic1=20&sic2=36&sic3=3634&sicl=3634&sich=3639",
    "Manufacturing -> Electronics -> Electric Lighting & Wiring Equip": "sic1=20&sic2=36&sic3=3640&sicl=3640&sich=3650",
    "Manufacturing -> Electronics -> Household Audio & Video Equipmen": "sic1=20&sic2=36&sic3=3651&sicl=3651&sich=3651",
    "Manufacturing -> Electronics -> Phonograph Records & Prerecorded": "sic1=20&sic2=36&sic3=3652&sicl=3652&sich=3660",
    "Manufacturing -> Electronics -> Telephone & Telegraph Apparatus": "sic1=20&sic2=36&sic3=3661&sicl=3661&sich=3662",
    "Manufacturing -> Electronics -> Radio & Tv Broadcasting & Commun": "sic1=20&sic2=36&sic3=3663&sicl=3663&sich=3668",
    "Manufacturing -> Electronics -> Communications Equipment": "sic1=20&sic2=36&sic3=3669&sicl=3669&sich=3669",
    "Manufacturing -> Electronics -> Electronic Components & Accessor": "sic1=20&sic2=36&sic3=3670&sicl=3670&sich=3671",
    "Manufacturing -> Electronics -> Printed Circuit Boards": "sic1=20&sic2=36&sic3=3672&sicl=3672&sich=3673",
    "Manufacturing -> Electronics -> Semiconductors & Related Devices": "sic1=20&sic2=36&sic3=3674&sicl=3674&sich=3676",
    "Manufacturing -> Electronics -> Electronic Coils & Transformers &": "sic1=20&sic2=36&sic3=3677&sicl=3677&sich=3677",
    "Manufacturing -> Electronics -> Electronic Connectors": "sic1=20&sic2=36&sic3=3678&sicl=3678&sich=3678",
    "Manufacturing -> Electronics -> Electronic Components": "sic1=20&sic2=36&sic3=3679&sicl=3679&sich=3689",
    "Manufacturing -> Electronics -> Miscellaneous Electrical Machine": "sic1=20&sic2=36&sic3=3690&sicl=3690&sich=3694",
    "Manufacturing -> Electronics -> Magnetic & Optical Recording Med": "sic1=20&sic2=36&sic3=3695&sicl=3695&sich=3710",
    "Manufacturing -> Transportation Equipment": "sic1=20&sic2=37&sic3=0&sicl=3700&sich=3799",
    "Manufacturing -> Transportation Equipment -> Motor Vehicles & Passenger Car B": "sic1=20&sic2=37&sic3=3711&sicl=3711&sich=3712",
    "Manufacturing -> Transportation Equipment -> Truck & Bus Bodies": "sic1=20&sic2=37&sic3=3713&sicl=3713&sich=3713",
    "Manufacturing -> Transportation Equipment -> Motor Vehicle Parts & Accessories": "sic1=20&sic2=37&sic3=3714&sicl=3714&sich=3714",
    "Manufacturing -> Transportation Equipment -> Truck Trailers": "sic1=20&sic2=37&sic3=3715&sicl=3715&sich=3715",
    "Manufacturing -> Transportation Equipment -> Motor Homes": "sic1=20&sic2=37&sic3=3716&sicl=3716&sich=3719",
    "Manufacturing -> Transportation Equipment -> Aircraft & Parts": "sic1=20&sic2=37&sic3=3720&sicl=3720&sich=3720",
    "Manufacturing -> Transportation Equipment -> Aircraft": "sic1=20&sic2=37&sic3=3721&sicl=3721&sich=3723",
    "Manufacturing -> Transportation Equipment -> Aircraft Engines & Engine Parts": "sic1=20&sic2=37&sic3=3724&sicl=3724&sich=3727",
    "Manufacturing -> Transportation Equipment -> Aircraft Parts & Auxiliary Equip": "sic1=20&sic2=37&sic3=3728&sicl=3728&sich=3729",
    "Manufacturing -> Transportation Equipment -> Ship & Boat Building & Repairing": "sic1=20&sic2=37&sic3=3730&sicl=3730&sich=3742",
    "Manufacturing -> Transportation Equipment -> Railroad Equipment": "sic1=20&sic2=37&sic3=3743&sicl=3743&sich=3750",
    "Manufacturing -> Transportation Equipment -> Motorcycles, Bicycles & Parts": "sic1=20&sic2=37&sic3=3751&sicl=3751&sich=3759",
    "Manufacturing -> Transportation Equipment ->  Guided Missiles & Space Vehicles": "sic1=20&sic2=37&sic3=3760&sicl=3760&sich=3789",
    "Manufacturing -> Transportation Equipment -> Miscellaneous Transportation Equ": "sic1=20&sic2=37&sic3=3790&sicl=3790&sich=3811",
    "Manufacturing -> Specialty Instruments": "sic1=20&sic2=38&sicl=3800&sich=3899",
    "Manufacturing -> Specialty Instruments -> Search, Detection, Navigation": "sic1=20&sic2=38&sic3=3812&sicl=3812&sich=3820",
    "Manufacturing -> Specialty Instruments -> Laboratory Apparatus & Furniture": "sic1=20&sic2=38&sic3=3821&sicl=3821&sich=3821",
    "Manufacturing -> Specialty Instruments -> Auto Controls For Regulating Res": "sic1=20&sic2=38&sic3=3822&sicl=3822&sich=3822",
    "Manufacturing -> Specialty Instruments -> Industrial Instruments For Measurement": "sic1=20&sic2=38&sic3=3823&sicl=3823&sich=3823",
    "Manufacturing -> Specialty Instruments -> Totalizing Fluid Meter and Counting Device Manufacturing": "sic1=20&sic2=38&sic3=3824&sicl=3824&sich=3824",
    "Manufacturing -> Specialty Instruments -> Instruments For Meas & Testing o": "sic1=20&sic2=38&sic3=3825&sicl=3825&sich=3825",
    "Manufacturing -> Specialty Instruments -> Laboratory Analytical Instrument": "sic1=20&sic2=38&sic3=3826&sicl=3826&sich=3826",
    "Manufacturing -> Specialty Instruments -> Optical Instruments & Lenses": "sic1=20&sic2=38&sic3=3827&sicl=3827&sich=3828",
    "Manufacturing -> Specialty Instruments -> Measuring & Controlling Devices": "sic1=20&sic2=38&sic3=3829&sicl=3829&sich=3840",
    "Manufacturing -> Specialty Instruments -> Surgical & Medical Instruments &": "sic1=20&sic2=38&sic3=3841&sicl=3841&sich=3841",
    "Manufacturing -> Specialty Instruments -> Orthopedic, Prosthetic & Surgical": "sic1=20&sic2=38&sic3=3842&sicl=3842&sich=3842",
    "Manufacturing -> Specialty Instruments -> Dental Equipment & Supplies": "sic1=20&sic2=38&sic3=3843&sicl=3843&sich=3843",
    "Manufacturing -> Specialty Instruments -> X-Ray Apparatus & Tubes & Relate": "sic1=20&sic2=38&sic3=3844&sicl=3844&sich=3844",
    "Manufacturing -> Specialty Instruments -> Electromedical and Electrotherapeutic Apparatus": "sic1=20&sic2=38&sic3=3845&sicl=3845&sich=3850",
    "Manufacturing -> Specialty Instruments -> Ophthalmic Goods": "sic1=20&sic2=38&sic3=3851&sicl=3851&sich=3860",
    "Manufacturing -> Specialty Instruments -> Photographic Equipment & Supplie": "sic1=20&sic2=38&sic3=3861&sicl=3861&sich=3872",
    "Manufacturing -> Specialty Instruments -> Watches, Clocks, Clockwork Opera": "sic1=20&sic2=38&sic3=3873&sicl=3873&sich=3909",
    "Manufacturing -> Miscellaneous Manufacturing": "sic1=20&sic2=39&sic3=0&sicl=3900&sich=3999",
    "Manufacturing -> Miscellaneous Manufacturing -> Jewelry, Silverware & Plated War": "sic1=20&sic2=39&sic3=3910&sicl=3910&sich=3910",
    "Manufacturing -> Miscellaneous Manufacturing -> Jewelry, Precious Metal": "sic1=20&sic2=39&sic3=3911&sicl=3911&sich=3930",
    "Manufacturing -> Miscellaneous Manufacturing -> Musical Instruments": "sic1=20&sic2=39&sic3=3931&sicl=3931&sich=3941",
    "Manufacturing -> Miscellaneous Manufacturing -> Dolls & Stuffed Toys": "sic1=20&sic2=39&sic3=3942&sicl=3942&sich=3943",
    "Manufacturing -> Miscellaneous Manufacturing -> Games, Toys & Children’s Vehicle": "sic1=20&sic2=39&sic3=3944&sicl=3944&sich=3948",
    "Manufacturing -> Miscellaneous Manufacturing -> Sporting & Athletic Goods": "sic1=20&sic2=39&sic3=3949&sicl=3949&sich=3949",
    "Manufacturing -> Miscellaneous Manufacturing -> Pens, Pencils & Other Artists’ M": "sic1=20&sic2=39&sic3=3950&sicl=3950&sich=3959",
    "Manufacturing -> Miscellaneous Manufacturing -> Costumes Jewelry & Novelties": "sic1=20&sic2=39&sic3=3960&sicl=3960&sich=3989",
    "Manufacturing -> Miscellaneous Manufacturing -> Miscellaneous Manufacturing Indu": "sic1=20&sic2=39&sic3=3990&sicl=3990&sich=4010",
    "Transportation & Utilities": "sic1=40&sic2=0&sicl=4000&sich=4999",
    "Transportation & Utilities -> Railroads": "sic1=40&sic2=40&sicl=4000&sich=4099",
    "Transportation & Utilities -> Railroads -> Railroads, Line-Haul Operating": "sic1=40&sic2=40&sic3=4011&sicl=4011&sich=4012",
    "Transportation & Utilities -> Railroads -> Railroad Switching & Terminal Es": "sic1=40&sic2=40&sic3=4013&sicl=4013&sich=4099",
    "Transportation & Utilities -> Passenger Road Transportation": "sic1=40&sic2=41&sicl=4100&sich=4209",
    "Transportation & Utilities -> Road Freight Transportation": "sic1=40&sic2=42&sic3=0&sicl=4200&sich=4299",
    "Transportation & Utilities -> Road Freight Transportation -> Trucking & Courier Services (No": "sic1=40&sic2=42&sic3=4210&sicl=4210&sich=4212",
    "Transportation & Utilities -> Road Freight Transportation -> Trucking (No Local)": "sic1=40&sic2=42&sic3=4213&sicl=4213&sich=4219",
    "Transportation & Utilities -> Road Freight Transportation -> Public Warehousing & Storage": "sic1=40&sic2=42&sic3=4220&sicl=4220&sich=4230",
    "Transportation & Utilities -> Road Freight Transportation -> Terminal Maintenance Facilities": "sic1=40&sic2=42&sic3=4231&sicl=4231&sich=4399",
    "Transportation & Utilities -> USPS": "sic1=40&sic2=43&sicl=4300&sich=4399",
    "Transportation & Utilities -> Water Transportation": "sic1=40&sic2=44&sic3=0&sicl=4400&sich=4499",
    "Transportation & Utilities -> Water Transportation -> Water Transportation": "sic1=40&sic2=44&sic3=4400&sicl=4400&sich=4411",
    "Transportation & Utilities -> Water Transportation -> Deep Sea Foreign Transportation": "sic1=40&sic2=44&sic3=4412&sicl=4412&sich=4511",
    "Transportation & Utilities -> Air Transportation": "sic1=40&sic2=45&sic3=0&sicl=4500&sich=4599",
    "Transportation & Utilities -> Air Transportation -> Air Transportation, Scheduled": "sic1=40&sic2=45&sic3=4512&sicl=4512&sich=4512",
    "Transportation & Utilities -> Air Transportation -> Air Courier Services": "sic1=40&sic2=45&sic3=4513&sicl=4513&sich=4521",
    "Transportation & Utilities -> Air Transportation -> Air Transportation, Nonscheduled": "sic1=40&sic2=45&sic3=4522&sicl=4522&sich=4580",
    "Transportation & Utilities -> Air Transportation -> Airports, Flying Fields & Airpor": "sic1=40&sic2=45&sic3=4581&sicl=4581&sich=4609",
    "Transportation & Utilities -> Pipelines": "sic1=40&sic2=46&sicl=4610&sich=4699",
    "Transportation & Utilities -> Transportation Services": "sic1=40&sic2=47&sic3=0&sicl=4700&sich=4799",
    "Transportation & Utilities -> Transportation Services -> Transportation Services": "sic1=40&sic2=47&sic3=4700&sicl=4700&sich=4730",
    "Transportation & Utilities -> Transportation Services -> Arrangement of Transportation of": "sic1=40&sic2=47&sic3=4731&sicl=4731&sich=4811",
    "Transportation & Utilities -> Communications": "sic1=40&sic2=48&sic3=0&sicl=4800&sich=4899",
    "Transportation & Utilities -> Communications -> Radiotelephone Communications": "sic1=40&sic2=48&sic3=4812&sicl=4812&sich=4812",
    "Transportation & Utilities -> Communications -> Telephone Communications (No Rad": "sic1=40&sic2=48&sic3=4813&sicl=4813&sich=4821",
    "Transportation & Utilities -> Communications -> Telegraph & Other Message Commun": "sic1=40&sic2=48&sic3=4822&sicl=4822&sich=4831",
    "Transportation & Utilities -> Communications -> Radio Broadcasting Stations": "sic1=40&sic2=48&sic3=4832&sicl=4832&sich=4832",
    "Transportation & Utilities -> Communications -> Television Broadcasting Stations": "sic1=40&sic2=48&sic3=4833&sicl=4833&sich=4840",
    "Transportation & Utilities -> Communications -> Cable & Other Pay Television Ser": "sic1=40&sic2=48&sic3=4841&sicl=4841&sich=4898",
    "Transportation & Utilities -> Communications -> Communications Services": "sic1=40&sic2=48&sic3=4899&sicl=4899&sich=4899",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs": "sic1=40&sic2=49&sic3=0&sicl=4900&sich=4999",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Electric, Gas, & Sanitary Svcs": "sic1=40&sic2=49&sic3=4900&sicl=4900&sich=4910",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Electric Services": "sic1=40&sic2=49&sic3=4911&sicl=4911&sich=4921",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Natural Gas Transmission": "sic1=40&sic2=49&sic3=4922&sicl=4922&sich=4922",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Natural Gas Transmission & Distr": "sic1=40&sic2=49&sic3=4923&sicl=4923&sich=4923",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Natural Gas Distribution": "sic1=40&sic2=49&sic3=4924&sicl=4924&sich=4930",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Electric & Other Services Combin": "sic1=40&sic2=49&sic3=4931&sicl=4931&sich=4931",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Gas & Other Services Combined": "sic1=40&sic2=49&sic3=4932&sicl=4932&sich=4940",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Water Supply": "sic1=40&sic2=49&sic3=4941&sicl=4941&sich=4949",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Sanitary Services": "sic1=40&sic2=49&sic3=4950&sicl=4950&sich=4952",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Refuse Systems": "sic1=40&sic2=49&sic3=4953&sicl=4953&sich=4954",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Hazardous Waste Management": "sic1=40&sic2=49&sic3=4955&sicl=4955&sich=4960",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Steam & Air-Conditioning Supply": "sic1=40&sic2=49&sic3=4961&sicl=4961&sich=4990",
    "Transportation & Utilities -> Electric, Gas, & Sanitary Svcs -> Cogeneration Services & Small Po": "sic1=40&sic2=49&sic3=4991&sicl=4991&sich=4999",
    "Wholesale Trade": "sic1=50&sic2=0&sicl=5000&sich=5199",
    "Wholesale Trade -> Durable Goods -> Durable Goods": "sic1=50&sic2=50&sic3=5000&sicl=5000&sich=5009",
    "Wholesale Trade -> Durable Goods -> Motor Vehicles & Motor Vehicle P": "sic1=50&sic2=50&sic3=5010&sicl=5010&sich=5012",
    "Wholesale Trade -> Durable Goods -> Motor Vehicles Supplies & New Par": "sic1=50&sic2=50&sic3=5013&sicl=5013&sich=5019",
    "Wholesale Trade -> Durable Goods -> Furniture & Home Furnishings": "sic1=50&sic2=50&sic3=5020&sicl=5020&sich=5029",
    "Wholesale Trade -> Durable Goods -> Lumber & Other Construction Mate": "sic1=50&sic2=50&sic3=5030&sicl=5030&sich=5030",
    "Wholesale Trade -> Durable Goods -> Lumber, Plywood, Millwork & Wood": "sic1=50&sic2=50&sic3=5031&sicl=5031&sich=5039",
    "Wholesale Trade -> Durable Goods -> Professional & Commercial Equipment": "sic1=50&sic2=50&sic3=5040&sicl=5040&sich=5044",
    "Wholesale Trade -> Durable Goods -> Computers & Peripheral Equipment": "sic1=50&sic2=50&sic3=5045&sicl=5045&sich=5046",
    "Wholesale Trade -> Durable Goods -> Medical, Dental & Hospital Equip": "sic1=50&sic2=50&sic3=5047&sicl=5047&sich=5049",
    "Wholesale Trade -> Durable Goods -> Metals & Minerals (No Petroleum)": "sic1=50&sic2=50&sic3=5050&sicl=5050&sich=5050",
    "Wholesale Trade -> Durable Goods -> Metals Services Centers & Offices": "sic1=50&sic2=50&sic3=5051&sicl=5051&sich=5062",
    "Wholesale Trade -> Durable Goods -> Electrical Apparatus & Equipment": "sic1=50&sic2=50&sic3=5063&sicl=5063&sich=5063",
    "Wholesale Trade -> Durable Goods -> Electrical Appliances, Tv & Radi": "sic1=50&sic2=50&sic3=5064&sicl=5064&sich=5064",
    "Wholesale Trade -> Durable Goods -> Electronic Parts & Equipment": "sic1=50&sic2=50&sic3=5065&sicl=5065&sich=5069",
    "Wholesale Trade -> Durable Goods -> Hardware & Plumbing & Heating Eq": "sic1=50&sic2=50&sic3=5070&sicl=5070&sich=5071",
    "Wholesale Trade -> Durable Goods -> Hardware": "sic1=50&sic2=50&sic3=5072&sicl=5072&sich=5079",
    "Wholesale Trade -> Durable Goods -> Machinery, Equipment & Supplies": "sic1=50&sic2=50&sic3=5080&sicl=5080&sich=5081",
    "Wholesale Trade -> Durable Goods -> Construction & Mining (No Petro)": "sic1=50&sic2=50&sic3=5082&sicl=5082&sich=5083",
    "Wholesale Trade -> Durable Goods -> Industrial Machinery & Equipment": "sic1=50&sic2=50&sic3=5084&sicl=5084&sich=5089",
    "Wholesale Trade -> Durable Goods -> Misc Durable Goods": "sic1=50&sic2=50&sic3=5090&sicl=5090&sich=5093",
    "Wholesale Trade -> Durable Goods -> Jewelry, Watches, Precious Stone": "sic1=50&sic2=50&sic3=5094&sicl=5094&sich=5098",
    # "Wholesale Trade -> Durable Goods -> Durable Goods": "sic1=50&sic2=50&sic3=5099&sicl=5099&sich=5109",
    "Wholesale Trade -> Nondurable Goods": "sic1=50&sic2=51&sic3=0&sicl=5100&sich=5199",
    "Wholesale Trade -> Nondurable Goods -> Paper & Paper Products": "sic1=50&sic2=51&sic3=5110&sicl=5110&sich=5121",
    "Wholesale Trade -> Nondurable Goods -> Drugs, Proprietaries & Druggists": "sic1=50&sic2=51&sic3=5122&sicl=5122&sich=5129",
    "Wholesale Trade -> Nondurable Goods -> Apparel, Piece Goods & Notions": "sic1=50&sic2=51&sic3=5130&sicl=5130&sich=5139",
    "Wholesale Trade -> Nondurable Goods -> Groceries & Related Products": "sic1=50&sic2=51&sic3=5140&sicl=5140&sich=5140",
    "Wholesale Trade -> Nondurable Goods -> Groceries, General Line": "sic1=50&sic2=51&sic3=5141&sicl=5141&sich=5149",
    "Wholesale Trade -> Nondurable Goods -> Farm Product Raw Materials": "sic1=50&sic2=51&sic3=5150&sicl=5150&sich=5159",
    "Wholesale Trade -> Nondurable Goods -> Chemicals & Allied Products": "sic1=50&sic2=51&sic3=5160&sicl=5160&sich=5170",
    "Wholesale Trade -> Nondurable Goods -> Petroleum Bulk Stations & Termin": "sic1=50&sic2=51&sic3=5171&sicl=5171&sich=5171",
    "Wholesale Trade -> Nondurable Goods -> Petroleum & Petroleum Products (": "sic1=50&sic2=51&sic3=5172&sicl=5172&sich=5179",
    "Wholesale Trade -> Nondurable Goods -> Beer, Wine & Distilled Alcoholic": "sic1=50&sic2=51&sic3=5180&sicl=5180&sich=5189",
    "Wholesale Trade -> Nondurable Goods -> Miscellaneous Nondurable Goods": "sic1=50&sic2=51&sic3=5190&sicl=5190&sich=5199",
    "Retail Trade": "sic1=52&sic2=0&sicl=5200&sich=5999",
    "Retail Trade -> Building Materials": "sic1=52&sic2=52&sic3=0&sicl=5200&sich=5299",
    "Retail Trade -> Building Materials -> Building Materials, Hardware, Ga": "sic1=52&sic2=52&sic3=5200&sicl=5200&sich=5210",
    "Retail Trade -> Building Materials -> Lumber & Other Buildings Material": "sic1=52&sic2=52&sic3=5211&sicl=5211&sich=5270",
    "Retail Trade -> Building Materials -> Mobile Home Dealers": "sic1=52&sic2=52&sic3=5271&sicl=5271&sich=5310",
    "Retail Trade -> General Merchandise": "sic1=52&sic2=53&sicl=5300&sich=5399",
    "Retail Trade -> General Merchandise -> Department Stores": "sic1=52&sic2=53&sic3=5311&sicl=5311&sich=5330",
    "Retail Trade -> General Merchandise -> Variety Stores": "sic1=52&sic2=53&sic3=5331&sicl=5331&sich=5398",
    "Retail Trade -> General Merchandise -> Misc General Merchandise Stores": "sic1=52&sic2=53&sic3=5399&sicl=5399&sich=5399",
    "Retail Trade -> Grocery": "sic1=52&sic2=54&sic3=0&sicl=5400&sich=5499",
    "Retail Trade -> Grocery -> Food Stores": "sic1=52&sic2=54&sic3=5400&sicl=5400&sich=5410",
    "Retail Trade -> Grocery -> Grocery Stores": "sic1=52&sic2=54&sic3=5411&sicl=5411&sich=5411",
    "Retail Trade -> Grocery -> Convenience Stores": "sic1=52&sic2=54&sic3=5412&sicl=5412&sich=5499",
    "Retail Trade -> Auto Dealers & Service Stations": "sic1=52&sic2=55&sic3=0&sicl=5500&sich=5599",
    "Retail Trade -> Auto Dealers & Service Stations -> Auto Dealers & Gasoline Stations": "sic1=52&sic2=55&sic3=5500&sicl=5500&sich=5530",
    "Retail Trade -> Auto Dealers & Service Stations -> Auto & Home Supply Stores": "sic1=52&sic2=55&sic3=5531&sicl=5531&sich=5599",
    "Retail Trade -> Apparel & Accessory Stores": "sic1=52&sic2=56&sic3=0&sicl=5600&sich=5699",
    "Retail Trade -> Apparel & Accessory Stores -> Apparel & Accessory Stores": "sic1=52&sic2=56&sic3=5600&sicl=5600&sich=5620",
    "Retail Trade -> Apparel & Accessory Stores -> Women’s Clothing Stores": "sic1=52&sic2=56&sic3=5621&sicl=5621&sich=5650",
    "Retail Trade -> Apparel & Accessory Stores -> Family Clothing Stores": "sic1=52&sic2=56&sic3=5651&sicl=5651&sich=5660",
    "Retail Trade -> Apparel & Accessory Stores -> Shoe Stores": "sic1=52&sic2=56&sic3=5661&sicl=5661&sich=5699",
    "Retail Trade -> Home Furniture": "sic1=52&sic2=57&sic3=0&sicl=5700&sich=5799",
    "Retail Trade -> Home Furniture -> Home Furniture, Furnishings & Eq": "sic1=52&sic2=57&sic3=5700&sicl=5700&sich=5711",
    "Retail Trade -> Home Furniture -> Furniture Stores": "sic1=52&sic2=57&sic3=5712&sicl=5712&sich=5730",
    "Retail Trade -> Home Furniture -> Ratio, Tv & Consumer Electronics": "sic1=52&sic2=57&sic3=5731&sicl=5731&sich=5733",
    "Retail Trade -> Home Furniture -> Computer & Computer Software Sto": "sic1=52&sic2=57&sic3=5734&sicl=5734&sich=5734",
    "Retail Trade -> Home Furniture -> Record & Prerecord Tape Stores": "sic1=52&sic2=57&sic3=5735&sicl=5735&sich=5809",
    "Retail Trade -> Eating & Drinking Places": "sic1=52&sic2=58&sic3=0&sicl=5800&sich=5899",
    "Retail Trade -> Eating & Drinking Places -> Eating & Drinking Places": "sic1=52&sic2=58&sic3=5810&sicl=5810&sich=5811",
    "Retail Trade -> Eating & Drinking Places -> Eating Places": "sic1=52&sic2=58&sic3=5812&sicl=5812&sich=5899",
    "Retail Trade -> Miscellaneous Retail": "sic1=52&sic2=59&sic3=0&sicl=5900&sich=5999",
    "Retail Trade -> Miscellaneous Retail -> Miscellaneous Retail": "sic1=52&sic2=59&sic3=5900&sicl=5900&sich=5911",
    "Retail Trade -> Miscellaneous Retail -> Drug Stores & Proprietary Stores": "sic1=52&sic2=59&sic3=5912&sicl=5912&sich=5939",
    "Retail Trade -> Miscellaneous Retail -> Miscellaneous Shopping Goods Sto": "sic1=52&sic2=59&sic3=5940&sicl=5940&sich=5943",
    "Retail Trade -> Miscellaneous Retail -> Jewelry Stores": "sic1=52&sic2=59&sic3=5944&sicl=5944&sich=5944",
    "Retail Trade -> Miscellaneous Retail -> Hobby, Toy & Game Shops": "sic1=52&sic2=59&sic3=5945&sicl=5945&sich=5959",
    "Retail Trade -> Miscellaneous Retail -> Nonstore Retailers": "sic1=52&sic2=59&sic3=5960&sicl=5960&sich=5960",
    "Retail Trade -> Miscellaneous Retail -> Catalog & Mail-Order Houses": "sic1=52&sic2=59&sic3=5961&sicl=5961&sich=5989",
    "Retail Trade -> Miscellaneous Retail -> Retail Stores": "sic1=52&sic2=59&sic3=5990&sicl=5990&sich=6020",
    "Financial": "sic1=60&sic2=0&sicl=6000&sich=6799",
    "Financial -> Depository Institutions": "sic1=60&sic2=60&sicl=6000&sich=6099",
    "Financial -> Depository Institutions -> National Commercial Banks": "sic1=60&sic2=60&sic3=6021&sicl=6021&sich=6021",
    "Financial -> Depository Institutions -> State Commercial Banks": "sic1=60&sic2=60&sic3=6022&sicl=6022&sich=6028",
    "Financial -> Depository Institutions -> Commercial Banks": "sic1=60&sic2=60&sic3=6029&sicl=6029&sich=6034",
    "Financial -> Depository Institutions -> Savings Institution, Federally C": "sic1=60&sic2=60&sic3=6035&sicl=6035&sich=6035",
    "Financial -> Depository Institutions -> Savings Institution, Not Federa": "sic1=60&sic2=60&sic3=6036&sicl=6036&sich=6098",
    "Financial -> Depository Institutions -> Functions Related to Despository": "sic1=60&sic2=60&sic3=6099&sicl=6099&sich=6110",
    "Financial -> Non-depository Credit Inst": "sic1=60&sic2=61&sic3=0&sicl=6100&sich=6199",
    "Financial -> Non-depository Credit Inst -> Federal & Federally-Sponsored Cr": "sic1=60&sic2=61&sic3=6111&sicl=6111&sich=6140",
    "Financial -> Non-depository Credit Inst -> Personal Credit Institutions": "sic1=60&sic2=61&sic3=6141&sicl=6141&sich=6152",
    "Financial -> Non-depository Credit Inst -> Short-Term Business Credit Insti": "sic1=60&sic2=61&sic3=6153&sicl=6153&sich=6158",
    "Financial -> Non-depository Credit Inst -> Miscellaneous Business Credit In": "sic1=60&sic2=61&sic3=6159&sicl=6159&sich=6161",
    "Financial -> Non-depository Credit Inst -> Mortgage Bankers & Loan Correspo": "sic1=60&sic2=61&sic3=6162&sicl=6162&sich=6162",
    "Financial -> Non-depository Credit Inst -> Loan Brokers": "sic1=60&sic2=61&sic3=6163&sicl=6163&sich=6171",
    "Financial -> Non-depository Credit Inst -> Finance Lessors": "sic1=60&sic2=61&sic3=6172&sicl=6172&sich=6188",
    "Financial -> Non-depository Credit Inst -> Asset-Backed Securities": "sic1=60&sic2=61&sic3=6189&sicl=6189&sich=6198",
    "Financial -> Non-depository Credit Inst -> Finance Services": "sic1=60&sic2=61&sic3=6199&sicl=6199&sich=6199",
    "Financial -> Security & Commodity Brokers": "sic1=60&sic2=62&sic3=0&sicl=6200&sich=6299",
    "Financial -> Security & Commodity Brokers -> Security & Commodity Brokers, De": "sic1=60&sic2=62&sic3=6200&sicl=6200&sich=6210",
    "Financial -> Security & Commodity Brokers -> Security Brokers, Dealers & Flot": "sic1=60&sic2=62&sic3=6211&sicl=6211&sich=6220",
    "Financial -> Security & Commodity Brokers -> Commodity Contracts Brokers & De": "sic1=60&sic2=62&sic3=6221&sicl=6221&sich=6281",
    "Financial -> Security & Commodity Brokers -> Investment Advice": "sic1=60&sic2=62&sic3=6282&sicl=6282&sich=6310",
    "Financial -> Insurance Carriers": "sic1=60&sic2=63&sic3=0&sicl=6300&sich=6399",
    "Financial -> Insurance Carriers -> Life Insurance": "sic1=60&sic2=63&sic3=6311&sicl=6311&sich=6320",
    "Financial -> Insurance Carriers -> Accident & Health Insurance": "sic1=60&sic2=63&sic3=6321&sicl=6321&sich=6323",
    "Financial -> Insurance Carriers -> Hospital & Medical Service Plans": "sic1=60&sic2=63&sic3=6324&sicl=6324&sich=6330",
    "Financial -> Insurance Carriers -> Fire, Marine & Casualty Insurance": "sic1=60&sic2=63&sic3=6331&sicl=6331&sich=6350",
    "Financial -> Insurance Carriers -> Surety Insurance": "sic1=60&sic2=63&sic3=6351&sicl=6351&sich=6360",
    "Financial -> Insurance Carriers -> Title Insurance": "sic1=60&sic2=63&sic3=6361&sicl=6361&sich=6398",
    "Financial -> Insurance Carriers -> Insurance Carriers": "sic1=60&sic2=63&sic3=6399&sicl=6399&sich=6410",
    "Financial -> Insurance Agents": "sic1=60&sic2=64&sicl=6411&sich=6499",
    "Financial -> Real Estate": "sic1=60&sic2=65&sic3=0&sicl=6500&sich=6699",
    "Financial -> Real Estate -> Real Estate": "sic1=60&sic2=65&sic3=6500&sicl=6500&sich=6509",
    "Financial -> Real Estate -> Real Estate Operators (No Developers)": "sic1=60&sic2=65&sic3=6510&sicl=6510&sich=6511",
    "Financial -> Real Estate -> Operators of Nonresidential Buildings": "sic1=60&sic2=65&sic3=6512&sicl=6512&sich=6512",
    "Financial -> Real Estate -> Operators of Apartment Buildings": "sic1=60&sic2=65&sic3=6513&sicl=6513&sich=6518",
    "Financial -> Real Estate -> Lessors of Real Property": "sic1=60&sic2=65&sic3=6519&sicl=6519&sich=6530",
    "Financial -> Real Estate -> Real Estate Agents & Managers": "sic1=60&sic2=65&sic3=6531&sicl=6531&sich=6531",
    "Financial -> Real Estate -> Real Estate Dealers (For Their O": "sic1=60&sic2=65&sic3=6532&sicl=6532&sich=6551",
    "Financial -> Real Estate -> Land Subdividers & Developers (N": "sic1=60&sic2=65&sic3=6552&sicl=6552&sich=6769",
    "Financial -> Holding & Investment Offices": "sic1=60&sic2=67&sic3=0&sicl=6700&sich=6999",
    "Financial -> Holding & Investment Offices -> Blank Checks": "sic1=60&sic2=67&sic3=6770&sicl=6770&sich=6791",
    "Financial -> Holding & Investment Offices -> Oil Royalty Traders": "sic1=60&sic2=67&sic3=6792&sicl=6792&sich=6793",
    "Financial -> Holding & Investment Offices -> Patent Owners & Lessors": "sic1=60&sic2=67&sic3=6794&sicl=6794&sich=6794",
    "Financial -> Holding & Investment Offices -> Mineral Royalty Traders": "sic1=60&sic2=67&sic3=6795&sicl=6795&sich=6797",
    "Financial -> Holding & Investment Offices -> Real Estate Investment Trusts": "sic1=60&sic2=67&sic3=6798&sicl=6798&sich=6798",
    "Financial -> Holding & Investment Offices -> Investors": "sic1=60&sic2=67&sic3=6799&sicl=6799&sich=6999",
    "Services": "sic1=70&sic2=0&sicl=7000&sich=8999",
    "Services -> Hotels": "sic1=70&sic2=70&sic3=0&sicl=7000&sich=7199",
    "Services -> Hotels -> Hotels, Rooming Houses, Camps &": "sic1=70&sic2=70&sic3=7000&sicl=7000&sich=7010",
    "Services -> Hotels -> Hotels & Motels": "sic1=70&sic2=70&sic3=7011&sicl=7011&sich=7199",
    "Services -> Personal Services": "sic1=70&sic2=72&sicl=7200&sich=7309",
    "Services -> Business Services": "sic1=70&sic2=73&sic3=0&sicl=7300&sich=7499",
    "Services -> Business Services -> Advertising": "sic1=70&sic2=73&sic3=7310&sicl=7310&sich=7310",
    "Services -> Business Services -> Advertising Agencies": "sic1=70&sic2=73&sic3=7311&sicl=7311&sich=7319",
    "Services -> Business Services -> Consumer Credit Reporting, Colle": "sic1=70&sic2=73&sic3=7320&sicl=7320&sich=7329",
    "Services -> Business Services -> Mailing, Reproduction, Commercia": "sic1=70&sic2=73&sic3=7330&sicl=7330&sich=7330",
    "Services -> Business Services -> Direct Mail Advertising Services": "sic1=70&sic2=73&sic3=7331&sicl=7331&sich=7339",
    "Services -> Business Services -> To Dwellings & Other Buildings": "sic1=70&sic2=73&sic3=7340&sicl=7340&sich=7349",
    "Services -> Business Services -> Miscellaneous Equipment Rental &": "sic1=70&sic2=73&sic3=7350&sicl=7350&sich=7358",
    "Services -> Business Services -> Equipment Rental & Leasing": "sic1=70&sic2=73&sic3=7359&sicl=7359&sich=7360",
    "Services -> Business Services -> Employment Agencies": "sic1=70&sic2=73&sic3=7361&sicl=7361&sich=7362",
    "Services -> Business Services -> Help Supply Services": "sic1=70&sic2=73&sic3=7363&sicl=7363&sich=7369",
    "Services -> Business Services -> Computer Programming, Data Proce": "sic1=70&sic2=73&sic3=7370&sicl=7370&sich=7370",
    "Services -> Business Services -> Computer Programming Services": "sic1=70&sic2=73&sic3=7371&sicl=7371&sich=7371",
    "Services -> Business Services -> Prepackaged Software": "sic1=70&sic2=73&sic3=7372&sicl=7372&sich=7372",
    "Services -> Business Services -> Computer Integrated Systems Desi": "sic1=70&sic2=73&sic3=7373&sicl=7373&sich=7373",
    "Services -> Business Services -> Computer Processing & Data Prepa": "sic1=70&sic2=73&sic3=7374&sicl=7374&sich=7376",
    "Services -> Business Services -> Computer Rental & Leasing": "sic1=70&sic2=73&sic3=7377&sicl=7377&sich=7379",
    "Services -> Business Services -> Miscellaneous Business Services": "sic1=70&sic2=73&sic3=7380&sicl=7380&sich=7380",
    "Services -> Business Services -> Detective, Guard & Armored Car S": "sic1=70&sic2=73&sic3=7381&sicl=7381&sich=7383",
    "Services -> Business Services -> Photofinishing Laboratories": "sic1=70&sic2=73&sic3=7384&sicl=7384&sich=7384",
    "Services -> Business Services -> Telephone Interconnect Systems": "sic1=70&sic2=73&sic3=7385&sicl=7385&sich=7388",
    "Services -> Business Services -> Business Services": "sic1=70&sic2=73&sic3=7389&sicl=7389&sich=7499",
    "Services -> Automotive Repair": "sic1=70&sic2=75&sic3=0&sicl=7500&sich=7599",
    "Services -> Automotive Repair -> Automotive Repair, Services & Pa": "sic1=70&sic2=75&sic3=7500&sicl=7500&sich=7509",
    "Services -> Automotive Repair -> Auto Rental & Leasing (No Driver": "sic1=70&sic2=75&sic3=7510&sicl=7510&sich=7599",
    "Services -> Miscellaneous Repair": "sic1=70&sic2=76&sicl=7600&sich=7811",
    "Services -> Motion Pictures": "sic1=70&sic2=78&sic3=0&sicl=7800&sich=7899",
    "Services -> Motion Pictures -> Motion Picture & Video Tape Prod": "sic1=70&sic2=78&sic3=7812&sicl=7812&sich=7818",
    "Services -> Motion Pictures -> Allied to Motion Picture Product": "sic1=70&sic2=78&sic3=7819&sicl=7819&sich=7821",
    "Services -> Motion Pictures -> Motion Picture & Video Tape Dist": "sic1=70&sic2=78&sic3=7822&sicl=7822&sich=7828",
    "Services -> Motion Pictures -> Allied to Motion Picture Distrib": "sic1=70&sic2=78&sic3=7829&sicl=7829&sich=7829",
    "Services -> Motion Pictures -> Motion Picture Theaters": "sic1=70&sic2=78&sic3=7830&sicl=7830&sich=7840",
    "Services -> Motion Pictures -> Video Tape Rental": "sic1=70&sic2=78&sic3=7841&sicl=7841&sich=7899",
    "Services -> Amusement & Rec Svcs": "sic1=70&sic2=79&sic3=0&sicl=7900&sich=7999",
    "Services -> Amusement & Rec Svcs -> Amusement Recreation Services": "sic1=70&sic2=79&sic3=7900&sicl=7900&sich=7947",
    "Services -> Amusement & Rec Svcs -> Racing, Including Track Operation": "sic1=70&sic2=79&sic3=7948&sicl=7948&sich=7989",
    "Services -> Amusement & Rec Svcs -> Miscellaneous Amusement & Recrea": "sic1=70&sic2=79&sic3=7990&sicl=7990&sich=7996",
    "Services -> Amusement & Rec Svcs -> Membership Sports & Recreation C": "sic1=70&sic2=79&sic3=7997&sicl=7997&sich=7999",
    "Services -> Health Services": "sic1=70&sic2=80&sic3=0&sicl=8000&sich=8099",
    "Services -> Health Services -> Health Services": "sic1=70&sic2=80&sic3=8000&sicl=8000&sich=8010",
    "Services -> Health Services -> Offices & Clinics of Doctors of": "sic1=70&sic2=80&sic3=8011&sicl=8011&sich=8049",
    "Services -> Health Services -> Nursing & Personal Care Facilities": "sic1=70&sic2=80&sic3=8050&sicl=8050&sich=8050",
    "Services -> Health Services -> Skilled Nursing Care Facilities": "sic1=70&sic2=80&sic3=8051&sicl=8051&sich=8059",
    "Services -> Health Services -> Hospitals": "sic1=70&sic2=80&sic3=8060&sicl=8060&sich=8061",
    "Services -> Health Services -> General Medical & Surgical Hospitals": "sic1=70&sic2=80&sic3=8062&sicl=8062&sich=8070",
    "Services -> Health Services -> Medical Laboratories": "sic1=70&sic2=80&sic3=8071&sicl=8071&sich=8081",
    "Services -> Health Services -> Home Health Care Services": "sic1=70&sic2=80&sic3=8082&sicl=8082&sich=8089",
    "Services -> Health Services -> Misc Health & Allied Services": "sic1=70&sic2=80&sic3=8090&sicl=8090&sich=8092",
    "Services -> Health Services -> Specialty Outpatient Facilities": "sic1=70&sic2=80&sic3=8093&sicl=8093&sich=8110",
    "Services -> Legal Services": "sic1=70&sic2=81&sicl=8111&sich=8199",
    "Services -> Educational Services": "sic1=70&sic2=82&sicl=8200&sich=8299",
    "Services -> Social Services": "sic1=70&sic2=83&sic3=0&sicl=8300&sich=8399",
    "Services -> Social Services -> Social Services": "sic1=70&sic2=83&sic3=8300&sicl=8300&sich=8350",
    "Services -> Social Services -> Child Day Care Services": "sic1=70&sic2=83&sic3=8351&sicl=8351&sich=8599",
    "Services -> Museums": "sic1=70&sic2=84&sicl=8400&sich=8599",
    "Services -> Membership Organizations": "sic1=70&sic2=86&sicl=8600&sich=8699",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs": "sic1=70&sic2=87&sic3=0&sicl=8700&sich=8899",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs -> Engineering, Accounting, Research": "sic1=70&sic2=87&sic3=8700&sicl=8700&sich=8710",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs -> Engineering Services": "sic1=70&sic2=87&sic3=8711&sicl=8711&sich=8730",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs -> Commercial Physical & Biological": "sic1=70&sic2=87&sic3=8731&sicl=8731&sich=8733",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs -> Testing Laboratories": "sic1=70&sic2=87&sic3=8734&sicl=8734&sich=8740",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs -> Management Services": "sic1=70&sic2=87&sic3=8741&sicl=8741&sich=8741",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs -> Management Consulting Services": "sic1=70&sic2=87&sic3=8742&sicl=8742&sich=8743",
    "Services -> Engr, Acct, Rsrch, Mgmt Svcs -> Facilities Support Management Se": "sic1=70&sic2=87&sic3=8744&sicl=8744&sich=8879",
    "Services -> Miscellaneous Services": "sic1=70&sic2=89&sicl=8900&sich=9720",
    "Closed-End Funds": "sic1=0&sicl=0&sich=99",
}
d_open_insider = {
    "lcb": "latest-cluster-buys",
    "lpsb": "latest-penny-stock-buys",
    "lit": "latest-insider-trading",
    "lip": "insider-purchases",
    "blip": "latest-insider-purchases-25k",
    "blop": "latest-officer-purchases-25k",
    "blcp": "latest-ceo-cfo-purchases-25k",
    "lis": "insider-sales",
    "blis": "latest-insider-sales-100k",
    "blos": "latest-officer-sales-100k",
    "blcs": "latest-ceo-cfo-sales-100k",
    "topt": "top-officer-purchases-of-the-day",
    "toppw": "top-officer-purchases-of-the-week",
    "toppm": "top-officer-purchases-of-the-month",
    "tipt": "top-insider-purchases-of-the-day",
    "tippw": "top-insider-purchases-of-the-week",
    "tippm": "top-insider-purchases-of-the-month",
    "tist": "top-insider-sales-of-the-day",
    "tispw": "top-insider-sales-of-the-week",
    "tispm": "top-insider-sales-of-the-month",
}


@log_start_end(log=logger)
def check_valid_range(
    category: str, field: str, val: str, min_range: int, max_range: int
) -> str:
    """Check valid range of data being used

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    min_range : int
        min value to allow
    max_range : int
        max value to allow

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = ""
    if val:
        try:
            ival = int(val)

            if ival < min_range or ival > max_range:
                error = (
                    f"Invalid {category}.{field} '{str(ival)}'. "
                    f"Choose value between {min_range} and {max_range}, inclusive."
                )
                logging.exception(error)
        except ValueError:
            error = f"Invalid {category}.{field} '{val}'. Not a valid integer.\n"
            logging.exception(error)

    return error


@log_start_end(log=logger)
def check_dates(d_date: Dict) -> str:
    """Check valid dates

    Parameters
    ----------
    d_date : Dict
        dictionary with dates from open insider

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    possible_dates = [
        "All dates",
        "Custom",
        "Latest Day",
        "Last 3 days",
        "Last 1 week",
        "Last 2 weeks",
        "Last 1 month",
        "Last 2 months",
        "Last 3 months",
        "Last 6 months",
        "Last 1 year",
        "Last 2 years",
        "Last 4 years",
    ]

    error = ""

    if d_date["FilingDate"] not in possible_dates:
        error += (
            f"Invalid FilingDate '{d_date['FilingDate']}'. "
            f"Choose one of the following options: {', '.join(possible_dates)}.\n"
        )
    else:
        if d_date["FilingDate"] == "Custom":
            try:
                datetime.strptime(d_date["FilingDateFrom"], "%Y-%m-%d")
            except ValueError:
                error += f"Invalid FilingDateFrom '{d_date['FilingDateFrom']}' (format: dd/mm/yyyy).\n"
            try:
                datetime.strptime(d_date["FilingDateTo"], "%Y-%m-%d")
            except ValueError:
                error += f"Invalid FilingDateTo '{d_date['FilingDateTo']}' (format: dd/mm/yyyy).\n"

    if d_date["TradingDate"] not in possible_dates:
        error += (
            f"Invalid TradingDate '{d_date['TradingDate']}'. "
            f"Choose one of the following options: {', '.join(possible_dates)}.\n"
        )
    else:
        if d_date["TradingDate"] == "Custom":
            try:
                datetime.strptime(d_date["TradingDateFrom"], "%Y-%m-%d")
            except ValueError:
                error += f"Invalid TradingDateFrom '{d_date['TradingDateFrom']}' (format: dd/mm/yyyy).\n"

            try:
                datetime.strptime(d_date["TradingDateTo"], "%Y-%m-%d")
            except ValueError:
                error += f"Invalid TradingDateTo '{d_date['TradingDateTo']}' (format: dd/mm/yyyy).\n"
    if error:
        logging.exception(error)
    return error


@log_start_end(log=logger)
def check_valid_multiple(category: str, field: str, val: str, multiple: int) -> str:
    """Check valid value being a multiple

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    multiple : int
        value must be multiple of this number

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = ""
    if val:
        try:
            ival = int(val)

            if ival % multiple != 0:
                error = f"Invalid {category}.{field} '{str(ival)}'. Choose value multiple of {str(multiple)}.\n"
                logging.exception(error)
        except ValueError:
            error = f"Invalid {category}.{field} '{val}'. Not a valid integer.\n"
            logging.exception(error)
    return error


@log_start_end(log=logger)
def check_boolean_list(category: str, d_data: Dict, l_fields_to_check: List) -> str:
    """Check list of fields being bools

    Parameters
    ----------
    category : str
        category of open insider screener
    d_data : Dict
        data dictionary
    l_fields_to_check : List[str]
        list of fields from data dictionary to check if they are bool

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = ""

    for field in l_fields_to_check:
        if d_data[field] not in ["true", ""]:
            error += f"Invalid {category}.{field} '{d_data[field]}'. Needs to be either 'true' or '' (empty).\n"

    return error


@log_start_end(log=logger)
def check_in_list(
    category: str, field: str, val: int, l_possible_vals: List[str]
) -> str:
    """Check value being in possible list

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    l_possible_vals : List[str]
        list of possible values that should be allowed

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = ""

    if val:
        if val not in l_possible_vals:
            error += (
                f"Invalid {category}.{field} '{val}'. "
                f"Choose one of the following options: {', '.join(l_possible_vals)}.\n"
            )

    return error


@log_start_end(log=logger)
def check_int_in_list(
    category: str, field: str, val: str, l_possible_vals: List[int]
) -> str:
    """Check int value being in possible list

    Parameters
    ----------
    category : str
        category of open insider screener
    field : str
        field from category of open insider screener
    val : str
        value's field of category from open insider screener
    l_possible_vals : List[str]
        list of possible values that should be allowed

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = ""

    if val:
        try:
            ival = int(val)

            if ival not in l_possible_vals:
                error += (
                    f"Invalid {category}.{field} '{val}'. "
                    f"Choose one of the following options: {', '.join([str(x) for x in l_possible_vals])}.\n"
                )
                logging.exception(error)
        except ValueError:
            error += f"Invalid {category}.{field} '{val}'. Not a valid integer.\n"
            logging.exception(error)
    return error


@log_start_end(log=logger)
def check_open_insider_general(d_general) -> str:
    """Check valid open insider general

    Parameters
    ----------
    d_date : Dict
        dictionary of general

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = check_valid_range(
        "General", "SharePriceMin", d_general["SharePriceMin"], 0, 9999
    )

    error += check_valid_range(
        "General", "SharePriceMax", d_general["SharePriceMax"], 0, 9999
    )

    error += check_valid_range(
        "General", "LiquidityMinM", d_general["LiquidityMinM"], 0, 9999
    )

    error += check_valid_range(
        "General", "LiquidityMaxM", d_general["LiquidityMaxM"], 0, 9999
    )

    return error


@log_start_end(log=logger)
def check_open_insider_date(d_date: Dict) -> str:
    """Check valid open insider date

    Parameters
    ----------
    d_date : Dict
        dictionary of date

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = check_dates(d_date)
    error += check_valid_range(
        "Date", "FilingDelayMin", d_date["FilingDelayMin"], 0, 99
    )
    error += check_valid_range(
        "Date", "FilingDelayMax", d_date["FilingDelayMax"], 0, 99
    )
    error += check_valid_range("Date", "NDaysAgo", d_date["NDaysAgo"], 0, 99)

    return error


@log_start_end(log=logger)
def check_open_insider_transaction_filing(d_transaction_filing: Dict) -> str:
    """Check valid open insider transaction filing

    Parameters
    ----------
    d_transaction_filing : Dict
        dictionary of transaction filing

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    filings_to_check = [
        "P_Purchase",
        "S_Sale",
        "A_Grant",
        "D_SaleToLoss",
        "G_Gift",
        "NoDeriv",
        "F_Tax",
        "M_OptionEx",
        "X_OptionEx",
        "C_CnvDeriv",
        "W_Inherited",
        "MultipleDays",
    ]

    error = check_boolean_list(
        "TransactionFiling", d_transaction_filing, filings_to_check
    )
    error += check_valid_multiple(
        "TransactionFiling", "TradedMinK", d_transaction_filing["TradedMinK"], 5
    )
    error += check_valid_multiple(
        "TransactionFiling", "TradedMaxK", d_transaction_filing["TradedMaxK"], 5
    )
    error += check_valid_range(
        "TransactionFiling",
        "OwnChangeMinPct",
        d_transaction_filing["OwnChangeMinPct"],
        0,
        99,
    )
    error += check_valid_range(
        "TransactionFiling",
        "OwnChangeMaxPct",
        d_transaction_filing["OwnChangeMaxPct"],
        0,
        99,
    )

    return error


@log_start_end(log=logger)
def check_open_insider_industry(d_industry: Dict) -> str:
    """Check valid open insider industry

    Parameters
    ----------
    d_industry : Dict
        dictionary of industry

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    industry = d_industry["SectorSubsectorIndustry"]
    if industry not in d_SectorSubsectorIndustry:
        return f"Invalid Industry.SectorSubsectorIndustry '{industry}'. See comments at the end of template.ini file.\n"

    return ""


@log_start_end(log=logger)
def check_open_insider_insider_title(d_insider_title: Dict) -> str:
    """Check valid open insider title

    Parameters
    ----------
    d_insider_title : Dict
        dictionary of title

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    titles_to_check = [
        "COB",
        "CEO",
        "Pres",
        "COO",
        "CFO",
        "GC",
        "VP",
        "Officer",
        "Director",
        "10PctOwn",
        "Other",
    ]

    error = check_boolean_list("InsiderTitle", d_insider_title, titles_to_check)

    return error


@log_start_end(log=logger)
def check_open_insider_others(d_others: Dict) -> str:
    """Check valid open insider others

    Parameters
    ----------
    d_others : Dict
        dictionary of others

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    possible_groupby = ["Filing", "Company"]
    error = check_in_list("Others", "GroupBy", d_others["GroupBy"], possible_groupby)

    possible_sortby = ["Filing Date", "Trade Date", "Ticker Symbol", "Trade Value"]
    error = check_in_list("Others", "SortBy", d_others["SortBy"], possible_sortby)

    possible_maxresults = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    error += check_int_in_list(
        "Others", "MaxResults", d_others["MaxResults"], possible_maxresults
    )

    error += check_valid_range("Others", "Page", d_others["Page"], 0, 99)

    return error


@log_start_end(log=logger)
def check_open_insider_company_totals(d_company_totals: Dict) -> str:
    """Check valid open insider company totals

    Parameters
    ----------
    d_company_totals : Dict
        dictionary of company totals

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = check_valid_range(
        "CompanyTotals", "FilingsMin", d_company_totals["FilingsMin"], 0, 99
    )

    error += check_valid_range(
        "CompanyTotals", "FilingsMax", d_company_totals["FilingsMax"], 0, 99
    )

    error += check_valid_range(
        "CompanyTotals", "InsidersMin", d_company_totals["InsidersMin"], 0, 9
    )

    error += check_valid_range(
        "CompanyTotals", "InsidersMax", d_company_totals["InsidersMax"], 0, 9
    )

    error += check_valid_range(
        "CompanyTotals", "OfficersMin", d_company_totals["OfficersMin"], 0, 9
    )

    error += check_valid_range(
        "CompanyTotals", "OfficersMax", d_company_totals["OfficersMax"], 0, 9
    )

    error += check_valid_multiple(
        "CompanyTotals", "TradedMinK", d_company_totals["TradedMinK"], 5
    )

    error += check_valid_multiple(
        "CompanyTotals", "TradedMaxK", d_company_totals["TradedMaxK"], 5
    )

    error += check_valid_range(
        "CompanyTotals", "OwnChangeMinPct", d_company_totals["OwnChangeMinPct"], 0, 99
    )

    error += check_valid_range(
        "CompanyTotals", "OwnChangeMaxPct", d_company_totals["OwnChangeMaxPct"], 0, 99
    )

    return error


@log_start_end(log=logger)
def check_open_insider_screener(
    d_general: Dict,
    d_date: Dict,
    d_transaction_filing: Dict,
    d_industry: Dict,
    d_insider_title: Dict,
    d_others: Dict,
    d_company_totals: Dict,
) -> str:
    """Check valid open insider screener

    Parameters
    ----------
    d_general : Dict
        dictionary of general
    d_date : Dict
        dictionary of date
    d_transaction_filing : Dict
        dictionary of transaction filing
    d_industry : Dict
        dictionary of industry
    d_insider_title : Dict
        dictionary of insider title
    d_others : Dict
        dictionary of others
    d_company_totals : Dict
        dictionary of company totals

    Returns
    -------
    error : str
        error message. If empty, no error.
    """
    error = check_open_insider_general(d_general)
    error += check_open_insider_date(d_date)
    error += check_open_insider_transaction_filing(d_transaction_filing)
    error += check_open_insider_industry(d_industry)
    error += check_open_insider_insider_title(d_insider_title)
    error += check_open_insider_others(d_others)
    if d_others["GroupBy"] == "Company":
        error += check_open_insider_company_totals(d_company_totals)

    return error


@log_start_end(log=logger)
def get_preset_choices() -> Dict:
    """
    Return a dict containing keys as name of preset and
    filepath as value
    """

    PRESETS_PATH = (
        get_current_user().preferences.USER_PRESETS_DIRECTORY / "stocks" / "insider"
    )
    PRESETS_PATH_DEFAULT = MISCELLANEOUS_DIRECTORY / "stocks" / "insider"

    preset_choices = {}

    if PRESETS_PATH.exists():
        preset_choices.update(
            {
                filepath.name.strip(".ini"): filepath
                for filepath in PRESETS_PATH.iterdir()
                if filepath.suffix == ".ini"
            }
        )

    if PRESETS_PATH_DEFAULT.exists():
        preset_choices.update(
            {
                filepath.name.strip(".ini"): filepath
                for filepath in PRESETS_PATH_DEFAULT.iterdir()
                if filepath.suffix == ".ini"
            }
        )

    return preset_choices


@log_start_end(log=logger)
def get_open_insider_link(preset_loaded: str) -> str:
    """Get open insider link

    Parameters
    ----------
    preset_loaded: str
        Loaded preset filter

    Returns
    -------
    link : str
        open insider filtered link
    """
    preset = configparser.RawConfigParser()
    preset.optionxform = str  # type: ignore
    choices = get_preset_choices()
    if preset_loaded not in choices:
        console.print("[red]Could not find the link[/red]\n")
        return ""
    preset.read(choices[preset_loaded])

    d_general = dict(preset["General"])
    d_date = dict(preset["Date"])
    d_transaction_filing = dict(preset["TransactionFiling"])
    d_industry = dict(preset["Industry"])
    d_insider_title = dict(preset["InsiderTitle"])
    d_others = dict(preset["Others"])
    d_company_totals = dict(preset["CompanyTotals"])

    result = check_open_insider_screener(
        d_general,
        d_date,
        d_transaction_filing,
        d_industry,
        d_insider_title,
        d_others,
        d_company_totals,
    )

    if result:
        console.print(result)
        return ""

    d_FilingTradingDate = {
        "All dates": "0",
        "Custom": "-1",
        "Latest Day": "1",
        "Last 3 days": "3",
        "Last 1 week": "7",
        "Last 2 weeks": "14",
        "Last 1 month": "30",
        "Last 2 months": "60",
        "Last 3 months": "90",
        "Last 6 months": "180",
        "Last 1 year": "365",
        "Last 2 years": "730",
        "Last 4 years": "1461",
    }
    d_GroupBy = {
        "Filing": "0",
        "Company": "2",
    }
    d_SortBy = {
        "Filing Date": 0,
        "Trade Date": 1,
        "Ticker Symbol": 2,
        "Trade Value": 8,
    }

    link = "http://openinsider.com/screener?"

    # General
    link += f"s={d_general['Tickers'].replace(' ', '+')}&"
    link += f"o={d_general['Insider'].replace(' ', '+')}&"
    link += f"pl={d_general['SharePriceMin']}&"
    link += f"ph={d_general['SharePriceMax']}&"
    link += f"ll={d_general['LiquidityMinM']}&"
    link += f"lh={d_general['LiquidityMaxM']}&"

    # Date
    link += f"fd={d_FilingTradingDate[d_date['FilingDate']]}&"
    if d_date["FilingDate"] == "Custom":
        link += f"fdr={d_date['FilingDateFrom'].replace('/','%2F')}-{d_date['FilingDateTo'].replace('/','%2F')}&"
    else:
        link += "fdr=&"
    link += f"td={d_FilingTradingDate[d_date['TradingDate']]}&"
    if d_date["TradingDate"] == "Custom":
        link += f"tdr={d_date['TradingDateFrom'].replace('/','%2F')}-{d_date['TradingDateTo'].replace('/','%2F')}&"
    else:
        link += "tdr=&"
    link += f"fdlyl={d_date['FilingDelayMin']}&"
    link += f"fdlyh={d_date['FilingDelayMax']}&"
    link += f"daysago={d_date['NDaysAgo']}&"

    # Transaction Filing
    link += f"xp={'1' if d_transaction_filing['P_Purchase'] == 'true' else ''}&"
    link += f"xs={'1' if d_transaction_filing['S_Sale'] == 'true' else ''}&"
    if d_transaction_filing["A_Grant"] == "true":
        link += "xa=1&"
    if d_transaction_filing["D_SaleToLoss"] == "true":
        link += "xd=1&"
    if d_transaction_filing["G_Gift"] == "true":
        link += "xg=1&"
    if d_transaction_filing["NoDeriv"] == "true":
        link += "excludeDerivRelated=1&"
    if d_transaction_filing["F_Tax"] == "true":
        link += "xf=1&"
    if d_transaction_filing["M_OptionEx"] == "true":
        link += "xm=1&"
    if d_transaction_filing["X_OptionEx"] == "true":
        link += "xx=1&"
    if d_transaction_filing["C_CnvDeriv"] == "true":
        link += "xc=1&"
    if d_transaction_filing["W_Inherited"] == "true":
        link += "xw=1&"
    if d_transaction_filing["MultipleDays"] == "true":
        link += "tmult=1&"
    link += f"vl={d_transaction_filing['TradedMinK']}&"
    link += f"vh={d_transaction_filing['TradedMaxK']}&"
    link += f"ocl={d_transaction_filing['OwnChangeMinPct']}&"
    link += f"och={d_transaction_filing['OwnChangeMaxPct']}&"

    # Industry
    link += f"{d_SectorSubsectorIndustry[d_industry['SectorSubsectorIndustry']]}&"

    # Insider Title
    if d_insider_title["Officer"] == "true":
        link += "isofficer=1&"
    if d_insider_title["COB"] == "true":
        link += "iscob=1&"
    if d_insider_title["CEO"] == "true":
        link += "isceo=1&"
    if d_insider_title["Pres"] == "true":
        link += "ispres=1&"
    if d_insider_title["COO"] == "true":
        link += "iscoo=1&"
    if d_insider_title["CFO"] == "true":
        link += "iscfo=1&"
    if d_insider_title["GC"] == "true":
        link += "isgc=1&"
    if d_insider_title["VP"] == "true":
        link += "isvp=1&"
    if d_insider_title["Director"] == "true":
        link += "isdirector=1&"
    if d_insider_title["10PctOwn"] == "true":
        link += "istenpercent=1&"
    if d_insider_title["Other"] == "true":
        link += "isother=1&"

    # Others
    link += f"grp={d_GroupBy[d_others['GroupBy']]}&"

    # Company Totals
    link += f"nfl={d_company_totals['FilingsMin']}&"
    link += f"nfh={d_company_totals['FilingsMax']}&"
    link += f"nil={d_company_totals['InsidersMin']}&"
    link += f"nih={d_company_totals['InsidersMax']}&"
    link += f"nol={d_company_totals['OfficersMin']}&"
    link += f"noh={d_company_totals['OfficersMax']}&"
    link += f"v2l={d_company_totals['TradedMinK']}&"
    link += f"v2h={d_company_totals['TradedMaxK']}&"
    link += f"oc2l={d_company_totals['OwnChangeMinPct']}&"
    link += f"oc2h={d_company_totals['OwnChangeMaxPct']}&"

    # Others
    link += f"sortcol={d_SortBy[d_others['SortBy']]}&"
    link += f"cnt={d_others['MaxResults']}&"
    link += f"page={d_others['Page']}"

    return link


@log_start_end(log=logger)
def get_open_insider_data(url: str, has_company_name: bool) -> pd.DataFrame:
    """Get open insider link

    Parameters
    ----------
    url: str
        open insider link with filters to retrieve data from
    has_company_name: bool
        contains company name columns

    Returns
    -------
    data : pd.DataFrame
        open insider filtered data
    """
    text_soup_open_insider = BeautifulSoup(request(url).text, "lxml")

    if len(text_soup_open_insider.find_all("tbody")) == 0:
        console.print("No insider trading found.")
        return pd.DataFrame()

    l_filing_link = []
    l_ticker_link = []
    l_insider_link = []

    idx = 0
    for val in text_soup_open_insider.find_all("tbody")[1].find_all("a"):
        if idx == 0:
            l_filing_link.append(val["href"])
            idx += 1
        elif idx == 1:
            l_ticker_link.append("http://openinsider.com" + val["href"])
            idx += 1
        elif idx == 2 and has_company_name:
            idx += 1
        else:
            l_insider_link.append("http://openinsider.com" + val["href"])
            idx = 0

    l_X = []
    l_filing_date = []
    l_trading_date = []
    l_ticker = []
    l_company = []
    l_insider = []
    l_title = []
    l_trade_type = []
    l_price = []
    l_quantity = []
    l_owned = []
    l_delta_own = []
    l_value = []

    idx = 0
    for val in text_soup_open_insider.find_all("tbody")[1].find_all("td"):
        if idx == 0:
            l_X.append(val.text)
            idx += 1
        elif idx == 1:
            l_filing_date.append(val.text)
            idx += 1
        elif idx == 2:
            l_trading_date.append(val.text)
            idx += 1
        elif idx == 3:
            l_ticker.append(val.text.strip())
            idx += 1
        elif idx == 4 and has_company_name:
            l_company.append(val.text)
            idx += 1
        elif idx == (5 - int(not has_company_name)):
            l_insider.append(val.text)
            idx += 1
        elif idx == (6 - int(not has_company_name)):
            l_title.append(val.text)
            idx += 1
        elif idx == (7 - int(not has_company_name)):
            l_trade_type.append(val.text)
            idx += 1
        elif idx == (8 - int(not has_company_name)):
            l_price.append(val.text)
            idx += 1
        elif idx == (9 - int(not has_company_name)):
            l_quantity.append(val.text)
            idx += 1
        elif idx == (10 - int(not has_company_name)):
            l_owned.append(val.text)
            idx += 1
        elif idx == (11 - int(not has_company_name)):
            l_delta_own.append(val.text)
            idx += 1
        elif idx == (12 - int(not has_company_name)):
            l_value.append(val.text)
            idx += 1
        elif idx < (16 - int(not has_company_name)):
            idx += 1
        else:
            idx = 0

    d_open_insider_filtered = {
        "X": l_X,
        "Filing Date": l_filing_date,
        "Trading Date": l_trading_date,
        "Ticker": l_ticker,
        "Insider": l_insider,
        "Title": l_title,
        "Trade Type": l_trade_type,
        "Price": l_price,
        "Quantity": l_quantity,
        "Owned": l_owned,
        "Delta Own": l_delta_own,
        "Value": l_value,
        "Filing Link": l_filing_link,
        "Ticker Link": l_ticker_link,
        "Insider Link": l_insider_link,
    }
    if has_company_name:
        d_open_insider_filtered["Company"] = l_company

    return pd.DataFrame(d_open_insider_filtered)


@log_start_end(log=logger)
def get_insider_types() -> Dict:
    """Get insider types available for insider data

    Returns:
        Dict: Dictionary with insider types and respective description
    """
    return d_open_insider


@log_start_end(log=logger)
def get_print_insider_data(type_insider: str = "lcb"):
    """Print insider data

    Parameters
    ----------
    type_insider: str
        Insider type of data. Available types can be accessed through get_insider_types().

    Returns
    -------
    data : pd.DataFrame
        Open insider filtered data
    """
    response = request(
        f"http://openinsider.com/{d_open_insider[type_insider]}",
        headers={"User-Agent": "Mozilla/5.0"},
    )

    df = pd.read_html(response.text)[-3]
    remove_cols = ["1d", "1w", "1m", "6m"]

    if set(remove_cols).issubset(set(df.columns)):
        df = df.drop(columns=remove_cols).fillna("-")
    else:
        console.print("No data found for the given insider type.", style="red")
        df = pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    columns = [
        "X",
        "Filing Date",
        "Trade Date",
        "Ticker",
        "Company Name",
        "Industry" if type_insider == "lcb" else "Insider Name",
        "Title",
        "Trade Type",
        "Price",
        "Qty",
        "Owned",
        "Diff Own",
        "Value",
    ]

    if df.shape[1] == 13:
        df.columns = columns
    else:
        df.columns = columns[1:]
    df["Filing Date"] = df["Filing Date"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=10)) if isinstance(x, str) else x
    )
    df["Company Name"] = df["Company Name"].apply(
        lambda x: " ".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
    )
    df["Title"] = df["Title"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=10)) if isinstance(x, str) else x
    )
    if type_insider == "lcb":
        df["Industry"] = df["Industry"].apply(
            lambda x: " ".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
        )
    else:
        df["Insider Name"] = df["Insider Name"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
        )

    return df
