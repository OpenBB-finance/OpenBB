"""USDA ERS Purchase to Plate national average prices catalog, fetch, and parser."""

import csv
import io
import zipfile
from collections import OrderedDict
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/purchase-to-plate"

CATALOG: dict[str, dict] = {
    "national_average_prices": {
        "media_path": (
            "/media/6557/purchase-to-plate-national-average-prices"
            "-for-nhanes-csv-format.zip"
        ),
        "member": "pp_national_average_prices_csv.csv",
    },
}

DEFAULT_TABLE = "national_average_prices"

CYCLE_BY_YEAR: "OrderedDict[str, str]" = OrderedDict(
    [
        ("2011/2012", "cycle_2011_2012"),
        ("2013/2014", "cycle_2013_2014"),
        ("2015/2016", "cycle_2015_2016"),
        ("2017/2018", "cycle_2017_2018"),
    ]
)

CYCLE_ORDER: tuple[str, ...] = tuple(CYCLE_BY_YEAR.values())

CYCLE_HEADERS: "OrderedDict[str, str]" = OrderedDict(
    [(field, year) for year, field in CYCLE_BY_YEAR.items()]
)

FOOD_GROUPS: "OrderedDict[str, dict]" = OrderedDict(
    [
        ("milk", {"digit": "1", "label": "Milk and milk products"}),
        ("meat", {"digit": "2", "label": "Meat, poultry, fish, and mixtures"}),
        ("eggs", {"digit": "3", "label": "Eggs"}),
        ("legumes", {"digit": "4", "label": "Legumes, nuts, and seeds"}),
        ("grains", {"digit": "5", "label": "Grain products"}),
        ("fruits", {"digit": "6", "label": "Fruits"}),
        ("vegetables", {"digit": "7", "label": "Vegetables"}),
        ("fats", {"digit": "8", "label": "Fats, oils, and salad dressings"}),
        ("sugars", {"digit": "9", "label": "Sugars, sweets, and beverages"}),
    ]
)

DEFAULT_FOOD_GROUP = "milk"

DIGIT_TO_GROUP: dict[str, str] = {
    meta["digit"]: slug for slug, meta in FOOD_GROUPS.items()
}

MOD_NULL_TOKENS = frozenset({"0", "na", "n/a", ""})

VALUE_NULL_TOKENS = frozenset({"na", "n/a", ""})


def media_path(table: str) -> str:
    """Return a table's zip media path.

    Parameters
    ----------
    table : str
        Table key from CATALOG.

    Returns
    -------
    str
        The '/media/{id}/{name}.zip' path of the table's archive.
    """
    return CATALOG[table]["media_path"]


def build_url(table: str) -> str:
    """Return a table's full download URL."""
    return f"{BASE_URL}{media_path(table)}"


def group_options() -> list[dict]:
    """Build the labeled FNDDS food-group options."""
    return [
        {"label": meta["label"], "value": slug} for slug, meta in FOOD_GROUPS.items()
    ]


def food_group_slug(food_code: str) -> str | None:
    """Map an eight-digit FNDDS food code to its food-group slug.

    Parameters
    ----------
    food_code : str
        Eight-digit FNDDS food code; its leading digit names the food group.

    Returns
    -------
    str | None
        Food-group slug, or None when the leading digit is unmapped.
    """
    return DIGIT_TO_GROUP.get(food_code[:1])


def normalize_mod(mod_code: str | None) -> str:
    """Normalize a modification code, mapping absent codes to the base '0'.

    Parameters
    ----------
    mod_code : str | None
        Raw modification code; '0' on 2011/2012 rows, 'NA' on later cycles
        whose sheet lacks the column.

    Returns
    -------
    str
        The base code '0' for unmodified items, else the modification code.
    """
    text = (mod_code or "").strip()
    return "0" if text.casefold() in MOD_NULL_TOKENS else text


def clean_token(value: str | None) -> str | None:
    """Strip a raw cell, mapping empty text and the 'NA' sentinel to None."""
    text = (value or "").strip()
    return None if text.casefold() in VALUE_NULL_TOKENS else text


def parse_price(value: str | None) -> float | None:
    """Parse a raw price cell to a float, keeping full precision.

    Parameters
    ----------
    value : str | None
        Raw price_100gm cell, nominal dollars per 100 edible grams, or 'NA'.

    Returns
    -------
    float | None
        The raw price as a float, or None for an 'NA' or empty cell.
    """
    text = (value or "").strip()
    if text.casefold() in VALUE_NULL_TOKENS:
        return None
    return float(text)


def extract_csv_text(zip_bytes: bytes, member: str) -> str:
    """Extract and decode one CSV member from a table's zip archive.

    Parameters
    ----------
    zip_bytes : bytes
        Raw bytes of the table's zip archive.
    member : str
        Member CSV file name to read.

    Returns
    -------
    str
        The decoded CSV text of the member, tolerating stray cp1252 bytes.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        raw = archive.read(member)
    return raw.decode("utf-8-sig", errors="replace")


def parse_rows(text: str) -> list[dict]:
    """Parse the national-average-prices CSV into long, normalized records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns year, food_code, mod_code,
        food_description, method, method_description, nhanes, price_100gm.

    Returns
    -------
    list[dict]
        Records with food_code, mod_code, food_group, cycle, cycle_index,
        food_description, method_description, nhanes, and price keys, one per
        source row of a recognized survey cycle.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        cycle = CYCLE_BY_YEAR.get((row.get("year") or "").strip())
        if cycle is None:
            continue
        food_code = (row.get("food_code") or "").strip()
        records.append(
            {
                "food_code": food_code,
                "mod_code": normalize_mod(row.get("mod_code")),
                "food_group": food_group_slug(food_code),
                "cycle": cycle,
                "cycle_index": CYCLE_ORDER.index(cycle),
                "food_description": (row.get("food_description") or "").strip(),
                "method_description": clean_token(row.get("method_description")),
                "nhanes": clean_token(row.get("nhanes")),
                "price": parse_price(row.get("price_100gm")),
            }
        )
    return records


async def afetch_table(table: str = DEFAULT_TABLE) -> list[dict]:
    """Download and parse a table's CSV through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from CATALOG.

    Returns
    -------
    list[dict]
        Long, normalized records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = CATALOG[table]
    content = await afetch_ers_file(config["media_path"], product=PRODUCT_PAGE)
    return parse_rows(extract_csv_text(content, config["member"]))
