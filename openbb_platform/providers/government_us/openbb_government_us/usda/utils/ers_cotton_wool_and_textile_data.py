"""USDA ERS Cotton, Wool, and Textile Data file catalog and long-format parsers."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
YEARBOOK_PRODUCT = "data-products/cotton-wool-and-textile-data/cotton-and-wool-yearbook"
RFE_PRODUCT = (
    "data-products/cotton-wool-and-textile-data/"
    "raw-fiber-equivalents-of-us-textile-trade-data"
)

M_US_COTTON = "/media/7122/us-cotton-supply-and-demand.csv"
M_PRICES = "/media/7123/cotton-prices.csv"
M_WORLD = "/media/7124/world-cotton-supply-and-demand.csv"
M_FIBER_DEMAND = "/media/7127/us-fiber-demand.csv"
M_WOOL = "/media/7126/us-wool-supply-and-demand.csv"
M_TEXTILE = "/media/7125/us-textile-fiber-trade.csv"
M_RFE_IMPORTS_BY_FIBER = "/media/5485/table-1-us-textile-imports-by-fiber.csv"
M_RFE_EXPORTS_BY_FIBER = "/media/5487/table-2-us-textile-exports-by-fiber.csv"
M_RFE_IMPORTS_BY_ORIGIN = (
    "/media/5489/table-3-us-cotton-textile-and-apparel-imports-by-origin.csv"
)
M_RFE_EXPORTS_BY_DESTINATION = (
    "/media/5491/table-4-us-cotton-textile-and-apparel-exports-by-destination.csv"
)

ROW_DIM_FIELDS = (
    "geography",
    "measure",
    "trade_category",
    "textile_group",
    "item",
)

COLUMN_DIM_FIELDS = ("measure", "trade_category", "textile_group", "item")

MONTH_NAMES = {
    "1": "Jan",
    "2": "Feb",
    "3": "Mar",
    "4": "Apr",
    "5": "May",
    "6": "Jun",
    "7": "Jul",
    "8": "Aug",
    "9": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}

MONTH_ORDER = {name: index for index, name in enumerate(MONTH_NAMES.values(), start=1)}

FREQUENCY_RANK = {"Annual": 0, "Quarterly": 1, "Monthly": 2}

TABLE_NUMBER_COLS = ("table_number", "table_num")


def classify_frequency(period) -> str:
    """Classify a within-year period token into a reporting frequency.

    Parameters
    ----------
    period : object
        The record's period token: None, 'annual', 'Season', a month number
        '1'..'12', or a quarter label 'Q1'..'Q4'.

    Returns
    -------
    str
        'Monthly', 'Quarterly', or 'Annual'.
    """
    if period is None:
        return "Annual"
    token = str(period).strip()
    if token in MONTH_NAMES:
        return "Monthly"
    if token.upper() in ("Q1", "Q2", "Q3", "Q4"):
        return "Quarterly"
    return "Annual"


async def table_frequencies(table: str, **kwargs) -> list[str]:
    """List the reporting frequencies a table publishes, coarsest first.

    Parameters
    ----------
    table : str
        Table key from CWT_TABLES.

    Returns
    -------
    list[str]
        Distinct frequencies present in the table, ordered Annual, Quarterly,
        Monthly.
    """
    records = await afetch_table(table)
    found = {classify_frequency(record["period"]) for record in records}
    return sorted(found, key=lambda freq: FREQUENCY_RANK.get(freq, 9))


_DEFAULTS = {
    "product": YEARBOOK_PRODUCT,
    "year_col": "period",
    "period_col": None,
    "series_col": "category",
    "unit_col": "units",
    "dims": (),
    "normalize_measure": False,
    "pivot": "series",
}


def _cfg(label: str, media: str, number: str, **overrides) -> dict:
    """Build one table configuration, filling the shared defaults."""
    return {"label": label, "media": media, "number": number, **_DEFAULTS, **overrides}


CWT_TABLES: dict[str, dict] = {
    "cotton_supply_and_use": _cfg("U.S. cotton - 1. Supply and use", M_US_COTTON, "1"),
    "upland_cotton_supply_and_use": _cfg(
        "U.S. cotton - 2. Upland supply and use", M_US_COTTON, "2"
    ),
    "els_cotton_supply_and_use": _cfg(
        "U.S. cotton - 3. Extra Long Staple supply and use", M_US_COTTON, "3"
    ),
    "upland_planted_acreage_by_state": _cfg(
        "U.S. cotton - 4. Upland planted acreage by State",
        M_US_COTTON,
        "4",
        series_col="geography",
    ),
    "upland_harvested_acreage_by_state": _cfg(
        "U.S. cotton - 5. Upland harvested acreage by State",
        M_US_COTTON,
        "5",
        series_col="geography",
    ),
    "upland_lint_yield_by_state": _cfg(
        "U.S. cotton - 6. Upland lint yield by State",
        M_US_COTTON,
        "6",
        series_col="geography",
    ),
    "upland_production_by_state": _cfg(
        "U.S. cotton - 7. Upland production by State",
        M_US_COTTON,
        "7",
        series_col="geography",
    ),
    "els_acreage_by_state": _cfg(
        "U.S. cotton - 8. Extra Long Staple acreage by State",
        M_US_COTTON,
        "8",
        series_col="geography",
        dims=(("measure", "category"),),
        normalize_measure=True,
    ),
    "els_production_and_yield_by_state": _cfg(
        "U.S. cotton - 9. Extra Long Staple production and yield by State",
        M_US_COTTON,
        "9",
        series_col="geography",
        dims=(("measure", "category"),),
        normalize_measure=True,
    ),
    "cotton_supply_and_disappearance_monthly": _cfg(
        "U.S. cotton - 10. Supply and disappearance, by month",
        M_US_COTTON,
        "10",
        period_col="month",
    ),
    "upland_farm_spot_mill_prices": _cfg(
        "Prices - 11. Upland farm, spot, and mill prices", M_PRICES, "11"
    ),
    "fiber_prices": _cfg("Prices - 12. Fiber prices", M_PRICES, "12"),
    "cotton_price_quotes_monthly": _cfg(
        "Prices - 13. Cotton price quotations, monthly",
        M_PRICES,
        "13",
        period_col="time_period",
    ),
    "cotton_price_quotes_annual": _cfg(
        "Prices - 14. Cotton price quotations, annual", M_PRICES, "14"
    ),
    "world_cotton_supply_and_use": _cfg(
        "World - 15. World cotton supply and use", M_WORLD, "15"
    ),
    "foreign_cotton_supply_and_use": _cfg(
        "World - 16. Foreign cotton supply and use", M_WORLD, "16"
    ),
    "cotton_exports_major_exporters": _cfg(
        "World - 17. Exports, major foreign exporters",
        M_WORLD,
        "17",
        series_col="geography",
    ),
    "cotton_imports_major_importers": _cfg(
        "World - 18. Imports, major importers",
        M_WORLD,
        "18",
        series_col="geography",
    ),
    "former_soviet_union_cotton_supply_and_use": _cfg(
        "World - 19. Former Soviet Union supply and use", M_WORLD, "19"
    ),
    "brazil_cotton_supply_and_use": _cfg(
        "World - 20. Brazil supply and use", M_WORLD, "20"
    ),
    "turkey_cotton_supply_and_use": _cfg(
        "World - 21. Turkey supply and use", M_WORLD, "21"
    ),
    "china_cotton_supply_and_use": _cfg(
        "World - 22. China supply and use", M_WORLD, "22"
    ),
    "india_cotton_supply_and_use": _cfg(
        "World - 23. India supply and use", M_WORLD, "23"
    ),
    "pakistan_cotton_supply_and_use": _cfg(
        "World - 24. Pakistan supply and use", M_WORLD, "24"
    ),
    "cotton_fiber_demand_total_and_per_capita": _cfg(
        "U.S. fiber demand - 25. Cotton fiber demand, total and per capita",
        M_FIBER_DEMAND,
        "25",
    ),
    "per_capita_cotton_demand": _cfg(
        "U.S. fiber demand - 26. Per capita domestic cotton demand",
        M_FIBER_DEMAND,
        "26",
    ),
    "cotton_and_synthetic_mill_use": _cfg(
        "U.S. fiber demand - 27. Cotton and synthetic staple mill use",
        M_FIBER_DEMAND,
        "27",
    ),
    "wool_supply_and_use": _cfg("Wool - 28. Supply and use", M_WOOL, "28"),
    "raw_wool_imports_for_mill_use": _cfg(
        "Wool - 29. Raw wool imports for mill use", M_WOOL, "29"
    ),
    "raw_wool_imports_by_origin": _cfg(
        "Wool - 30. Raw wool imports by country of origin",
        M_WOOL,
        "30",
        dims=(("geography", "geography"),),
    ),
    "raw_wool_exports_by_destination": _cfg(
        "Wool - 31. Raw wool exports by country of destination",
        M_WOOL,
        "31",
        dims=(("geography", "geography"),),
    ),
    "wool_tops_trade": _cfg(
        "Wool - 32. Trade in wool tops",
        M_WOOL,
        "32",
        dims=(("geography", "geography"),),
    ),
    "shorn_wool_prices": _cfg("Wool - 33. Shorn wool prices", M_WOOL, "33"),
    "mohair_exports_by_destination": _cfg(
        "Wool - 34. Mohair exports by country of destination",
        M_WOOL,
        "34",
        series_col="geography",
    ),
    "raw_fiber_equivalent_textile_manufactures": _cfg(
        "Textile trade - 35. Raw-fiber equivalent of manufactures",
        M_TEXTILE,
        "35",
        series_col="fiber",
        dims=(("trade_category", "trade_category"),),
    ),
    "raw_cotton_equivalent_imports": _cfg(
        "Textile trade - 36. Raw-cotton equivalent of imports",
        M_TEXTILE,
        "36",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_cotton_equivalent_exports": _cfg(
        "Textile trade - 37. Raw-cotton equivalent of exports",
        M_TEXTILE,
        "37",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_linen_equivalent_imports": _cfg(
        "Textile trade - 38. Raw-linen equivalent of imports",
        M_TEXTILE,
        "38",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_linen_equivalent_exports": _cfg(
        "Textile trade - 39. Raw-linen equivalent of exports",
        M_TEXTILE,
        "39",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_wool_equivalent_imports": _cfg(
        "Textile trade - 40. Raw-wool equivalent of imports",
        M_TEXTILE,
        "40",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_wool_equivalent_exports": _cfg(
        "Textile trade - 41. Raw-wool equivalent of exports",
        M_TEXTILE,
        "41",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_silk_equivalent_imports": _cfg(
        "Textile trade - 42. Raw-silk equivalent of imports",
        M_TEXTILE,
        "42",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_silk_equivalent_exports": _cfg(
        "Textile trade - 43. Raw-silk equivalent of exports",
        M_TEXTILE,
        "43",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_synthetic_equivalent_imports": _cfg(
        "Textile trade - 44. Raw-synthetic equivalent of imports",
        M_TEXTILE,
        "44",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "raw_synthetic_equivalent_exports": _cfg(
        "Textile trade - 45. Raw-synthetic equivalent of exports",
        M_TEXTILE,
        "45",
        series_col="textile_category",
        period_col="month",
        dims=(("textile_group", "textile_group"),),
    ),
    "rfe_textile_imports_by_fiber": _cfg(
        "Raw-fiber equivalent - T1. Textile imports, by fiber",
        M_RFE_IMPORTS_BY_FIBER,
        "1",
        product=RFE_PRODUCT,
        series_col="fiber",
        unit_col="unit",
        dims=(("item", "Item"),),
    ),
    "rfe_textile_exports_by_fiber": _cfg(
        "Raw-fiber equivalent - T2. Textile exports, by fiber",
        M_RFE_EXPORTS_BY_FIBER,
        "2",
        product=RFE_PRODUCT,
        year_col="year",
        series_col="fiber",
        unit_col="unit",
        dims=(("item", "Item"),),
    ),
    "rfe_cotton_textile_imports_by_origin": _cfg(
        "Raw-fiber equivalent - T3. Cotton textile imports, by origin",
        M_RFE_IMPORTS_BY_ORIGIN,
        "3",
        product=RFE_PRODUCT,
        year_col="year",
        series_col=None,
        unit_col="unit",
        dims=(("geography", "Region/country"),),
        pivot="years",
    ),
    "rfe_cotton_textile_exports_by_destination": _cfg(
        "Raw-fiber equivalent - T4. Cotton textile exports, by destination",
        M_RFE_EXPORTS_BY_DESTINATION,
        "4",
        product=RFE_PRODUCT,
        year_col="year",
        series_col=None,
        unit_col="unit",
        dims=(("geography", "Region/country"),),
        pivot="years",
    ),
}


def _table_number(row: dict) -> str:
    """Return the row's table-number cell across the two source column names."""
    for col in TABLE_NUMBER_COLS:
        value = row.get(col)
        if value is not None:
            return value.strip()
    return ""


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's rows from its source CSV into long-format records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the source file, which may hold several tables.
    table : str
        Table key from CWT_TABLES.

    Returns
    -------
    list[dict]
        Records carrying the table key, integer year, within-year period, the
        five row-dimension fields, the unit, the series name, and the numeric
        value. Rows for other tables, or whose value is blank or non-numeric,
        are skipped.
    """
    config = CWT_TABLES[table]
    number = config["number"]
    series_col = config["series_col"]
    period_col = config["period_col"]
    year_col = config["year_col"]
    unit_col = config["unit_col"]
    normalize = config["normalize_measure"]
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        if _table_number(row) != number:
            continue
        raw_value = (row.get("value") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_label = (row.get(year_col) or "").strip()
        if not year_label[:4].isdigit():
            continue
        record: dict = {
            "table": table,
            "year": int(year_label[:4]),
            "period": (
                ((row.get(period_col) or "").strip() or None) if period_col else None
            ),
            "geography": None,
            "measure": None,
            "trade_category": None,
            "textile_group": None,
            "item": None,
            "unit": (row.get(unit_col) or "").strip() or None,
            "series": (row.get(series_col) or "").strip() if series_col else None,
            "value": value,
        }
        for out_field, source_col in config["dims"]:
            raw = (row.get(source_col) or "").strip()
            if out_field == "measure" and normalize:
                raw = raw.casefold()
            record[out_field] = raw or None
        records.append(record)
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one cotton-wool-textile table through the ERS cache.

    Parameters
    ----------
    table : str
        Table key from CWT_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = CWT_TABLES[table]
    content = await afetch_ers_file(config["media"], product=config["product"])
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
