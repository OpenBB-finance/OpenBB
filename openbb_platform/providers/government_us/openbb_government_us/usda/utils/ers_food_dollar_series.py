"""USDA ERS Food Dollar Series file catalog and parser."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/food-dollar-series"

NULL_STRINGS = frozenset({"", "Not available"})

FOOD_DOLLAR_FILES: dict[str, dict] = {
    "nominal": {
        "media_id": 7055,
        "slug": "food-dollar-nominal-data-2011-model-1993-2023",
        "value_columns": [
            "Salary_and_benefits",
            "Property_income",
            "Output_taxes",
            "Imports",
            "Total",
        ],
        "units": {
            "share": "Cents per Domestic Food Dollar",
            "level": "million dollars",
        },
        "tables": list(range(1, 23)),
    },
    "real": {
        "media_id": 7057,
        "slug": "food-dollar-real-data-2011-model-1993-2023",
        "value_columns": ["Value_added", "Imports", "Total"],
        "units": {
            "share": "Cents per Domestic Real Food Dollar",
            "level": "million 2017 dollars",
        },
        "tables": list(range(1, 7)),
    },
}

TABLE_NAMES: dict[int, str] = {
    1: "Food dollar",
    2: "Food at home dollar",
    3: "Food away from home dollar",
    4: "Food and beverage dollar",
    5: "Home food and beverage dollar",
    6: "Away food and beverage dollar",
    7: "Food at home: Cereals",
    8: "Food at home: Bakery products",
    9: "Food at home: Beef, pork and other meats",
    10: "Food at home: Poultry",
    11: "Food at home: Fish and seafood",
    12: "Food at home: Fresh milk",
    13: "Food at home: Processed dairy products",
    14: "Food at home: Eggs",
    15: "Food at home: Fats and oils",
    16: "Food at home: Fresh Fruits",
    17: "Food at home: Fresh vegetables",
    18: "Food at home: Processed fruits and vegetables",
    19: "Food at home: Sugar and sweets",
    20: "Food at home: Other foods",
    21: "Home food and beverage: Nonalcoholic beverages",
    22: "Home food and beverage: Alcoholic beverages",
}

COMPONENT_COLUMNS: dict[str, str] = {
    "total": "Total",
    "salary_and_benefits": "Salary_and_benefits",
    "property_income": "Property_income",
    "output_taxes": "Output_taxes",
    "imports": "Imports",
    "value_added": "Value_added",
}

COMPONENT_LABELS: dict[str, str] = {
    "total": "Total",
    "salary_and_benefits": "Salary and benefits",
    "property_income": "Property income",
    "output_taxes": "Output taxes",
    "imports": "Imports",
    "value_added": "Value added",
}

SERIES_COMPONENTS: dict[str, list[str]] = {
    "nominal": [
        "total",
        "salary_and_benefits",
        "property_income",
        "output_taxes",
        "imports",
    ],
    "real": ["total", "value_added", "imports"],
}


def media_path(series: str) -> str:
    """Build the media path for one series' tidy CSV.

    Parameters
    ----------
    series : str
        Series key from FOOD_DOLLAR_FILES, 'nominal' or 'real'.

    Returns
    -------
    str
        The '/media/{media_id}/{slug}.csv' path of the series' CSV file.
    """
    entry = FOOD_DOLLAR_FILES[series]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def build_url(series: str) -> str:
    """Build the download URL for one series' tidy CSV.

    Parameters
    ----------
    series : str
        Series key from FOOD_DOLLAR_FILES, 'nominal' or 'real'.

    Returns
    -------
    str
        Full URL of the series' CSV file.
    """
    return f"{BASE_URL}{media_path(series)}"


def to_float(value: str | None) -> float | None:
    """Coerce a source cell to a float, mapping null tokens to None.

    Parameters
    ----------
    value : str | None
        Raw cell text; the literal 'Not available' and empty strings stand
        in for a missing value.

    Returns
    -------
    float | None
        The parsed value, or None for a null token.
    """
    text = (value or "").strip()
    if text in NULL_STRINGS:
        return None
    return float(text)


def parse_rows(text: str, series: str) -> list[dict]:
    """Parse one series' tidy CSV text into row records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns Table_num, Table_name, Category_num,
        Category_desc, Year, Units, and the series' value columns.
    series : str
        Series key from FOOD_DOLLAR_FILES tagged on the parse, selecting the
        value columns to coerce.

    Returns
    -------
    list[dict]
        Records with table_num, category_num, industry_group, year, units,
        and one float-or-None entry per series value column.
    """
    value_columns = FOOD_DOLLAR_FILES[series]["value_columns"]
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        record = {
            "table_num": int(row["Table_num"]),
            "category_num": int(row["Category_num"]),
            "industry_group": (row["Category_desc"] or "").strip(),
            "year": int(row["Year"]),
            "units": (row["Units"] or "").strip(),
        }
        for column in value_columns:
            record[column] = to_float(row.get(column))
        rows.append(record)
    return rows


async def afetch_series(series: str, **kwargs) -> list[dict]:
    """Download and parse one series' tidy CSV through the ERS disk cache.

    Parameters
    ----------
    series : str
        Series key from FOOD_DOLLAR_FILES, 'nominal' or 'real'.

    Returns
    -------
    list[dict]
        Row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(series), product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"), series)
