"""Corpus validation script.

Downloads company facts JSON from SEC for all target CIKs (rate-limited to
10 req/s), runs the full extraction + validation pipeline (annual & quarterly),
and writes a detailed report of all identity violations and diagnostics.

Usage:
    cd openbb_platform/providers/sec
    python tests/validate_corpus.py

Output:
    tests/corpus_validation_report.txt

WARNING: This script will download nearly 1000 files from the SEC site and run complete extractions.
"""

# pylint: disable=C0302,R0911,R0912,R0913,R0914,R0915,W0603
# flake8: noqa

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import requests

from openbb_sec.utils.company_facts import (
    MULTI_CIK_TICKERS,
    resolve_company_facts,
)
from openbb_sec.utils.statement_schema import StatementSchema

_SEC_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SEC_ROOT))

FULL_CORPUS: dict[str, str] = {
    "0000001800": "Abbott Laboratories",
    "0000002488": "Advanced Micro Devices Inc.",
    "0000002969": "Air Products and Chemicals, Inc.",
    "0000003570": "Cheniere Energy, Inc.",
    "0000004127": "Skyworks Solutions, Inc.",
    "0000004281": "Howmet Aerospace Inc.",
    "0000004457": "U-Haul Holding Company",
    "0000004904": "American Electric Power",
    "0000004962": "American Express Co",
    "0000004977": "Aflac Incorporated",
    "0000005272": "American International Group, Inc.",
    "0000005513": "Unum Group",
    "0000006201": "American Airlines Group Inc.",
    "0000006281": "Analog Devices",
    "0000006951": "Applied Materials",
    "0000007084": "Archer-Daniels-Midland Company",
    "0000007431": "Armstrong World Industries, Inc.",
    "0000007536": "Arrow Electronics, Inc.",
    "0000008670": "ADP",
    "0000008818": "Avery Dennison Corporation",
    "0000008858": "Avnet, Inc.",
    "0000009389": "Ball Corporation",
    "0000010456": "Baxter International Inc.",
    "0000010795": "Becton, Dickinson and Company",
    "0000011544": "W. R. Berkley Corporation",
    "0000012208": "Bio-Rad Laboratories, Inc.",
    "0000012659": "H&R Block, Inc.",
    "0000012927": "Boeing Co",
    "0000014272": "Bristol-Myers Squibb Company",
    "0000014693": "Brown-Forman Corporation",
    "0000014930": "Brunswick Corporation",
    "0000015615": "MasTec, Inc.",
    "0000016058": "CACI International Inc",
    "0000016732": "Campbell Soup Company",
    "0000016918": "Constellation Brands, Inc.",
    "0000017843": "Carpenter Technology Corporation",
    "0000018230": "Caterpillar Inc",
    "0000019584": "Chemed Corporation",
    "0000019617": "JPMorgan Chase & Co",
    "0000020212": "Churchill Downs Incorporated",
    "0000020286": "Cincinnati Financial Corporation",
    "0000021076": "The Clorox Company",
    "0000021175": "CNA Financial Corporation",
    "0000021344": "Coca Cola Co",
    "0000021665": "Colgate-Palmolive Company",
    "0000022356": "Commerce Bancshares, Inc.",
    "0000023217": "Conagra Brands, Inc.",
    "0000024545": "Molson Coors Beverage Company",
    "0000024741": "Corning Incorporated",
    "0000025232": "Cousins Properties Incorporated",
    "0000025445": "Crane NXT, Co.",
    "0000026172": "Cummins Inc.",
    "0000026324": "Curtiss-Wright Corporation",
    "0000027419": "Target Corporation",
    "0000027904": "Delta Air Lines, Inc.",
    "0000028917": "Dillard's, Inc.",
    "0000029534": "Dollar General Corporation",
    "0000029644": "Donaldson Company, Inc.",
    "0000029905": "Dover Corporation",
    "0000029989": "Omnicom Group Inc.",
    "0000030625": "Flowserve Corporation",
    "0000030697": "The Wendy's Company",
    "0000031462": "Ecolab Inc.",
    "0000031791": "PerkinElmer, Inc.",
    "0000032604": "Emerson Electric Co.",
    "0000033185": "Equifax Inc.",
    "0000033213": "EQT Corporation",
    "0000034088": "Exxon Mobil Corporation",
    "0000034903": "Federal Realty Investment Trust",
    "0000035527": "Fifth Third Bancorp",
    "0000036104": "U.S. Bancorp",
    "0000036270": "M&T Bank Corporation",
    "0000036377": "First Hawaiian, Inc.",
    "0000036966": "First Horizon Corporation",
    "0000037785": "FMC Corporation",
    "0000037808": "F.N.B. Corporation",
    "0000037996": "Ford Motor Company",
    "0000038777": "Franklin Resources, Inc.",
    "0000039263": "Cullen/Frost Bankers, Inc.",
    "0000039911": "The Gap, Inc.",
    "0000040533": "General Dynamics Corporation",
    "0000040545": "GE Aerospace",
    "0000040704": "General Mills, Inc.",
    "0000040729": "Ally Financial Inc.",
    "0000040987": "Genuine Parts Company",
    "0000042888": "Graco Inc.",
    "0000045012": "Halliburton Company",
    "0000046080": "Hasbro, Inc.",
    "0000046619": "HEICO Corporation",
    "0000047111": "The Hershey Company",
    "0000047217": "HP Inc.",
    "0000048465": "Hormel Foods Corporation",
    "0000048898": "Hubbell Incorporated",
    "0000049071": "Humana Inc.",
    "0000049196": "Huntington Bancshares Incorporated",
    "0000049600": "EastGroup Properties, Inc.",
    "0000049826": "Illinois Tool Works Inc.",
    "0000050863": "Intel",
    "0000051143": "IBM Corporation",
    "0000051253": "International Flavors & Fragrances Inc.",
    "0000051434": "International Paper Company",
    "0000052827": "Rayonier Inc.",
    "0000052988": "Jacobs Solutions Inc.",
    "0000055785": "Kimberly-Clark Corporation",
    "0000056047": "Kirby Corporation",
    "0000056873": "The Kroger Co.",
    "0000059478": "Eli Lilly and Company",
    "0000059527": "Lincoln Electric Holdings, Inc.",
    "0000059558": "Lincoln National Corporation",
    "0000060086": "Loews Corporation",
    "0000060519": "Louisiana-Pacific Corporation",
    "0000060667": "Lowe's Companies, Inc.",
    "0000062709": "Marsh & McLennan Companies, Inc.",
    "0000062996": "Masco Corporation",
    "0000063276": "Mattel, Inc.",
    "0000063754": "McCormick & Company, Incorporated",
    "0000063908": "McDonald's Corporation",
    "0000064040": "S&P Global Inc.",
    "0000064803": "CVS Health Corporation",
    "0000065984": "Entergy Corporation",
    "0000066570": "MSA Safety Incorporated",
    "0000066740": "3M Company",
    "0000067716": "MDU Resources Group, Inc.",
    "0000068505": "Motorola Solutions, Inc.",
    "0000070145": "National Fuel Gas Company",
    "0000070318": "Tenet Healthcare Corporation",
    "0000070858": "Bank of America Corporation",
    "0000071691": "The New York Times Company",
    "0000072331": "Nordson Corporation",
    "0000072741": "Eversource Energy",
    "0000072903": "Xcel Energy",
    "0000072971": "Wells Fargo & Company",
    "0000073124": "Northern Trust Corporation",
    "0000073309": "Nucor Corporation",
    "0000074208": "UDR, Inc.",
    "0000074260": "Old Republic International Corporation",
    "0000074303": "Olin Corporation",
    "0000075362": "Paccar",
    "0000075677": "Packaging Corporation of America",
    "0000076334": "Parker-Hannifin Corporation",
    "0000077476": "PepsiCo",
    "0000078003": "Pfizer Inc.",
    "0000078128": "Essential Utilities, Inc.",
    "0000078239": "PVH Corp.",
    "0000079282": "Brown & Brown, Inc.",
    "0000079879": "PPG Industries, Inc.",
    "0000080424": "Procter & Gamble Co",
    "0000080661": "The Progressive Corporation",
    "0000082811": "Regal Rexnord Corporation",
    "0000084246": "RLI Corp.",
    "0000084839": "Rollins, Inc.",
    "0000085535": "Royal Gold, Inc.",
    "0000085961": "Ryder System, Inc.",
    "0000086312": "The Travelers Companies, Inc.",
    "0000088121": "Seaboard Corporation",
    "0000089089": "Service Corporation International",
    "0000089439": "Mueller Industries, Inc.",
    "0000089800": "The Sherwin-Williams Company",
    "0000091142": "A. O. Smith Corporation",
    "0000091388": "SMITHFIELD FOODS INC",
    "0000091419": "The J. M. Smucker Company",
    "0000091440": "Snap-on Incorporated",
    "0000091576": "KeyCorp",
    "0000091767": "Sonoco Products Company",
    "0000092122": "The Southern Company",
    "0000092230": "Truist Financial Corporation",
    "0000092380": "Southwest Airlines Co.",
    "0000093410": "Chevron Corp",
    "0000093556": "Stanley Black & Decker, Inc.",
    "0000093751": "State Street Corporation",
    "0000096021": "Sysco Corporation",
    "0000096223": "Jefferies Financial Group Inc.",
    "0000096943": "Teleflex Incorporated",
    "0000097210": "Teradyne, Inc.",
    "0000097476": "Texas Instruments",
    "0000097745": "Thermo Fisher Scientific Inc.",
    "0000098362": "The Timken Company",
    "0000100493": "Tyson Foods, Inc.",
    "0000100517": "United Airlines Holdings, Inc.",
    "0000100885": "Union Pacific Corporation",
    "0000101829": "RTX Corporation",
    "0000102729": "Valmont Industries, Inc.",
    "0000103379": "V.F. Corporation",
    "0000104169": "Walmart Inc.",
    "0000105016": "Watsco, Inc.",
    "0000105634": "EMCOR Group, Inc.",
    "0000105770": "West Pharmaceutical Services, Inc.",
    "0000106040": "Western Digital",
    "0000106535": "Weyerhaeuser Company",
    "0000106640": "Whirlpool Corporation",
    "0000107263": "The Williams Companies, Inc.",
    "0000108312": "Woodward, Inc.",
    "0000109198": "The TJX Companies, Inc.",
    "0000109380": "Zions Bancorporation, National Association",
    "0000109563": "Applied Industrial Technologies, Inc.",
    "0000110621": "RPM International Inc.",
    "0000200406": "Johnson & Johnson",
    "0000202058": "L3Harris Technologies, Inc.",
    "0000216228": "ITT Inc.",
    "0000217346": "Textron Inc.",
    "0000275880": "Parsons Corporation",
    "0000277135": "W.W. Grainger, Inc.",
    "0000277948": "CSX Corporation",
    "0000310158": "Merck & Co., Inc.",
    "0000310764": "Stryker Corporation",
    "0000313616": "Danaher Corporation",
    "0000313927": "Church & Dwight Co., Inc.",
    "0000315189": "Deere & Company",
    "0000315213": "Robert Half International Inc.",
    "0000315293": "Aon plc",
    "0000315852": "Range Resources Corporation",
    "0000316709": "The Charles Schwab Corporation",
    "0000317540": "Coca-Cola Consolidated, Inc.",
    "0000318154": "Amgen Inc",
    "0000319201": "KLA Corporation",
    "0000320187": "NIKE, Inc.",
    "0000320193": "Apple Inc.",
    "0000320335": "Globe Life Inc.",
    "0000350698": "AutoNation, Inc.",
    "0000350894": "SEI Investments Company",
    "0000352541": "Alliant Energy Corporation",
    "0000352915": "Universal Health Services, Inc.",
    "0000354190": "Arthur J. Gallagher & Co.",
    "0000354950": "HOME DEPOT, INC.",
    "0000355811": "Gentex Corporation",
    "0000701985": "Bath & Body Works, Inc.",
    "0000702165": "Norfolk Southern Corporation",
    "0000704532": "Onto Innovation Inc.",
    "0000707549": "Lam Research",
    "0000711404": "The Cooper Companies, Inc.",
    "0000712515": "Electronic Arts",
    "0000713676": "The PNC Financial Services Group, Inc.",
    "0000715957": "Dominion Energy, Inc.",
    "0000717605": "Hexcel Corporation",
    "0000719955": "Williams-Sonoma, Inc.",
    "0000720005": "Raymond James Financial, Inc.",
    "0000720672": "Stifel Financial Corp.",
    "0000721371": "Cardinal Health, Inc.",
    "0000723125": "Micron Technology",
    "0000723254": "Cintas",
    "0000723531": "Paychex",
    "0000723612": "Avis Budget Group, Inc.",
    "0000726728": "Realty Income Corporation",
    "0000726958": "Casey's General Stores, Inc.",
    "0000728535": "J.B. Hunt Transport Services, Inc.",
    "0000730263": "Thor Industries, Inc.",
    "0000730272": "Repligen Corporation",
    "0000731766": "UnitedHealth Group Incorporated",
    "0000731802": "Atmos Energy Corporation",
    "0000732712": "Verizon Communications Inc",
    "0000732717": "AT&T Inc.",
    "0000737758": "The Toro Company",
    "0000740260": "Ventas, Inc.",
    "0000745732": "Ross Stores",
    "0000746515": "Expeditors International of Washington, Inc.",
    "0000749251": "Gartner, Inc.",
    "0000751364": "NNN REIT, Inc.",
    "0000753308": "NextEra Energy, Inc.",
    "0000759944": "Citizens Financial Group, Inc.",
    "0000763901": "Popular, Inc.",
    "0000764038": "SouthState Corporation",
    "0000764065": "Cleveland-Cliffs Inc.",
    "0000764180": "Altria Group, Inc.",
    "0000764478": "Best Buy Co., Inc.",
    "0000764622": "Pinnacle West Capital Corporation",
    "0000765880": "Healthpeak Properties, Inc.",
    "0000766421": "Alaska Air Group, Inc.",
    "0000766704": "Welltower Inc.",
    "0000769397": "Autodesk",
    "0000769520": "The Middleby Corporation",
    "0000772406": "Cirrus Logic, Inc.",
    "0000773840": "Honeywell International Inc",
    "0000775158": "Oshkosh Corporation",
    "0000776867": "White Mountains Insurance Group, Ltd.",
    "0000779152": "Jack Henry & Associates, Inc.",
    "0000783325": "WEC Energy Group, Inc.",
    "0000785161": "Encompass Health Corporation",
    "0000788784": "Public Service Enterprise Group Incorporated",
    "0000789019": "MICROSOFT CORPORATION",
    "0000789570": "MGM Resorts International",
    "0000790051": "Carlisle Companies Incorporated",
    "0000793952": "Harley-Davidson, Inc.",
    "0000794170": "Toll Brothers, Inc.",
    "0000794367": "Macy's, Inc.",
    "0000796343": "Adobe Inc.",
    "0000797468": "Occidental Petroleum Corporation",
    "0000798354": "Fiserv, Inc.",
    "0000798941": "First Citizens BancShares, Inc.",
    "0000801337": "Webster Financial Corporation",
    "0000802481": "Pilgrim's Pride Corporation",
    "0000804328": "Qualcomm",
    "0000811156": "CMS Energy Corporation",
    "0000811809": "BHP GROUP LIMITED",
    "0000812011": "Vail Resorts, Inc.",
    "0000813672": "Cadence Design Systems",
    "0000814453": "Newell Brands Inc.",
    "0000814547": "Fair Isaac Corporation",
    "0000815556": "Fastenal",
    "0000816761": "Teradata Corporation",
    "0000818479": "DENTSPLY SIRONA Inc.",
    "0000820027": "Ameriprise Financial, Inc.",
    "0000820313": "Amphenol Corporation",
    "0000820318": "Coherent, Inc.",
    "0000821189": "EOG Resources, Inc.",
    "0000822416": "PulteGroup, Inc.",
    "0000822818": "Clean Harbors, Inc.",
    "0000823768": "Waste Management, Inc.",
    "0000824142": "AAON, Inc.",
    "0000825542": "The Scotts Miracle-Gro Company",
    "0000827052": "Edison International",
    "0000827054": "Microchip Technology",
    "0000829224": "Starbucks",
    "0000831001": "Citigroup Inc.",
    "0000831259": "Freeport-McMoRan Inc.",
    "0000831641": "Tetra Tech, Inc.",
    "0000832101": "IDEX Corporation",
    "0000842023": "Bio-Techne Corporation",
    "0000842162": "Lear Corporation",
    "0000849399": "NortonLifeLock Inc.",
    "0000849869": "Silgan Holdings Inc.",
    "0000851205": "Cognex Corporation",
    "0000851968": "Mohawk Industries, Inc.",
    "0000853816": "Landstar System, Inc.",
    "0000855658": "Lattice Semiconductor Corporation",
    "0000857005": "PTC Inc.",
    "0000858470": "Coterra Energy Inc.",
    "0000858877": "CISCO SYSTEMS, INC.",
    "0000859737": "Hologic, Inc.",
    "0000860730": "HCA Healthcare, Inc.",
    "0000860731": "Tyler Technologies, Inc.",
    "0000860748": "Kemper Corporation",
    "0000861884": "Reliance Steel & Aluminum Co.",
    "0000864749": "Trimble Inc.",
    "0000865752": "Monster Beverage",
    "0000866291": "Allegro MicroSystems, Inc.",
    "0000866374": "Flex Ltd.",
    "0000866787": "AutoZone, Inc.",
    "0000868857": "Aecom",
    "0000871763": "ManpowerGroup Inc.",
    "0000872589": "Regeneron Pharmaceuticals",
    "0000873303": "Sarepta Therapeutics, Inc.",
    "0000874015": "Ionis Pharmaceuticals, Inc.",
    "0000874716": "Idexx Laboratories",
    "0000874761": "The AES Corporation",
    "0000874766": "The Hartford Financial Services Group, Inc.",
    "0000875045": "Biogen Inc.",
    "0000875320": "Vertex Pharmaceuticals",
    "0000875357": "BOK Financial Corporation",
    "0000876437": "MGIC Investment Corporation",
    "0000877212": "Zebra Technologies Corporation",
    "0000878927": "Old Dominion Freight Line",
    "0000879101": "Kimco Realty Corporation",
    "0000879169": "Incyte Corporation",
    "0000880266": "AGCO Corporation",
    "0000882095": "Gilead Sciences",
    "0000882184": "D.R. Horton, Inc.",
    "0000882835": "Roper Technologies",
    "0000883241": "Synopsys",
    "0000884614": "UGI Corporation",
    "0000885550": "Credit Acceptance Corporation",
    "0000885725": "Boston Scientific Corporation",
    "0000886982": "GOLDMAN SACHS GROUP INC",
    "0000887343": "Columbia Banking System, Inc.",
    "0000887936": "FTI Consulting, Inc.",
    "0000888491": "Omega Healthcare Investors, Inc.",
    "0000889331": "Littelfuse, Inc.",
    "0000891103": "Match Group, Inc.",
    "0000895126": "Expand Energy Corporation",
    "0000895417": "Equity LifeStyle Properties, Inc.",
    "0000895421": "Morgan Stanley",
    "0000896622": "AptarGroup, Inc.",
    "0000896878": "Intuit",
    "0000898173": "O'Reilly Automotive",
    "0000898174": "Reinsurance Group of America, Incorporated",
    "0000898293": "Jabil Inc.",
    "0000899051": "The Allstate Corporation",
    "0000899689": "Vornado Realty Trust",
    "0000900075": "Copart",
    "0000906107": "Equity Residential",
    "0000906163": "NVR, Inc.",
    "0000906345": "Camden Property Trust",
    "0000906553": "Boyd Gaming Corporation",
    "0000908255": "BorgWarner Inc.",
    "0000908937": "Sirius XM Holdings Inc.",
    "0000909832": "Costco",
    "0000910521": "Deckers Outdoor Corporation",
    "0000910606": "Regency Centers Corporation",
    "0000912593": "Sun Communities, Inc.",
    "0000912595": "Mid-America Apartment Communities, Inc.",
    "0000912958": "Millicom International Cellular S.A.",
    "0000913144": "RenaissanceRe Holdings Ltd.",
    "0000914475": "Neurocrine Biosciences, Inc.",
    "0000915389": "Eastman Chemical Company",
    "0000915912": "AvalonBay Communities, Inc.",
    "0000915913": "Albemarle Corporation",
    "0000916076": "Martin Marietta Materials, Inc.",
    "0000916365": "Tractor Supply Company",
    "0000916540": "Darling Ingredients Inc.",
    "0000917251": "Agree Realty Corporation",
    "0000918646": "Eagle Materials Inc.",
    "0000920148": "Labcorp Holdings Inc.",
    "0000920371": "Simpson Manufacturing Co., Inc.",
    "0000920522": "Essex Property Trust, Inc.",
    "0000920760": "Lennar Corporation",
    "0000921082": "Highwoods Properties, Inc.",
    "0000921738": "PENN Entertainment, Inc.",
    "0000921825": "First Industrial Realty Trust, Inc.",
    "0000922224": "PPL Corporation",
    "0000924805": "Freedom Holding Corp.",
    "0000927066": "DaVita Inc.",
    "0000927628": "Capital One Financial Corporation",
    "0000927653": "McKesson Corporation",
    "0000929008": "WESCO International, Inc.",
    "0000935703": "Dollar Tree, Inc.",
    "0000936340": "DTE Energy Company",
    "0000936395": "Ciena Corporation",
    "0000936468": "Lockheed Martin Corporation",
    "0000937556": "Masimo Corporation",
    "0000937966": "ASML Holding",
    "0000939767": "Exelixis, Inc.",
    "0000940944": "Darden Restaurants, Inc.",
    "0000943452": "Westinghouse Air Brake Technologies Corporation",
    "0000943819": "ResMed Inc.",
    "0000944695": "The Hanover Insurance Group, Inc.",
    "0000945841": "Pool Corporation",
    "0000946581": "Take-Two Interactive",
    "0000947263": "TORONTO DOMINION BANK",
    "0000947484": "Arch Capital Group Ltd.",
    "0000949870": "The Boston Beer Company, Inc.",
    "0001000228": "Henry Schein, Inc.",
    "0001000697": "Waters Corporation",
    "0001001039": "Legacy Walt Disney Co",
    "0001001250": "The Estee Lauder Companies Inc.",
    "0001001838": "Southern Copper Corporation",
    "0001002047": "NetApp, Inc.",
    "0001002910": "Ameren Corporation",
    "0001003078": "MSC Industrial Direct Co., Inc.",
    "0001004434": "Affiliated Managers Group, Inc.",
    "0001004980": "PG&E Corporation",
    "0001005284": "Universal Display Corporation",
    "0001012100": "Sealed Air Corporation",
    "0001013237": "FactSet Research Systems Inc.",
    "0001013857": "Pegasystems Inc.",
    "0001013871": "NRG Energy, Inc.",
    "0001014473": "VeriSign, Inc.",
    "0001015328": "Wintrust Financial Corporation",
    "0001018724": "AMAZON COM INC",
    "0001018963": "ATI Inc.",
    "0001019849": "Penske Automotive Group, Inc.",
    "0001020569": "Iron Mountain Incorporated",
    "0001021635": "OGE Energy Corp.",
    "0001021860": "NOV Inc.",
    "0001022079": "Quest Diagnostics Incorporated",
    "0001022671": "Steel Dynamics, Inc.",
    "0001023128": "Lithia Motors, Inc.",
    "0001024305": "Coty Inc.",
    "0001024478": "Rockwell Automation, Inc.",
    "0001025378": "W. P. Carey Inc.",
    "0001025996": "Kilroy Realty Corporation",
    "0001029199": "Euronet Worldwide, Inc.",
    "0001031296": "FirstEnergy Corp.",
    "0001031308": "Bentley Systems, Incorporated",
    "0001032033": "SLM Corporation",
    "0001032208": "Sempra",
    "0001034054": "SBA Communications Corporation",
    "0001035002": "Valero Energy Corporation",
    "0001035267": "Intuitive Surgical",
    "0001035443": "Alexandria Real Estate Equities, Inc.",
    "0001035983": "Comfort Systems USA, Inc.",
    "0001037038": "Ralph Lauren Corporation",
    "0001037540": "BXP, Inc.",
    "0001037646": "Mettler-Toledo International Inc.",
    "0001037868": "AMETEK, Inc.",
    "0001037976": "Jones Lang LaSalle Incorporated",
    "0001039684": "ONEOK, Inc.",
    "0001041061": "Yum! Brands, Inc.",
    "0001042046": "American Financial Group, Inc.",
    "0001043219": "Annaly Capital Management, Inc.",
    "0001043277": "C.H. Robinson Worldwide, Inc.",
    "0001045450": "EPR Properties",
    "0001045609": "Prologis, Inc.",
    "0001045810": "NVIDIA CORP",
    "0001046257": "Ingredion Incorporated",
    "0001046311": "Choice Hotels International, Inc.",
    "0001047127": "Amkor Technology, Inc.",
    "0001047862": "Consolidated Edison, Inc.",
    "0001048286": "Marriott International",
    "0001048477": "BioMarin Pharmaceutical Inc.",
    "0001048695": "F5, Inc.",
    "0001048911": "FedEx Corporation",
    "0001049502": "MKS Inc.",
    "0001050446": "MicroStrategy Inc.",
    "0001050797": "Columbia Sportswear Company",
    "0001050915": "Quanta Services, Inc.",
    "0001051470": "Crown Castle Inc.",
    "0001053507": "American Tower Corporation",
    "0001056696": "Manhattan Associates, Inc.",
    "0001057352": "CoStar Group",
    "0001057877": "IDACORP, Inc.",
    "0001058090": "Chipotle Mexican Grill, Inc.",
    "0001058290": "Cognizant",
    "0001059556": "Moody's Corporation",
    "0001060391": "Republic Services, Inc.",
    "0001062579": "Amdocs Limited",
    "0001063761": "Simon Property Group, Inc.",
    "0001065088": "eBay Inc.",
    "0001065280": "Netflix",
    "0001065696": "LKQ Corporation",
    "0001067701": "United Rentals, Inc.",
    "0001067983": "BERKSHIRE HATHAWAY INC",
    "0001068851": "Prosperity Bancshares, Inc.",
    "0001069157": "East West Bancorp, Inc.",
    "0001069183": "Axon Enterprise Inc.",
    "0001069202": "Lennox International Inc.",
    "0001069878": "Trex Company, Inc.",
    "0001070750": "Host Hotels & Resorts, Inc.",
    "0001071739": "Centene Corporation",
    "0001075124": "Thomson Reuters Corporation",
    "0001075531": "Booking Holdings",
    "0001082554": "United Therapeutics Corporation",
    "0001086222": "Akamai Technologies, Inc.",
    "0001088856": "Corcept Therapeutics Incorporated",
    "0001089063": "DICK'S Sporting Goods, Inc.",
    "0001090012": "Devon Energy Corporation",
    "0001090425": "Lamar Advertising Company",
    "0001090727": "United Parcel Service, Inc.",
    "0001090872": "Agilent Technologies, Inc.",
    "0001091667": "Charter Communications",
    "0001093557": "DexCom",
    "0001094285": "Teledyne Technologies Incorporated",
    "0001096343": "Markel Corporation",
    "0001097149": "Align Technology, Inc.",
    "0001097864": "ON Semiconductor Corporation",
    "0001099219": "MetLife, Inc.",
    "0001099590": "MercadoLibre",
    "0001099800": "Edwards Lifesciences Corporation",
    "0001100682": "Charles River Laboratories International, Inc.",
    "0001101239": "Equinix, Inc.",
    "0001101302": "Entegris, Inc.",
    "0001103982": "Mondelez International",
    "0001104506": "Insmed Incorporated",
    "0001108524": "Salesforce, Inc.",
    "0001109354": "Bruker Corporation",
    "0001109357": "Exelon",
    "0001110803": "Illumina, Inc.",
    "0001111711": "NiSource Inc.",
    "0001111928": "IPG Photonics Corporation",
    "0001113169": "T. Rowe Price Group, Inc.",
    "0001115055": "Pinnacle Financial Partners, Inc.",
    "0001116132": "Tapestry, Inc.",
    "0001120193": "Nasdaq, Inc.",
    "0001121788": "Garmin Ltd.",
    "0001123360": "Global Payments Inc.",
    "0001124140": "Exact Sciences Corporation",
    "0001126328": "Principal Financial Group, Inc.",
    "0001128928": "Flowers Foods, Inc.",
    "0001130310": "CenterPoint Energy, Inc.",
    "0001133421": "Northrop Grumman Corporation",
    "0001136869": "Zimmer Biomet Holdings, Inc.",
    "0001136893": "Fidelity National Information Services, Inc.",
    "0001137774": "Prudential Financial, Inc.",
    "0001137789": "Seagate Technology Holdings",
    "0001138118": "CBRE Group, Inc.",
    "0001140859": "Cencora, Inc.",
    "0001141391": "Mastercard Incorporated",
    "0001142417": "Nexstar Media Group, Inc.",
    "0001144215": "Acuity Brands, Inc.",
    "0001145197": "Insulet Corporation",
    "0001156039": "Elevance Health Inc.",
    "0001156375": "CME Group Inc.",
    "0001159036": "Halozyme Therapeutics, Inc.",
    "0001159152": "James Hardie Industries plc",
    "0001163165": "ConocoPhillips",
    "0001164727": "Newmont Corporation",
    "0001166003": "XPO Logistics, Inc.",
    "0001166691": "Comcast",
    "0001170010": "CarMax, Inc.",
    "0001174922": "Wynn Resorts, Limited",
    "0001175454": "Corpay, Inc.",
    "0001176948": "Ares Management Corporation",
    "0001177394": "TD SYNNEX Corporation",
    "0001177609": "Five Below, Inc.",
    "0001177702": "Saia, Inc.",
    "0001178670": "Alnylam Pharmaceuticals",
    "0001179929": "Molina Healthcare, Inc.",
    "0001206264": "Somnigroup International Inc",
    "0001212545": "Western Alliance Bancorporation",
    "0001214816": "AXIS Capital Holdings Limited",
    "0001219601": "Crown Holdings, Inc.",
    "0001232524": "Jazz Pharmaceuticals plc",
    "0001236275": "QXO, Inc.",
    "0001237831": "Globus Medical, Inc.",
    "0001260221": "TransDigm Group Incorporated",
    "0001261333": "DocuSign, Inc.",
    "0001262039": "Fortinet",
    "0001262823": "Westlake Corporation",
    "0001267238": "Assurant, Inc.",
    "0001273813": "Assured Guaranty Ltd.",
    "0001274494": "First Solar, Inc.",
    "0001278021": "MarketAxess Holdings Inc.",
    "0001280452": "Monolithic Power Systems",
    "0001281761": "Regions Financial Corporation",
    "0001282637": "NewMarket Corporation",
    "0001283699": "T-Mobile US",
    "0001285785": "The Mosaic Company",
    "0001286681": "Domino's Pizza, Inc.",
    "0001287865": "Medical Properties Trust, Inc.",
    "0001288776": "Google Inc.",
    "0001289419": "Morningstar, Inc.",
    "0001289460": "Texas Roadhouse, Inc.",
    "0001289490": "Extra Space Storage Inc.",
    "0001297989": "ExlService Holdings, Inc.",
    "0001297996": "Digital Realty Trust, Inc.",
    "0001298675": "CubeSmart",
    "0001300514": "Las Vegas Sands Corp.",
    "0001302215": "Houlihan Lokey, Inc.",
    "0001306830": "Celanese Corporation",
    "0001307954": "Huntsman Corporation",
    "0001308547": "Dolby Laboratories, Inc.",
    "0001309108": "WEX Inc.",
    "0001311370": "Lazard Ltd",
    "0001315098": "Roblox Corporation",
    "0001316835": "Builders FirstSource, Inc.",
    "0001318605": "Tesla, Inc.",
    "0001321655": "Palantir Technologies",
    "0001321732": "Penumbra, Inc.",
    "0001324404": "CF Industries Holdings, Inc.",
    "0001324424": "Expedia Group, Inc.",
    "0001324948": "RBC Bearings Incorporated",
    "0001326160": "Duke Energy Corporation",
    "0001326380": "GameStop Corp.",
    "0001326801": "Meta Platforms",
    "0001327567": "Palo Alto Networks",
    "0001327811": "Workday, Inc.",
    "0001331875": "Fidelity National Financial, Inc.",
    "0001333986": "Equitable Holdings, Inc.",
    "0001334036": "Crocs, Inc.",
    "0001335258": "Live Nation Entertainment, Inc.",
    "0001336917": "Under Armour, Inc.",
    "0001336920": "Leidos Holdings, Inc.",
    "0001341439": "Oracle Corporation",
    "0001341766": "Celsius Holdings, Inc.",
    "0001352010": "EPAM Systems, Inc.",
    "0001357615": "KBR, Inc.",
    "0001360604": "Healthcare Realty Trust Incorporated",
    "0001360901": "Evercore Inc.",
    "0001361658": "Travel + Leisure Co.",
    "0001364742": "BLACKROCK FINANCE, INC.",
    "0001365135": "The Western Union Company",
    "0001370637": "Etsy, Inc.",
    "0001370946": "Owens Corning",
    "0001373715": "ServiceNow, Inc.",
    "0001375365": "Super Micro Computer, Inc.",
    "0001381197": "Interactive Brokers Group, Inc.",
    "0001381668": "TFS Financial Corporation",
    "0001383312": "Broadridge Financial Solutions, Inc.",
    "0001384905": "RingCentral, Inc.",
    "0001389170": "Targa Resources Corp.",
    "0001390777": "The Bank of New York Mellon Corporation",
    "0001393052": "Veeva Systems Inc.",
    "0001393311": "Public Storage",
    "0001393818": "Blackstone Inc.",
    "0001396009": "Vulcan Materials Company",
    "0001397187": "Lululemon Athletica Inc.",
    "0001397911": "LPL Financial Holdings Inc.",
    "0001398659": "Genpact Limited",
    "0001402057": "CDW Corporation",
    "0001402436": "SS&C Technologies Holdings, Inc.",
    "0001403161": "VISA INC.",
    "0001403568": "Ulta Beauty, Inc.",
    "0001404655": "HubSpot, Inc.",
    "0001404912": "KKR & Co. Inc.",
    "0001408075": "Graphic Packaging Holding Company",
    "0001408198": "MSCI Inc.",
    "0001410636": "American Water Works Company, Inc.",
    "0001411207": "Allison Transmission Holdings, Inc.",
    "0001413329": "Philip Morris International Inc.",
    "0001413447": "NXP Semiconductors",
    "0001418135": "Keurig Dr Pepper",
    "0001418819": "Iridium Communications Inc.",
    "0001423689": "AGNC Investment Corp.",
    "0001428439": "Roku, Inc.",
    "0001433195": "AppFolio, Inc.",
    "0001433270": "Antero Resources Corporation",
    "0001433642": "Hamilton Lane Incorporated",
    "0001434588": "Grand Canyon Education, Inc.",
    "0001437107": "Warner Bros. Discovery",
    "0001437578": "Bright Horizons Family Solutions Inc.",
    "0001441816": "MongoDB, Inc.",
    "0001442145": "Verisk",
    "0001443646": "Booz Allen Hamilton Holding Corporation",
    "0001447669": "Twilio Inc.",
    "0001455863": "Americold Realty Trust, Inc.",
    "0001463101": "Enphase Energy, Inc.",
    "0001465128": "Starwood Property Trust, Inc.",
    "0001466258": "Trane Technologies plc",
    "0001467623": "Dropbox, Inc.",
    "0001467831": "Howard Hughes Holdings Inc.",
    "0001467858": "General Motors Company",
    "0001468174": "Hyatt Hotels Corporation",
    "0001468522": "Ferrovial SE",
    "0001472787": "First American Financial Corporation",
    "0001474432": "Everpure, Inc",
    "0001474735": "Generac Holdings Inc.",
    "0001475922": "Primerica, Inc.",
    "0001477294": "Sensata Technologies Holding plc",
    "0001477333": "Cloudflare, Inc.",
    "0001478242": "IQVIA Holdings Inc.",
    "0001479094": "STAG Industrial, Inc.",
    "0001486159": "Chord Energy Corporation",
    "0001486957": "BWX Technologies, Inc.",
    "0001487712": "Air Lease Corporation",
    "0001492422": "Apellis Pharmaceuticals, Inc.",
    "0001492691": "Knight-Swift Transportation Holdings Inc.",
    "0001493594": "MACOM Technology Solutions Holdings, Inc.",
    "0001501585": "Huntington Ingalls Industries, Inc.",
    "0001506293": "Pinterest, Inc.",
    "0001506307": "Kinder Morgan, Inc.",
    "0001507079": "Floor & Decor Holdings, Inc.",
    "0001510295": "Marathon Petroleum Corporation",
    "0001511737": "Ubiquiti Inc.",
    "0001512673": "Block, Inc.",
    "0001515673": "Ultragenyx Pharmaceutical Inc.",
    "0001516513": "Doximity, Inc.",
    "0001519751": "Fortune Brands Home & Security, Inc.",
    "0001520006": "Matador Resources Company",
    "0001520697": "Acadia Healthcare Company, Inc.",
    "0001524472": "Xylem Inc.",
    "0001527166": "The Carlyle Group Inc.",
    "0001528396": "Guidewire Software, Inc.",
    "0001528849": "Rh",
    "0001530950": "Post Holdings, Inc.",
    "0001531152": "BJ's Wholesale Club Holdings, Inc.",
    "0001534701": "Phillips 66",
    "0001535527": "CrowdStrike",
    "0001535929": "Voya Financial, Inc.",
    "0001539838": "Diamondback Energy",
    "0001543151": "Uber Technologies, Inc.",
    "0001551152": "AbbVie Inc.",
    "0001552033": "TransUnion",
    "0001555280": "Zoetis Inc.",
    "0001556593": "Rithm Capital Corp.",
    "0001557860": "Globant S.A.",
    "0001559720": "Airbnb",
    "0001560385": "Liberty Live Group",
    "0001561550": "Datadog",
    "0001562088": "Duolingo, Inc.",
    "0001562401": "American Homes 4 Rent",
    "0001564708": "News Corporation",
    "0001567683": "Clearway Energy, Inc.",
    "0001570585": "Liberty Global plc",
    "0001571123": "Science Applications International Corporation",
    "0001571283": "Rexford Industrial Realty, Inc.",
    "0001571949": "Intercontinental Exchange, Inc.",
    "0001571996": "Dell Technologies Inc.",
    "0001573516": "Murphy USA Inc.",
    "0001575515": "Sprouts Farmers Market, Inc.",
    "0001575965": "Gaming and Leisure Properties, Inc.",
    "0001579091": "Instacart (Maplebear Inc.)",
    "0001579298": "Burlington Stores, Inc.",
    "0001581068": "Brixmor Property Group Inc.",
    "0001583708": "SentinelOne, Inc.",
    "0001584207": "OneMain Holdings, Inc.",
    "0001584509": "Aramark",
    "0001585521": "Zoom Communications, Inc.",
    "0001585689": "Hilton Worldwide Holdings Inc.",
    "0001590364": "FTAI Aviation Ltd.",
    "0001590714": "Element Solutions Inc",
    "0001590895": "Caesars Entertainment, Inc.",
    "0001590955": "Paycom Software, Inc.",
    "0001591698": "Paylocity Holding Corporation",
    "0001592386": "Virtu Financial, Inc.",
    "0001594805": "Shopify",
    "0001596532": "Arista Networks, Inc.",
    "0001599298": "Summit Therapeutics Inc.",
    "0001600033": "e.l.f. Beauty, Inc.",
    "0001601046": "Keysight Technologies, Inc.",
    "0001601712": "Synchrony Financial",
    "0001602065": "Viper Energy, Inc.",
    "0001603923": "Weatherford International plc",
    "0001604028": "Advanced Drainage Systems, Inc.",
    "0001604778": "Qorvo, Inc.",
    "0001604821": "Natera, Inc.",
    "0001607678": "Viking Therapeutics, Inc.",
    "0001609550": "Inspire Medical Systems, Inc.",
    "0001609711": "GoDaddy Inc.",
    "0001611052": "Procore Technologies, Inc.",
    "0001611647": "Freshpet, Inc.",
    "0001611983": "Liberty Broadband Corporation",
    "0001616707": "Wayfair Inc.",
    "0001617406": "Park Hotels & Resorts Inc.",
    "0001617640": "Zillow Group, Inc. Class A",
    "0001618563": "National Storage Affiliates Trust",
    "0001618673": "Performance Food Group Company",
    "0001618732": "Nutanix, Inc.",
    "0001622536": "Talen Energy Corporation",
    "0001623925": "Antero Midstream Corporation",
    "0001627857": "SailPoint, Inc.",
    "0001628171": "Revolution Medicines, Inc.",
    "0001633917": "PayPal",
    "0001633931": "TopBuild Corp.",
    "0001633978": "Lumentum Holdings Inc.",
    "0001635088": "Roivant Sciences Ltd.",
    "0001636222": "Wingstop Inc.",
    "0001636519": "Madison Square Garden Sports Corp.",
    "0001637207": "Planet Fitness, Inc.",
    "0001637459": "Kraft Heinz",
    "0001639300": "Ollie's Bargain Outlet Holdings, Inc.",
    "0001639438": "CAVA Group, Inc.",
    "0001639920": "Spotify Technology S.A.",
    "0001640147": "Snowflake Inc.",
    "0001642896": "Samsara Inc.",
    "0001645590": "Hewlett Packard Enterprise Company",
    "0001646972": "Albertsons Companies, Inc.",
    "0001647088": "WillScot Holdings Corporation",
    "0001650107": "Coca-Cola Europacific Partners",
    "0001650164": "Toast, Inc.",
    "0001650372": "Atlassian",
    "0001650729": "SiteOne Landscape Supply, Inc.",
    "0001652044": "Alphabet Inc.",
    "0001653482": "GitLab Inc.",
    "0001658566": "Permian Resources Corporation",
    "0001659166": "Fortive Corporation",
    "0001660134": "Okta, Inc.",
    "0001665918": "US Foods Holding Corp.",
    "0001666700": "DuPont de Nemours, Inc.",
    "0001668397": "Medpace Holdings, Inc.",
    "0001669162": "Kinsale Capital Group, Inc.",
    "0001670592": "YETI Holdings, Inc.",
    "0001671933": "The Trade Desk, Inc.",
    "0001674101": "Vertiv Holdings Co",
    "0001674862": "Ashland Inc.",
    "0001674910": "Valvoline Inc.",
    "0001675149": "Alcoa Corporation",
    "0001679273": "Lamb Weston Holdings, Inc.",
    "0001679788": "Coinbase Global, Inc.",
    "0001681459": "TechnipFMC plc",
    "0001682852": "Moderna, Inc.",
    "0001685040": "Brighthouse Financial, Inc.",
    "0001687229": "Invitation Homes Inc.",
    "0001688568": "DXC Technology Company",
    "0001690820": "Carvana Co.",
    "0001691493": "Nu Holdings Ltd.",
    "0001692063": "Schneider National, Inc.",
    "0001692819": "Vistra Corp.",
    "0001699150": "Ingersoll Rand Inc.",
    "0001699838": "Confluent, Inc.",
    "0001701605": "Baker Hughes",
    "0001703056": "ADT Inc.",
    "0001705696": "VICI Properties Inc.",
    "0001707753": "Elastic N.V.",
    "0001707925": "Linde plc",
    "0001709048": "GLOBALFOUNDRIES Inc.",
    "0001711269": "Evergy, Inc.",
    "0001713445": "Reddit, Inc.",
    "0001713683": "Zscaler",
    "0001717115": "Tempus AI, Inc.",
    "0001718512": "Gates Industrial Corporation plc",
    "0001720635": "nVent Electric plc",
    "0001722482": "Avantor, Inc.",
    "0001722684": "Wyndham Hotels & Resorts, Inc.",
    "0001730168": "Broadcom Inc.",
    "0001734722": "UiPath Inc.",
    "0001736297": "Astera Labs, Inc. Common Stock",
    "0001737806": "PDD Holdings",
    "0001739104": "Elanco Animal Health Incorporated",
    "0001739940": "Cigna Corporation",
    "0001744489": "Walt Disney Co",
    "0001745201": "Viking Holdings Ltd",
    "0001748790": "Amcor plc",
    "0001751008": "Applovin Corp",
    "0001751788": "Dow Inc.",
    "0001754301": "Fox Corporation",
    "0001755672": "Corteva, Inc.",
    "0001757073": "Envista Holdings Corp",
    "0001757898": "STERIS plc",
    "0001758730": "Tradeweb Markets Inc.",
    "0001759509": "Lyft, Inc.",
    "0001764046": "Clarivate Plc",
    "0001766502": "Chewy, Inc.",
    "0001772016": "BellRing Brands, Inc.",
    "0001773383": "Dynatrace, Inc.",
    "0001780312": "AST SpaceMobile, Inc.",
    "0001781335": "Otis Worldwide Corporation",
    "0001783180": "Carrier Global Corporation",
    "0001783398": "UWM Holdings Corporation",
    "0001783879": "Robinhood Markets, Inc.",
    "0001786352": "Bill.com Holdings, Inc.",
    "0001786431": "Reynolds Consumer Products Inc.",
    "0001786842": "Vontier Corporation",
    "0001787425": "XP Inc.",
    "0001792044": "Viatris Inc.",
    "0001792580": "Ovintiv Inc.",
    "0001792789": "DoorDash",
    "0001794515": "ZoomInfo Technologies Inc.",
    "0001794669": "Shift4 Payments, Inc.",
    "0001796209": "APi Group Corporation",
    "0001800227": "IAC InterActive Corp.",
    "0001801368": "MP Materials Corp.",
    "0001802768": "Royalty Pharma plc",
    "0001803599": "Concentrix Corporation",
    "0001805284": "Rocket Companies, Inc.",
    "0001810806": "Unity Software Inc.",
    "0001811074": "Texas Pacific Land Corporation",
    "0001811210": "Lucid Group, Inc.",
    "0001811414": "QuantumScape Corporation",
    "0001818201": "CCC Intelligent Solutions Holdings Inc.",
    "0001818874": "SoFi Technologies, Inc.",
    "0001819928": "DoubleVerify Holdings, Inc.",
    "0001819994": "Rocket Lab USA, Inc.",
    "0001820953": "Affirm Holdings, Inc.",
    "0001821825": "Organon & Co.",
    "0001822479": "Sotera Health Company",
    "0001823945": "Blue Owl Capital Inc.",
    "0001827090": "Certara, Inc.",
    "0001828108": "Aurora Innovation, Inc.",
    "0001833756": "Leonardo DRS, Inc.",
    "0001834584": "Coupang, Inc.",
    "0001834622": "Hayward Holdings, Inc.",
    "0001835632": "Marvell Technology",
    "0001841666": "APA Corporation",
    "0001842022": "DT Midstream, Inc.",
    "0001849253": "Ryan Specialty Holdings, Inc.",
    "0001849635": "Trump Media & Technology Group Corp.",
    "0001852244": "GXO Logistics, Inc.",
    "0001856525": "Core & Main, Inc.",
    "0001858681": "Apollo Global Management, Inc.",
    "0001858985": "On Holding AG",
    "0001866581": "Dutch Bros Inc.",
    "0001867072": "Kyndryl Holdings, Inc.",
    "0001868159": "Lineage, Inc.",
    "0001868275": "Constellation Energy",
    "0001872195": "Bullish",
    "0001874178": "Rivian Automotive, Inc.",
    "0001876042": "Circle Internet Group",
    "0001877322": "ESAB Corporation",
    "0001880661": "TPG Inc.",
    "0001883685": "DraftKings Inc.",
    "0001897762": "Ingram Micro Holding Corporation",
    "0001902733": "nCino, Inc.",
    "0001915657": "HF Sinclair Corporation",
    "0001932393": "GE HealthCare",
    "0001943896": "Rubrik, Inc.",
    "0001944013": "Crane Company",
    "0001944048": "Kenvue Inc.",
    "0001957132": "SharkNinja, Inc.",
    "0001964738": "Solventum Corporation",
    "0001967680": "Veralto Corporation",
    "0001973239": "Arm Holdings",
    "0001973266": "TKO Group Holdings, Inc.",
    "0001977102": "Birkenstock Holding plc",
    "0001988894": "Amer Sports, Inc.",
    "0001996810": "GE Vernova Inc.",
    "0001996862": "Bunge Global S.A.",
    "0002000178": "Loar Holdings Inc.",
    "0002011286": "Amentum Holdings, Inc.",
    "0002011641": "Ferguson plc",
    "0002012383": "BlackRock, Inc.",
    "0002015845": "Everus Construction Group, Inc.",
    "0002017206": "Millrose Properties, Inc.",
    "0002019410": "Caris Life Sciences, Inc.",
    "0002023554": "Sandisk Corporation",
    "0002025410": "StandardAero, Inc.",
    "0002040127": "Karman Holdings Inc.",
    "0002041385": "Ralliant Corp.",
    "0002042694": "Primo Brands Corporation",
    "0002054696": "NIQ Global Intelligence Plc",
    "0002057463": "GCI Liberty, Inc.",
    "0002058873": "Qnity Electronics, Inc.",
    "0002064124": "Figure Technology Solutions, Inc. Class A Common Stock",
    "0002064953": "Solstice Advanced Materials Inc.",
    "0002067876": "Versant Media Group, Inc. Class A Common Stock When-Issued",
    "0002071778": "Fermi Inc. Common Stock",
}

# All CIK*.json files live alongside this script in openbb_sec/
CACHE_DIR = Path(__file__).resolve().parent

HEADERS = {
    "User-Agent": "OpenBB Research validation@openbb.co",
    "Accept-Encoding": "gzip, deflate",
}

# Conservative rate limiter: 5 requests/second (well under SEC's 10/s limit)
_MIN_INTERVAL = 0.2  # seconds between requests
_last_request_time: float = 0.0


def _rate_limit():
    """Sleep to enforce at most 5 requests per second."""
    global _last_request_time
    now = time.monotonic()
    elapsed = now - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def download_facts(cik: str) -> dict | None:
    """Download (or load from cache) the company-facts JSON for a CIK."""
    cache_path = CACHE_DIR / f"CIK{cik}.json"
    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    _rate_limit()
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f" FAILED ({exc})", end="")
        return None

    data = resp.json()
    with open(cache_path, "w") as f:
        json.dump(data, f)
    return data


_schema = StatementSchema()
# Source provenance categories (ordered from most to least reliable).
_SOURCE_CATEGORIES = (
    "direct_xbrl",  # Raw XBRL tag value from SEC filing
    "q4_h2_derived",  # Q4 = FY-(Q1+Q2+Q3), H2 = FY-H1 (expected quarterly math)
    "cross_stmt_lock",  # Value locked from another statement (identity_lock)
    "algebraic_impute",  # Derived from algebraic identity (imputed: X + Y - Z)
    "hierarchical_rollup",  # Parent = sum of children (imputed-rollup)
    "balancing_plug",  # Residual "other_*" plug (imputed-plug)
    "scope_correction",  # Scope/tag correction (corrected, scope-aligned, reconciled)
    "identity_enforced",  # Overridden by identity verification pass
    "period_derived",  # Cash BOP = prior period EOP (derived: cash_at_end_of_period)
    "suspect_zero",  # Zero-valued imputed item (imputed-zero)
)


def _classify_source(source: str) -> str:
    """Classify a source string into a provenance category."""
    if not source:
        return "direct_xbrl"  # shouldn't happen, but safe default
    if source.startswith("imputed-zero"):
        return "suspect_zero"
    if source.startswith("Q4:") or source.startswith("H2:"):
        return "q4_h2_derived"
    if "(identity_lock)" in source:
        return "cross_stmt_lock"
    if source.startswith("imputed-rollup"):
        return "hierarchical_rollup"
    if source.startswith("imputed-plug"):
        return "balancing_plug"
    if source.startswith("imputed"):
        return "algebraic_impute"
    if source.startswith(("corrected:", "scope-aligned:", "reconciled:")):
        return "scope_correction"
    if source.startswith("identity-enforced:"):
        return "identity_enforced"
    if source.startswith("derived:"):
        return "period_derived"
    # Anything with a namespace prefix (us-gaap:, ifrs-full:) is direct XBRL.
    # Also includes (fallback) and (NCI-corrected) variants — still raw data.
    return "direct_xbrl"


def validate_one(cik: str, name: str, facts_json: dict) -> dict:
    """Run full annual + quarterly validation for one company.

    Returns a dict summarizing the results.
    """
    result = {
        "cik": cik,
        "name": name,
        "entity_name": facts_json.get("entityName", ""),
        "company_type": "",
        "annual": {"diagnostics": [], "dates": {}, "error": None, "sources": {}},
        "quarterly": {"diagnostics": [], "dates": {}, "error": None, "sources": {}},
    }

    for freq in ("annual", "quarterly"):
        try:
            res = resolve_company_facts(facts_json, period=freq)
            result["company_type"] = res.company_type

            # Collect dates per statement
            is_dates = sorted({r["period_ending"] for r in res.income_statement})
            bs_dates = sorted({r["period_ending"] for r in res.balance_sheet})
            cf_dates = sorted({r["period_ending"] for r in res.cash_flow})
            result[freq]["dates"] = {
                "income_statement": is_dates,
                "balance_sheet": bs_dates,
                "cash_flow": cf_dates,
            }

            # Collect source provenance counts per statement
            stmt_sources: dict[str, dict[str, int]] = {}
            for stmt_name, records in [
                ("income_statement", res.income_statement),
                ("balance_sheet", res.balance_sheet),
                ("cash_flow", res.cash_flow),
            ]:
                counts: dict[str, int] = {cat: 0 for cat in _SOURCE_CATEGORIES}
                for rec in records:
                    cat = _classify_source(rec.get("source", ""))
                    counts[cat] += 1
                stmt_sources[stmt_name] = counts
            result[freq]["sources"] = stmt_sources

            # Collect diagnostics
            for d in res.diagnostics:
                result[freq]["diagnostics"].append(
                    {
                        "date": d.date,
                        "tag": d.tag,
                        "expected": d.expected,
                        "actual": d.actual,
                        "formula": d.formula,
                        "identity": d.identity,
                        "diff": abs(d.actual - d.expected),
                    }
                )
        except Exception as exc:
            result[freq]["error"] = f"{type(exc).__name__}: {exc}"

    return result


def format_report(all_results: list[dict]) -> str:
    """Format the full validation results into a readable report."""
    lines: list[str] = []
    sep = "=" * 90

    lines.append(sep)
    lines.append("  EXPANDED CORPUS VALIDATION REPORT")
    lines.append(f"  Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Total companies: {len(all_results)}")
    lines.append(sep)
    lines.append("")

    # ---------- Summary statistics ----------
    n_annual_clean = 0
    n_quarterly_clean = 0
    n_annual_diag = 0
    n_quarterly_diag = 0
    n_annual_error = 0
    n_quarterly_error = 0
    total_annual_violations = 0
    total_quarterly_violations = 0

    for r in all_results:
        if r["annual"]["error"]:
            n_annual_error += 1
        elif r["annual"]["diagnostics"]:
            n_annual_diag += 1
            total_annual_violations += len(r["annual"]["diagnostics"])
        else:
            n_annual_clean += 1

        if r["quarterly"]["error"]:
            n_quarterly_error += 1
        elif r["quarterly"]["diagnostics"]:
            n_quarterly_diag += 1
            total_quarterly_violations += len(r["quarterly"]["diagnostics"])
        else:
            n_quarterly_clean += 1

    lines.append("SUMMARY")
    lines.append("-" * 50)
    lines.append(
        f"  Annual   — Clean: {n_annual_clean}  |  "
        f"Violations: {n_annual_diag} ({total_annual_violations} total)  |  "
        f"Errors: {n_annual_error}"
    )
    lines.append(
        f"  Quarterly — Clean: {n_quarterly_clean}  |  "
        f"Violations: {n_quarterly_diag} ({total_quarterly_violations} total)  |  "
        f"Errors: {n_quarterly_error}"
    )
    lines.append("")

    # ---------- Company type breakdown ----------
    type_counts: dict[str, int] = {}
    for r in all_results:
        ct = r["company_type"] or "(unknown)"
        type_counts[ct] = type_counts.get(ct, 0) + 1
    lines.append("COMPANY TYPE BREAKDOWN")
    lines.append("-" * 50)
    for ct, cnt in sorted(type_counts.items()):
        lines.append(f"  {ct}: {cnt}")
    lines.append("")

    # ---------- Source provenance breakdown ----------
    # Aggregate across all companies per (frequency, statement)
    _CAT_LABELS = {
        "direct_xbrl": "Direct XBRL",
        "q4_h2_derived": "Q4/H2 derivation",
        "cross_stmt_lock": "Cross-stmt lock",
        "algebraic_impute": "Algebraic impute",
        "hierarchical_rollup": "Hierarchical rollup",
        "balancing_plug": "Balancing plug",
        "scope_correction": "Scope correction",
        "identity_enforced": "Identity enforced",
        "period_derived": "Period derived",
        "suspect_zero": "Suspect zero",
    }

    for freq_label, freq_key in [("ANNUAL", "annual"), ("QUARTERLY", "quarterly")]:
        lines.append(f"SOURCE PROVENANCE — {freq_label}")
        lines.append("-" * 90)
        # Header
        lines.append(
            f"  {'Category':<25s}  {'Income Stmt':>12s}  {'Balance Sheet':>14s}"
            f"  {'Cash Flow':>12s}  {'Total':>12s}"
        )
        lines.append("  " + "-" * 80)

        # Aggregate
        totals_by_stmt: dict[str, dict[str, int]] = {
            s: {cat: 0 for cat in _SOURCE_CATEGORIES}
            for s in ("income_statement", "balance_sheet", "cash_flow")
        }
        for r in all_results:
            freq_data = r.get(freq_key, {})
            for stmt_name, counts in freq_data.get("sources", {}).items():
                for cat, cnt in counts.items():
                    totals_by_stmt[stmt_name][cat] += cnt

        grand_total = 0
        for cat in _SOURCE_CATEGORIES:
            is_n = totals_by_stmt["income_statement"][cat]
            bs_n = totals_by_stmt["balance_sheet"][cat]
            cf_n = totals_by_stmt["cash_flow"][cat]
            row_total = is_n + bs_n + cf_n
            grand_total += row_total
            if row_total == 0:
                continue
            lines.append(
                f"  {_CAT_LABELS.get(cat, cat):<25s}"
                f"  {is_n:>12,d}  {bs_n:>14,d}  {cf_n:>12,d}  {row_total:>12,d}"
            )

        # Totals row
        is_t = sum(totals_by_stmt["income_statement"].values())
        bs_t = sum(totals_by_stmt["balance_sheet"].values())
        cf_t = sum(totals_by_stmt["cash_flow"].values())
        lines.append("  " + "-" * 80)
        lines.append(
            f"  {'TOTAL':<25s}  {is_t:>12,d}  {bs_t:>14,d}"
            f"  {cf_t:>12,d}  {grand_total:>12,d}"
        )

        # Percentage breakdown (excluding Q4/H2 since it's expected)
        if grand_total > 0:
            direct = sum(totals_by_stmt[s]["direct_xbrl"] for s in totals_by_stmt)
            q4h2 = sum(totals_by_stmt[s]["q4_h2_derived"] for s in totals_by_stmt)
            computed = grand_total - direct - q4h2
            lines.append("")
            lines.append(
                f"  Direct XBRL: {direct:,d} ({100*direct/grand_total:.1f}%)"
                f"  |  Q4/H2: {q4h2:,d} ({100*q4h2/grand_total:.1f}%)"
                f"  |  Other computed: {computed:,d} ({100*computed/grand_total:.1f}%)"
            )
        lines.append("")

    # ---------- Failures & violations detail ----------
    lines.append(sep)
    lines.append("  DETAILED RESULTS — FAILURES AND VIOLATIONS")
    lines.append(sep)
    lines.append("")

    any_issues = False
    for r in all_results:
        has_issue = (
            r["annual"]["error"]
            or r["quarterly"]["error"]
            or r["annual"]["diagnostics"]
            or r["quarterly"]["diagnostics"]
        )
        if not has_issue:
            continue
        any_issues = True

        lines.append(f"--- {r['name']} (CIK {r['cik']}) ---")
        lines.append(f"    Entity: {r['entity_name']}")
        lines.append(f"    Type:   {r['company_type']}")
        lines.append("")

        for freq in ("annual", "quarterly"):
            fd = r[freq]
            if fd["error"]:
                lines.append(f"  [{freq.upper()}] ERROR: {fd['error']}")
                lines.append("")
            elif fd["diagnostics"]:
                lines.append(
                    f"  [{freq.upper()}] {len(fd['diagnostics'])} identity violation(s):"
                )
                for d in fd["diagnostics"]:
                    lines.append(
                        f"    • {d['date']} | {d['tag']}"
                        f"  expected={d['expected']:,.0f}"
                        f"  actual={d['actual']:,.0f}"
                        f"  diff={d['diff']:,.0f}"
                    )
                    lines.append(f"      identity: {d['identity']}")
                    lines.append(f"      formula:  {d['formula']}")
                lines.append("")

        lines.append("")

    if not any_issues:
        lines.append("  *** ALL COMPANIES PASSED WITH ZERO DIAGNOSTICS ***")
        lines.append("")

    # ---------- Clean companies list ----------
    lines.append(sep)
    lines.append("  CLEAN COMPANIES (zero diagnostics, no errors)")
    lines.append(sep)
    lines.append("")
    for r in all_results:
        has_issue = (
            r["annual"]["error"]
            or r["quarterly"]["error"]
            or r["annual"]["diagnostics"]
            or r["quarterly"]["diagnostics"]
        )
        if not has_issue:
            # Summarize source counts for this company
            parts = []
            for fk in ("annual", "quarterly"):
                src = r.get(fk, {}).get("sources", {})
                direct = sum(s.get("direct_xbrl", 0) for s in src.values())
                total = sum(sum(s.values()) for s in src.values())
                if total > 0:
                    pct = 100 * direct / total
                    parts.append(f"{fk[0].upper()}:{direct}/{total}={pct:.0f}%")
            src_summary = f"  [{', '.join(parts)}]" if parts else ""
            lines.append(
                f"  ✓ {r['name']} (CIK {r['cik']}, type={r['company_type']})"
                f"{src_summary}"
            )

    lines.append("")
    lines.append(sep)
    lines.append("  END OF REPORT")
    lines.append(sep)

    return "\n".join(lines)


def main():
    """Run the full validation pipeline and save the report."""
    report_path = Path(__file__).resolve().parent / "corpus_validation_report.txt"
    print(f"Corpus: {len(FULL_CORPUS)} companies")
    print(f"Cache dir: {CACHE_DIR}")
    print()

    # --- Phase 1: Download all company facts (rate-limited) ---
    print("Phase 1: Downloading company facts from SEC ...")
    download_failures = []
    facts_cache: dict[str, dict] = {}

    for i, (cik, name) in enumerate(sorted(FULL_CORPUS.items()), 1):
        cache_path = CACHE_DIR / f"CIK{cik}.json"
        status = "cached" if cache_path.exists() else "downloading"
        print(
            f"  [{i:3d}/{len(FULL_CORPUS)}] CIK {cik} {name:40s} ... {status}",
            end="",
            flush=True,
        )

        data = download_facts(cik)
        if data is None:
            print(" FAILED")
            download_failures.append((cik, name))
        else:
            facts_cache[cik] = data
            print(" ok")

    if download_failures:
        print(f"\n  WARNING: {len(download_failures)} download failure(s):")
        for cik, name in download_failures:
            print(f"    - CIK {cik} ({name})")
    print()

    # --- Phase 1b: Download and prepare multi-CIK merged entities ---
    # For tickers in MULTI_CIK_TICKERS, download any missing CIKs
    # and build a merged facts_json for unified validation.
    merged_entities: dict[str, tuple[str, dict]] = (
        {}
    )  # ticker -> (display_name, merged_facts_json)
    merged_ciks: set[str] = set()  # CIKs that are part of a merge group

    for ticker, cik_list in MULTI_CIK_TICKERS.items():
        # Check if at least one CIK from this group is in the corpus
        in_corpus = [c for c in cik_list if c in FULL_CORPUS]
        if not in_corpus:
            continue

        # Download any missing CIKs not already in facts_cache
        all_facts = []
        all_ok = True
        for c in cik_list:
            if c in facts_cache:
                all_facts.append(facts_cache[c])
            else:
                # Need to download this CIK (it's not in the corpus but needed for merge)
                print(
                    f"  Downloading CIK {c} for {ticker} merge ... ", end="", flush=True
                )
                data = download_facts(c)
                if data:
                    facts_cache[c] = data
                    all_facts.append(data)
                    print("ok")
                else:
                    print("FAILED")
                    all_ok = False

        if not all_ok or len(all_facts) < 2:
            continue

        # Merge using StatementSchema.merge_facts
        primary = all_facts[0]  # first = newest CIK
        merged_facts = _schema.merge_facts(*all_facts)
        merged_json = {
            "entityName": primary.get("entityName", ""),
            "cik": primary.get("cik", ""),
            "facts": merged_facts,
        }
        display_name = f"{FULL_CORPUS.get(cik_list[0], primary.get('entityName', ticker))} [MERGED:{ticker}]"
        merged_entities[ticker] = (display_name, merged_json)
        merged_ciks.update(cik_list)
        print(f"  Prepared merged entity: {display_name} ({len(cik_list)} CIKs)")

    print()

    # --- Phase 2: Run validation pipeline (parallel) ---
    print("Phase 2: Running validation pipeline ...")

    # Build work items: list of (cik, name, facts_json)
    work_items: list[tuple[str, str, dict]] = []

    non_merged = {k: v for k, v in FULL_CORPUS.items() if k not in merged_ciks}
    for cik, name in sorted(non_merged.items()):
        if cik in facts_cache:
            work_items.append((cik, name, facts_cache[cik]))

    for ticker, (display_name, merged_json) in sorted(merged_entities.items()):
        cik_primary = MULTI_CIK_TICKERS[ticker][0]
        work_items.append((cik_primary, display_name, merged_json))

    total_to_validate = len(work_items)
    n_workers = min(os.cpu_count() or 4, total_to_validate)
    print(f"  {total_to_validate} companies, {n_workers} workers")

    all_results: list[dict] = []
    t0 = time.monotonic()

    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        future_to_item = {
            pool.submit(validate_one, cik, name, facts_json): (cik, name)
            for cik, name, facts_json in work_items
        }
        for idx, future in enumerate(as_completed(future_to_item), 1):
            cik, name = future_to_item[future]
            result = future.result()

            n_diag_a = len(result["annual"]["diagnostics"])
            n_diag_q = len(result["quarterly"]["diagnostics"])
            err_a = result["annual"]["error"]
            err_q = result["quarterly"]["error"]

            status_parts = []
            if err_a:
                status_parts.append("annual-ERROR")
            elif n_diag_a:
                status_parts.append(f"annual:{n_diag_a} violations")
            if err_q:
                status_parts.append("quarterly-ERROR")
            elif n_diag_q:
                status_parts.append(f"quarterly:{n_diag_q} violations")

            if status_parts:
                print(
                    f"  [{idx:3d}/{total_to_validate}] {name:40s}  ⚠  {' | '.join(status_parts)}"
                )
            else:
                print(
                    f"  [{idx:3d}/{total_to_validate}] {name:40s}  ✓  clean ({result['company_type']})"
                )

            all_results.append(result)

    elapsed = time.monotonic() - t0
    print(f"  Validated {total_to_validate} companies in {elapsed:.1f}s")

    # --- Phase 3: Write report ---
    print()
    print(f"Phase 3: Writing report to {report_path} ...")
    report_text = format_report(all_results)
    with open(report_path, "w") as f:
        f.write(report_text)
    print("Done.")

    # Also write machine-readable JSON
    json_path = report_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"JSON results: {json_path}")

    # Quick summary to stdout
    print()
    n_fail = sum(
        1
        for r in all_results
        if r["annual"]["diagnostics"]
        or r["quarterly"]["diagnostics"]
        or r["annual"]["error"]
        or r["quarterly"]["error"]
    )
    print(f"=== {len(all_results)} companies validated, {n_fail} with issues ===")


if __name__ == "__main__":
    main()
