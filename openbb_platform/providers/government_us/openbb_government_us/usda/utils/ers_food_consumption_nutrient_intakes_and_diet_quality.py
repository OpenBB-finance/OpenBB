"""USDA ERS Food Consumption, Nutrient Intakes, and Diet Quality catalog and parsers."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/food-consumption-nutrient-intakes-and-diet-quality"

TABLE_FILES: dict[str, str] = {
    "1_sample_sizes": "/media/5463/table-1-sample-sizes-by-population-subgroups-for-each-survey-cycle.csv",
    "2_nutrient_intake": "/media/5465/table-2-daily-nutrient-intake-by-food-source-1977-2018.csv",
    "3_nutrient_intake_share": "/media/5467/table-3-daily-nutrient-intake-and-share-by-food-source-1977-2018.csv",
    "4_nutrient_density": "/media/5469/table-4-nutrient-density-by-food-source-1977-2018.csv",
    "5_food_group_intake": "/media/5471/table-5-intakes-of-food-group-by-food-source-1977-2018.csv",
    "6_food_group_intake_share": "/media/5473/table-6-daily-food-equivalent-group-intake-and-share-by-food-source-1977-2018.csv",
    "7_food_group_density": "/media/5475/table-7-density-of-food-group-by-food-source-1977-2018.csv",
    "8_recommended_vs_actual_density": "/media/5477/table-8-the-2020-2025-recommended-and-2017-2018-nutrient-and-food-group-density.csv",
}

TABLE_LABELS: dict[str, str] = {
    "1_sample_sizes": "Table 1 - Sample sizes by population subgroup",
    "2_nutrient_intake": "Table 2 - Daily nutrient intake by food source",
    "3_nutrient_intake_share": "Table 3 - Daily nutrient intake and share by food source",
    "4_nutrient_density": "Table 4 - Nutrient density by food source",
    "5_food_group_intake": "Table 5 - Food group intake by food source",
    "6_food_group_intake_share": "Table 6 - Food group intake and share by food source",
    "7_food_group_density": "Table 7 - Food group density by food source",
    "8_recommended_vs_actual_density": "Table 8 - Recommended vs. actual density (2017-2018)",
}

DEFAULT_TABLE = "2_nutrient_intake"
SAMPLE_TABLE = "1_sample_sizes"
RECOMMENDED_TABLE = "8_recommended_vs_actual_density"
NUTRIENT_TABLES = frozenset(
    {"2_nutrient_intake", "3_nutrient_intake_share", "4_nutrient_density"}
)
FOOD_GROUP_TABLES = frozenset(
    {"5_food_group_intake", "6_food_group_intake_share", "7_food_group_density"}
)
INTAKE_TABLES = NUTRIENT_TABLES | FOOD_GROUP_TABLES

SURVEY_CYCLES: tuple[str, ...] = (
    "1977-1978",
    "1989-1991",
    "1994-1998",
    "2003-2004",
    "2005-2006",
    "2007-2008",
    "2009-2010",
    "2011-2012",
    "2013-2014",
    "2015-2016",
    "2017-2018",
)

FOOD_SOURCES: tuple[str, ...] = (
    "Total",
    "FAH",
    "FAFH",
    "FAFH: Restaurant",
    "FAFH: Fast food",
    "FAFH: School",
    "FAFH: Others",
)

DEMOGRAPHICS: tuple[str, ...] = (
    "US consumers aged 2 and above",
    "Sex - Males",
    "Sex - Females",
    "Ages 2-19",
    "Ages 20-64",
    "Ages 65 and above",
    "Cohort - Boys age 2-19",
    "Cohort - Girls age 2-19",
    "Cohort - Men age 20 and above",
    "Cohort - Women age 20 and above",
    "Income - low-income households",
    "Income - mid-income households",
    "Income - high-income households",
    "Race - Non-Hispanic White",
    "Race - Non-Hispanic Black",
    "Race - Hispanic",
    "Race - Other racial & ethnic",
    "Edu. - Less than high school",
    "Edu. - High school degree",
    "Edu. - College attended",
)
DEFAULT_DEMOGRAPHIC = "US consumers aged 2 and above"

STATISTIC_CHOICES: dict[str, str] = {"mean": "Mean", "se_of_mean": "SE of mean"}
DEFAULT_STATISTIC = "mean"

RECOMMENDED_COLUMNS: tuple[tuple[str, str], ...] = (
    (
        "Recommended density*:Nutrient or food group amount per 1,000 calories",
        "Recommended",
    ),
    (
        "2017-2018 Actual density-Total-Nutrient or food group amount per 1,000 calories",
        "Actual: Total",
    ),
    (
        "2017-2018 Actual density-FAH-Nutrient or food group amount per 1,000 calories",
        "Actual: FAH",
    ),
    (
        "2017-2018 Actual density-FAFH-Nutrient or food group amount per 1,000 calories",
        "Actual: FAFH",
    ),
    (
        "2017-2018 Actual density-Restaurant-Nutrient or food group amount per 1,000 calories",
        "Actual: Restaurant",
    ),
    (
        "2017-2018 Actual density-Fast food-Nutrient or food group amount per 1,000 calories",
        "Actual: Fast food",
    ),
    (
        "2017-2018 Actual density-School-Nutrient or food group amount per 1,000 calories",
        "Actual: School",
    ),
    (
        "2017-2018 density as a ratio of the recommended density-Total-Ratio of actual density to the recommended density",
        "Ratio: Total",
    ),
    (
        "2017-2018 density as a ratio of the recommended density-FAH-Ratio of actual density to the recommended density",
        "Ratio: FAH",
    ),
    (
        "2017-2018 density as a ratio of the recommended density-FAFH-Ratio of actual density to the recommended density",
        "Ratio: FAFH",
    ),
    (
        "2017-2018 density as a ratio of the recommended density-Restaurant-Ratio of actual density to the recommended density",
        "Ratio: Restaurant",
    ),
    (
        "2017-2018 density as a ratio of the recommended density-Fast food-Ratio of actual density to the recommended density",
        "Ratio: Fast food",
    ),
    (
        "2017-2018 density as a ratio of the recommended density-School-Ratio of actual density to the recommended density",
        "Ratio: School",
    ),
)
RECOMMENDED_COLUMN_MAP: dict[str, str] = {
    raw: label for raw, label in RECOMMENDED_COLUMNS
}
RECOMMENDED_COLUMN_ORDER: tuple[str, ...] = tuple(
    label for _, label in RECOMMENDED_COLUMNS
)

UNIT_ALIASES: dict[str, str] = {"Grams per 1,000": "Grams per 1,000 calories"}


def item_column(table: str) -> str:
    """Return the CSV column holding the row label for an intake table.

    Parameters
    ----------
    table : str
        Table key from TABLE_FILES.

    Returns
    -------
    str
        'Nutrient' for the nutrient tables, 'Food group' for the food-group
        tables.
    """
    return "Nutrient" if table in NUTRIENT_TABLES else "Food group"


def normalize_unit(measurement: str | None) -> str | None:
    """Normalize a Measurement label to a canonical unit or None.

    Parameters
    ----------
    measurement : str | None
        Raw Measurement cell, possibly with trailing spaces or a truncated
        'per 1,000' variant.

    Returns
    -------
    str | None
        The trimmed, canonical unit label, or None when the cell is empty.
    """
    unit = (measurement or "").strip()
    if not unit:
        return None
    return UNIT_ALIASES.get(unit, unit)


def split_cycle_variable(value: str | None) -> tuple[str, str]:
    """Split a 'Survey years:Variable' cell into its cycle and statistic.

    Parameters
    ----------
    value : str | None
        Cell such as '1977-1978-Mean' or '2017-2018-SE of mean'.

    Returns
    -------
    tuple[str, str]
        The survey cycle and the statistic label.
    """
    cycle, _, variable = (value or "").rpartition("-")
    return cycle.strip(), variable.strip()


def to_number(raw: str | None) -> float | None:
    """Coerce a source cell to a float, or None when blank or non-numeric.

    Parameters
    ----------
    raw : str | None
        Raw Value cell; blank, suppressed, and corrupted cells return None.

    Returns
    -------
    float | None
        The parsed value, or None.
    """
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def to_number_or_text(raw: str | None) -> float | str | None:
    """Coerce a source cell to a float, keeping a non-numeric range as text.

    Parameters
    ----------
    raw : str | None
        Raw Value cell; a numeric cell returns a float, a range such as
        '20-35' returns the raw string, a blank cell returns None.

    Returns
    -------
    float | str | None
        The parsed value.
    """
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return text


def parse_sample_sizes(text: str) -> list[dict]:
    """Parse the Table 1 sample-size CSV into long records.

    Parameters
    ----------
    text : str
        Decoded CSV text with Demographics, Survey years, and Sample size.

    Returns
    -------
    list[dict]
        Records with the demographic subgroup, survey cycle, integer sample
        size or None, and source order.
    """
    records: list[dict] = []
    for order, row in enumerate(csv.DictReader(StringIO(text))):
        size = (row.get("Sample size") or "").strip()
        records.append(
            {
                "demographic": (row.get("Demographics") or "").strip(),
                "cycle": (row.get("Survey years") or "").strip(),
                "value": int(size) if size.isdigit() else None,
                "order": order,
            }
        )
    return records


def parse_intake(text: str, table: str) -> list[dict]:
    """Parse an intake table (Tables 2-7) into long records.

    Parameters
    ----------
    text : str
        Decoded CSV text with the item, Food source, Measurement, Survey
        years:Variable, Value, and Demographics columns.
    table : str
        Table key from INTAKE_TABLES.

    Returns
    -------
    list[dict]
        Records with the item, food source, unit, demographic subgroup,
        statistic, survey cycle, numeric value or None, and source order.
    """
    column = item_column(table)
    records: list[dict] = []
    for order, row in enumerate(csv.DictReader(StringIO(text))):
        cycle, statistic = split_cycle_variable(row.get("Survey years:Variable"))
        records.append(
            {
                "item": (row.get(column) or "").strip(),
                "food_source": (row.get("Food source") or "").strip(),
                "units": normalize_unit(row.get("Measurement")),
                "demographics": (row.get("Demographics") or "").strip(),
                "statistic": statistic,
                "cycle": cycle,
                "value": to_number(row.get("Value")),
                "order": order,
            }
        )
    return records


def parse_recommended(text: str) -> list[dict]:
    """Parse the Table 8 recommended-versus-actual CSV into long records.

    Parameters
    ----------
    text : str
        Decoded CSV text with Nutrient or Food group, Variable, and Value.

    Returns
    -------
    list[dict]
        Records with the item, the wide column label, the numeric or text
        value, and source order; rows whose Variable is unmapped are skipped.
    """
    records: list[dict] = []
    for order, row in enumerate(csv.DictReader(StringIO(text))):
        variable = (row.get("Variable") or "").strip()
        column = RECOMMENDED_COLUMN_MAP.get(variable)
        if column is None:
            continue
        records.append(
            {
                "item": (row.get("Nutrient or Food group") or "").strip(),
                "column": column,
                "value": to_number_or_text(row.get("Value")),
                "order": order,
            }
        )
    return records


def parse_table(text: str, table: str) -> list[dict]:
    """Dispatch a table's CSV text to its long-format parser.

    Parameters
    ----------
    text : str
        Decoded CSV text.
    table : str
        Table key from TABLE_FILES.

    Returns
    -------
    list[dict]
        Long-format records for the table.
    """
    if table == SAMPLE_TABLE:
        return parse_sample_sizes(text)
    if table == RECOMMENDED_TABLE:
        return parse_recommended(text)
    return parse_intake(text, table)


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from TABLE_FILES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(TABLE_FILES[table], product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
