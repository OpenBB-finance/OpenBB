"""OpenBB JODI Provider Module Constants."""

from typing import Literal

OilProductType = Literal[
    "crude_oil",
    "ngl",
    "other_crude",
    "total_crude",
    "lpg",
    "naphtha",
    "gasoline",
    "kerosene",
    "jet_fuel",
    "gas_diesel_oil",
    "fuel_oil",
    "other_products",
    "total_products",
]
OilPrimaryProductType = Literal["crude_oil", "ngl", "other_crude", "total_crude"]
OilSecondaryProductType = Literal[
    "lpg",
    "naphtha",
    "gasoline",
    "kerosene",
    "jet_fuel",
    "gas_diesel_oil",
    "fuel_oil",
    "other_products",
    "total_products",
]
OilUnitType = Literal["kbd", "kbbl", "kl", "ktons", "conversion_factor"]
GasUnitType = Literal["m3", "tj", "ktons"]

OIL_TABLE_URLS = {
    "primary": "https://www.jodidata.org/_resources/files/downloads/oil-data/world_Primary_CSV.zip",
    "secondary": "https://www.jodidata.org/_resources/files/downloads/oil-data/world_Secondary_CSV.zip",
}
GAS_FILES_URL = "https://api.publisher.jodidata.org/web/files/gas"
GAS_DOWNLOAD_URL = (
    "https://www.jodidata.org/jodi-publisher/gas/{publication_id}/{filename}"
)

OIL_START_YEAR = 2002
GAS_START_YEAR = 2009

# Item codes and full names per 'A Guide on JODI-Oil World Database Item Names' (2017)
# and 'A Guide on JODI-Gas World Database Item Names' (2025).
OIL_PRODUCTS = {
    "crude_oil": ("CRUDEOIL", "primary"),
    "ngl": ("NGL", "primary"),
    "other_crude": ("OTHERCRUDE", "primary"),
    "total_crude": ("TOTCRUDE", "primary"),
    "lpg": ("LPG", "secondary"),
    "naphtha": ("NAPHTHA", "secondary"),
    "gasoline": ("GASOLINE", "secondary"),
    "kerosene": ("KEROSENE", "secondary"),
    "jet_fuel": ("JETKERO", "secondary"),
    "gas_diesel_oil": ("GASDIES", "secondary"),
    "fuel_oil": ("RESFUEL", "secondary"),
    "other_products": ("ONONSPEC", "secondary"),
    "total_products": ("TOTPRODS", "secondary"),
}

OIL_PRODUCT_LABELS = {
    "CRUDEOIL": "Crude oil",
    "NGL": "NGL",
    "OTHERCRUDE": "Other primary",
    "TOTCRUDE": "Total primary",
    "LPG": "Liquefied petroleum gases",
    "NAPHTHA": "Naphtha",
    "GASOLINE": "Motor and aviation gasoline",
    "KEROSENE": "Kerosenes",
    "JETKERO": "Kerosene type jet fuel",
    "GASDIES": "Gas/diesel oil",
    "RESFUEL": "Fuel oil",
    "ONONSPEC": "Other oil products",
    "TOTPRODS": "Total oil products",
}

OIL_FLOWS = {
    "production": {"primary": "INDPROD"},
    "from_other_sources": {"primary": "OSOURCES"},
    "imports": {"primary": "TOTIMPSB", "secondary": "TOTIMPSB"},
    "exports": {"primary": "TOTEXPSB", "secondary": "TOTEXPSB"},
    "products_transferred": {"primary": "TRANSBAK", "secondary": "PTRANSF"},
    "direct_use": {"primary": "DIRECUSE"},
    "stock_change": {"primary": "STOCKCH", "secondary": "STOCKCH"},
    "statistical_difference": {"primary": "STATDIFF", "secondary": "STATDIFF"},
    "refinery_intake": {"primary": "REFINOBS"},
    "refinery_output": {"secondary": "REFGROUT"},
    "receipts": {"secondary": "RECEIPTS"},
    "interproduct_transfers": {"secondary": "IPTRANSF"},
    "demand": {"secondary": "TOTDEMO"},
    "closing_stocks": {"primary": "CLOSTLV", "secondary": "CLOSTLV"},
}

OIL_FLOW_LABELS = {
    "INDPROD": "Production",
    "OSOURCES": "From other sources",
    "TOTIMPSB": "Imports",
    "TOTEXPSB": "Exports",
    "TRANSBAK": "Products transferred/Backflows",
    "PTRANSF": "Products transferred",
    "DIRECUSE": "Direct use",
    "STOCKCH": "Stock change",
    "STATDIFF": "Statistical difference",
    "REFINOBS": "Refinery intake",
    "REFGROUT": "Refinery output",
    "RECEIPTS": "Receipts",
    "IPTRANSF": "Interproduct transfers",
    "TOTDEMO": "Demand",
    "CLOSTLV": "Closing stocks",
}

OIL_UNITS = {
    "kbd": "KBD",
    "kbbl": "KBBL",
    "kl": "KL",
    "ktons": "KTONS",
    "conversion_factor": "CONVBBL",
}

OIL_UNIT_LABELS = {
    "kbd": "Thousand barrels per day",
    "kbbl": "Thousand barrels",
    "kl": "Thousand kilolitres",
    "ktons": "Thousand metric tons",
    "conversion_factor": "Conversion factor barrels/ktons",
}

GAS_FLOWS = {
    "production": "INDPROD",
    "from_other_sources": "OSOURCES",
    "imports": "TOTIMPSB",
    "lng_imports": "IMPLNG",
    "pipeline_imports": "IMPPIP",
    "exports": "TOTEXPSB",
    "lng_exports": "EXPLNG",
    "pipeline_exports": "EXPPIP",
    "stock_change": "STOCKCH",
    "demand": "TOTDEMO",
    "demand_calculated": "TOTDEMC",
    "electricity_and_heat_generation": "MAINTOT",
    "statistical_difference": "STATDIFF",
    "closing_stocks": "CLOSTLV",
}

GAS_FLOW_LABELS = {
    "INDPROD": "Production",
    "OSOURCES": "Receipts from other sources",
    "TOTIMPSB": "Imports",
    "IMPLNG": "LNG imports",
    "IMPPIP": "Pipeline imports",
    "TOTEXPSB": "Exports",
    "EXPLNG": "LNG exports",
    "EXPPIP": "Pipeline exports",
    "STOCKCH": "Stock change",
    "TOTDEMO": "Gross inland deliveries (observed)",
    "TOTDEMC": "Gross inland deliveries (calculated)",
    "MAINTOT": "Of which: electricity and heat generation",
    "STATDIFF": "Statistical difference",
    "CLOSTLV": "Closing stocks",
}

GAS_UNITS = {
    "m3": "M3",
    "tj": "TJ",
    "ktons": "KTONS",
}

GAS_UNIT_LABELS = {
    "m3": "Million cubic metres",
    "tj": "Terajoules",
    "ktons": "Thousand metric tons (LNG)",
}

ASSESSMENT_LABELS = {
    "1": "Reasonable levels of comparability",
    "2": "Consult metadata/use with caution",
    "3": "Not assessed",
    "4": "Under verification",
}

# Definitions per the JODI-Oil Monthly Questionnaire Short Definitions and the
# JODI-Gas Questionnaire brief reporting guide (www.jodidata.org).
NATURAL_GAS_DEFINITION = (
    "Natural gas is a mixture of gaseous hydrocarbons, primarily methane, but"
    " generally also including ethane, propane, and higher hydrocarbons in much"
    " smaller amounts, and some non-combustible gases such as nitrogen and carbon"
    " dioxide. It includes both non-associated and associated gas. Colliery gas,"
    " coal seam gas, and shale gas are included, while manufactured gas and biogas"
    " are excluded except when blended with natural gas for final consumption."
    " Natural gas liquids are excluded."
)

OIL_PRODUCT_DEFINITIONS = {
    "crude_oil": "Crude oil, including lease condensate and excluding NGL.",
    "ngl": "Liquid or liquefied hydrocarbons recovered from gas separation"
    " plants and gas processing facilities.",
    "other_crude": "Refinery feedstocks, additives/oxygenates, and other hydrocarbons.",
    "total_crude": "The sum of the primary categories: crude oil + NGL + other.",
    "lpg": "Liquefied petroleum gases, comprising propane and butane.",
    "naphtha": "Naphtha used as feedstock for producing high octane gasoline"
    " and as feedstock for the chemical/petrochemical industries.",
    "gasoline": "Motor gasoline and aviation gasoline; motor gasoline includes"
    " biogasoline, e.g. ethanol blends.",
    "kerosene": "Kerosenes, comprising jet kerosene and other kerosene.",
    "jet_fuel": "Kerosene type jet fuel: aviation fuel used for aviation"
    " turbine power units; a subset of the amount reported under kerosenes.",
    "gas_diesel_oil": "Gas/diesel oil, for automotive and other purposes;"
    " biodiesel is included.",
    "fuel_oil": "Heavy residual oil/boiler oil, including bunker oil.",
    "other_products": "Refinery gas, ethane, petroleum coke, lubricants, white"
    " spirit and SBP, bitumen, paraffin waxes, and other petroleum products.",
    "total_products": "The sum of all secondary product categories; demand for"
    " total products includes direct use of crude oil, NGL, and other"
    " hydrocarbons.",
}

OIL_FLOW_DEFINITIONS = {
    "production": "Marketed production, after removal of impurities but"
    " including quantities consumed by the producer in the production process.",
    "refinery_output": "Gross refinery output of finished products, including"
    " refinery fuel.",
    "from_other_sources": "Inputs of additives, biofuels, and other"
    " hydrocarbons produced from non-oil sources such as coal, natural gas,"
    " and renewable energy.",
    "receipts": "Primary product receipts (quantities of oil used directly"
    " without processing in a refinery) plus recycled products. Receipts for"
    " other oil products include direct use of crude oil and NGL.",
    "imports": "Goods having physically crossed the international boundaries,"
    " excluding transit trade and international marine and aviation bunkers.",
    "exports": "Goods having physically crossed the international boundaries,"
    " excluding transit trade and international marine and aviation bunkers.",
    "products_transferred": "For primary products, the sum of products"
    " transferred and backflows from the petrochemical industry; for secondary"
    " products, imported petroleum products reclassified as feedstocks for"
    " further processing in the refinery, without delivery to final consumers.",
    "interproduct_transfers": "Reclassification of products because their"
    " specification has changed or because they are blended into another"
    " product; a negative entry indicates a product to be reclassified, a"
    " positive entry a reclassified product. Interproduct transfers for other"
    " oil products include interproduct transfers of crude oil and NGL.",
    "direct_use": "Crude oil, NGL, and other hydrocarbons used directly"
    " without being processed in oil refineries, for example crude oil burned"
    " for electricity generation.",
    "stock_change": "Closing minus opening stock level; a positive number"
    " corresponds to a stock build, a negative number to a stock draw.",
    "statistical_difference": "Differences between observed supply flows and"
    " refinery intake or demand.",
    "refinery_intake": "Observed refinery throughputs.",
    "demand": "Deliveries or sales to the inland market (domestic consumption)"
    " plus refinery fuel plus international marine and aviation bunkers."
    " Demand for other oil products includes direct use of crude oil, NGL,"
    " and other primary hydrocarbons.",
    "closing_stocks": "The primary stock level at the end of the month within"
    " national territories; includes stocks held by importers, refiners,"
    " stock-holding organisations, and governments.",
}

GAS_FLOW_DEFINITIONS = {
    "production": "Dry marketable production within national boundaries,"
    " including offshore production, measured after purification and extraction"
    " of NGL and sulphur; excludes quantities reinjected, extraction losses,"
    " and quantities vented or flared; includes quantities used within the"
    " natural gas industry, in gas extraction, pipeline systems, and processing"
    " plants.",
    "from_other_sources": "Gas from energy products already accounted for in"
    " the production of other energy products, for example petroleum gases or"
    " biogases blended with natural gas.",
    "imports": "Amounts that have crossed the physical boundaries of the"
    " country, whether customs clearance has taken place or not; excludes goods"
    " in transit and goods temporarily admitted/withdrawn, includes re-imports;"
    " deliveries for international bunkers are excluded.",
    "pipeline_imports": "Imports of gaseous natural gas through pipelines.",
    "lng_imports": "Imports of liquefied natural gas through ocean tankers, on"
    " a re-gasified equivalent basis.",
    "exports": "Amounts that have crossed the physical boundaries of the"
    " country, whether customs clearance has taken place or not; excludes goods"
    " in transit and goods temporarily admitted/withdrawn, includes re-exports;"
    " deliveries for international bunkers are excluded.",
    "pipeline_exports": "Exports of gaseous natural gas through pipelines.",
    "lng_exports": "Exports of liquefied natural gas through ocean tankers, on"
    " a re-gasified equivalent basis.",
    "stock_change": "The difference between the closing and opening stock"
    " level of recoverable gas already extracted; a stock build is shown as a"
    " positive number, a stock draw as a negative number.",
    "demand_calculated": "Gross inland deliveries (calculated): production +"
    " receipts from other sources + imports - exports - stock change.",
    "statistical_difference": "The difference between the calculated and"
    " observed gross inland deliveries.",
    "demand": "Gross inland deliveries (observed): deliveries of marketable"
    " gas to the inland market, including gas used by the gas industry for"
    " heating and operation of equipment, losses in distribution, and"
    " deliveries to international marine and aviation bunkers.",
    "electricity_and_heat_generation": "Deliveries of natural gas for the"
    " generation of electricity and heat in power plants, including both"
    " main-activity and autoproducer plants.",
    "closing_stocks": "The stock level held on the national territory on the"
    " last day of the reference month.",
}

# Flow code -> balance-view field name, in questionnaire order.
OIL_BALANCE_FIELDS = {
    "INDPROD": "production",
    "REFGROUT": "refinery_output",
    "OSOURCES": "from_other_sources",
    "RECEIPTS": "receipts",
    "TOTIMPSB": "imports",
    "TOTEXPSB": "exports",
    "TRANSBAK": "products_transferred",
    "PTRANSF": "products_transferred",
    "IPTRANSF": "interproduct_transfers",
    "DIRECUSE": "direct_use",
    "STOCKCH": "stock_change",
    "STATDIFF": "statistical_difference",
    "REFINOBS": "refinery_intake",
    "TOTDEMO": "demand",
    "CLOSTLV": "closing_stocks",
}

GAS_BALANCE_FIELDS = {
    "INDPROD": "production",
    "OSOURCES": "from_other_sources",
    "TOTIMPSB": "imports",
    "IMPPIP": "pipeline_imports",
    "IMPLNG": "lng_imports",
    "TOTEXPSB": "exports",
    "EXPPIP": "pipeline_exports",
    "EXPLNG": "lng_exports",
    "STOCKCH": "stock_change",
    "TOTDEMC": "demand_calculated",
    "STATDIFF": "statistical_difference",
    "TOTDEMO": "demand",
    "MAINTOT": "electricity_and_heat_generation",
    "CLOSTLV": "closing_stocks",
}

# Product code -> demand-by-product field name, in published order.
OIL_PRODUCT_FIELDS = {
    "LPG": "lpg",
    "NAPHTHA": "naphtha",
    "GASOLINE": "gasoline",
    "KEROSENE": "kerosene",
    "JETKERO": "jet_fuel",
    "GASDIES": "gas_diesel_oil",
    "RESFUEL": "fuel_oil",
    "ONONSPEC": "other_products",
    "TOTPRODS": "total_products",
}

# ISO 3166-1 alpha-2 codes observed in the JODI world databases.
COUNTRIES = {
    "albania": "AL",
    "algeria": "DZ",
    "angola": "AO",
    "argentina": "AR",
    "armenia": "AM",
    "australia": "AU",
    "austria": "AT",
    "azerbaijan": "AZ",
    "bahrain": "BH",
    "bangladesh": "BD",
    "barbados": "BB",
    "belarus": "BY",
    "belgium": "BE",
    "belize": "BZ",
    "bermuda": "BM",
    "bolivia": "BO",
    "brazil": "BR",
    "brunei": "BN",
    "bulgaria": "BG",
    "canada": "CA",
    "chile": "CL",
    "china": "CN",
    "colombia": "CO",
    "costa_rica": "CR",
    "croatia": "HR",
    "cuba": "CU",
    "cyprus": "CY",
    "czechia": "CZ",
    "denmark": "DK",
    "dominican_republic": "DO",
    "ecuador": "EC",
    "egypt": "EG",
    "el_salvador": "SV",
    "equatorial_guinea": "GQ",
    "estonia": "EE",
    "eswatini": "SZ",
    "finland": "FI",
    "france": "FR",
    "gabon": "GA",
    "gambia": "GM",
    "georgia": "GE",
    "germany": "DE",
    "greece": "GR",
    "grenada": "GD",
    "guatemala": "GT",
    "guyana": "GY",
    "haiti": "HT",
    "honduras": "HN",
    "hong_kong": "HK",
    "hungary": "HU",
    "iceland": "IS",
    "india": "IN",
    "indonesia": "ID",
    "iran": "IR",
    "iraq": "IQ",
    "ireland": "IE",
    "italy": "IT",
    "jamaica": "JM",
    "japan": "JP",
    "kazakhstan": "KZ",
    "kuwait": "KW",
    "latvia": "LV",
    "libya": "LY",
    "lithuania": "LT",
    "luxembourg": "LU",
    "malaysia": "MY",
    "malta": "MT",
    "mauritius": "MU",
    "mexico": "MX",
    "moldova": "MD",
    "morocco": "MA",
    "myanmar": "MM",
    "nepal": "NP",
    "netherlands": "NL",
    "new_zealand": "NZ",
    "nicaragua": "NI",
    "niger": "NE",
    "nigeria": "NG",
    "north_macedonia": "MK",
    "norway": "NO",
    "oman": "OM",
    "panama": "PA",
    "papua_new_guinea": "PG",
    "paraguay": "PY",
    "peru": "PE",
    "philippines": "PH",
    "poland": "PL",
    "portugal": "PT",
    "qatar": "QA",
    "romania": "RO",
    "russia": "RU",
    "saudi_arabia": "SA",
    "serbia": "RS",
    "singapore": "SG",
    "slovakia": "SK",
    "slovenia": "SI",
    "south_africa": "ZA",
    "south_korea": "KR",
    "spain": "ES",
    "sudan": "SD",
    "suriname": "SR",
    "sweden": "SE",
    "switzerland": "CH",
    "syria": "SY",
    "taiwan": "TW",
    "tajikistan": "TJ",
    "thailand": "TH",
    "trinidad_and_tobago": "TT",
    "tunisia": "TN",
    "turkiye": "TR",
    "ukraine": "UA",
    "united_arab_emirates": "AE",
    "united_kingdom": "GB",
    "united_states": "US",
    "uruguay": "UY",
    "venezuela": "VE",
    "vietnam": "VN",
    "yemen": "YE",
}

CODE_TO_COUNTRY = {v: k for k, v in COUNTRIES.items()}

COUNTRY_LABELS = {
    code: name.replace("_", " ").title().replace(" And ", " and ")
    for name, code in COUNTRIES.items()
}

COUNTRY_WIDGET_OPTIONS = [
    {"label": COUNTRY_LABELS[code], "value": name} for name, code in COUNTRIES.items()
]

# 'choices' is never set for country params: the static package rejects None defaults
# when choices are set, and choices would reject ISO code input before validators run.
COUNTRY_SCHEMA_MULTI = {
    "multiple_items_allowed": True,
    "x-widget_config": {
        "options": COUNTRY_WIDGET_OPTIONS,
        "style": {"popupWidth": 450},
    },
}

COUNTRY_SCHEMA_SINGLE = {
    "x-widget_config": {
        "options": COUNTRY_WIDGET_OPTIONS,
        "style": {"popupWidth": 450},
    },
}

COUNTRY_MULTI_DESCRIPTION = (
    "The country or countries to get data for, by name or ISO 3166-1 alpha-2 code."
    + " If None, all reporting countries are returned."
)
COUNTRY_SINGLE_DESCRIPTION = (
    "The country to get data for, by name or ISO 3166-1 alpha-2 code."
)
OIL_UNIT_DESCRIPTION = (
    "The unit of measurement."
    + " kbd: thousand barrels per day; kbbl: thousand barrels;"
    + " kl: thousand kilolitres; ktons: thousand metric tons;"
    + " conversion_factor: barrels per thousand metric tons."
)
GAS_UNIT_DESCRIPTION = (
    "The unit of measurement."
    + " m3: million cubic metres (at 15C, 760 mm Hg);"
    + " tj: terajoules, on a gross calorific value basis;"
    + " ktons: thousand metric tons, on a re-gasified equivalent basis,"
    + " reported only for LNG trade amounts."
)

PRIMARY_PRODUCTS = ["crude_oil", "ngl", "other_crude", "total_crude"]
SECONDARY_PRODUCTS = [name for name in OIL_PRODUCTS if name not in PRIMARY_PRODUCTS]

OIL_PRODUCT_CHOICES_DESCRIPTION = "\n".join(
    f"    {name}: {OIL_PRODUCT_DEFINITIONS[name]}" for name in OIL_PRODUCTS
)
OIL_PRIMARY_PRODUCT_CHOICES_DESCRIPTION = "\n".join(
    f"    {name}: {OIL_PRODUCT_DEFINITIONS[name]}" for name in PRIMARY_PRODUCTS
)
OIL_SECONDARY_PRODUCT_CHOICES_DESCRIPTION = "\n".join(
    f"    {name}: {OIL_PRODUCT_DEFINITIONS[name]}" for name in SECONDARY_PRODUCTS
)
USE_CACHE_DESCRIPTION = (
    "If True, the source tables are cached under the user cache directory"
    + " and revalidated against the source at most once per day,"
    + " downloading again only when JODI has published an update."
)
