"""USDA ERS Major Land Uses file catalog and parsers."""

import csv
import re
from io import StringIO

from openbb_core.app.model.abstract.error import OpenBBError

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/major-land-uses"

MAJOR_LAND_USES_FILES: dict[str, dict] = {
    "land_use": {
        "media_path": "/media/5639/all-data-in-csv-comma-separated-values-format.csv",
        "format": "csv",
    },
    "cropland_used_for_crops": {
        "media_path": "/media/5647/summary-table-3-total-cropland-used-for-crops"
        + "-cropland-harvested-including-double-cropped-crop-failure-and-cultivated"
        + "-summer-fallow-for-the-united-states-annual-1910-2025.xlsx",
        "format": "xlsx",
    },
}

LAND_USE_CATEGORIES: dict[str, str] = {
    "cropland_idled": "Cropland idled",
    "cropland_used_for_crops": "Cropland used for crops",
    "cropland_used_for_pasture": "Cropland used for pasture",
    "defense_and_industrial": "Land in defense and industrial areas",
    "farmsteads_roads_and_miscellaneous_farmland": (
        "Farmsteads, roads, and miscellaneous farmland"
    ),
    "forest_use_land": "Forest-use land (all)",
    "grassland_pasture_and_range": "Grassland pasture and range",
    "grazed_forest_use_land": "Grazed forest-use land grazed",
    "miscellaneous_other_land": "Miscellaneous other land",
    "rural_parks_and_wildlife": "Land in rural parks and wildlife areas",
    "rural_transportation": "Land in rural transportation facilities",
    "special_uses": "All special uses of land",
    "total_cropland": "Total cropland",
    "total_land": "Total land",
    "ungrazed_forest_use_land": "Ungrazed forest-use land",
    "urban_areas": "Land in urban areas",
}

LABEL_TO_SLUG = {label: slug for slug, label in LAND_USE_CATEGORIES.items()}

GEOGRAPHIES: tuple[str, ...] = (
    "48 States",
    "Alabama",
    "Alaska",
    "Appalachian",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Corn Belt",
    "Delaware",
    "Delta States",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Lake States",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Mountain",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Northeast",
    "Northern Plains",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pacific",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Southeast",
    "Southern Plains",
    "Tennessee",
    "Texas",
    "U.S. total",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
)

AGGREGATE_GEOGRAPHIES = {"48 States", "U.S. total"}

CROPLAND_VARIABLES: tuple[str, ...] = (
    "total_crops_harvested",
    "double_cropped",
    "cropland_harvested",
    "crop_failure",
    "cultivated_summer_fallow",
    "total_cropland_used_for_crops",
)

YEAR_PATTERN = re.compile(r"^(\d{4})(?:\s|$)")


def parse_land_use_csv(text: str) -> list[dict]:
    """Parse the all-data CSV into tidy land-use records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns ID, Region, Region or State, Year,
        Land use, Value, Units, Release date, and Source.

    Returns
    -------
    list[dict]
        Records with year, geography, region, is_aggregate, land_use,
        value (expanded from thousands to acres, 'N.A.' as None), and
        is_preliminary keys.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        geography = (row.get("Region or State") or "").strip()
        region = (row.get("Region") or "").strip()
        label = re.sub(r"\s+", " ", (row.get("Land use") or "").strip())
        raw_value = (row.get("Value") or "").strip()
        is_aggregate = region.endswith(" total") or geography in AGGREGATE_GEOGRAPHIES
        records.append(
            {
                "year": int(row["Year"]),
                "geography": geography,
                "region": None if is_aggregate else region,
                "is_aggregate": is_aggregate,
                "land_use": LABEL_TO_SLUG.get(label, label),
                "value": (
                    None if raw_value in {"", "N.A."} else float(raw_value) * 1000
                ),
                "is_preliminary": None,
            }
        )
    return records


def parse_cropland_xlsx(content: bytes) -> list[dict]:
    """Parse the annual cropland-used-for-crops workbook into tidy records.

    Parameters
    ----------
    content : bytes
        Raw XLSX bytes of summary table 3.

    Returns
    -------
    list[dict]
        Records with year, geography ('United States'), region (None),
        is_aggregate (True), land_use (one of CROPLAND_VARIABLES), value
        (expanded from millions to acres, blanks as None), and
        is_preliminary keys.

    Raises
    ------
    OpenBBError
        If the workbook does not have the expected seven columns.
    """
    from io import BytesIO

    import pandas as pd

    frame = (
        pd.read_excel(BytesIO(content), header=None)
        .dropna(how="all")
        .dropna(axis=1, how="all")
        .reset_index(drop=True)
    )
    if frame.shape[1] != len(CROPLAND_VARIABLES) + 1:
        raise OpenBBError(
            "Unexpected column layout in the cropland-used-for-crops workbook:"
            + f" found {frame.shape[1]} columns, expected"
            + f" {len(CROPLAND_VARIABLES) + 1}."
        )
    records: list[dict] = []
    for row in frame.iloc[2:].itertuples(index=False):
        label = str(row[0]).strip()
        match = YEAR_PATTERN.match(label)
        if match is None:
            break
        year = int(match.group(1))
        is_preliminary = "5/" in label
        for variable, value in zip(CROPLAND_VARIABLES, row[1:]):
            records.append(
                {
                    "year": year,
                    "geography": "United States",
                    "region": None,
                    "is_aggregate": True,
                    "land_use": variable,
                    "value": None if pd.isna(value) else float(value) * 1_000_000,
                    "is_preliminary": is_preliminary,
                }
            )
    return records


async def afetch_land_use() -> list[dict]:
    """Download and parse the all-data CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Tidy records from parse_land_use_csv.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(
        MAJOR_LAND_USES_FILES["land_use"]["media_path"], product=PRODUCT_PAGE
    )
    return parse_land_use_csv(content.decode("utf-8-sig"))


async def afetch_cropland_used_for_crops() -> list[dict]:
    """Download and parse summary table 3 through the ERS disk cache.

    Returns
    -------
    list[dict]
        Tidy records from parse_cropland_xlsx.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(
        MAJOR_LAND_USES_FILES["cropland_used_for_crops"]["media_path"],
        product=PRODUCT_PAGE,
    )
    return parse_cropland_xlsx(content)
