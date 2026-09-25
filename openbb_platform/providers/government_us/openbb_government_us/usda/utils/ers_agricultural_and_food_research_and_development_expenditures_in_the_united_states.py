"""USDA ERS agricultural and food R&D expenditures catalog and parser."""

import csv
import re
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = (
    "data-products/agricultural-and-food-research-and-development-expenditures"
    "-in-the-united-states"
)
MEDIA_PATH = (
    "/media/5692/agricultural-and-food-research-and-development-rd-expenditures"
    "-in-the-united-states-1970-2022.csv"
)

MEASURES = ("nominal", "real")

SERIES: dict[str, str] = {
    "Public agricultural and food R&D": "public_total",
    "Public agricultural and food R&D performed by USDA intramural agencies": "public_usda_intramural",
    "Public agricultural & food R&D performed by State universities and cooperating institutions": "public_state_universities",
    "Private agriculture input industries R&D": "private_input_industries",
    "Private food industry R&D": "private_food_industry",
    "R&D Price Index": "rd_price_index",
}

SERIES_ORDER = (
    "public_total",
    "public_usda_intramural",
    "public_state_universities",
    "private_input_industries",
    "private_food_industry",
    "rd_price_index",
)

PAREN_PATTERN = re.compile(r"\s*\([^)]*\)\s*$")


def parse_attribute(attribute: str) -> tuple[str | None, str | None]:
    """Split a source Attribute label into its series field and measure.

    Parameters
    ----------
    attribute : str
        Attribute label as published, with a trailing parenthetical stating
        the measure, e.g. 'Private food industry R&D (current U.S. dollars-
        millions)'.

    Returns
    -------
    tuple[str | None, str | None]
        The mapped series field name and the measure ('nominal', 'real', or
        None for the measure-agnostic price index). (None, None) when the
        series is not recognized.
    """
    text = attribute.strip()
    match = PAREN_PATTERN.search(text)
    descriptor = match.group(0).lower() if match else ""
    base = PAREN_PATTERN.sub("", text).strip()
    field = SERIES.get(base)
    if field is None:
        return None, None
    if "constant" in descriptor:
        return field, "real"
    if "current" in descriptor:
        return field, "nominal"
    return field, None


def parse_csv(text: str) -> list[dict]:
    """Parse the R&D expenditures CSV into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text with Year, Attribute, and Value columns.

    Returns
    -------
    list[dict]
        One record per recognized (year, attribute) observation, carrying the
        integer year, the series field, the measure, and the numeric value
        (None for the 'NA' token).
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        year_label = (row.get("Year") or "").strip()
        if len(year_label) < 4 or not year_label[:4].isdigit():
            continue
        field, measure = parse_attribute(row.get("Attribute") or "")
        if field is None:
            continue
        raw_value = (row.get("Value") or "").strip()
        value = None if is_null_token(raw_value) else float(raw_value)
        records.append(
            {
                "year": int(year_label[:4]),
                "series": field,
                "measure": measure,
                "value": value,
            }
        )
    return records


async def afetch_records() -> list[dict]:
    """Download and parse the R&D expenditures CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Long-format records from parse_csv.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    return parse_csv(content.decode("utf-8-sig", errors="replace"))
