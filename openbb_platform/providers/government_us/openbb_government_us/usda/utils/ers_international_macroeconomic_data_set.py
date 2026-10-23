"""USDA ERS International Macroeconomic Data Set file catalog and parsers."""

import csv
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/international-macroeconomic-data-set"

GROWTH_MARKER = "Percent Change"

INTERNATIONAL_MACRO_FILES: dict[str, dict] = {
    "real_gdp": {
        "label": "Real GDP (billions of 2017 dollars)",
        "media": "/media/6157/historical-and-projected-real-gross-domestic"
        "-product-gdp-and-growth-rates-of-gdp-for-baseline-countriesregions"
        "-in-billions-of-2017-dollars-1970-2035.csv",
        "mojibake": False,
    },
    "real_gdp_per_capita": {
        "label": "Real GDP per capita (2017 dollars)",
        "media": "/media/6159/historical-and-projected-real-gdp-per-capita-and"
        "-growth-rates-for-baseline-countriesregions-in-billions-of-2017"
        "-dollars-1970-2035.csv",
        "mojibake": False,
    },
    "gdp_deflator": {
        "label": "GDP deflator (2017 = 100)",
        "media": "/media/6161/historical-and-projected-gdp-deflator-and-growth"
        "-rates-of-gdp-deflator-for-baseline-countriesregions-in-billions-of"
        "-2017-dollars-1970-2035.csv",
        "mojibake": False,
    },
    "real_gdp_shares": {
        "label": "Real GDP shares (share of world GDP)",
        "media": "/media/6163/historical-and-projected-real-gdp-shares-and"
        "-growth-rates-for-baseline-countriesregions-in-billions-of-2017"
        "-dollars-1970-2035.csv",
        "mojibake": False,
    },
    "real_exchange_rate": {
        "label": "Real exchange rate (2017 = 100)",
        "media": "/media/6165/historical-and-projected-real-exchange-rate-and"
        "-growth-rates-for-baseline-countriesregions-in-billions-of-2017"
        "-dollars-1970-2035.csv",
        "mojibake": False,
    },
    "cpi": {
        "label": "Consumer price index (2017 = 100)",
        "media": "/media/6167/historical-and-projected-consumer-price-indices"
        "-cpi-for-baseline-countriesregions-1970-2035.csv",
        "mojibake": False,
    },
    "population": {
        "label": "Population",
        "media": "/media/6169/historical-and-projected-population-and-growth"
        "-rates-for-baseline-countriesregions-1970-2035.csv",
        "mojibake": True,
    },
}

DEFAULT_VARIABLE = "real_gdp"
DEFAULT_MEASURE = "level"

MEASURES: dict[str, str] = {
    "level": "Level",
    "growth": "Percent change, year to year",
}

OBSERVATION_RELABEL: dict[str, str] = {
    "US Ag. Trade Weighted Exchange Rate, 2017=100": "US Ag. Trade Weighted",
}


def is_growth_unit(unit: str) -> bool:
    """Return whether a Unit label is a year-to-year percent-change series."""
    return GROWTH_MARKER in unit


def repair_mojibake(text: str) -> str:
    """Repair a double-encoded UTF-8 label, leaving clean labels unchanged.

    Parameters
    ----------
    text : str
        Observation label, possibly double-encoded UTF-8 such as
        "CÃ´te d'Ivoire".

    Returns
    -------
    str
        The Latin-1 to UTF-8 round-tripped label, e.g. "Côte d'Ivoire";
        the input unchanged when it is plain ASCII or cannot be repaired.
    """
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text


def parse_rows(text: str, mojibake: bool = False) -> list[dict]:
    """Parse one variable's CSV text into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text with the Observation, Year, Unit, and Value columns.
    mojibake : bool
        Whether the file's observation labels are double-encoded UTF-8 and
        must be repaired.

    Returns
    -------
    list[dict]
        Records with observation, year, unit, and value keys. Fully blank
        padding rows, non-year rows, and rows whose value is a null token or
        non-numeric are dropped.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        observation = (row.get("Observation") or "").strip()
        year_token = (row.get("Year") or "").strip()
        unit = (row.get("Unit") or "").strip()
        raw_value = (row.get("Value") or "").strip()
        if not (observation or year_token or unit or raw_value):
            continue
        if not year_token.isdigit():
            continue
        if is_null_token(raw_value):
            continue
        try:
            value = float(raw_value)
        except ValueError:
            continue
        if mojibake:
            observation = repair_mojibake(observation)
        observation = OBSERVATION_RELABEL.get(observation, observation)
        records.append(
            {
                "observation": observation,
                "year": int(year_token),
                "unit": unit,
                "value": value,
            }
        )
    return records


async def afetch_records(variable: str) -> list[dict]:
    """Download and parse one variable's CSV through the ERS disk cache.

    Parameters
    ----------
    variable : str
        Variable key from INTERNATIONAL_MACRO_FILES.

    Returns
    -------
    list[dict]
        Long-format records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = INTERNATIONAL_MACRO_FILES[variable]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    return parse_rows(
        content.decode("utf-8-sig", errors="replace"), mojibake=config["mojibake"]
    )
