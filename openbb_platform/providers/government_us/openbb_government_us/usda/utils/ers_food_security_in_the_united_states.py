"""USDA ERS Food Security in the United States file catalog and long parsers."""

import csv
import re
import zipfile
from collections import OrderedDict
from io import BytesIO, StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/food-security-in-the-united-states"
MEDIA_PATH = "/media/799/food-security-csv-data-files.zip"
MEMBER_PREFIX = "foodsecurity_csv_datafiles/"

STATE_LABEL_FIXES = {"U.S. total": "United States", "U.S.": "United States"}

ALL_HOUSEHOLDS_MEASURES = (
    ("Total", "Total households (1,000)"),
    ("Food secure-1,000", "Food secure (1,000)"),
    ("Food secure-percent", "Food secure (percent)"),
    ("Food insecure-1,000", "Food insecure (1,000)"),
    ("Food insecure-percent", "Food insecure (percent)"),
    ("Low food security-1,000", "Low food security (1,000)"),
    ("Low food security-percent", "Low food security (percent)"),
    ("Very low food security-1,000", "Very low food security (1,000)"),
    ("Very low food security-percent", "Very low food security (percent)"),
)

CHILDREN_MEASURES = (
    ("Total", "Total households (1,000)"),
    ("Food-secure households-1,000", "Food-secure households (1,000)"),
    ("Food-secure households-percent", "Food-secure households (percent)"),
    ("Food-insecure households-1,000", "Food-insecure households (1,000)"),
    ("Food-insecure households-percent", "Food-insecure households (percent)"),
    (
        "Households with food-insecure children-1,000",
        "Households with food-insecure children (1,000)",
    ),
    (
        "Households with food-insecure children-percent",
        "Households with food-insecure children (percent)",
    ),
    (
        "Households with very low food security among children-1,000",
        "Households with very low food security among children (1,000)",
    ),
    (
        "Households with very low food security among children-percent",
        "Households with very low food security among children (percent)",
    ),
)

EDUCATION_MEASURES = (
    ("Total", "Total households (1,000)"),
    ("Food insecure-1,000", "Food insecure (1,000)"),
    ("Food insecure-percent", "Food insecure (percent)"),
    ("Food insecure-share", "Food insecure (share of food insecure)"),
    ("Very low food security-1,000", "Very low food security (1,000)"),
    ("Very low food security-percent", "Very low food security (percent)"),
    ("Very low food security-share", "Very low food security (share of very low)"),
)

STATE_MEASURES = (
    ("Food insecurity prevalence", "Food insecurity prevalence (percent)"),
    ("Food insecurity margin of error", "Food insecurity margin of error"),
    (
        "Very low food security prevalence",
        "Very low food security prevalence (percent)",
    ),
    (
        "Very low food security margin of error",
        "Very low food security margin of error",
    ),
)

FOOD_SECURITY_TABLES: "OrderedDict[str, dict]" = OrderedDict(
    [
        (
            "national_trend",
            {
                "label": "National trend - all U.S. households",
                "member": "foodsecurity-all-households-2024.csv",
                "dims": (
                    ("Category", "category"),
                    ("Subcategory", "subcategory"),
                    ("Sub-subcategory", "sub_subcategory"),
                ),
                "measures": ALL_HOUSEHOLDS_MEASURES,
                "year_is_period": False,
                "category_mode": "only_all",
            },
        ),
        (
            "by_characteristic",
            {
                "label": "By household characteristic",
                "member": "foodsecurity-all-households-2024.csv",
                "dims": (
                    ("Category", "category"),
                    ("Subcategory", "subcategory"),
                    ("Sub-subcategory", "sub_subcategory"),
                ),
                "measures": ALL_HOUSEHOLDS_MEASURES,
                "year_is_period": False,
                "category_mode": "exclude_all",
            },
        ),
        (
            "households_with_children",
            {
                "label": "Households with children",
                "member": "foodsecurity-hh-with-children-2024.csv",
                "dims": (
                    ("Category", "category"),
                    ("Subcategory", "subcategory"),
                ),
                "measures": CHILDREN_MEASURES,
                "year_is_period": False,
                "category_mode": None,
            },
        ),
        (
            "child_trends",
            {
                "label": "Child food security trends",
                "member": "foodsecurity-child-trends-2024.csv",
                "dims": (("Category", "category"),),
                "measures": CHILDREN_MEASURES,
                "year_is_period": False,
                "category_mode": None,
            },
        ),
        (
            "education_employment_disability",
            {
                "label": "Education, employment, and disability",
                "member": "foodsecurity-educ-emp-dis-2024.csv",
                "dims": (
                    ("Category", "category"),
                    ("Subcategory", "subcategory"),
                    ("Sub-subcategory", "sub_subcategory"),
                ),
                "measures": EDUCATION_MEASURES,
                "year_is_period": False,
                "category_mode": None,
            },
        ),
        (
            "by_state",
            {
                "label": "By State (3-year averages)",
                "member": "foodsecurity-state-2024.csv",
                "dims": (("State", "state"),),
                "measures": STATE_MEASURES,
                "year_is_period": True,
                "category_mode": None,
            },
        ),
    ]
)

DIM_FIELDS = ("category", "subcategory", "sub_subcategory", "state")


def normalize_header(header: str) -> str:
    """Normalize a source header, replacing the replacement character and spaces.

    Parameters
    ----------
    header : str
        Header cell as published, which may carry a U+FFFD replacement
        character in place of a space and stray leading or trailing spaces.

    Returns
    -------
    str
        The header with U+FFFD turned into a space, internal whitespace
        collapsed, and the ends stripped.
    """
    return re.sub(r"\s+", " ", header.replace("�", " ")).strip()


def clean_number(cell: str) -> float | None:
    """Parse a numeric cell, stripping the replacement character and commas.

    Parameters
    ----------
    cell : str
        Value cell as published, which may carry a U+FFFD prefix, thousands
        separators, or an N/A placeholder token.

    Returns
    -------
    float | None
        The parsed value, or None when the cell is blank or non-numeric.
    """
    text = cell.replace("�", "").replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _extract_dims(config: dict, raw: list[str], index: dict[str, int]) -> dict:
    """Read a row's dimension fields, defaulting missing ones to None.

    Parameters
    ----------
    config : dict
        Table config from FOOD_SECURITY_TABLES.
    raw : list[str]
        The row cells.
    index : dict[str, int]
        Header name to column position map.

    Returns
    -------
    dict
        The four dimension fields, with the national state labels normalized.
    """
    dims: dict = {field: None for field in DIM_FIELDS}
    for source_col, output_field in config["dims"]:
        position = index.get(source_col)
        value = (
            raw[position].strip()
            if position is not None and position < len(raw)
            else ""
        )
        if output_field == "state":
            value = STATE_LABEL_FIXES.get(value, value)
        dims[output_field] = value or None
    return dims


def _category_excluded(config: dict, category: str | None) -> bool:
    """Return whether a row's category is filtered out by the table's mode."""
    mode = config["category_mode"]
    if mode == "only_all":
        return category != "All households"
    if mode == "exclude_all":
        return category == "All households"
    return False


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's CSV text into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the table member.
    table : str
        Table key from FOOD_SECURITY_TABLES.

    Returns
    -------
    list[dict]
        One record per year, dimension path, and measure, carrying the year
        label, its integer sort year, the four dimension fields, the clean
        measure label as series, and the numeric value. Rows whose year label
        is blank or non-numeric are dropped.
    """
    config = FOOD_SECURITY_TABLES[table]
    rows = list(csv.reader(StringIO(text)))
    if not rows:
        return []
    header = [normalize_header(cell) for cell in rows[0]]
    index = {name: position for position, name in enumerate(header)}
    year_index = index.get("Year")
    if year_index is None:
        return []
    records: list[dict] = []
    for raw in rows[1:]:
        if len(raw) <= year_index:
            continue
        cell = raw[year_index]
        year_label = (
            cell.replace("�", "-").strip() if config["year_is_period"] else cell.strip()
        )
        if not year_label[:4].isdigit():
            continue
        dims = _extract_dims(config, raw, index)
        if _category_excluded(config, dims["category"]):
            continue
        sort_year = int(year_label[:4])
        for source_col, label in config["measures"]:
            position = index.get(source_col)
            if position is None or position >= len(raw):
                continue
            records.append(
                {
                    "table": table,
                    "year": year_label,
                    "sort_year": sort_year,
                    "category": dims["category"],
                    "subcategory": dims["subcategory"],
                    "sub_subcategory": dims["sub_subcategory"],
                    "state": dims["state"],
                    "series": label,
                    "value": clean_number(raw[position]),
                }
            )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one food-security table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from FOOD_SECURITY_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = FOOD_SECURITY_TABLES[table]
    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    with zipfile.ZipFile(BytesIO(content)) as archive:
        raw = archive.read(MEMBER_PREFIX + config["member"])
    return parse_table(raw.decode("utf-8-sig", errors="replace"), table)


async def afetch_categories(table: str) -> list[str]:
    """List a table's distinct category labels in published order.

    Parameters
    ----------
    table : str
        Table key from FOOD_SECURITY_TABLES.

    Returns
    -------
    list[str]
        Distinct non-null Category values, in first-seen order.
    """
    records = await afetch_table(table)
    seen: list[str] = []
    for record in records:
        category = record["category"]
        if category and category not in seen:
            seen.append(category)
    return seen
