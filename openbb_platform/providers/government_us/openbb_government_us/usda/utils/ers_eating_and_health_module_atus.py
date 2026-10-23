"""USDA ERS Eating and Health Module (ATUS) file catalog and long-format parser."""

import csv
from io import StringIO

PRODUCT_PAGE = "data-products/eating-and-health-module-atus"
RELEASE_YEARS = ("2023", "2022")
VALUE_SUFFIXES = (", mean", ", standard error")

EATING_HEALTH_TABLES: dict[str, dict] = {
    "eating_and_drinking_time": {
        "label": "Table 1 - Eating and drinking, associated activities, and"
        + " secondary eating time, age 15+ and 18+",
        "media": {
            "2023": "/media/6532/table-1-average-minutes-per-day-spent-in-and"
            + "-percent-of-us-civilian-population-age-15-and-older-and-age-18-and"
            + "-older-engaged-in-eating-and-drinking-associated-activities-and"
            + "-secondary-eating-on-an-average-day-in-2023.csv",
            "2022": "/media/6516/table-1-time-spent-in-and-percent-of-us-civilian"
            + "-population-engaged-in-eating-and-drinking-associated-activities-and"
            + "-secondary-eating-on-an-average-day-in-2022-age-15-and-older-and-age"
            + "-18-and-older.csv",
        },
    },
    "eating_time_by_subgroup": {
        "label": "Table 2 - Eating and drinking time by age bracket and"
        + " metropolitan status",
        "media": {
            "2023": "/media/6534/table-2-average-minutes-per-day-spent-in-and"
            + "-percent-of-us-civilian-population-engaged-in-eating-and-drinking"
            + "-associated-activities-and-secondary-eating-on-an-average-day-in"
            + "-2023-by-various-subgroups.csv",
            "2022": "/media/6518/table-2-time-spent-in-and-percent-of-us-civilian"
            + "-population-engaged-in-eating-and-drinking-associated-activities-and"
            + "-secondary-eating-on-an-average-day-in-2022-by-various-subgroups.csv",
        },
    },
    "grocery_shopper_and_meal_preparer": {
        "label": "Table 3 - Usual grocery shopper and usual meal preparer in the"
        + " household",
        "media": {
            "2023": "/media/6536/table-3-usual-grocery-shopper-and-usual-meal"
            + "-preparer-in-the-household-on-an-average-day-in-2023.csv",
            "2022": "/media/6520/table-3-usual-grocery-shopper-and-usual-meal"
            + "-preparer-in-the-household-on-an-average-day-in-2022.csv",
        },
    },
    "fast_food_purchases": {
        "label": "Table 4 - Fast-food purchases over the previous 7 days",
        "media": {
            "2023": "/media/6538/table-4-fast-food-purchases-number-of-times-over"
            + "-previous-7-days-on-an-average-day-in-2023-for-us-civilian"
            + "-population-who-purchased-fast-food-in-the-previous-week.csv",
            "2022": "/media/6522/table-4-fast-food-purchases-number-of-times-over"
            + "-previous-7-days-on-an-average-day-in-2022-for-us-civilian"
            + "-population-who-purchased-fast-food-in-the-previous-week.csv",
        },
    },
    "activities_by_grocery_responsibility": {
        "label": "Table 5 - Selected activities by grocery-shopping"
        + " responsibility, age 18+",
        "media": {
            "2023": "/media/6540/table-5-average-minutes-per-day-spent-in-selected"
            + "-activities-by-how-much-of-the-grocery-shopping-the-interviewee-is"
            + "-responsible-for-on-an-average-day-in-2023-age-18-and-older.csv",
            "2022": "/media/6524/table-5-average-time-spent-in-selected-activities"
            + "-by-how-much-of-the-grocery-shopping-the-interviewee-is-responsible"
            + "-for-on-an-average-day-in-2022-age-18-and-older.csv",
        },
    },
    "activities_by_meal_prep_responsibility": {
        "label": "Table 6 - Selected activities by meal-preparation"
        + " responsibility, age 18+",
        "media": {
            "2023": "/media/6542/table-6-average-minutes-per-day-spent-in-selected"
            + "-activities-by-how-much-of-the-meal-preparation-the-interviewee-is"
            + "-responsible-for-on-an-average-day-in-2023-age-18-and-older.csv",
            "2022": "/media/6526/table-6-average-time-spent-in-selected-activities"
            + "-by-how-much-of-the-meal-preparation-the-interviewee-is-responsible"
            + "-for-on-an-average-day-in-2022-age-18-and-older.csv",
        },
    },
    "activities_by_food_security": {
        "label": "Table 7 - Selected food-related activities by food-security"
        + " subgroups, age 18+",
        "media": {
            "2023": "/media/6544/table-7-average-minutes-per-day-spent-in-selected"
            + "-food-related-and-other-activities-on-an-average-day-in-2023-age-18"
            + "-and-older.csv",
            "2022": "/media/6528/table-7-average-minutes-per-day-spent-in-selected"
            + "-food-related-and-other-activities-on-an-average-day-in-2022-age-18"
            + "-and-older.csv",
        },
    },
    "activities_by_bmi_group": {
        "label": "Table 8 - Selected food-related activities by BMI group,"
        + " age 20+",
        "media": {
            "2023": "/media/6546/table-8-average-minutes-per-day-spent-in-selected"
            + "-food-related-and-other-activities-on-an-average-day-in-2023-age-20"
            + "-and-older.csv",
            "2022": "/media/6530/table-8-average-minutes-per-day-spent-in-selected"
            + "-food-related-and-other-activities-on-an-average-day-in-2022-age-20"
            + "-and-older.csv",
        },
    },
}


def _to_float(raw: str) -> float | None:
    """Coerce a source cell to a float, mapping blanks and non-numerics to None."""
    text = raw.strip()
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one wide table CSV into long-format cell records.

    Parameters
    ----------
    text : str
        Decoded text of the table's CSV.
    table : str
        Table slug from EATING_HEALTH_TABLES.

    Returns
    -------
    list[dict]
        One record per data-row and value-column cell, carrying the leading
        dimensions mapped to category, subgroup, and measure_type, the value
        column header and ordinal, the source row ordinal, and the float value
        with blank or suppressed cells coerced to None. The constant leading
        title column is dropped; dimension columns are the non-value columns and
        value columns are those whose header ends in ', mean' or ', standard
        error'.
    """
    reader = csv.reader(StringIO(text))
    header = next(reader, None)
    if not header:
        return []
    dim_indices: list[int] = []
    value_columns: list[tuple[int, str]] = []
    for index, name in enumerate(header):
        if index == 0:
            continue
        if name.strip().endswith(VALUE_SUFFIXES):
            value_columns.append((index, name))
        else:
            dim_indices.append(index)
    records: list[dict] = []
    row_ord = 0
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        dims = [(row[i].strip() if i < len(row) else "") for i in dim_indices]
        category = dims[0] if len(dims) > 0 and dims[0] else None
        subgroup = dims[1] if len(dims) > 1 and dims[1] else None
        measure_type = dims[2] if len(dims) > 2 and dims[2] else None
        for series_ord, (index, name) in enumerate(value_columns):
            raw = row[index] if index < len(row) else ""
            records.append(
                {
                    "table": table,
                    "row_ord": row_ord,
                    "category": category,
                    "subgroup": subgroup,
                    "measure_type": measure_type,
                    "series": name,
                    "series_ord": series_ord,
                    "value": _to_float(raw),
                }
            )
        row_ord += 1
    return records


async def afetch_table(table: str, year: str, **kwargs) -> list[dict]:
    """Download and parse one table's release-year CSV through the ERS cache.

    Parameters
    ----------
    table : str
        Table slug from EATING_HEALTH_TABLES.
    year : str
        Release year from RELEASE_YEARS.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    media_path = EATING_HEALTH_TABLES[table]["media"][year]
    content = await afetch_ers_file(media_path, product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
