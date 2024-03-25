""" FRED helpers. """

import csv
import os
from pathlib import Path
from typing import Dict, List, Literal

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


def comma_to_float_list(v: str) -> List[float]:
    """Convert comma-separated string to list of floats."""
    try:
        return [float(m) for m in v.split(",")]
    except ValueError as e:
        raise ValueError(
            "'maturity' must be a float or a comma-separated string of floats"
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
