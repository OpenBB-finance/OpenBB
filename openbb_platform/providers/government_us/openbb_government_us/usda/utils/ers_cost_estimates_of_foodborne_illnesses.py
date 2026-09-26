"""USDA ERS Cost Estimates of Foodborne Illnesses file catalog and wide parser."""

import csv
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

PRODUCT_PAGE = "data-products/cost-estimates-of-foodborne-illnesses"

COST_ESTIMATES_TABLES: dict[str, dict] = {
    "cases_and_cost": {
        "media_path": "/media/5317/cases-total-cost-and-per-case-cost-by-pathogen.csv",
        "label": "Cases, total cost, and per-case cost, by pathogen",
        "value_columns": (
            {
                "source": "Mean number of cases",
                "label": "Mean number of cases",
                "kind": "int",
            },
            {
                "source": "Mean total cost (millions)",
                "label": "Mean total cost (2023 $ millions)",
                "kind": "float",
            },
            {
                "source": " Mean per-case cost",
                "label": "Mean per-case cost (2023 $)",
                "kind": "float",
            },
        ),
    },
    "health_outcome_cost": {
        "media_path": "/media/5319/mean-cost-for-specific-health-outcomes-by-pathogen.csv",
        "label": "Mean cost for specific health outcomes, by pathogen",
        "value_columns": (
            {
                "source": "No physician's visit mean",
                "label": "No physician's visit",
                "kind": "float",
            },
            {
                "source": "No physician's visit CrI",
                "label": "No physician's visit (CrI)",
                "kind": "text",
            },
            {
                "source": "Physician's visit only mean",
                "label": "Physician's visit only",
                "kind": "float",
            },
            {
                "source": "Physician's visit only CrI",
                "label": "Physician's visit only (CrI)",
                "kind": "text",
            },
            {
                "source": "Hospitalized, recovered",
                "label": "Hospitalized, recovered",
                "kind": "float",
            },
            {
                "source": "Hospitalized, recovered Crl",
                "label": "Hospitalized, recovered (CrI)",
                "kind": "text",
            },
            {
                "source": "Hospitalized, died",
                "label": "Hospitalized, died",
                "kind": "float",
            },
            {
                "source": "Hospitalized, died Crl",
                "label": "Hospitalized, died (CrI)",
                "kind": "text",
            },
            {
                "source": "Chronic outcomes",
                "label": "Chronic outcomes",
                "kind": "float",
            },
            {
                "source": "Chronic outcomes Crl",
                "label": "Chronic outcomes (CrI)",
                "kind": "text",
            },
            {
                "source": "Total",
                "label": "Total",
                "kind": "float",
            },
            {
                "source": "Total Crl",
                "label": "Total (CrI)",
                "kind": "text",
            },
        ),
    },
}


def coerce_value(raw: str | None, kind: str):
    """Coerce a raw cell to an int, float, stripped text, or None.

    Parameters
    ----------
    raw : str | None
        The raw cell value.
    kind : str
        The target kind: 'int', 'float', or 'text'.

    Returns
    -------
    int | float | str | None
        The coerced value; None for empty cells and placeholder tokens.
    """
    value = (raw or "").strip()
    if not value or is_null_token(value):
        return None
    if kind == "text":
        return value
    number = float(value)
    return int(number) if kind == "int" else number


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one cost-estimates CSV into wide per-pathogen records.

    Parameters
    ----------
    text : str
        Decoded text of the selected table's CSV.
    table : str
        Table slug from COST_ESTIMATES_TABLES.

    Returns
    -------
    list[dict]
        One record per pathogen, carrying the source order, table slug,
        pathogen classification, pathogen name, and the table's
        human-labeled value columns. Rows without a pathogen are skipped.
    """
    config = COST_ESTIMATES_TABLES[table]
    records: list[dict] = []
    for order, row in enumerate(csv.DictReader(StringIO(text))):
        pathogen = (row.get("Pathogen") or "").strip()
        if not pathogen:
            continue
        record: dict = {
            "_order": order,
            "_table": table,
            "pathogen_classification": (
                row.get("Pathogen classification") or ""
            ).strip()
            or None,
            "pathogen": pathogen,
        }
        for column in config["value_columns"]:
            record[column["label"]] = coerce_value(
                row.get(column["source"]), column["kind"]
            )
        records.append(record)
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one cost-estimates table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table slug from COST_ESTIMATES_TABLES.

    Returns
    -------
    list[dict]
        Wide per-pathogen records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    media_path = COST_ESTIMATES_TABLES[table]["media_path"]
    content = await afetch_ers_file(media_path, product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
