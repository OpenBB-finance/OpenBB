"""USDA ERS Wheat Data file catalog and long-format parsers."""

import csv
import zipfile
from io import BytesIO, StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/wheat-data"

ALL_YEARS_ZIP = "/media/5709/wheat-data-all-years.zip"
QUARTERLY_ZIP = "/media/5708/wheat-by-class-quarterly.zip"

CLASS_CANON: dict[str, str] = {
    "all wheat": "All wheat",
    "durum": "Durum",
    "hard red spring": "Hard red spring",
    "hard red winter": "Hard red winter",
    "hard white": "Hard white",
    "soft red winter": "Soft red winter",
    "soft white": "Soft white",
    "white": "White",
    "rye": "Rye",
}

WHEAT_DATA_FILES: dict[str, dict] = {
    "wheat_acreage_production_yield_price": {
        "label": "U.S. wheat: acreage, production, yield, and farm price",
        "media": ALL_YEARS_ZIP,
        "member": "01_Wheat_US_Acreage_Production_Yield_and_Farm_Price.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc2",
        "value_name": None,
        "row_dims": (("Commodity_Desc2", "wheat_class"),),
    },
    "rye_acreage_production_yield_price": {
        "label": "U.S. rye: acreage, production, yield, and farm price",
        "media": ALL_YEARS_ZIP,
        "member": "02_Rye_US_Acreage_Production_Yield_and_Farm_Price.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc2",
        "value_name": None,
        "row_dims": (("Commodity_Desc2", "wheat_class"),),
    },
    "world_supply_and_disappearance": {
        "label": "World and U.S. wheat supply and disappearance",
        "media": ALL_YEARS_ZIP,
        "member": "03_04_World_wheat_supply_and_disappearance.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": None,
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (),
    },
    "us_supply_and_disappearance": {
        "label": "U.S. wheat supply and disappearance, by class",
        "media": ALL_YEARS_ZIP,
        "member": "05_11_US_Supply_And_Disappearance.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (("Commodity_Desc2", "wheat_class"),),
    },
    "rye_supply_and_disappearance": {
        "label": "U.S. rye supply and disappearance",
        "media": ALL_YEARS_ZIP,
        "member": "12_Rye_US_Supply_And_Disappearance.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (),
    },
    "food_use": {
        "label": "U.S. wheat food use",
        "media": ALL_YEARS_ZIP,
        "member": "13_16_Food_Use.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Commodity_Desc2",
        "value_name": None,
        "row_dims": (("Commodity_Desc", "commodity_group"),),
    },
    "government_and_private_stocks": {
        "label": "Government and private wheat stocks",
        "media": ALL_YEARS_ZIP,
        "member": "17_Government_and_private_stocks.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (),
    },
    "domestic_and_international_prices": {
        "label": "Domestic and international wheat prices",
        "media": ALL_YEARS_ZIP,
        "member": "18_20_Domestic_and_international_prices.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Commodity_Desc",
        "value_name": None,
        "row_dims": (("Geography_Desc", "geography"), ("Unit_Desc", "unit")),
    },
    "export_import_trade_by_component": {
        "label": "Wheat export and import trade, by component",
        "media": ALL_YEARS_ZIP,
        "member": "21_24_Export_and_import_trade_data_by_component.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (
            ("Commodity_Desc", "product"),
            ("Commodity_Desc2", "commodity_group"),
        ),
    },
    "all_wheat_destination_exports": {
        "label": "All-wheat exports, by destination",
        "media": ALL_YEARS_ZIP,
        "member": "25_All_wheat_destination_export_trade_data.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": None,
        "value_name": "Exports",
        "row_dims": (("Geography_Desc", "geography"),),
    },
    "by_class_inspections": {
        "label": "Wheat inspections, by class and destination",
        "media": ALL_YEARS_ZIP,
        "member": "26_By_class_inspections _data.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Commodity_Desc",
        "value_name": None,
        "row_dims": (("Geography_Desc", "geography"),),
    },
    "exports_by_government_program": {
        "label": "Wheat exports, by government program",
        "media": ALL_YEARS_ZIP,
        "member": "27_Exports_by_government_program.csv",
        "value_col": "Amount",
        "year_col": "Fiscal_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (),
    },
    "flour_production_and_disappearance": {
        "label": "Wheat flour production and disappearance",
        "media": ALL_YEARS_ZIP,
        "member": "28_31_Flour_production_and_disappearance.csv",
        "value_col": "Amount",
        "year_col": "Calendar_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (
            ("Commodity_Desc2", "product"),
            ("Commodity_Desc", "commodity_group"),
        ),
    },
    "wheat_flour_price_relationships": {
        "label": "Wheat and flour price relationships",
        "media": ALL_YEARS_ZIP,
        "member": "32_33_Wheat_and_flour_price_relationships.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Commodity_Desc2",
        "value_name": None,
        "row_dims": (("Geography_Desc", "geography"),),
    },
    "by_class_trade_data": {
        "label": "Wheat trade, by class",
        "media": ALL_YEARS_ZIP,
        "member": "34_35_By-class_trade_data.csv",
        "value_col": "Amount",
        "year_col": "Marketing_Year",
        "period_col": "Timeperiod_Desc",
        "series_col": "Attribute_Desc",
        "value_name": None,
        "row_dims": (("Commodity_Desc", "wheat_class"),),
    },
    "by_class_quarterly": {
        "label": "By-class quarterly balance sheet",
        "media": QUARTERLY_ZIP,
        "member": "wheat-by-class-quarterly.csv",
        "value_col": "Value",
        "year_col": "MarketingYear",
        "period_col": "TimePeriod",
        "series_col": "Attribute",
        "value_name": None,
        "row_dims": (("Class", "wheat_class"), ("Unit", "unit")),
    },
}

ROW_DIM_FIELDS = (
    "wheat_class",
    "commodity_group",
    "product",
    "geography",
    "unit",
)


def normalize_class(value: str) -> str:
    """Normalize a wheat-class label to its canonical casing.

    Parameters
    ----------
    value : str
        Class label as published, e.g. 'All Wheat'.

    Returns
    -------
    str
        Canonical label, e.g. 'All wheat'; the input unchanged when unknown.
    """
    return CLASS_CANON.get(value.strip().casefold(), value.strip())


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's CSV text into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the table member.
    table : str
        Table key from WHEAT_DATA_FILES.

    Returns
    -------
    list[dict]
        Records carrying the year label, integer year, period, the five
        row-dimension fields, the series name, and the numeric amount.
        Rows whose value is blank or non-numeric are skipped.
    """
    config = WHEAT_DATA_FILES[table]
    series_col = config["series_col"]
    period_col = config["period_col"]
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        raw_value = (row.get(config["value_col"]) or "").strip()
        try:
            amount = float(raw_value)
        except ValueError:
            continue
        year_label = (row.get(config["year_col"]) or "").strip()
        if not year_label[:4].isdigit():
            continue
        record: dict = {
            "table": table,
            "marketing_year": year_label,
            "year": int(year_label[:4]),
            "period": (
                ((row.get(period_col) or "").strip() or None) if period_col else None
            ),
            "wheat_class": None,
            "commodity_group": None,
            "product": None,
            "geography": None,
            "unit": None,
        }
        for source_col, output_field in config["row_dims"]:
            value = (row.get(source_col) or "").strip()
            if output_field == "wheat_class":
                value = normalize_class(value)
            record[output_field] = value or None
        record["series"] = (
            (row.get(series_col) or "").strip() if series_col else config["value_name"]
        )
        record["amount"] = amount
        records.append(record)
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one wheat-data table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from WHEAT_DATA_FILES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = WHEAT_DATA_FILES[table]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    with zipfile.ZipFile(BytesIO(content)) as archive:
        raw = archive.read(config["member"])
    return parse_table(raw.decode("utf-8-sig", errors="replace"), table)
