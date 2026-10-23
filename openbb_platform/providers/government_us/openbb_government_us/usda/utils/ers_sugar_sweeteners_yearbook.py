"""USDA ERS Sugar and Sweeteners Yearbook file catalog and long-format parser."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/sugar-and-sweeteners-yearbook-tables"

DIMENSION_FIELDS: tuple[tuple[str, str], ...] = (
    ("Commodity_desc", "commodity_desc"),
    ("Commodity_desc2", "commodity_desc2"),
    ("Geographic_extent", "geographic_extent"),
    ("Geographic_extent2", "geographic_extent2"),
    ("Source_or_destination", "source_or_destination"),
    ("Fiscal_year_entered", "fiscal_year_entered"),
    ("Fiscal_year_quota", "fiscal_year_quota"),
    ("Forecast_yearmonth", "forecast_yearmonth"),
)

DIMENSION_OUTPUT_FIELDS: tuple[str, ...] = tuple(out for _, out in DIMENSION_FIELDS)

SUGAR_SWEETENERS_FILES: dict[str, dict] = {
    "table_2": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "2",
        "label": "Table 2: World white (refined) sugar nearby futures price, ICE Contract Number 5, monthly, quarterly, and by calendar and fiscal year, since 1980, cents per pound",
    },
    "table_3a": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "3a",
        "label": "Table 3a: World raw sugar price, monthly, quarterly, and by calendar and fiscal year, 1960 to 2011, cents per pound, discontinued as of July 1, 2011",
    },
    "table_3b": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "3b",
        "label": "Table 3b: World raw sugar nearby futures price, ICE Contract Number 11, monthly, quarterly, and by calendar and fiscal year, since 1989, cents per pound",
    },
    "table_4": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "4",
        "label": "Table 4: U.S. raw sugar nearby futures price, ICE Contract Number 16, monthly, quarterly, and by calendar and fiscal year, since 1960, cents per pound",
    },
    "table_5": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "5",
        "label": "Table 5: U.S. spot price for bulk refined beet sugar, Midwest markets, monthly, quarterly, and by calendar and fiscal year, since 1960, cents per pound",
    },
    "table_5a": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "5a",
        "label": "Table 5a: U.S. calendar price for bulk refined cane sugar, Northeast markets, monthly, quarterly, and by calendar and fiscal year, since 1999, cents per pound",
    },
    "table_6": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "6",
        "label": "Table 6: U.S. retail refined sugar price, monthly, quarterly, and by calendar and fiscal year, since 1960, cents per pound",
    },
    "table_7": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "7",
        "label": "Table 7: U.S. spot price for bulk glucose syrup, Midwest markets, monthly, quarterly, and by calendar and fiscal year, since 1975, cents per pound (dry weight)",
    },
    "table_8": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "8",
        "label": "Table 8: U.S. spot price for bulk dextrose, Midwest markets, monthly, quarterly, and by calendar and fiscal year, since 1975, cents per pound (dry weight)",
    },
    "table_9": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "9",
        "label": "Table 9: U.S. price for bulk high-fructose corn syrup, Midwest markets, monthly, quarterly, and by calendar and fiscal year, since 1994, cents per pound (dry weight)",
    },
    "table_10": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "10",
        "label": "Table 10: U.S. producer price index for corn sweeteners and sugar, monthly, not seasonally adjusted, since 1967",
    },
    "table_11": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "11",
        "label": "Table 11: U.S. consumer price index for sugar and selected sweetener-containing products, monthly and by calendar year, in U.S. city average, all urban consumers, not seasonally adjusted, since 1978",
    },
    "table_12": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "12",
        "label": "Table 12: Sugarbeet price per ton, by State and United States, since 1972/73, dollars per ton",
    },
    "table_13": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "13",
        "label": "Table 13: Sugarcane for sugar: price per ton, by State, since 1972/73, dollars per ton",
    },
    "table_31a": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "31a",
        "label": "Table 31a: Net cost of corn starch to U.S. wet-millers, Midwest markets, quarterly, since 1990",
    },
    "table_31b": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "31b",
        "label": "Table 31b: Net cost of corn starch to U.S. wet-millers, Midwest markets, by calendar and fiscal year, since 1990",
    },
    "table_54": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "54",
        "label": "Table 54: Mexico's price of estándar (standard) sugar, wholesale center, Mexico City, monthly and by calendar and fiscal year, since 1994",
    },
    "table_55": {
        "media": "/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv",
        "number": "55",
        "label": "Table 55: Mexico's price of refinada (refined) sugar, wholesale center, Mexico City, monthly and by calendar and fiscal year, since 1994",
    },
    "table_14": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "14",
        "label": "Table 14: U.S. sugarbeet: area planted (1,000 acres), area harvested (1,000 acres), yield per acre (short tons per acre), and production (1,000 short tons), by State and region, by crop year, since 1980/81",
    },
    "table_15": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "15",
        "label": "Table 15: U.S. sugarcane: area, yield, production, sugar output, recovery rate, and sugar yield per acre, by crop year and fiscal year (Louisiana only)",
    },
    "table_16": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "16",
        "label": "Table 16: U.S. beet and cane sugar production (including Puerto Rico), by fiscal year and share of total, since 1969/70",
    },
    "table_17": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "17",
        "label": "Table 17: U.S. sugarbeet area, yield, and production, by crop year and fiscal year, since 1980/81",
    },
    "table_18": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "18",
        "label": "Table 18: U.S. production of beet sugar and cane sugar by State, monthly, quarterly, and by calendar year and fiscal year, since 1992 (1,000 short tons, raw value)",
    },
    "table_19": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "19",
        "label": "Table 19: U.S. cane and beet sugar deliveries and exports, monthly, quarterly, and by calendar year and fiscal year, since 1992 (1,000 short tons, raw value)",
    },
    "table_20a": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "20a",
        "label": "Table 20a: U.S. sugar deliveries for human consumption by type of user, by calendar year, since 1949 (1,000 short tons, refined value)",
    },
    "table_20b": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "20b",
        "label": "Table 20b: U.S. sugar deliveries for human consumption by type of user, monthly and quarterly, since 2001 (1,000 short tons, refined value)",
    },
    "table_21": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "21",
        "label": "Table 21: U.S. sugar deliveries: industrial and nonindustrial uses by region, monthly, quarterly, and by calendar year (1,000 short tons, refined value)",
    },
    "table_22": {
        "media": "/media/7096/us-sugar-crop-production-and-sugar-production-deliveries-and-stocks.csv",
        "number": "22",
        "label": "Table 22: U.S. sugar stocks held by primary distributors, quarterly (1,000 short tons, raw value)",
    },
    "table_46": {
        "media": "/media/5151/us-honey-production-and-trade.csv",
        "number": "46",
        "label": "Table 46: U.S. honey production, imports, exports, stocks, and average price, by calendar year, since 1986",
    },
    "table_47": {
        "media": "/media/5151/us-honey-production-and-trade.csv",
        "number": "47",
        "label": "Table 47: Honey: number of colonies, yield, production, stocks, price, and value by top producing States and United States, by calendar year, since 1986",
    },
    "table_48a": {
        "media": "/media/5151/us-honey-production-and-trade.csv",
        "number": "48a",
        "label": "Table 48a: U.S. honey imports, by country of source, calendar year, since 1989, metric tons",
    },
    "table_48b": {
        "media": "/media/5151/us-honey-production-and-trade.csv",
        "number": "48b",
        "label": "Table 48b: U.S. honey imports, by country of source, calendar year, since 1989, million pounds",
    },
    "table_49": {
        "media": "/media/7144/us-consumption-of-caloric-sweeteners.csv",
        "number": "49",
        "label": "Table 49: U.S. total estimated deliveries of caloric sweeteners for domestic food and beverage use (1,000 short tons, dry basis), by calendar year, since 1966",
    },
    "table_50": {
        "media": "/media/7144/us-consumption-of-caloric-sweeteners.csv",
        "number": "50",
        "label": "Table 50: U.S. per capita caloric sweeteners estimated deliveries for domestic food and beverage use (pounds, dry basis), by calendar year, since 1966",
    },
    "table_51": {
        "media": "/media/7144/us-consumption-of-caloric-sweeteners.csv",
        "number": "51",
        "label": "Table 51: Refined cane and beet sugar: estimated number of per capita calories consumed daily, by calendar year, since 1970",
    },
    "table_52": {
        "media": "/media/7144/us-consumption-of-caloric-sweeteners.csv",
        "number": "52",
        "label": "Table 52: High-fructose corn syrup: estimated number of per capita calories consumed daily, by calendar year, since 1970",
    },
    "table_53": {
        "media": "/media/7144/us-consumption-of-caloric-sweeteners.csv",
        "number": "53",
        "label": "Table 53: Other sweeteners: estimated number of per capita calories consumed daily, by calendar year, since 1970",
    },
    "table_24a": {
        "media": "/media/7097/the-machine-readable-file-combines-the-data-from-the-3-excel-tables-us-and-mexico-fiscal-year-sugar-supply-and-use-table-25-us-monthly-estimates-of-sugar-supply-and-use-and-table-26-monthly-estimates-of-mexican-sugar-supply-and-use.csv",
        "number": "24a",
        "label": "Table 24a: U.S. sugar: supply and use (including Puerto Rico), by fiscal year, 1,000 short tons, raw value, since 2000/01",
    },
    "table_24b": {
        "media": "/media/7097/the-machine-readable-file-combines-the-data-from-the-3-excel-tables-us-and-mexico-fiscal-year-sugar-supply-and-use-table-25-us-monthly-estimates-of-sugar-supply-and-use-and-table-26-monthly-estimates-of-mexican-sugar-supply-and-use.csv",
        "number": "24b",
        "label": "Table 24b: U.S. sugar: supply and use (including Puerto Rico), by fiscal year, 1,000 metric tons, raw value, since 2000/01",
    },
    "table_25": {
        "media": "/media/7097/the-machine-readable-file-combines-the-data-from-the-3-excel-tables-us-and-mexico-fiscal-year-sugar-supply-and-use-table-25-us-monthly-estimates-of-sugar-supply-and-use-and-table-26-monthly-estimates-of-mexican-sugar-supply-and-use.csv",
        "number": "25",
        "label": "Table 25: Monthly estimates of U.S. sugar supply and use (1,000 short tons, raw value)",
    },
    "table_26": {
        "media": "/media/7097/the-machine-readable-file-combines-the-data-from-the-3-excel-tables-us-and-mexico-fiscal-year-sugar-supply-and-use-table-25-us-monthly-estimates-of-sugar-supply-and-use-and-table-26-monthly-estimates-of-mexican-sugar-supply-and-use.csv",
        "number": "26",
        "label": "Table 26: Monthly estimates of Mexican sugar supply and use (1,000 metric tons, actual weight)",
    },
    "table_56a": {
        "media": "/media/7097/the-machine-readable-file-combines-the-data-from-the-3-excel-tables-us-and-mexico-fiscal-year-sugar-supply-and-use-table-25-us-monthly-estimates-of-sugar-supply-and-use-and-table-26-monthly-estimates-of-mexican-sugar-supply-and-use.csv",
        "number": "56a",
        "label": "Table 56a: Mexico: sugar production and supply, and sugar and high-fructose corn syrup utilization, by fiscal year, 1,000 metric tons, tel quel, since 1995/96",
    },
    "table_56b": {
        "media": "/media/7097/the-machine-readable-file-combines-the-data-from-the-3-excel-tables-us-and-mexico-fiscal-year-sugar-supply-and-use-table-25-us-monthly-estimates-of-sugar-supply-and-use-and-table-26-monthly-estimates-of-mexican-sugar-supply-and-use.csv",
        "number": "56b",
        "label": "Table 56b: Mexico: sugar production and supply, and sugar and high-fructose corn syrup utilization, by fiscal year, 1,000 metric tons, raw value, since 1995/96",
    },
    "table_27": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "27",
        "label": "Table 27: U.S. use of field corn, by marketing year, since 1990/91 (million bushels)",
    },
    "table_28": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "28",
        "label": "Table 28: U.S. high-fructose corn syrup (HFCS) deliveries, quarterly, by fiscal and calendar year, since 1992 (1,000 short tons, dry weight)",
    },
    "table_29": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "29",
        "label": "Table 29: U.S. high-fructose corn syrup (HFCS) production, quarterly, by fiscal and calendar year, since 1992 (1,000 short tons, dry weight)",
    },
    "table_30": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "30",
        "label": "Table 30: U.S. high-fructose corn syrup supply and use, by calendar and fiscal year, since 1992 (1,000 short tons, dry weight)",
    },
    "table_34a": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "34a",
        "label": "Table 34a: U.S. exports of high-fructose corn syrup to Mexico, since 1995 (metric tons, dry weight basis)",
    },
    "table_34b": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "34b",
        "label": "Table 34b: U.S. exports of high-fructose corn syrup to all countries, since 1995 (metric tons, dry weight basis)",
    },
    "table_35a": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "35a",
        "label": "Table 35a: Mexican imports of high-fructose corn syrup from the United States, since 1995 (metric tons, dry weight basis)",
    },
    "table_35b": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "35b",
        "label": "Table 35b: Mexican imports of high-fructose corn syrup from all countries, since 1995 (metric tons, dry weight basis)",
    },
    "table_36": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "36",
        "label": "Table 36: U.S. corn refinery exports, by calendar year, since 1980 (metric tons)",
    },
    "table_37": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "37",
        "label": "Table 37: U.S. dextrose supply and use, by calendar year, since 1964 (1,000 short tons, dry weight)",
    },
    "table_38": {
        "media": "/media/7095/the-machine-readable-file-combines-the-data-from-the-2-excel-tables-us-corn-sweetener-supply-and-use-and-corn-sweetener-trade.csv",
        "number": "38",
        "label": "Table 38: U.S. glucose supply and use, by calendar year, since 1964 (1,000 short tons, dry weight)",
    },
    "table_57": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "57",
        "label": "Table 57: U.S. raw sugar tariff-rate quota World Trade Organization allocations, entries, and shortfalls, by fiscal year quota, since 1996 (metric tons, raw value)",
    },
    "table_58a": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "58a",
        "label": "Table 58a: U.S. refined sugar tariff-rate quota World Trade Organization allocations and entries by month, since fiscal year quota 2008 (metric tons, raw value)",
    },
    "table_58b": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "58b",
        "label": "Table 58b: U.S. refined sugar tariff-rate quota World Trade Organization allocations and entries, fiscal year 2007 (metric tons, raw value)",
    },
    "table_58c": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "58c",
        "label": "Table 58c: U.S. refined sugar tariff-rate quota World Trade Organization allocations and entries, fiscal year 2006 (metric tons, raw value)",
    },
    "table_59a": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "59a",
        "label": "Table 59a: U.S. sugar tariff-rate quota allocations and entries by month under free trade agreements, since fiscal year 2008 (metric tons, raw value)",
    },
    "table_59b": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "59b",
        "label": "Table 59b: U.S. sugar tariff-rate quota annual allocations and entries under free trade agreements, fiscal years 2006 and 2007 (metric tons, raw value)",
    },
    "table_60a": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "60a",
        "label": "Table 60a: U.S. imports of sugar from Mexico, monthly, since fiscal year 2011, metric tons, commercial weight",
    },
    "table_60b": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "60b",
        "label": "Table 60b: U.S. imports of sugar from Mexico, monthly, since fiscal year 2011, metric tons, raw value",
    },
    "table_60c": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "60c",
        "label": "Table 60c: U.S. imports of sugar from Mexico, monthly, fiscal years 2008 to 2010, metric tons, raw value",
    },
    "table_60d": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "60d",
        "label": "Table 60d: U.S. imports of sugar from Mexico by port, monthly, since fiscal year 2011, metric tons, commercial weight",
    },
    "table_60e": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "60e",
        "label": "Table 60e: U.S. imports of sugar from Mexico by port, fiscal year, since fiscal year 2011, metric tons, commercial weight",
    },
    "table_61a": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "61a",
        "label": "Table 61a: U.S. monthly sugar imports by source, since fiscal year 2008 (metric tons, raw value)",
    },
    "table_61b": {
        "media": "/media/7098/the-machine-readable-file-combines-the-data-from-the-5-excel-tables-table-57-to-table-61.csv",
        "number": "61b",
        "label": "Table 61b: U.S. monthly sugar imports by source, since fiscal year 2008 (short tons, raw value)",
    },
}


FOLD_DIM_FIELDS: tuple[str, ...] = (
    "commodity_desc",
    "commodity_desc2",
    "geographic_extent",
    "geographic_extent2",
    "source_or_destination",
    "fiscal_year_entered",
    "fiscal_year_quota",
)


def frequency_rank(period_cat: str | None) -> int:
    """Rank a period category from annual (0) to quarterly (1) to monthly (2)."""
    label = (period_cat or "").casefold()
    if "quarter" in label:
        return 1
    if "month" in label:
        return 2
    return 0


def within_year_label(period_cat: str | None, period_desc: str | None) -> str:
    """Return the within-year period label for a sub-annual row, else empty.

    Parameters
    ----------
    period_cat : str | None
        Published Period_cat value, e.g. 'Month' or 'Calendar year quarter'.
    period_desc : str | None
        Published Period_desc value, e.g. 'Jan', 'Q1 (Jan-Mar)', or 'Dec_31'.

    Returns
    -------
    str
        The month name, quarter code, or month-day label for sub-annual rows,
        or an empty string for annual rows.
    """
    if frequency_rank(period_cat) == 0:
        return ""
    desc = period_desc or ""
    if "quarter" in (period_cat or "").casefold():
        return desc.split(" ")[0]
    return desc


async def table_frequencies(table: str, **kwargs) -> list[str]:
    """List the period categories a table publishes, annual bases first.

    Parameters
    ----------
    table : str
        Table key from SUGAR_SWEETENERS_FILES.

    Returns
    -------
    list[str]
        Distinct Period_cat values present in the table, ordered from annual
        bases through quarters to months.
    """
    records = await afetch_table(table)
    cats = {record["period_cat"] for record in records if record["period_cat"]}
    return sorted(cats, key=lambda cat: (frequency_rank(cat), cat))


def period_sort_rank(period_cat: str | None) -> int:
    """Return the intra-year granularity rank of a period category.

    Parameters
    ----------
    period_cat : str | None
        Published Period_cat value, e.g. 'Month', 'Calendar year quarter',
        or 'Fiscal year'.

    Returns
    -------
    int
        0 for annual categories, 1 for quarters, 2 for months, ordering the
        rows within a year from the annual summary down to the finest period.
    """
    label = (period_cat or "").casefold()
    if "quarter" in label:
        return 1
    if "month" in label:
        return 2
    return 0


def period_sort_num(period: str | None) -> int:
    """Return the numeric ordinal of a period token, 0 when non-numeric.

    Parameters
    ----------
    period : str | None
        Published Period value, e.g. '1' for January, '4' for a quarter, or
        a four-digit year for an annual row.

    Returns
    -------
    int
        The integer value of the token, or 0 when it is not an integer.
    """
    try:
        return int(period or "")
    except ValueError:
        return 0


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's rows from a combined CSV into long-format records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the file that carries the table.
    table : str
        Table key from SUGAR_SWEETENERS_FILES.

    Returns
    -------
    list[dict]
        One record per observation of the selected table, carrying the
        integer year, the year and period labels, the eight dimension
        fields, the attribute name, the unit, and the numeric value. Rows
        for other tables, blank or non-numeric values, and non-numeric year
        labels are skipped.
    """
    number = SUGAR_SWEETENERS_FILES[table]["number"]
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        if (row.get("Table_number") or "").strip() != number:
            continue
        raw_value = (row.get("Value") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_label = (row.get("Year") or "").strip()
        if not year_label[:4].isdigit():
            continue
        record: dict = {
            "table": table,
            "number": number,
            "year": int(year_label[:4]),
            "year_cat": (row.get("Year_cat") or "").strip() or None,
            "year_desc": (row.get("Year_desc") or "").strip() or None,
            "period": (row.get("Period") or "").strip() or None,
            "period_cat": (row.get("Period_cat") or "").strip() or None,
            "period_desc": (row.get("Period_desc") or "").strip() or None,
            "attribute": (row.get("Attribute_desc") or "").strip(),
            "unit": (row.get("Unit") or "").strip(),
            "value": value,
        }
        for source_col, output_field in DIMENSION_FIELDS:
            record[output_field] = (row.get(source_col) or "").strip() or None
        records.append(record)
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one yearbook table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from SUGAR_SWEETENERS_FILES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = SUGAR_SWEETENERS_FILES[table]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
