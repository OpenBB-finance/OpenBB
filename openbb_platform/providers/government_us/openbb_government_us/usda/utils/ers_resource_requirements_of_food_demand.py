"""USDA ERS Resource Requirements of Food Demand catalog and long parser."""

import csv
import io
import zipfile
from collections import OrderedDict

PRODUCT_PAGE = "data-products/resource-requirements-of-food-demand"
MEDIA_PATH = "/media/7066/resource-requirements-of-food-demand.zip"
CSV_MEMBER = "resource-requirements-food-demand-data.csv"

TABLES: "OrderedDict[str, str]" = OrderedDict(
    [
        ("Xf0000", "Food and food-related"),
        ("Xf1000", "Food"),
        ("Xf1100", "Food at home"),
        ("Xf1101", "Cereals"),
        ("Xf1102", "Bakery products"),
        ("Xf1103", "Beef"),
        ("Xf1104", "Pork"),
        ("Xf1105", "Other meats"),
        ("Xf1106", "Poultry"),
        ("Xf1107", "Fish and seafood"),
        ("Xf1108", "Fresh milk"),
        ("Xf1109", "Processed dairy products"),
        ("Xf1110", "Fresh eggs"),
        ("Xf1111", "Processed eggs"),
        ("Xf1112", "Fats and oils"),
        ("Xf1113", "Fresh fruits"),
        ("Xf1114", "Fresh vegetables"),
        ("Xf1115", "Canned, frozen, and dried fruits and vegetables"),
        ("Xf1116", "Sugar and sweets"),
        ("Xf1117", "Snack foods"),
        ("Xf1118", "Frozen prepared foods"),
        ("Xf1119", "Processed fruit and vegetable canning and drying"),
        ("Xf1120", "Seasonings, sauces, and dressings"),
        ("Xf1121", "Dry, condensed, and evaporated dairy and non-dairy products"),
        ("Xf1122", "Tree nuts and peanuts"),
        ("Xf1123", "Fresh cut produce plus grab-and-go foods"),
        ("Xf1124", "Miscellaneous foods and ingredients"),
        ("Xf1125", "Fruit and vegetable juices"),
        ("Xf1126", "Food consumed on farms"),
        ("Xf1127", "Coffee, tea, and beverage materials"),
        ("Xf1128", "Soft drinks and bottled water"),
        ("Xf1200", "Food away from home"),
        ("Xf1201", "Food at full-service restaurants"),
        ("Xf1202", "Food at limited-service restaurants"),
        ("Xf1203", "Food at other food and drinking places"),
        ("Xf1204", "Food at schools and colleges"),
        ("Xf1205", "Food furnished to employees (including military)"),
        ("Xf1206", "Institutional and employer furnished meals plus food assistance"),
        (
            "Xf1207",
            "Food and non-alcoholic beverages at work (per diem and expensing)",
        ),
        ("Xf2000", "Alcohol"),
        ("Xf2100", "Alcohol at home"),
        ("Xf2101", "Beer"),
        ("Xf2102", "Wine"),
        ("Xf2103", "Spirits"),
        ("Xf2200", "Alcohol away from home"),
        ("Xf2201", "Alcohol at full-service restaurants"),
        ("Xf2202", "Alcohol at limited-service restaurants"),
        ("Xf2203", "Alcohol at other food and drinking places"),
        ("Xf3000", "Households"),
    ]
)

ENERGY_SOURCE_COLUMNS: dict[str, str] = {
    "TOTAL": "energy_total",
    "PA": "energy_pa",
    "NG": "energy_ng",
    "ES": "energy_es",
    "CL": "energy_cl",
    "LO": "energy_lo",
    "BF": "energy_bf",
    "WW": "energy_ww",
    "WD": "energy_wd",
    "HY": "energy_hy",
    "GE": "energy_ge",
    "SO": "energy_so",
    "WY": "energy_wy",
    "CC": "energy_cc",
    "SF": "energy_sf",
}

MEASURE_COLUMNS: list[str] = [
    "employment",
    "water",
    "energy_total",
    "energy_pa",
    "energy_ng",
    "energy_es",
    "energy_cl",
    "energy_lo",
    "energy_bf",
    "energy_ww",
    "energy_wd",
    "energy_hy",
    "energy_ge",
    "energy_so",
    "energy_wy",
    "energy_cc",
    "energy_sf",
]


def measure_column(resource: str, source_code: str) -> str | None:
    """Map a resource and source code to a wide measure-column name.

    Parameters
    ----------
    resource : str
        Resource dimension, one of 'Employment', 'Water', or 'Energy'.
    source_code : str
        Source code within the resource; 'TOTAL' or a two-letter energy
        source such as 'PA' or 'NG'.

    Returns
    -------
    str | None
        The wide-column name, or None when the resource and source do not
        map to a known measure column.
    """
    name = (resource or "").strip()
    code = (source_code or "").strip().upper()
    if name == "Employment":
        column = "employment"
    elif name == "Water":
        column = "water"
    elif name == "Energy":
        column = ENERGY_SOURCE_COLUMNS.get(code)
    else:
        column = None
    return column if column in MEASURE_COLUMNS else None


def parse_table(text: str, table: str) -> list[dict]:
    """Parse the linearized CSV into one table's long-format observations.

    Parameters
    ----------
    text : str
        Decoded text of the resource-requirements data CSV.
    table : str
        Table number to keep, e.g. 'Xf0000'.

    Returns
    -------
    list[dict]
        Records carrying the table number, integer year, the supply-chain
        stage label and ordinal, the wide measure-column name, the numeric
        value, and source order. Rows outside the table, with an unmapped
        resource, a blank year, or a non-numeric value are skipped.
    """
    records: list[dict] = []
    for order, row in enumerate(csv.DictReader(io.StringIO(text))):
        if (row.get("TableNumber") or "").strip() != table:
            continue
        column = measure_column(row.get("Resource", ""), row.get("SourceCode", ""))
        if column is None:
            continue
        raw_value = (row.get("Data") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_raw = (row.get("Year") or "").strip()
        if not (len(year_raw) == 4 and year_raw.isdigit()):
            continue
        try:
            stage_ord = int((row.get("SupplyChainStageNumber") or "").strip())
        except ValueError:
            stage_ord = 0
        records.append(
            {
                "table": table,
                "year": int(year_raw),
                "stage": (row.get("SupplyChainStageDescription") or "").strip() or None,
                "stage_ord": stage_ord,
                "column": column,
                "value": value,
            }
        )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table number from TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    text = (
        zipfile.ZipFile(io.BytesIO(content))
        .read(CSV_MEMBER)
        .decode("utf-8-sig", errors="replace")
    )
    return parse_table(text, table)
