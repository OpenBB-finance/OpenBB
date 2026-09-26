"""USDA ERS Milk Cost of Production Estimates file catalog and parsers."""

import csv
import re
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/milk-cost-of-production-estimates"

MILK_COST_FILES: dict[str, dict] = {
    "by_state": {
        "media_id": 5057,
        "slug": "by-state",
        "dimension": "state",
    },
    "by_size_of_operation": {
        "media_id": 5059,
        "slug": "by-size-of-operation",
        "dimension": "size_of_operation",
    },
}

STATE_CHOICES: dict[str, str] = {
    "us_total": "U.S. total",
    "california": "California",
    "indiana": "Indiana",
    "iowa": "Iowa",
    "kentucky": "Kentucky",
    "michigan": "Michigan",
    "minnesota": "Minnesota",
    "new_york": "New York",
    "ohio": "Ohio",
    "pennsylvania": "Pennsylvania",
    "wisconsin": "Wisconsin",
}

SIZE_CHOICES: dict[str, str] = {
    "fewer_than_50_cows": "Fewer than 50 cows",
    "50_99_cows": "50–99 cows",
    "100_199_cows": "100–199 cows",
    "200_499_cows": "200–499 cows",
    "500_999_cows": "500–999 cows",
    "1000_1999_cows": "1,000–1,999 cows",
    "2000_cows_or_more": "2,000 cows or more",
    "all_sizes": "All sizes",
}

CATEGORY_CHOICES: dict[str, str] = {
    "gross_value_of_production": "Gross value of production",
    "operating_costs": "Operating costs",
    "allocated_overhead": "Allocated overhead",
    "costs_listed": "Costs listed",
    "net_value": "Net value",
    "supporting_information": "Supporting information",
}

ITEM_CHOICES: dict[str, str] = {
    "bedding_and_litter": "Bedding and litter",
    "capital_recovery_of_machinery_and_equipment": (
        "Capital recovery of machinery and equipment"
    ),
    "cattle": "Cattle",
    "custom_services": "Custom services",
    "fuel_lube_and_electricity": "Fuel, lube, and electricity",
    "general_farm_overhead": "General farm overhead",
    "grazed_feed": "Grazed feed",
    "hired_labor": "Hired labor",
    "homegrown_harvested_feed": "Homegrown harvested feed",
    "interest_on_operating_capital": "Interest on operating capital",
    "marketing": "Marketing",
    "milk_cows": "Milk cows",
    "milk_sold": "Milk sold",
    "opportunity_cost_of_land": "Opportunity cost of land",
    "opportunity_cost_of_unpaid_labor": "Opportunity cost of unpaid labor",
    "other_income": "Other income",
    "other_operating_costs": "Other, operating costs",
    "output_per_cow": "Output per cow",
    "purchased_feed": "Purchased feed",
    "repairs": "Repairs",
    "taxes_and_insurance": "Taxes and insurance",
    "total_allocated_overhead": "Total, allocated overhead",
    "total_costs_listed": "Total, costs listed",
    "total_feed_costs": "Total, feed costs",
    "total_gross_value_of_production": "Total, gross value of production",
    "total_operating_costs": "Total, operating costs",
    "value_of_production_less_operating_costs": (
        "Value of production less operating costs"
    ),
    "value_of_production_less_total_costs_listed": (
        "Value of production less total costs listed"
    ),
    "veterinary_and_medicine": "Veterinary and medicine",
}

SUPERSCRIPT_PATTERN = re.compile(r"[¹²³]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def media_path(report: str) -> str:
    """Build the media path for one report's tidy CSV.

    Parameters
    ----------
    report : str
        Report key from MILK_COST_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the report's CSV file.
    """
    entry = MILK_COST_FILES[report]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def build_url(report: str) -> str:
    """Build the download URL for one report's tidy CSV.

    Parameters
    ----------
    report : str
        Report key from MILK_COST_FILES.

    Returns
    -------
    str
        Full URL of the report's CSV file.
    """
    return f"{BASE_URL}{media_path(report)}"


def clean_item(item: str) -> str:
    """Strip footnote superscripts and normalize whitespace in an item label.

    Parameters
    ----------
    item : str
        Item label as published, e.g. 'Other, operating costs ² '.

    Returns
    -------
    str
        Cleaned label shared by both reports, e.g. 'Other, operating costs'.
    """
    return WHITESPACE_PATTERN.sub(" ", SUPERSCRIPT_PATTERN.sub("", item)).strip()


def decode_csv(content: bytes) -> str:
    """Decode CSV bytes as UTF-8, falling back to cp1252.

    Parameters
    ----------
    content : bytes
        Raw file content; the by-size-of-operation CSV is cp1252-encoded.

    Returns
    -------
    str
        Decoded CSV text.
    """
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("cp1252")


def parse_rows(text: str, report: str) -> list[dict]:
    """Parse one report's tidy CSV text into row records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns Commodity, Category, Item, Units,
        Size, Region, Country, Year, Value, and Survey base year.
    report : str
        Report key from MILK_COST_FILES, deciding whether Region or Size
        carries the report's dimension.

    Returns
    -------
    list[dict]
        Records with category, item, unit, state, size_of_operation, year,
        value, and survey_base_year keys, skipping rows with an empty Value.
    """
    by_state = MILK_COST_FILES[report]["dimension"] == "state"
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        value = (row.get("Value") or "").strip()
        if not value:
            continue
        rows.append(
            {
                "category": (row.get("Category") or "").strip(),
                "item": clean_item(row.get("Item") or ""),
                "unit": (row.get("Units") or "").strip(),
                "state": (row.get("Region") or "").strip() if by_state else None,
                "size_of_operation": (
                    None if by_state else (row.get("Size") or "").strip()
                ),
                "year": int((row.get("Year") or "").strip()),
                "value": float(value),
                "survey_base_year": (row.get("Survey base year") or "").strip(),
            }
        )
    return rows


async def afetch_report(report: str, **kwargs) -> list[dict]:
    """Download and parse one report's tidy CSV through the ERS disk cache.

    Parameters
    ----------
    report : str
        Report key from MILK_COST_FILES.

    Returns
    -------
    list[dict]
        Row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(report), product=PRODUCT_PAGE)
    return parse_rows(decode_csv(content), report)
