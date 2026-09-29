"""FRED helpers."""

import csv
import os
from pathlib import Path
from typing import Literal

from openbb_core.app.model.abstract.error import OpenBBError

YIELD_CURVES = {
    "nominal": {
        "DGS1MO": "month_1",
        "DGS3MO": "month_3",
        "DGS6MO": "month_6",
        "DGS1": "year_1",
        "DGS2": "year_2",
        "DGS3": "year_3",
        "DGS5": "year_5",
        "DGS7": "year_7",
        "DGS10": "year_10",
        "DGS20": "year_20",
        "DGS30": "year_30",
    },
    "real": {
        "DFII5": "year_5",
        "DFII7": "year_7",
        "DFII10": "year_10",
        "DFII20": "year_20",
        "DFII30": "year_30",
    },
    "breakeven": {
        "T5YIEM": "year_5",
        "T7YIEM": "year_7",
        "T10YIEM": "year_10",
        "T20YIEM": "year_20",
        "T30YIEM": "year_30",
    },
    "treasury_minus_fed_funds": {
        "T3MFF": "month_3",
        "T6MFF": "month_6",
        "T1YFF": "year_1",
        "T5YFF": "year_5",
        "T10YFF": "year_10",
    },
    "corporate_spot": {
        "HQMCB6MT": "month_6",
        "HQMCB1YR": "year_1",
        "HQMCB2YR": "year_2",
        "HQMCB3YR": "year_3",
        "HQMCB5YR": "year_5",
        "HQMCB7YR": "year_7",
        "HQMCB10YR": "year_10",
        "HQMCB20YR": "year_20",
        "HQMCB30YR": "year_30",
        "HQMCB50YR": "year_50",
        "HQMCB75YR": "year_75",
        "HQMCB100YR": "year_100",
    },
    "corporate_par": {
        "HQMCB2YRP": "year_2",
        "HQMCB5YRP": "year_5",
        "HQMCB10YRP": "year_10",
        "HQMCB30YRP": "year_30",
    },
}

CPI_COUNTRIES = [
    "australia",
    "austria",
    "belgium",
    "brazil",
    "bulgaria",
    "canada",
    "chile",
    "china",
    "croatia",
    "cyprus",
    "czech_republic",
    "denmark",
    "estonia",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "iceland",
    "india",
    "indonesia",
    "ireland",
    "israel",
    "italy",
    "japan",
    "korea",
    "latvia",
    "lithuania",
    "luxembourg",
    "malta",
    "mexico",
    "netherlands",
    "new_zealand",
    "norway",
    "poland",
    "portugal",
    "romania",
    "russian_federation",
    "slovak_republic",
    "slovakia",
    "slovenia",
    "south_africa",
    "spain",
    "sweden",
    "switzerland",
    "turkey",
    "united_kingdom",
    "united_states",
]

CpiCountries = Literal[
    "australia",
    "austria",
    "belgium",
    "brazil",
    "bulgaria",
    "canada",
    "chile",
    "china",
    "croatia",
    "cyprus",
    "czech_republic",
    "denmark",
    "estonia",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "iceland",
    "india",
    "indonesia",
    "ireland",
    "israel",
    "italy",
    "japan",
    "korea",
    "latvia",
    "lithuania",
    "luxembourg",
    "malta",
    "mexico",
    "netherlands",
    "new_zealand",
    "norway",
    "poland",
    "portugal",
    "romania",
    "russian_federation",
    "slovak_republic",
    "slovakia",
    "slovenia",
    "south_africa",
    "spain",
    "sweden",
    "switzerland",
    "turkey",
    "united_kingdom",
    "united_states",
]


def comma_to_float_list(v: str) -> list[float]:
    """Convert comma-separated string to list of floats."""
    try:
        return [float(m) for m in v.split(",")]
    except ValueError as e:
        raise OpenBBError(
            "maturity must be a float or a comma-separated string of floats"
        ) from e


def read_reference(file: str) -> list[dict]:
    """Read one of the packaged reference tables.

    Parameters
    ----------
    file : str
        The file name, relative to this module.

    Returns
    -------
    list[dict]
        One entry per row, with any byte-order mark stripped from the headers.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))

    with open(Path(current_dir, file), encoding="utf-8") as csv_file_handler:
        return [
            {key.lstrip("\ufeff"): value for key, value in row.items()}
            for row in csv.DictReader(csv_file_handler)
        ]


def all_cpi_options(harmonized: bool = False) -> list[dict]:
    """Get all CPI options."""
    return read_reference("harmonized_cpi.csv" if harmonized else "cpi.csv")


def process_projections(data: dict) -> list[dict]:
    """Process projection data."""
    dates: list = []

    for value in data.values():
        dates.extend([entry["date"] for entry in value])

    ldata: list = []

    for date in sorted(set(dates)):
        entry: dict = {"date": date}

        for key, value in data.items():
            val = [item["value"] for item in value if item["date"] == date]
            entry[key] = (float(val[0]) if val[0] != "." else None) if val else None

        ldata.append(entry)

    return ldata


def spot_rates() -> list[dict]:
    """Get every corporate spot rate series the package knows of.

    Returns
    -------
    list[dict]
        One entry per series, carrying its maturity, category, and series id.
    """
    return read_reference("corporate_spot_rates.csv")


def get_spot_maturities(category: list[str]) -> list[float]:
    """Get the maturities published for one or more spot rate categories.

    Parameters
    ----------
    category : list[str]
        The categories to read, such as 'spot_rate' or 'par_yield'.

    Returns
    -------
    list[float]
        The maturities, in years, in ascending order.
    """
    return sorted(
        {
            float(s["Maturity"].replace("y", ""))
            for s in spot_rates()
            if s["Category"] in category
        }
    )


def get_spot_series_id(maturity: list[float], category: list[str]) -> list[dict]:
    """Get Spot series id."""
    return [
        s
        for s in spot_rates()
        if float(s["Maturity"].replace("y", "")) in maturity
        and s["Category"] in category
    ]


BOP_COUNTRIES = {
    "argentina": "ARG",
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "china": "CHN",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czechia": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "india": "IND",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JAP",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "poland": "POL",
    "portugal": "PRT",
    "russia": "RUS",
    "saudi_arabia": "SAU",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "south_africa": "ZAF",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
    "g7": "G7",
    "g20": "G20",
}

BOP_COUNTRY_CHOICES = Literal[
    "argentina",
    "australia",
    "austria",
    "belgium",
    "brazil",
    "canada",
    "chile",
    "china",
    "colombia",
    "costa_rica",
    "czechia",
    "denmark",
    "estonia",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "iceland",
    "india",
    "indonesia",
    "ireland",
    "israel",
    "italy",
    "japan",
    "korea",
    "latvia",
    "lithuania",
    "luxembourg",
    "mexico",
    "netherlands",
    "new_zealand",
    "norway",
    "poland",
    "portugal",
    "russia",
    "saudi_arabia",
    "slovak_republic",
    "slovenia",
    "south_africa",
    "spain",
    "sweden",
    "switzerland",
    "turkey",
    "united_kingdom",
    "united_states",
    "g7",
    "g20",
]


def get_bop_series(country: str) -> dict:
    """Get the series IDs for the B6 Balance of Payments Report."""
    return dict(
        balance_percent_of_gdp=f"{country}B6BLTT02STSAQ",
        balance_total=f"{country}B6BLTT01CXCUSAQ",
        balance_total_services=f"{country}B6BLSE01CXCUSAQ",
        balance_total_secondary_income=f"{country}B6BLSI01CXCUSAQ",
        balance_total_goods=f"{country}B6BLTD01CXCUSAQ",
        balance_total_primary_income=f"{country}B6BLPI01CXCUSAQ",
        credits_services_percent_of_goods_and_services=f"{country}B6CRSE03STSAQ",
        credits_services_percent_of_current_account=f"{country}B6CRSE02STSAQ",
        credits_total_services=f"{country}B6CRSE01CXCUSAQ",
        credits_total_goods=f"{country}B6CRTD01CXCUSAQ",
        credits_total_primary_income=f"{country}B6CRPI01CXCUSAQ",
        credits_total_secondary_income=f"{country}B6CRSI01CXCUSAQ",
        credits_total=f"{country}B6CRTT01CXCUSAQ",
        debits_services_percent_of_goods_and_services=f"{country}B6DBSE03STSAQ",
        debits_services_percent_of_current_account=f"{country}B6DBSE02STSAQ",
        debits_total_services=f"{country}B6DBSE01CXCUSAQ",
        debits_total_goods=f"{country}B6DBTD01CXCUSAQ",
        debits_total_primary_income=f"{country}B6DBPI01CXCUSAQ",
        debits_total=f"{country}B6DBTT01CXCUSAQ",
        debits_total_secondary_income=f"{country}B6DBSI01CXCUSAQ",
    )
