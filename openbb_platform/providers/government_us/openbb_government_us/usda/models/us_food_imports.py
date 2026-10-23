"""USDA ERS U.S. Food Imports Model."""

from collections import OrderedDict
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_us_food_imports import (
    DEFAULT_COMMODITY,
    DEFAULT_FOOD_GROUP,
    FOOD_GROUPS,
    MEASURES,
    SOURCE_MEASURES,
    clean_country,
    food_group_column_label,
    product_lines,
    unit_label,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

TABLES = ("by_food_group", "by_source")

TABLE_OPTIONS = [
    {"label": "By food group", "value": "by_food_group"},
    {"label": "By source country", "value": "by_source"},
]

MEASURE_OPTIONS = [
    {"label": "Value (million $)", "value": "value"},
    {"label": "Volume", "value": "volume"},
    {"label": "Value, year-over-year change (%)", "value": "value_change"},
    {"label": "Volume, year-over-year change (%)", "value": "volume_change"},
    {"label": "Unit price", "value": "unit_price"},
    {"label": "Price inflation (%)", "value": "inflation"},
]

FOOD_GROUP_OPTIONS = [
    {"label": label, "value": code} for code, label in FOOD_GROUPS.items()
]


def _column_key(base_label: str, uniform_unit: str | None, uom: str) -> str:
    """Build a wide column key, appending the source unit when it varies by column."""
    if uniform_unit is None:
        return f"{base_label} ({unit_label(uom)})"
    return base_label


def _finalize(
    by_year: dict[int, dict], column_order: "OrderedDict[str, None]"
) -> list["UsFoodImportsData"]:
    """Emit year rows in ascending order with a consistent wide column set."""
    results: list[UsFoodImportsData] = []
    for year in sorted(by_year):
        source = by_year[year]
        row = {
            "year": source["year"],
            "food_group": source["food_group"],
            "commodity": source["commodity"],
            "unit": source["unit"],
        }
        for key in column_order:
            row[key] = source.get(key)
        results.append(UsFoodImportsData.model_validate(row))
    return results


def _pivot_food_group(
    query: "UsFoodImportsQueryParams", records: list[dict], spec: dict
) -> list["UsFoodImportsData"]:
    """Pivot aggregate rows into a year-by-food-group wide table."""
    selected = [
        record
        for record in records
        if record["category"] == spec["category"]
        and record["subcategory"] in spec["subcategories"]
        and (record["uom"] == "percent") == spec["percent"]
    ]
    column_order: OrderedDict[str, None] = OrderedDict()
    for record in sorted(selected, key=lambda record: record["row_number"]):
        base = food_group_column_label(record["commodity"])
        column_order.setdefault(
            _column_key(base, spec["uniform_unit"], record["uom"]), None
        )
    by_year: dict[int, dict] = {}
    for record in selected:
        year = record["year"]
        if query.start_year is not None and year < query.start_year:
            continue
        if query.end_year is not None and year > query.end_year:
            continue
        base = food_group_column_label(record["commodity"])
        key = _column_key(base, spec["uniform_unit"], record["uom"])
        row = by_year.get(year)
        if row is None:
            row = {
                "year": year,
                "food_group": None,
                "commodity": None,
                "unit": spec["uniform_unit"],
            }
            by_year[year] = row
        row[key] = record["value"]
    return _finalize(by_year, column_order)


def _pivot_source(
    query: "UsFoodImportsQueryParams", records: list[dict], spec: dict
) -> list["UsFoodImportsData"]:
    """Pivot one food group's detail rows into a year-by-source-country wide table."""
    if query.measure not in SOURCE_MEASURES:
        return []
    group = query.food_group
    commodity = query.commodity
    if not commodity:
        lines = product_lines(records, group)
        commodity = lines[0] if lines else DEFAULT_COMMODITY
    selected = [
        record
        for record in records
        if record["category"] == group
        and record["subcategory"] == "Foods"
        and record["commodity"] == commodity
        and ((record["uom"] == "Million $") == (query.measure == "value"))
    ]
    column_order: OrderedDict[str, None] = OrderedDict()
    for record in sorted(selected, key=lambda record: record["row_number"]):
        base = clean_country(record["country"])
        column_order.setdefault(
            _column_key(base, spec["uniform_unit"], record["uom"]), None
        )
    group_label = FOOD_GROUPS.get(group, group)
    by_year: dict[int, dict] = {}
    for record in selected:
        year = record["year"]
        if query.start_year is not None and year < query.start_year:
            continue
        if query.end_year is not None and year > query.end_year:
            continue
        base = clean_country(record["country"])
        key = _column_key(base, spec["uniform_unit"], record["uom"])
        row = by_year.get(year)
        if row is None:
            row = {
                "year": year,
                "food_group": group_label,
                "commodity": commodity,
                "unit": spec["uniform_unit"],
            }
            by_year[year] = row
        row[key] = record["value"]
    return _finalize(by_year, column_order)


class UsFoodImportsQueryParams(QueryParams):
    """USDA ERS U.S. Food Imports Query Parameters.

    Source: https://www.ers.usda.gov/data-products/us-food-imports
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": "by_food_group",
                "multiSelect": False,
                "multiple": False,
                "options": TABLE_OPTIONS,
            },
        },
        "measure": {
            "x-widget_config": {
                "label": "Measure",
                "value": "value",
                "multiSelect": False,
                "multiple": False,
                "options": MEASURE_OPTIONS,
                "style": {"popupWidth": 300},
            },
        },
        "food_group": {
            "x-widget_config": {
                "label": "Food group (source table)",
                "value": DEFAULT_FOOD_GROUP,
                "multiSelect": False,
                "multiple": False,
                "options": FOOD_GROUP_OPTIONS,
                "style": {"popupWidth": 280},
            },
        },
        "commodity": {
            "x-widget_config": {
                "label": "Commodity (source table)",
                "type": "endpoint",
                "value": DEFAULT_COMMODITY,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/food_import_commodities",
                "optionsParams": {"food_group": "$food_group"},
                "style": {"popupWidth": 380},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default="by_food_group",
        description="Table to retrieve. 'by_food_group' spreads the 14 food"
        + " groups and a total-foods column across the years; 'by_source'"
        + " spreads the source countries of the selected food group and"
        + " product line across the years. Valid tables are:\n    "
        + ", ".join(TABLES)
        + "\n",
    )
    measure: str = Field(
        default="value",
        description="Measure to spread into the wide columns. 'by_source'"
        + " supports only 'value' and 'volume'. Valid measures are:\n    "
        + ", ".join(MEASURES)
        + "\n",
    )
    food_group: str = Field(
        default=DEFAULT_FOOD_GROUP,
        description="Food group whose source countries are spread into columns"
        + " for the 'by_source' table. Ignored by the 'by_food_group' table."
        + " Valid food groups are:\n    "
        + ", ".join(FOOD_GROUPS)
        + "\n",
    )
    commodity: str | None = Field(
        default=None,
        description="Product line within the selected food group for the"
        + " 'by_source' table, e.g. 'Fresh or chilled fruit'. If None, the"
        + " food group's total line is used. Ignored by the 'by_food_group'"
        + " table.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from 1999, the first year of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return "by_food_group"
        table = v.strip() if isinstance(v, str) else v
        if table not in TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(TABLES)
            )
        return table

    @field_validator("measure", mode="before", check_fields=False)
    @classmethod
    def _validate_measure(cls, v):
        """Validate measure."""
        if not v:
            return "value"
        measure = v.strip() if isinstance(v, str) else v
        if measure not in MEASURES:
            raise OpenBBError(
                f"Invalid measure: {measure}. Valid measures are: "
                + ", ".join(MEASURES)
            )
        return measure

    @field_validator("food_group", mode="before", check_fields=False)
    @classmethod
    def _validate_food_group(cls, v):
        """Validate food_group."""
        if not v:
            return DEFAULT_FOOD_GROUP
        group = v.strip() if isinstance(v, str) else v
        if group not in FOOD_GROUPS:
            raise OpenBBError(
                f"Invalid food group: {group}. Valid food groups are: "
                + ", ".join(FOOD_GROUPS)
            )
        return group

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _validate_commodity(cls, v):
        """Normalize commodity to a stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None


class UsFoodImportsData(NullTokenMixin, Data):
    """USDA ERS U.S. Food Imports Data.

    One selected table pivoted to a wide layout: the years stay in the rows
    while the food-group or source-country dimension spreads into value
    columns, whose set is fixed for the food-group table and varies by food
    group for the source-country table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS U.S. Food Imports",
                "$.description": "Annual U.S. food import value, volume, unit"
                " prices, and price inflation by food group, and by source"
                " country within a food group, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Calendar year of the observation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "number",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    food_group: str | None = Field(
        default=None,
        description="Food group of the source-country table."
        + " None for the by-food-group table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Food group", "hide": True}
        },
    )
    commodity: str | None = Field(
        default=None,
        description="Product line of the source-country table, as published."
        + " None for the by-food-group table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "hide": True}
        },
    )
    unit: str | None = Field(
        default=None,
        description="Unit shared by every value column, when uniform;"
        + " None when the unit varies by column and is carried in each"
        + " column header instead.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit", "hide": True}},
    )


class UsFoodImportsFetcher(
    Fetcher[
        UsFoodImportsQueryParams,
        list[UsFoodImportsData],
    ]
):
    """Fetch USDA ERS U.S. Food Imports."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> UsFoodImportsQueryParams:
        """Transform the query params."""
        return UsFoodImportsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsFoodImportsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the summary file's long-format rows."""
        from openbb_government_us.usda.utils import ers_us_food_imports

        return await ers_us_food_imports.afetch_records()

    @staticmethod
    def transform_data(
        query: UsFoodImportsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[UsFoodImportsData]:
        """Pivot the long-format rows into the selected wide table."""
        spec = MEASURES[query.measure]
        if query.table == "by_source":
            return _pivot_source(query, data, spec)
        return _pivot_food_group(query, data, spec)
