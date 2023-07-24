import csv
from typing import List, Literal


CPI_COUNTRIES = Literal[
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
    "euro_area",
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

CPI_UNITS = Literal["growth_previous", "growth_same", "index_2015"]

CPI_FREQUENCY = Literal["monthly", "quarterly", "annual"]


def all_cpi_options(harmonized: bool = False) -> List[dict]:
    data = []

    file = "harmonized_cpi.csv" if harmonized else "cpi.csv"
    with open(file, encoding="utf-8") as csv_file_handler:
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
