"""USDA ERS International Baseline Data file catalog and long-format parsers."""

import csv
import zipfile
from collections import OrderedDict
from io import BytesIO, StringIO

from openbb_core.app.model.abstract.error import OpenBBError

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/international-baseline-data"
MEDIA_PATH = "/media/5324/international-baseline-data-sets.zip"

INTERNATIONAL_BASELINE_FILES: dict[str, tuple[str, str]] = {
    "international_baseline": (MEDIA_PATH, PRODUCT_PAGE)
}

COMMODITIES: tuple[str, ...] = (
    "Barley",
    "Beef and veal",
    "Corn",
    "Cotton",
    "Pork",
    "Poultry",
    "Rice",
    "Sorghum",
    "Soybean meal",
    "Soybean oil",
    "Soybeans",
    "Wheat",
)

DEFAULT_COMMODITY = "Wheat"
DEFAULT_ATTRIBUTE = "Production"


def build_url() -> str:
    """Build the download URL of the international baseline data ZIP."""
    return f"{BASE_URL}{MEDIA_PATH}"


def select_csv_member(names: list[str]) -> str:
    """Return the archive's sole tidy CSV member name.

    Parameters
    ----------
    names : list[str]
        Member names of the international baseline ZIP.

    Returns
    -------
    str
        The single member whose name ends in '.csv', the current long-term
        projection release; the year in its name changes each annual release
        so it is resolved by extension, never hardcoded.

    Raises
    ------
    OpenBBError
        When the archive holds no CSV member.
    """
    for name in names:
        if name.lower().endswith(".csv"):
            return name
    raise OpenBBError("No CSV member found in the international baseline archive.")


def parse_amount(raw: str) -> float | None:
    """Parse an Amount cell into a float, or None for the 'No data' token.

    Parameters
    ----------
    raw : str
        Amount cell as published.

    Returns
    -------
    float | None
        The numeric amount; None when the cell is blank or a non-numeric
        placeholder such as 'No data'.
    """
    text = raw.replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_rows(text: str) -> list[dict]:
    """Parse the projection CSV text into tidy long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the long-term projection member.

    Returns
    -------
    list[dict]
        Records with country, topic, commodity, attribute, unit, year,
        year_type, and amount keys. The amount is None for the 'No data'
        placeholder; the constant Data_Release_Year is carried as context
        only and never returned as a value.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        records.append(
            {
                "country": (row.get("Country") or "").strip(),
                "topic": (row.get("Topic") or "").strip(),
                "commodity": (row.get("Commodity") or "").strip(),
                "attribute": (row.get("Attribute") or "").strip(),
                "unit": (row.get("Unit") or "").strip(),
                "year": (row.get("Year") or "").strip(),
                "year_type": (row.get("Year_type") or "").strip(),
                "amount": parse_amount(row.get("Amount") or ""),
            }
        )
    return records


def attributes_for_commodity(records: list[dict], commodity: str) -> list[str]:
    """List a commodity's attributes in published source order.

    Parameters
    ----------
    records : list[dict]
        Long-format records from parse_rows.
    commodity : str
        Commodity name, e.g. 'Wheat'.

    Returns
    -------
    list[str]
        Distinct Attribute values for the commodity, in first-seen order.
    """
    seen: OrderedDict[str, None] = OrderedDict()
    for record in records:
        if record["commodity"] == commodity and record["attribute"]:
            seen.setdefault(record["attribute"], None)
    return list(seen)


def countries_for_commodity(records: list[dict], commodity: str) -> list[str]:
    """List a commodity's countries and regions in published source order.

    Parameters
    ----------
    records : list[dict]
        Long-format records from parse_rows.
    commodity : str
        Commodity name, e.g. 'Wheat'.

    Returns
    -------
    list[str]
        Distinct Country values for the commodity, in first-seen order.
    """
    seen: OrderedDict[str, None] = OrderedDict()
    for record in records:
        if record["commodity"] == commodity and record["country"]:
            seen.setdefault(record["country"], None)
    return list(seen)


async def afetch_records() -> list[dict]:
    """Download and parse the projection CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Long-format records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    with zipfile.ZipFile(BytesIO(content)) as archive:
        member = select_csv_member(archive.namelist())
        raw = archive.read(member)
    return parse_rows(raw.decode("utf-8-sig", errors="replace"))
