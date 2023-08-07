import csv
import os
from pathlib import Path
from typing import List


def all_cpi_options(harmonized: bool = False) -> List[dict]:
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
    series = all_cpi_options(harmonized)
    for item in series:
        item.pop("series_id")
    return series
