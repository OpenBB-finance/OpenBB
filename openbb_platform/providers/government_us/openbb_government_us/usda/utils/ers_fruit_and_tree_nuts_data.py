"""USDA ERS Fruit and Tree Nuts Yearbook file catalog and long-format parser."""

import csv
import re
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = (
    "data-products/fruit-and-tree-nuts-data/fruit-and-tree-nuts-yearbook-tables"
)
YEARBOOK_MEDIA = "/media/7009/all-fruit-and-tree-nuts-yearbook-data.csv"

CODE_PATTERN = re.compile(r"^Table\s+([A-H])\s*-\s*(\d+)")

MONTH_NUMBERS: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

CATEGORY_LABELS: dict[str, str] = {
    "A": "U.S. summary and per-capita availability",
    "B": "Noncitrus fruit",
    "C": "Citrus",
    "D": "Berries",
    "E": "Melons",
    "F": "Tree nuts",
    "G": "Supply and per-capita availability",
    "H": "Import share",
}

TABLE_TITLES: dict[str, str] = {
    "A-1": "Fruit and tree nuts: Per capita availability, United States, 1976 to date",
    "A-2": "Fruit and tree nuts: Area bearing, United States, 1980 to date",
    "A-3": "Fruit and tree nuts: Utilized production and value of production, United States, 1980 to date",
    "A-4": "Selected citrus and noncitrus fruit: Area bearing, United States, 1980 to date",
    "A-5": "Selected citrus and noncitrus fruit: Production, United States, 1980 to date",
    "A-6": "Fruit and tree nuts: Price indexes for fruit and nuts, United States, 1980 to date",
    "A-7": "Selected citrus and noncitrus fruit, fresh: Retail price, average annual, United States, 1980 to date",
    "A-8": "Apples, fresh: U.S. monthly average retail price, marketing spread, and grower price, 1989 to date",
    "A-9": "Peaches, fresh: U.S. monthly average retail price, marketing spread, and grower price, 1989 to date",
    "A-10": "Pears, fresh: U.S. monthly average retail price, marketing spread, and grower price, 1989 to date",
    "A-11": "Grapes, fresh: U.S. monthly average retail price, marketing spread, and grower price, 1995 to date",
    "A-12": "Strawberries, fresh: U.S. monthly average retail price, marketing spread, and grower price, 1990 to date",
    "A-13": "Oranges, fresh: U.S. monthly average retail price, marketing spread, and grower price, 1989/90 to date",
    "A-14": "Grapefruit, fresh: U.S. monthly average retail price, marketing spread, and grower price, 1989/90 to date",
    "A-15": "Lemons, fresh: U.S. monthly retail price, marketing spread, and grower price, 1989/90 to date",
    "B-1": "Noncitrus fruit: Utilized production and value, United States, 1980 to date",
    "B-2": "Noncitrus fruit, dried: Utilized production (dry basis), California, 1980 to 2018",
    "B-3": "Apples: Production, utilization, and season-average grower price, United States, 1980 to date",
    "B-4": "Apples, fresh: Price received by growers, monthly, United States, 1980 to date",
    "B-5": "Apples: Processed utilization and season-average grower price, United States, 1980 to 2017",
    "B-6": "Apricots: Production, utilization, and season-average grower price, United States, 1980 to date",
    "B-7": "Avocados: Production, season-average grower price, and value, by State, 1980/81 to date",
    "B-8": "Bananas: Number of farms, area harvested, production, price, and value, Hawaii, 1980 to date",
    "B-9": "Sweet cherries: Production, utilization, and season-average grower price, United States, 1980 to date",
    "B-10": "Tart cherries: Production, utilization, and season-average grower price, United States, 1980 to date",
    "B-11": "Figs: Production, utilization, and season-average grower price, California, 1980 to 2018",
    "B-12": "Grapes: Production, utilization, and season-average grower price, United States, 1980 to date",
    "B-13": "Grapes: Utilized production and season-average grower price, California, 1980 to date",
    "B-14": "Grapes: Processed utilization and season-average grower price, United States, 1980 to 2017",
    "B-15": "Grapes, fresh: Price received by growers, monthly, United States, 1995 to date",
    "B-16": "Kiwifruit: Area bearing, production, season-average grower price, and value, California, 1980 to date",
    "B-17": "Nectarines: Production, utilization, and season-average grower price, California, 1980 to date",
    "B-18": "Nectarines: Production, utilization, and season-average grower price, Washington, 2005 to 2018",
    "B-19": "Olives: Area bearing, production, utilization, season-average grower price, and value, California, 1980 to date",
    "B-20": "Papayas: Area harvested, yield, production, utilization, and season-average grower price, Hawaii, 1980 to date",
    "B-21": "Peaches: Production, utilization, and season-average grower price, United States, 1980 to date",
    "B-22": "Peaches, fresh: Price received by growers, monthly, United States, 1980 to date",
    "B-23": "Peaches: Processed utilization, and season-average grower price, United States, 1980 to 2018",
    "B-24": "Pears: Production, utilization, and season-average grower price, United States, 1980 to date",
    "B-25": "Pears, Bartlett: Production, utilization, and season-average grower price, United States, 1980 to 2018",
    "B-26": "Pears, fresh: Price received by growers, monthly, United States, 1980 to date",
    "B-27": "Plums: Area bearing, production, season-average grower price, and value, California, 1980 to date",
    "B-28": "Prunes: Area bearing, production, season-average grower price, and value, California, 1980 to date",
    "B-29": "Plums and prunes: Production, utilization, and season-average grower price, four States, 1980 to 2016",
    "C-1": "Grapefruit: Area bearing and yield, by State, 1980/81 to date",
    "C-2": "Grapefruit: Production, by State, 1980/81 to date",
    "C-3": "Grapefruit: Utilized production, by State, 1980/81 to date",
    "C-4": "Grapefruit: Price received by growers - equivalent on-tree returns, by State, 1980/81 to date",
    "C-5": "Grapefruit: Price received by growers - equivalent on-tree returns, monthly, United States, 1980/81 to date",
    "C-6": "Grapefruit, processed: Utilized production, Florida, 1980/81 to date",
    "C-7": "Grapefruit, frozen concentrate: Processors stocks, pack, supplies, and movement, Florida, 1980/81 to date",
    "C-8": "Grapefruit, chilled juice: Processors stocks, pack, supplies, and movement, Florida, 1985/86 to date",
    "C-9": "Lemons: Area bearing, yield, and production, by State, 1980/81 to date",
    "C-10": "Lemons: Utilized production, by State, 1980/81 to date",
    "C-11": "Lemons: Price received by growers - equivalent on-tree returns, by State, 1980/81 to date",
    "C-12": "Lemons: Price received by growers - equivalent on-tree returns, monthly, United States, 1980/81 to date",
    "C-13": "Oranges: Area bearing and yield per acre, by State, 1980/81 to date",
    "C-14": "Oranges: Production, by State, 1980/81 to date",
    "C-15": "Oranges: Utilized production, by State, 1980/81 to date",
    "C-16": "Oranges: Price received by growers - equivalent on-tree returns, by State, 1980/81 to date",
    "C-17": "Oranges: Price received by growers - equivalent on-tree returns, monthly, United States, 1980/81 to date",
    "C-18": "Oranges, processed: Utilized production, Florida, 1980/81 to date",
    "C-19": "Oranges, frozen concentrate: Processors stocks, pack, supplies, and movement, Florida, 1980/81 to date",
    "C-20": "Oranges, chilled juice: Processors stocks, pack, supplies, and movement, Florida, 1985/86 to date",
    "D-1": "Blackberries: Area bearing, yield, production, and season-average grower price, Oregon, 1980 to 2017",
    "D-2": "Blueberries: Area harvested, yield, production, and season-average grower price, by State, various years to date",
    "D-3": "Boysenberries and loganberries: Area harvested, yield, production, and season-average grower price, California and Oregon, various years to 2018",
    "D-4": "Black raspberries: Area harvested, yield, production, and season-average grower price, Oregon, Washington, and California, 1980 to 2017",
    "D-5": "Red raspberries: Area harvested, yield, utilized production, and season-average grower price, Oregon, Washington, and California, 1980 to date",
    "D-6": "Raspberries: Area harvested, yield, utilized production, grower price, and value, California, 1992 to date",
    "D-7": "Cranberries: Area harvested, yield, production, utilization, season-average grower price, and value, United States, 1980 to date",
    "D-8": "Strawberries: Area harvested, production, season-average grower price, and value, United States, 1980 to date",
    "D-9": "Strawberries, fresh and processed: Production, season-average grower price, and value, United States, 1980 to date",
    "D-10": "Strawberries, fresh: Price received by growers, monthly, United States, 1980 to date",
    "E-1": "Melons: Per capita availability, 1970 to date",
    "E-2": "Melons: Area harvested and production, 1980 to date",
    "E-3": "Melons: Production, by country, 2001 to 2024",
    "E-4": "Melons: Area harvested, by country, 2001 to 2024",
    "E-5": "Melons: Production, selected States, 1990 to date",
    "E-6": "Cantaloupe, fresh: Price received by growers, 1995 to date",
    "E-7": "Melons: Supply and availability, farm weight, 1970 to date",
    "E-8": "Cantaloupe: Supply, availability, and price, farm weight, 1970 to date",
    "E-9": "Honeydew: Supply, availability, and price, farm weight, 1970 to date",
    "E-10": "Watermelon: Supply, availability, and season-average price received by growers, farm weight, 1970 to date",
    "F-1": "Tree nuts: Area bearing, United States, 1980/81 to date",
    "F-2": "Tree nuts: Gross returns, United States, 1980/81 to date",
    "F-3": "Tree nuts: Utilized production, shelled basis, United States, 1980/81 to date",
    "F-4": "Tree nuts: Price received by growers, season-average, United States, 1980/81 to date",
    "F-5": "Tree nuts: Value of production, United States, 1980/81 to date",
    "F-6": "Tree nuts: Supply and availability, shelled basis, United States, 1980/81 to date",
    "F-7": "Almonds: Area bearing, yield, production (shelled basis), season-average grower price, and value, California, 1980 to date",
    "F-8": "Almonds: Supply and availability (shelled basis), 1980/81 to date",
    "F-9": "Hazelnuts: Area bearing and yield (in-shell), by State, 1980 to date",
    "F-10": "Hazelnuts: Production (in-shell), season-average grower price, and value, by State, 1980 to date",
    "F-11": "Hazelnuts: Supply and availability (shelled basis), 1980/81 to date",
    "F-12": "Macadamias: Area bearing, yield, production (in-shell), season-average grower price, and value, Hawaii, 1980 to date",
    "F-13": "Pecans: Production (in-shell), season-average grower price, and value, United States, 1980 to date",
    "F-14": "Pecans: Supply and availability (shelled basis), 1980/81 to date",
    "F-15": "Pistachios: Production (in-shell), season-average grower price, and value, California, 1980 to date",
    "F-16": "Pistachios: Supply and availability (shelled basis), 1980/81 to date",
    "F-17": "Walnuts: Production (in-shell), season-average grower price, and value, California, 1980 to date",
    "F-18": "Walnuts: Supply and utilization (shelled basis), 1980/81 to date",
    "G-1": "Apples, fresh: Supply and availability, 1980/81 to date",
    "G-2": "Apricots, fresh: Supply and availability, 1980 to date",
    "G-3": "Avocados, fresh: Supply and availability, 1980/81 to date",
    "G-4": "Bananas, fresh: Supply and availability, 1980 to date",
    "G-5": "Blueberries, fresh: Supply and availability, 1980 to date",
    "G-6": "Grapes, fresh: Supply and availability, 1980/81 to date",
    "G-7": "Kiwifruit, fresh: Supply and availability, 1988/89 to date",
    "G-8": "Mangoes, fresh: Supply and availability, 1980 to date",
    "G-9": "Papayas, fresh: Supply and availability, 1980 to date",
    "G-10": "Peaches and nectarines, fresh: Supply and availability, 1980 to date",
    "G-11": "Pears, fresh: Supply and availability, 1980/81 to date",
    "G-12": "Pineapples, fresh: Supply and availability, 1980 to date",
    "G-13": "Raspberries, fresh: Supply and availability, 1992 to date",
    "G-14": "Strawberries, fresh: Supply and availability, 1980 to date",
    "G-15": "Grapefruit, fresh: Supply and availability, 1980/81 to date",
    "G-16": "Lemons, fresh: Supply and availability, 1980/81 to date",
    "G-17": "Limes, fresh: Supply and availability, 1980/81 to date",
    "G-18": "Oranges, fresh: Supply and availability, 1980/81 to date",
    "G-19": "Tangerines and tangelos, fresh: Supply and availability, 1980/81 to date",
    "G-20": "Apples, canned: Supply and availability, 1980/81 to date",
    "G-21": "Apricots, canned: Supply and availability, 1980/81 to date",
    "G-22": "Sweet cherries, canned: Supply and availability, 1980/81 to date",
    "G-23": "Tart cherries, canned: Supply and availability, 1980/81 to date",
    "G-24": "Olives, canned: Supply and availability, 1980/81 to date",
    "G-25": "Peaches, canned: Supply and availability, 1980/81 to date",
    "G-26": "Pears, canned: Supply and availability, 1980/81 to date",
    "G-27": "Pineapples, canned: Supply and availability, processed-weight basis, 1980 to date",
    "G-28": "Plums, canned: Supply and availability, 1980/81 to date",
    "G-29": "Apples, juice and cider: Supply and availability, 1980/81 to date",
    "G-30": "Grapes, juice: Supply and availability, 1980/81 to date",
    "G-31": "Grapefruit, juice: Supply and availability, 1980/81 to date",
    "G-32": "Oranges, juice: Supply and availability, 1985/86 to date",
    "G-33": "Pineapples, juice: Supply and availability, 1980 to date",
    "G-34": "Prunes, dried: Supply and availability, 1980/81 to date",
    "G-35": "Grapes, dried: Supply and availability, 1980/81 to date",
    "G-36": "All fruit, fresh: Per capita availability, 1980 to date",
    "G-37": "Noncitrus fruit, canned: Per capita availability, product-weight basis, 1980/81 to date",
    "G-38": "All fruit, frozen: Per capita availability, product-weight basis, 1980 to date",
    "G-39": "All fruit, dried: Per capita availability, product-weight basis, 1980/81 to date",
    "G-40": "Selected fruit, juices: Per capita availability, 1980/81 to date",
    "G-41": "Selected noncitrus fruit, processed and fresh: Per capita availability, fresh-weight equivalent, 1980/81 to date",
    "G-42": "Citrus fruit, processed and fresh: Per capita availability, fresh-weight equivalent, 1980/81 to date",
    "G-43": "Selected fruit, all: Per capita availability, fresh-weight equivalent, 1980 to date",
    "G-44": "Tree nuts (shelled basis), all: Per capita availability, 1980/81 to date",
    "G-45": "U.S. population",
    "H-1": "Import share, fresh fruit: Percent of domestic fresh fruit availability accounted for by imports, 1975 to date",
    "H-2": "Import share, canned fruit: Percent of domestic canned fruit availability accounted for by imports, 1975 to date",
    "H-3": "Import share, frozen fruit: Percent of domestic frozen fruit availability accounted for by imports, 1976 to date",
    "H-4": "Import share, fruit juice: Percent of domestic fruit juice availability accounted for by imports, 1972 to date",
    "H-5": "Import share, dried fruit: Percent of domestic dried fruit availability accounted for by imports, 1975/76 to date",
}


def table_category(table: str) -> str:
    """Return the letter category of a yearbook table code.

    Parameters
    ----------
    table : str
        Table code such as 'A-1' or 'G-45'.

    Returns
    -------
    str
        The leading letter, one of A through H.
    """
    return table.split("-", 1)[0]


def category_tables(category: str | None = None) -> list[str]:
    """List the table codes belonging to a category, in published order.

    Parameters
    ----------
    category : str | None
        Letter category A through H. When None, every table is returned.

    Returns
    -------
    list[str]
        Table codes, ordered by letter then number.
    """
    letter = (category or "").strip().upper() or None
    return [
        code
        for code in TABLE_TITLES
        if letter is None or table_category(code) == letter
    ]


def parse_records(text: str, table: str) -> list[dict]:
    """Parse the yearbook CSV text into one table's long-format records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the combined yearbook file.
    table : str
        Table code to extract, e.g. 'A-1'.

    Returns
    -------
    list[dict]
        Records carrying the table code, year label, integer year, year
        unit, month name, the four source dimensions, unit, and the numeric
        value. Rows for other tables, blank or non-numeric values, and
        unparseable year labels are skipped.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        match = CODE_PATTERN.match(row.get("table_name") or "")
        if match is None:
            continue
        code = f"{match.group(1)}-{match.group(2)}"
        if code != table:
            continue
        raw_value = (row.get("value") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_label = (row.get("year_value") or "").strip()
        if not year_label[:4].isdigit():
            continue
        month = (row.get("month") or "").strip()
        records.append(
            {
                "table": code,
                "year_label": year_label,
                "year": int(year_label[:4]),
                "year_unit": (row.get("year_unit") or "").strip(),
                "month": month if month.casefold() in MONTH_NUMBERS else None,
                "variable": (row.get("variable") or "").strip(),
                "commodity": (row.get("commodity_element") or "").strip(),
                "market_segment": (row.get("market_segment") or "").strip(),
                "geography": (row.get("geographic_extent") or "").strip(),
                "unit": (row.get("unit") or "").strip(),
                "value": value,
            }
        )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one yearbook table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table code from TABLE_TITLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_records.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(YEARBOOK_MEDIA, product=PRODUCT_PAGE)
    return parse_records(content.decode("utf-8-sig", errors="replace"), table)
