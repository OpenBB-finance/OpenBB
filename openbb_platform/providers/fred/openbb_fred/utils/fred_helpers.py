"""FRED helpers."""

import csv
import os
from pathlib import Path
from typing import Dict, List, Literal

from openbb_core.app.model.abstract.error import OpenBBError

YIELD_CURVE_NOMINAL_RATES = [round(1 / 12, 3), 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
YIELD_CURVE_SPOT_RATES = [0.5, 1, 2, 3, 5, 7, 10, 20, 30, 50, 75, 100]
YIELD_CURVE_REAL_RATES = [5.0, 7, 10, 20, 30]
YIELD_CURVE_PAR_RATES = [2.0, 5, 10, 30]
YIELD_CURVE_SERIES_NOMINAL = {
    "1Month": "DGS1MO",
    "3Month": "DGS3MO",
    "6Month": "DGS6MO",
    "1Year": "DGS1",
    "2Year": "DGS2",
    "3Year": "DGS3",
    "5Year": "DGS5",
    "7Year": "DGS7",
    "10Year": "DGS10",
    "20Year": "DGS20",
    "30Year": "DGS30",
}
YIELD_CURVE_SERIES_REAL = {
    "5Year": "DFII5",
    "7Year": "DFII7",
    "10Year": "DFII10",
    "20Year": "DFII20",
    "30Year": "DFII30",
}
YIELD_CURVE_SERIES_CORPORATE_SPOT = {
    "6Month": "HQMCB6MT",
    "1Year": "HQMCB1YR",
    "2Year": "HQMCB2YR",
    "3Year": "HQMCB3YR",
    "5Year": "HQMCB5YR",
    "7Year": "HQMCB7YR",
    "10Year": "HQMCB10YR",
    "20Year": "HQMCB20YR",
    "30Year": "HQMCB30YR",
    "50Year": "HQMCB50YR",
    "75Year": "HQMCB75YR",
    "100Year": "HQMCB100YR",
}
YIELD_CURVE_SERIES_CORPORATE_PAR = {
    "2Year": "HQMCB2YRP",
    "5Year": "HQMCB5YRP",
    "10Year": "HQMCB10YRP",
    "30Year": "HQMCB30YRP",
}
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


def comma_to_float_list(v: str) -> List[float]:
    """Convert comma-separated string to list of floats."""
    try:
        return [float(m) for m in v.split(",")]
    except ValueError as e:
        raise OpenBBError(
            "maturity must be a float or a comma-separated string of floats"
        ) from e


def all_cpi_options(harmonized: bool = False) -> List[dict]:
    """Get all CPI options."""
    data = []

    current_dir = os.path.dirname(os.path.realpath(__file__))
    file = "harmonized_cpi.csv" if harmonized else "cpi.csv"

    with open(Path(current_dir, file), encoding="utf-8") as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        for rows in csv_reader:
            row = {key.lstrip("\ufeff"): value for key, value in rows.items()}
            data.append(row)
    return data


def get_cpi_options(harmonized: bool = False) -> List[dict]:
    """Get CPI options."""
    series = all_cpi_options(harmonized)
    for item in series:
        item.pop("series_id")
    return series


def process_projections(data: Dict) -> List[Dict]:
    """Process projection data."""
    # Get dates first
    dates = []
    for key, value in data.items():
        dates.extend([entry["date"] for entry in value])
    full_dates = sorted(list(set(dates)))

    # Loop through date and get dictionary of all keys
    ldata = []
    for date in full_dates:
        entry = {"date": date}
        for key, value in data.items():
            val = [item["value"] for item in value if item["date"] == date]
            if val:
                entry[key] = float(val[0]) if val[0] != "." else None
            else:
                entry[key] = None
        ldata.append(entry)

    return ldata


def get_ice_bofa_series_id(
    type_: Literal["yield", "yield_to_worst", "total_return", "spread"],
    category: Literal["all", "duration", "eur", "usd"],
    area: Literal["asia", "emea", "eu", "ex_g10", "latin_america", "us"],
    grade: Literal[
        "a",
        "aa",
        "aaa",
        "b",
        "bb",
        "bbb",
        "ccc",
        "crossover",
        "high_grade",
        "high_yield",
        "non_financial",
        "non_sovereign",
        "private_sector",
        "public_sector",
    ],
) -> List[dict]:
    """Get ICE BofA series id."""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file = "ice_bofa_indices.csv"

    series = []

    with open(Path(current_dir, file), encoding="utf-8") as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        for rows in csv_reader:
            row = {key.lstrip("\ufeff"): value for key, value in rows.items()}
            series.append(row)

    filtered_series = []

    units = "index" if type_ == "total_return" else "percent"

    for s in series:
        # pylint: disable=too-many-boolean-expressions
        if (
            s["Type"] == type_
            and s["Units"] == units
            and s["Frequency"] == "daily"
            and s["Asset Class"] == "bonds"
            and s["Category"] == category
            and s["Area"] == area
            and s["Grade"] == grade
        ):
            filtered_series.append(s)

    return filtered_series


def get_cp_series_id(maturity, category, grade) -> List[dict]:
    """Get CP series id."""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file = "commercial_paper.csv"

    series = []

    with open(Path(current_dir, file), encoding="utf-8") as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        for rows in csv_reader:
            row = {key.lstrip("\ufeff"): value for key, value in rows.items()}
            series.append(row)

    filtered_series = []

    category = (
        "non_financial"
        if (grade == "a2_p2" and category != "non_financial")
        else category
    )

    for s in series:
        if (
            s["Maturity"] == maturity
            and s["Category"] == category
            and s["Grade"] == grade
        ):
            filtered_series.append(s)

    return filtered_series


def get_spot_series_id(maturity: List[float], category: List[str]) -> List[dict]:
    """Get Spot series id."""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file = "corporate_spot_rates.csv"

    series = []

    with open(Path(current_dir, file), encoding="utf-8") as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        for rows in csv_reader:
            row = {key.lstrip("\ufeff"): value for key, value in rows.items()}
            series.append(row)

    filtered_series = []

    for s in series:
        s_maturity = float(s["Maturity"].replace("y", ""))
        if s_maturity in maturity and s["Category"] in category:
            filtered_series.append(s)

    return filtered_series


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
        # Current Account Balance in USD.
        balance_percent_of_gdp=f"{country}B6BLTT02STSAQ",
        balance_total=f"{country}B6BLTT01CXCUSAQ",
        balance_total_services=f"{country}B6BLSE01CXCUSAQ",
        balance_total_secondary_income=f"{country}B6BLSI01CXCUSAQ",
        balance_total_goods=f"{country}B6BLTD01CXCUSAQ",
        balance_total_primary_income=f"{country}B6BLPI01CXCUSAQ",
        # Current Account Credits in USD
        credits_services_percent_of_goods_and_services=f"{country}B6CRSE03STSAQ",
        credits_services_percent_of_current_account=f"{country}B6CRSE02STSAQ",
        credits_total_services=f"{country}B6CRSE01CXCUSAQ",
        credits_total_goods=f"{country}B6CRTD01CXCUSAQ",
        credits_total_primary_income=f"{country}B6CRPI01CXCUSAQ",
        credits_total_secondary_income=f"{country}B6CRSI01CXCUSAQ",
        credits_total=f"{country}B6CRTT01CXCUSAQ",
        # Current Account Debits in USD
        debits_services_percent_of_goods_and_services=f"{country}B6DBSE03STSAQ",
        debits_services_percent_of_current_account=f"{country}B6DBSE02STSAQ",
        debits_total_services=f"{country}B6DBSE01CXCUSAQ",
        debits_total_goods=f"{country}B6DBTD01CXCUSAQ",
        debits_total_primary_income=f"{country}B6DBPI01CXCUSAQ",
        debits_total=f"{country}B6DBTT01CXCUSAQ",
        debits_total_secondary_income=f"{country}B6DBSI01CXCUSAQ",
    )
