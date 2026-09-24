"""USDA ERS Fertilizer Use and Price workbook catalog and parsers."""

import re
from typing import Any

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/fertilizer-use-and-price"
WORKBOOK_MEDIA = (
    "/media/5291/all-fertilizer-use-and-price-tables-in-a-single-workbook.xls"
)

FOOTNOTE_PREFIXES = ("NA =", "NA=", "1/", "2/", "3/", "4/", "Source")
STATE_FOOTNOTE = re.compile(r"\s*\d+/\s*$")

FERTILIZER_TABLES: dict[str, dict] = {
    "us_plant_nutrient_consumption": {
        "label": "Table 1. U.S. consumption of plant nutrients",
        "sheet": 1,
        "group": "A",
        "month_col": None,
        "columns": {
            1: "Nitrogen (N)",
            2: "Phosphate (P2O5)",
            3: "Potash (K2O)",
            4: "Total",
            6: "Nitrogen share",
            7: "Phosphate share",
            8: "Potash share",
        },
    },
    "plant_nutrient_use_by_crop": {
        "label": "Table 2. Estimated U.S. plant nutrient use by selected crops",
        "sheet": 2,
        "group": "A",
        "month_col": None,
        "columns": {
            1: "Nitrogen - Corn",
            2: "Nitrogen - Cotton",
            3: "Nitrogen - Soybeans",
            4: "Nitrogen - Wheat",
            5: "Nitrogen - Other",
            6: "Phosphate - Corn",
            7: "Phosphate - Cotton",
            8: "Phosphate - Soybeans",
            9: "Phosphate - Wheat",
            10: "Phosphate - Other",
            11: "Potash - Corn",
            12: "Potash - Cotton",
            13: "Potash - Soybeans",
            14: "Potash - Wheat",
            15: "Potash - Other",
        },
    },
    "nutrient_material_class_consumption": {
        "label": "Table 3. U.S. consumption of single, multiple, and secondary and"
        " micro nutrients",
        "sheet": 3,
        "group": "A",
        "month_col": None,
        "columns": {
            1: "Multiple-nutrient material",
            2: "Single-nutrient material",
            3: "Secondary and micro-nutrients",
            4: "Total",
            6: "Multiple-nutrient material share",
            7: "Single-nutrient material share",
            8: "Secondary and micronutrients share",
        },
    },
    "nitrogen_material_consumption": {
        "label": "Table 4. U.S. consumption of selected nitrogen materials",
        "sheet": 4,
        "group": "A",
        "month_col": None,
        "columns": {
            1: "Ammonia (Anhydrous)",
            2: "Ammonia (Aqua)",
            4: "Ammonium (Nitrate)",
            5: "Ammonium (Sulfate)",
            6: "Nitrogen solutions",
            7: "Sodium nitrate",
            8: "Urea",
            9: "Other",
        },
    },
    "phosphate_potash_material_consumption": {
        "label": "Table 5. U.S. consumption of selected phosphate and potash"
        " fertilizers",
        "sheet": 5,
        "group": "A",
        "month_col": None,
        "columns": {
            1: "Superphosphates, grades 22% and under",
            2: "Superphosphates, grades over 22%",
            3: "Other single phosphates",
            5: "Diammonium phosphate (18-46-0)",
            6: "Monoammonium phosphate (11-(51-55)-0)",
            7: "Other nitrogen-phosphate grades",
            9: "Potassium chloride",
            10: "Other single-nutrient potash",
        },
    },
    "secondary_micronutrient_organic_consumption": {
        "label": "Table 6. U.S. consumption of selected secondary, micronutrients,"
        " and natural organic materials",
        "sheet": 6,
        "group": "A",
        "month_col": None,
        "columns": {
            1: "Gypsum",
            2: "Sulfur",
            3: "Sulfuric Acid",
            4: "Zinc compound",
            6: "Compost",
            7: "Dried manure",
            8: "Sewage sludge",
            9: "Other organic materials",
        },
    },
    "farm_prices": {
        "label": "Table 7. Average U.S. farm prices of selected fertilizers",
        "sheet": 7,
        "group": "A",
        "month_col": 1,
        "columns": {
            2: "Anhydrous ammonia",
            3: "Nitrogen solutions (30%)",
            4: "Urea 44-46% nitrogen",
            5: "Ammonium nitrate",
            6: "Sulfate of ammonium",
            7: "Super-phosphate 20% phosphate",
            8: "Super-phosphate 44-46% phosphate",
            9: "Diammonium phosphate (18-46-0)",
            10: "Potassium chloride 60% potassium",
        },
    },
    "price_indexes": {
        "label": "Table 8. Fertilizer price indexes",
        "sheet": 8,
        "group": "A",
        "month_col": None,
        "columns": {
            1: "Prices paid by farmers for fertilizer",
            2: "Prices received by farmers for all crops",
            4: "PPI All fertilizers",
            5: "PPI Nitrogen",
            6: "PPI Phosphate",
            7: "PPI Potash",
        },
    },
    "corn_nitrogen_share": {
        "label": "Table 9. Percent of corn acreage receiving nitrogen fertilizer,"
        " selected States",
        "sheet": 9,
        "group": "B",
        "unit": "Percent",
    },
    "corn_nitrogen_rate": {
        "label": "Table 10. Nitrogen used on corn, rate per fertilized acre"
        " receiving nitrogen, selected States",
        "sheet": 10,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "corn_phosphate_share": {
        "label": "Table 11. Percentage of corn acreage receiving phosphate"
        " fertilizer, selected States",
        "sheet": 11,
        "group": "B",
        "unit": "Percent",
    },
    "corn_phosphate_rate": {
        "label": "Table 12. Phosphate used on corn, rate per fertilized acre"
        " receiving phosphate fertilizer, selected States",
        "sheet": 12,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "corn_potash_share": {
        "label": "Table 13. Percentage of corn acreage receiving potash fertilizer,"
        " selected States",
        "sheet": 13,
        "group": "B",
        "unit": "Percent",
    },
    "corn_potash_rate": {
        "label": "Table 14. Potash used on corn, rate per fertilized acre receiving"
        " potash, selected States",
        "sheet": 14,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "cotton_nitrogen_share": {
        "label": "Table 15. Percentage of cotton acreage receiving nitrogen"
        " fertilizer, selected States",
        "sheet": 15,
        "group": "B",
        "unit": "Percent",
    },
    "cotton_nitrogen_rate": {
        "label": "Table 16. Nitrogen used on cotton, rate per fertilized acre"
        " receiving nitrogen, selected States",
        "sheet": 16,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "cotton_phosphate_share": {
        "label": "Table 17. Percentage of cotton acreage receiving phosphate"
        " fertilizer, selected States",
        "sheet": 17,
        "group": "B",
        "unit": "Percent",
    },
    "cotton_phosphate_rate": {
        "label": "Table 18. Phosphate used on cotton, rate per fertilized acre"
        " receiving phosphate, selected States",
        "sheet": 18,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "cotton_potash_share": {
        "label": "Table 19. Percentage of cotton acreage receiving potash"
        " fertilizer, selected States",
        "sheet": 19,
        "group": "B",
        "unit": "Percent",
    },
    "cotton_potash_rate": {
        "label": "Table 20. Potash used on cotton, rate per fertilized acre"
        " receiving potash, selected States",
        "sheet": 20,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "soybeans_nitrogen_share": {
        "label": "Table 21. Percentage of soybean acreage receiving nitrogen"
        " fertilizer, selected States",
        "sheet": 21,
        "group": "B",
        "unit": "Percent",
    },
    "soybeans_nitrogen_rate": {
        "label": "Table 22. Nitrogen used on soybeans, rate per fertilized acre"
        " receiving nitrogen, selected States",
        "sheet": 22,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "soybeans_phosphate_share": {
        "label": "Table 23. Percentage of soybean acreage receiving phosphate"
        " fertilizer, selected States",
        "sheet": 23,
        "group": "B",
        "unit": "Percent",
    },
    "soybeans_phosphate_rate": {
        "label": "Table 24. Phosphate used on soybeans, rate per fertilized acre"
        " receiving phosphate, selected States",
        "sheet": 24,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "soybeans_potash_share": {
        "label": "Table 25. Percentage of soybean acreage receiving potash"
        " fertilizer, selected States",
        "sheet": 25,
        "group": "B",
        "unit": "Percent",
    },
    "soybeans_potash_rate": {
        "label": "Table 26. Potash used on soybeans, rate per fertilized acre"
        " receiving potash, selected States",
        "sheet": 26,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "wheat_nitrogen_share": {
        "label": "Table 27. Percentage of wheat acreage receiving nitrogen"
        " fertilizer, selected States",
        "sheet": 27,
        "group": "B",
        "unit": "Percent",
    },
    "wheat_nitrogen_rate": {
        "label": "Table 28. Nitrogen used on wheat, rate per fertilized acre"
        " receiving nitrogen, selected States",
        "sheet": 28,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "wheat_phosphate_share": {
        "label": "Table 29. Percentage of wheat acreage receiving phosphate"
        " fertilizer, selected States",
        "sheet": 29,
        "group": "B",
        "unit": "Percent",
    },
    "wheat_phosphate_rate": {
        "label": "Table 30. Phosphate used on wheat, rate per fertilized acre"
        " receiving phosphate, selected States",
        "sheet": 30,
        "group": "B",
        "unit": "Pounds/acre",
    },
    "wheat_potash_share": {
        "label": "Table 31. Percentage of wheat acreage receiving potash fertilizer,"
        " selected States",
        "sheet": 31,
        "group": "B",
        "unit": "Percent",
    },
    "wheat_potash_rate": {
        "label": "Table 32. Potash used on wheat, rate per fertilized acre receiving"
        " potash, selected States",
        "sheet": 32,
        "group": "B",
        "unit": "Pounds/acre",
    },
}


def _year_of(cell: Any) -> int | None:
    """Return the integer year a cell encodes, or None when it is not a year.

    Parameters
    ----------
    cell : Any
        A worksheet cell value, a float year, or a text label.

    Returns
    -------
    int | None
        The four-digit year in 1900-2100, else None.
    """
    if isinstance(cell, bool):
        return None
    if isinstance(cell, (int, float)):
        year = int(cell)
    elif isinstance(cell, str):
        text = cell.strip()
        if not text[:4].isdigit():
            return None
        year = int(text[:4])
    else:
        return None
    return year if 1900 <= year <= 2100 else None


def _numeric(cell: Any) -> float | None:
    """Return a cell's value as a float, or None when it is not numeric.

    Parameters
    ----------
    cell : Any
        A worksheet cell value.

    Returns
    -------
    float | None
        The float value, else None for blank or non-numeric cells such as 'NA'.
    """
    try:
        return float(cell)
    except (TypeError, ValueError):
        return None


def parse_group_a(rows: list[list], table: str) -> list[dict]:
    """Parse a Group A national worksheet into long-format records.

    Parameters
    ----------
    rows : list[list]
        Worksheet cells as a list of row lists.
    table : str
        Table key from FERTILIZER_TABLES.

    Returns
    -------
    list[dict]
        Records carrying table, year, period, series, and value. Only rows
        whose first column parses to a year contribute; non-numeric value
        cells are skipped.
    """
    config = FERTILIZER_TABLES[table]
    columns: dict[int, str] = config["columns"]
    month_col = config["month_col"]
    records: list[dict] = []
    for row in rows:
        if not row:
            continue
        year = _year_of(row[0])
        if year is None:
            continue
        period = None
        if month_col is not None and month_col < len(row):
            period = str(row[month_col]).strip() or None
        for col, series in columns.items():
            if col >= len(row):
                continue
            value = _numeric(row[col])
            if value is None:
                continue
            records.append(
                {
                    "table": table,
                    "year": year,
                    "period": period,
                    "series": series,
                    "value": value,
                }
            )
    return records


def parse_group_b(rows: list[list], table: str) -> list[dict]:
    """Parse a Group B crop-by-state worksheet into long-format records.

    Parameters
    ----------
    rows : list[list]
        Worksheet cells as a list of row lists.
    table : str
        Table key from FERTILIZER_TABLES.

    Returns
    -------
    list[dict]
        Records carrying table, year, period (always None), series (the State
        name), and value. The State x Year matrix is emitted one cell per
        record; footnote and blank rows are skipped and 'U.S. average 1/' is
        renamed to 'U.S. average'.
    """
    header_index = None
    for index, row in enumerate(rows):
        if row and str(row[0]).strip() == "State":
            header_index = index
            break
    if header_index is None:
        return []
    header = rows[header_index]
    year_cols: dict[int, int] = {}
    for col in range(1, len(header)):
        year = _year_of(header[col])
        if year is not None:
            year_cols[col] = year
    records: list[dict] = []
    for row in rows[header_index + 1 :]:
        if not row:
            continue
        state = str(row[0]).strip()
        if not state or state.startswith(FOOTNOTE_PREFIXES):
            continue
        state = STATE_FOOTNOTE.sub("", state).strip()
        for col, year in year_cols.items():
            if col >= len(row):
                continue
            value = _numeric(row[col])
            if value is None:
                continue
            records.append(
                {
                    "table": table,
                    "year": year,
                    "period": None,
                    "series": state,
                    "value": value,
                }
            )
    return records


def parse_sheet(rows: list[list], table: str) -> list[dict]:
    """Parse one table's worksheet rows into long-format records.

    Parameters
    ----------
    rows : list[list]
        Worksheet cells as a list of row lists.
    table : str
        Table key from FERTILIZER_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from the group-appropriate parser.
    """
    if FERTILIZER_TABLES[table]["group"] == "A":
        return parse_group_a(rows, table)
    return parse_group_b(rows, table)


def _sheet_rows(content: bytes, sheet_index: int) -> list[list]:
    """Read one worksheet of the binary .xls workbook into a list of row lists.

    Parameters
    ----------
    content : bytes
        Raw .xls workbook bytes.
    sheet_index : int
        Zero-based worksheet index.

    Returns
    -------
    list[list]
        Cell values, row by row.
    """
    import xlrd

    workbook = xlrd.open_workbook(file_contents=content)
    sheet = workbook.sheet_by_index(sheet_index)
    return [
        [sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)
    ]


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download the workbook and parse one table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from FERTILIZER_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_sheet.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = FERTILIZER_TABLES[table]
    content = await afetch_ers_file(WORKBOOK_MEDIA, product=PRODUCT_PAGE)
    rows = _sheet_rows(content, config["sheet"])
    return parse_sheet(rows, table)
