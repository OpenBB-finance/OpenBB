import csv
import os
from pathlib import Path
from typing import Dict, List

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
                entry[key] = float(val[0]) if val != "." else float("nan")
            else:
                entry[key] = float("nan")
        ldata.append(entry)

    return ldata
