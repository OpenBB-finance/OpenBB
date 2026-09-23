"""USDA ERS Feed Grains Yearbook file catalog and parsers."""

import csv
import re
from io import StringIO

from openbb_core.app.model.abstract.error import OpenBBError

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/feed-grains-database/feed-grains-yearbook-tables"
MEDIA_PATH = "/media/5766/feed-grains-yearbook-tables-all-years.csv"

TABLE_GROUPS: dict[str, str] = {
    "acreage_and_farm_price": "U.S. Acreage, production, yield, and farm price",
    "animal_units": "Processed feeds and animal unit indexes",
    "industrial_use": "Feed, seed, and industrial uses",
    "prices": "Domestic and international prices",
    "production_and_stocks": "U.S. Production, harvested acreage, yield, and stocks",
    "rail_shipments": "Rail rates and grain shipments",
    "supply_and_use": "U.S. Supply and disappearance",
    "trade": "Exports and imports",
    "world_supply_and_use": "World production, supply, and disappearance",
}

FEED_GRAINS_TABLES: dict[str, dict] = {
    "acreage_production_and_price": {
        "number": 1,
        "name": "Table 1--Corn, sorghum, barley, and oats: Planted acreage,"
        " harvested acreage, production, yield, and price received by farmers",
        "group": "acreage_and_farm_price",
    },
    "foreign_coarse_grains_supply_and_use": {
        "number": 2,
        "name": "Table 2--Foreign coarse grains: Supply and disappearance",
        "group": "world_supply_and_use",
    },
    "feed_grains_supply_and_use": {
        "number": 3,
        "name": "Table 3--Feed grains (corn, sorghum, barley, and oats):"
        " Supply and disappearance, million metric tons",
        "group": "supply_and_use",
    },
    "corn_supply_and_use": {
        "number": 4,
        "name": "Table 4--Corn: Supply and disappearance, million bushels",
        "group": "supply_and_use",
    },
    "sorghum_supply_and_use": {
        "number": 5,
        "name": "Table 5--Sorghum: Supply and disappearance, million bushels",
        "group": "supply_and_use",
    },
    "barley_supply_and_use": {
        "number": 6,
        "name": "Table 6--Barley: Supply and disappearance, million bushels",
        "group": "supply_and_use",
    },
    "oats_supply_and_use": {
        "number": 7,
        "name": "Table 7--Oats: Supply and disappearance, million bushels",
        "group": "supply_and_use",
    },
    "hay_production_and_stocks": {
        "number": 8,
        "name": "Table 8--Hay: Production, harvested acreage, yield, and stocks",
        "group": "production_and_stocks",
    },
    "corn_and_sorghum_farm_prices": {
        "number": 9,
        "name": "Table 9--Corn and sorghum: Prices received by farmers, United States",
        "group": "prices",
    },
    "barley_and_oats_farm_prices": {
        "number": 10,
        "name": "Table 10--Barley and oats: Prices received by farmers,"
        " United States, dollars per bushel",
        "group": "prices",
    },
    "hay_farm_prices": {
        "number": 11,
        "name": "Table 11--Hay: Prices received by farmers, United States,"
        " dollars per ton",
        "group": "prices",
    },
    "corn_cash_prices": {
        "number": 12,
        "name": "Table 12--Corn: Cash prices at principal markets, dollars per bushel",
        "group": "prices",
    },
    "sorghum_cash_prices": {
        "number": 13,
        "name": "Table 13--Sorghum: Cash prices at principal markets,"
        " dollars per hundredweight",
        "group": "prices",
    },
    "barley_and_oats_cash_prices": {
        "number": 14,
        "name": "Table 14--Barley and Oats: Cash prices at principal markets,"
        " dollars per bushel",
        "group": "prices",
    },
    "feed_price_ratios": {
        "number": 15,
        "name": "Table 15--Feed-price ratios for livestock, poultry, and milk",
        "group": "prices",
    },
    "byproduct_feed_prices": {
        "number": 16,
        "name": "Table 16--Byproduct feeds: Wholesale price, bulk,"
        " specified markets, dollars per ton",
        "group": "prices",
    },
    "processed_corn_product_prices": {
        "number": 17,
        "name": "Table 17--Processed corn products: Quoted market prices",
        "group": "prices",
    },
    "corn_and_sorghum_exports": {
        "number": 18,
        "name": "Table 18--U.S. corn and sorghum exports",
        "group": "trade",
    },
    "barley_and_oats_exports": {
        "number": 19,
        "name": "Table 19--U.S. barley and oats exports",
        "group": "trade",
    },
    "corn_and_sorghum_imports": {
        "number": 20,
        "name": "Table 20--U.S. corn and sorghum imports",
        "group": "trade",
    },
    "barley_and_oats_imports": {
        "number": 21,
        "name": "Table 21--U.S. barley and oats imports",
        "group": "trade",
    },
    "corn_and_sorghum_exports_by_destination": {
        "number": 22,
        "name": "Table 22--U.S. corn and sorghum exports by selected destinations",
        "group": "trade",
    },
    "barley_and_oats_exports_by_destination": {
        "number": 23,
        "name": "Table 23--U.S. barley and oats exports by selected destinations",
        "group": "trade",
    },
    "corn_and_sorghum_imports_by_source": {
        "number": 24,
        "name": "Table 24--U.S. corn and sorghum imports by selected sources",
        "group": "trade",
    },
    "barley_and_oats_imports_by_source": {
        "number": 25,
        "name": "Table 25--U.S. barley and oats imports by selected sources",
        "group": "trade",
    },
    "white_corn_exports_by_destination": {
        "number": 26,
        "name": "Table 26--U.S. white corn exports by selected destinations",
        "group": "trade",
    },
    "world_coarse_grain_trade": {
        "number": 27,
        "name": "Table 27--World coarse grain trade: Selected exporters"
        " and importers by commodity",
        "group": "trade",
    },
    "rail_rates_and_grain_shipments": {
        "number": 28,
        "name": "Table 28--Rail rates and grain shipments",
        "group": "rail_shipments",
    },
    "processed_feeds_fed": {
        "number": 29,
        "name": "Table 29--Processed feeds: Quantities fed and feed per"
        " grain-consuming animal unit, 1,000 metric tons",
        "group": "animal_units",
    },
    "animal_unit_indexes": {
        "number": 30,
        "name": "Table 30--Indexes of feed consuming animal units, millions",
        "group": "animal_units",
    },
    "corn_food_seed_and_industrial_use": {
        "number": 31,
        "name": "Table 31--Corn: Food, seed, and industrial use, million bushels",
        "group": "industrial_use",
    },
    "ethanol_exports_by_destination": {
        "number": 32,
        "name": "Table 32--U.S. exports of ethyl alcohol by selected destinations",
        "group": "trade",
    },
    "ethanol_imports_by_source": {
        "number": 33,
        "name": "Table 33--U.S. imports of ethyl alcohol by selected sources",
        "group": "trade",
    },
    "distillers_dregs_exports_by_destination": {
        "number": 34,
        "name": "Table 34--U.S. exports of brewers' and distillers' dregs"
        " and waste by selected destination",
        "group": "trade",
    },
    "distillers_dregs_imports_by_source": {
        "number": 35,
        "name": "Table 35--U.S. imports of brewers' and distillers' dregs"
        " and waste by selected sources",
        "group": "trade",
    },
}

TABLE_NUMBER_PATTERN = re.compile(r"^Table (\d+)--")

NAME_TO_SLUG = {entry["name"]: slug for slug, entry in FEED_GRAINS_TABLES.items()}


def build_url() -> str:
    """Build the download URL of the all-years tidy yearbook CSV.

    Returns
    -------
    str
        Full URL of the yearbook CSV file.
    """
    return f"{BASE_URL}{MEDIA_PATH}"


def table_key(table_name: str) -> tuple[str, int]:
    """Resolve a published table name to its catalog slug and table number.

    Parameters
    ----------
    table_name : str
        Published table name, e.g. 'Table 28--Rail rates and grain shipments'.

    Returns
    -------
    tuple[str, int]
        Catalog slug and table number; uncataloged names fall back to a
        'table_{number}' slug.

    Raises
    ------
    OpenBBError
        If the table name does not carry a 'Table N--' prefix.
    """
    slug = NAME_TO_SLUG.get(table_name)
    if slug is not None:
        return slug, FEED_GRAINS_TABLES[slug]["number"]
    match = TABLE_NUMBER_PATTERN.match(table_name)
    if match is None:
        raise OpenBBError(f"Unrecognized table name: '{table_name}'")
    number = int(match.group(1))
    return f"table_{number}", number


def parse_rows(text: str) -> list[dict]:
    """Parse the yearbook CSV text into tidy row records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns table_group, table_name,
        commodity_group, commodity, attribute, geography, year, frequency,
        timeperiod, unit, and amount.

    Returns
    -------
    list[dict]
        Records with a derived table slug and table_number, stripped label
        columns, year as int, and value as float, skipping rows with an
        empty amount.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        amount = (row.get("amount") or "").strip()
        if not amount:
            continue
        table_name = (row.get("table_name") or "").strip()
        slug, number = table_key(table_name)
        rows.append(
            {
                "table": slug,
                "table_number": number,
                "table_name": table_name,
                "table_group": (row.get("table_group") or "").strip(),
                "commodity_group": (row.get("commodity_group") or "").strip(),
                "commodity": (row.get("commodity") or "").strip(),
                "attribute": (row.get("attribute") or "").strip(),
                "geography": (row.get("geography") or "").strip(),
                "year": int((row.get("year") or "").strip()),
                "frequency": (row.get("frequency") or "").strip(),
                "timeperiod": (row.get("timeperiod") or "").strip(),
                "unit": (row.get("unit") or "").strip(),
                "value": float(amount),
            }
        )
    return rows


async def afetch_yearbook(**kwargs) -> list[dict]:
    """Download and parse the all-years yearbook CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Raw row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig"))
