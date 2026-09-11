"""USDA ERS Food Expenditure Series file catalog and long-format parser."""

import csv
from io import StringIO

PRODUCT_PAGE = "data-products/food-expenditure-series"

MONTH_ORDER: dict[str, int] = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

STATES: tuple[str, ...] = (
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
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
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
)

FOOD_AND_ALCOHOL_LABELS: tuple[str, ...] = (
    "Food sales at grocery stores",
    "Food sales at convenience stores",
    "Food sales at other food stores",
    "Food sales at warehouse clubs and supercenters",
    "Food sales at other stores and foodservice",
    "Direct food selling by farmers, manufacturers, and wholesalers",
    "Home food production and donations",
    "Total food-at-home expenditures",
    "Food sales at full-service restaurants",
    "Food sales at limited-service restaurants",
    "Food sales at drinking places",
    "Food sales at hotels and motels",
    "Food sales at retail stores",
    "Food sales at recreational places",
    "Food sales at schools and colleges",
    "Food sales at other establishments, not elsewhere classified",
    "Food furnished and donated",
    "Total food-away-from-home expenditures",
    "Alcohol sales at liquor stores",
    "Alcohol-at-home sales at food stores",
    "Alcohol-at-home sales at other establishments, not elsewhere classified",
    "Total alcohol-at-home sales",
    "Alcohol sales at eating and drinking places",
    "Alcohol sales at hotels and motels",
    "Alcohol-away-from-home sales at other establishments, not elsewhere classified",
    "Total alcohol-away-from-home sales",
)

FOOD_EXPENDITURE_FILES: dict[str, dict] = {
    "food_and_alcohol": {
        "label": "Food and alcohol expenditures, by all purchasers",
        "dims": ("year",),
        "measure_selects_file": True,
        "taxes_selects_file": True,
        "files": {
            (
                "nominal",
                "with",
            ): "/media/5188/nominal-food-and-alcohol-expenditures-with-taxes-and-tips-for-all-purchasers.csv",
            (
                "nominal",
                "without",
            ): "/media/5190/nominal-food-and-alcohol-expenditures-without-taxes-and-tips-for-all-purchasers.csv",
            (
                "constant",
                "with",
            ): "/media/5192/constant-dollar-food-and-alcohol-expenditures-with-taxes-and-tips-for-all-purchasers.csv",
            (
                "constant",
                "without",
            ): "/media/5194/constant-dollar-food-and-alcohol-expenditures-without-taxes-and-tips-for-all-purchasers.csv",
        },
        "canonical_labels": FOOD_AND_ALCOHOL_LABELS,
    },
    "by_final_purchaser": {
        "label": "Food expenditures, by final purchaser",
        "dims": ("year",),
        "measure_selects_file": False,
        "taxes_selects_file": False,
        "files": {(): "/media/5196/food-expenditures-by-final-purchaser.csv"},
        "canonical_labels": None,
    },
    "normalized": {
        "label": "Normalized food expenditures and income shares",
        "dims": ("year",),
        "measure_selects_file": False,
        "taxes_selects_file": False,
        "files": {
            (): "/media/5198/normalized-food-expenditures-by-all-purchasers-and-household-final-users.csv"
        },
        "canonical_labels": None,
    },
    "monthly": {
        "label": "Monthly food sales",
        "dims": ("year", "month"),
        "measure_selects_file": False,
        "taxes_selects_file": False,
        "files": {
            (): "/media/5202/monthly-sales-of-food-with-taxes-and-tips-for-all-purchasers.csv"
        },
        "canonical_labels": None,
    },
    "monthly_by_outlet": {
        "label": "Monthly food sales, by outlet type",
        "dims": ("year", "month"),
        "measure_selects_file": False,
        "taxes_selects_file": False,
        "files": {
            (): "/media/5200/monthly-sales-of-food-with-taxes-and-tips-for-all-purchasers-by-outlet-type.csv"
        },
        "canonical_labels": None,
    },
    "state": {
        "label": "State food sales",
        "dims": ("year", "state"),
        "measure_selects_file": False,
        "taxes_selects_file": True,
        "files": {
            (
                "with",
            ): "/media/5204/state-food-sales-with-taxes-and-tips-for-all-purchasers.csv",
            (
                "without",
            ): "/media/5206/state-food-sales-without-taxes-and-tips-for-all-purchasers.csv",
        },
        "canonical_labels": None,
    },
    "state_per_capita": {
        "label": "State food sales, per capita",
        "dims": ("year", "state"),
        "measure_selects_file": False,
        "taxes_selects_file": True,
        "files": {
            (
                "with",
            ): "/media/5208/state-food-sales-per-capita-with-taxes-and-tips-for-all-purchasers.csv",
            (
                "without",
            ): "/media/5210/state-food-sales-per-capita-without-taxes-and-tips-for-all-purchasers.csv",
        },
        "canonical_labels": None,
    },
}


def resolve_media_path(table: str, measure: str, taxes: str) -> str:
    """Resolve a table's media path from the measure and tax-treatment selectors.

    Parameters
    ----------
    table : str
        Table key from FOOD_EXPENDITURE_FILES.
    measure : str
        'nominal' or 'constant'; selects the file only when the table splits
        its measures across files.
    taxes : str
        'with' or 'without'; selects the file only when the table splits its
        tax treatment across files.

    Returns
    -------
    str
        The media path of the selected CSV.
    """
    config = FOOD_EXPENDITURE_FILES[table]
    key: list[str] = []
    if config["measure_selects_file"]:
        key.append(measure)
    if config["taxes_selects_file"]:
        key.append(taxes)
    return config["files"][tuple(key)]


def clean_header(header: str) -> tuple[str, str | None]:
    """Split a verbose value-column header into a clean label and its measure.

    Parameters
    ----------
    header : str
        Column header as published, e.g. 'Food-at-home sales with taxes and
        tips (millions of nominal U.S. dollars)'.

    Returns
    -------
    tuple[str, str | None]
        The category label with the tax phrase and unit removed, and the
        measure the unit encodes: 'nominal', 'constant', or None for a
        percentage share.
    """
    text = header.strip()
    cut = text.find(" (")
    label = text[:cut] if cut != -1 else text
    unit = text[cut:].casefold() if cut != -1 else ""
    for phrase in (" with taxes and tips", " without taxes and tips"):
        if label.endswith(phrase):
            label = label[: -len(phrase)]
    label = label.strip()
    if "percentage" in unit:
        return label, None
    if "constant" in unit:
        return label, "constant"
    if "nominal" in unit:
        return label, "nominal"
    return label, None


def extract_unit(header: str) -> str:
    """Return a value-column header's parenthetical unit text, or '' when none.

    Parameters
    ----------
    header : str
        Column header as published, e.g. 'Food-at-home sales with taxes and
        tips (millions of nominal U.S. dollars)'.

    Returns
    -------
    str
        The unit inside the trailing parentheses with the outer pair removed,
        e.g. 'millions of nominal U.S. dollars'; empty when the header has no
        parenthetical.
    """
    text = header.strip()
    cut = text.find(" (")
    if cut == -1:
        return ""
    return text[cut + 2 :].rstrip().removesuffix(")")


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's wide CSV text into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the selected file.
    table : str
        Table key from FOOD_EXPENDITURE_FILES.

    Returns
    -------
    list[dict]
        One record per non-blank value cell, carrying the integer year, the
        optional month and state dimensions, the category label, the measure
        the column encodes, the source unit text, and the numeric value. Cells
        with a blank or non-numeric value, or rows with a non-numeric year,
        are skipped.
    """
    config = FOOD_EXPENDITURE_FILES[table]
    dims = config["dims"]
    canonical = config["canonical_labels"]
    rows = list(csv.reader(StringIO(text)))
    if not rows:
        return []
    header = rows[0]
    n_dims = len(dims)
    specs: list[tuple[int, str, str | None, str]] = []
    for offset, col in enumerate(range(n_dims, len(header))):
        unit = extract_unit(header[col])
        if canonical is not None:
            specs.append((col, canonical[offset], None, unit))
        else:
            label, measure = clean_header(header[col])
            specs.append((col, label, measure, unit))
    records: list[dict] = []
    for row in rows[1:]:
        if not row or not row[0][:4].isdigit():
            continue
        year = int(row[0][:4])
        month = row[1].strip() or None if "month" in dims else None
        state = row[1].strip() or None if "state" in dims else None
        for col, label, measure, unit in specs:
            raw = (row[col] if col < len(row) else "").strip()
            try:
                value = float(raw)
            except ValueError:
                continue
            records.append(
                {
                    "year": year,
                    "month": month,
                    "state": state,
                    "category": label,
                    "measure": measure,
                    "unit": unit,
                    "value": value,
                }
            )
    return records


async def afetch_table(table: str, measure: str, taxes: str) -> list[dict]:
    """Download and parse one table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from FOOD_EXPENDITURE_FILES.
    measure : str
        'nominal' or 'constant'.
    taxes : str
        'with' or 'without'.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    path = resolve_media_path(table, measure, taxes)
    content = await afetch_ers_file(path, product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
