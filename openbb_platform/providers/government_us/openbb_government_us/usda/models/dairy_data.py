"""USDA ERS Dairy Data Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_dairy_data import DAIRY_DATA_FILES
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "situation_at_a_glance"

Frequency = Literal["monthly", "quarterly", "annual"]


class DairyDataQueryParams(QueryParams):
    """USDA ERS Dairy Data Query Parameters.

    Source: https://www.ers.usda.gov/data-products/dairy-data
    """

    __json_schema_extra__ = {
        "table": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Table",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": slug.replace("_", " ").capitalize(), "value": slug}
                    for slug in sorted(DAIRY_DATA_FILES)
                ],
                "style": {"popupWidth": 340},
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "options": [
                    {"label": "Monthly", "value": "monthly"},
                    {"label": "Quarterly", "value": "quarterly"},
                    {"label": "Annual", "value": "annual"},
                ],
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table(s) to retrieve, as a comma-separated list of keys."
        + " The default, situation_at_a_glance, is a rolling snapshot of the"
        + " latest ~14 months; the other tables are full histories."
        + " Valid tables are:\n    "
        + ", ".join(sorted(DAIRY_DATA_FILES))
        + "\n",
    )
    frequency: Frequency | None = Field(
        default=None,
        description="Filter rows by observation frequency."
        + " Mixed-frequency tables carry annual rows alongside monthly or"
        + " quarterly rows; annual-only tables carry only 'annual' rows."
        + " If None, all frequencies are included.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from the beginning of each series.",
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
            return DEFAULT_TABLE
        tables = v.split(",") if isinstance(v, str) else list(v)
        tables = [table.strip() for table in tables if table and table.strip()]
        if not tables:
            return DEFAULT_TABLE
        unknown = [table for table in tables if table not in DAIRY_DATA_FILES]
        if unknown:
            raise OpenBBError(
                f"Invalid table(s): {', '.join(unknown)}. Valid tables are: "
                + ", ".join(sorted(DAIRY_DATA_FILES))
            )
        return ",".join(tables)


class DairyDataData(NullTokenMixin, Data):
    """USDA ERS Dairy Data.

    Tidy long-format records from the machine-readable files of the USDA ERS
    Dairy Data product: milk production, supply and utilization, per capita
    consumption, fluid sales, and related industry indicators.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Dairy Data",
                "$.description": "Milk production, supply and utilization, per-capita consumption, fluid sales, and dairy price series, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    category: str | None = Field(
        default=None,
        description="Category grouping of the data item, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Category", "pinned": "left"}
        },
    )
    data_item: str = Field(
        description="Data item name, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Data item", "pinned": "left"}
        },
    )
    unit: str = Field(
        description="Unit of the value, as published; casing varies by table.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit"}},
    )
    sub_table: str | None = Field(
        default=None,
        description="Published sub-table name within the dataset, e.g."
        + " 'Butter, monthly', 'M.E. Milk-fat basis, annual', or 'Milk cows'.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Sub-table", "hide": True}
        },
    )
    product: str | None = Field(
        default=None,
        description="Dairy product category."
        + " Only present for supply_utilization_products.",
        json_schema_extra={"x-widget_config": {"headerName": "Product", "hide": True}},
    )
    data_item_id: str | None = Field(
        default=None,
        description="Hierarchical data item code, e.g. '1-3.04.00'; the same"
        + " suffix identifies the same product across tables."
        + " Only present for milk_fat_skim_solids_allocation.",
        json_schema_extra={"x-widget_config": {"headerName": "Item ID", "hide": True}},
    )
    region: str | None = Field(
        default=None,
        description="ERS farm production region."
        + " Only present for milk_cows_by_state.",
        json_schema_extra={"x-widget_config": {"headerName": "Region", "hide": True}},
    )
    state: str | None = Field(
        default=None,
        description="State name; regional and national aggregates use"
        + " 'Total region'. Only present for milk_cows_by_state.",
        json_schema_extra={"x-widget_config": {"headerName": "State", "hide": True}},
    )


class DairyDataFetcher(
    Fetcher[
        DairyDataQueryParams,
        list[DairyDataData],
    ]
):
    """Fetch USDA ERS Dairy Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DairyDataQueryParams:
        """Transform the query params."""
        return DairyDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DairyDataQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected tables' tidy CSV rows."""
        import asyncio

        from openbb_government_us.usda.utils import ers_dairy_data

        selected = query.table.split(",")
        results = await asyncio.gather(
            *(ers_dairy_data.afetch_table(table) for table in selected)
        )
        records: list[dict] = []
        for table, rows in zip(selected, results):
            for row in rows:
                records.append({**row, "table": table})
        return records

    @staticmethod
    def transform_data(
        query: DairyDataQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DairyDataData]:
        """Pivot the observations into chronologically ordered date columns."""
        pivoted: dict[tuple, dict] = {}
        observations: dict[tuple, dict[str, Any]] = {}
        for order, record in enumerate(data):
            if query.frequency is not None and record["frequency"] != query.frequency:
                continue
            if query.start_year is not None and record["year"] < query.start_year:
                continue
            if query.end_year is not None and record["year"] > query.end_year:
                continue
            key = (
                record.get("table"),
                record.get("category"),
                record["data_item"],
                record["unit"],
                record.get("sub_table"),
                record.get("product"),
                record.get("region"),
                record.get("state"),
                record.get("data_item_id"),
            )
            row = pivoted.get(key)
            if row is None:
                observations[key] = {}
                row = {
                    "_order": order,
                    "category": record.get("category"),
                    "data_item": record["data_item"],
                    "unit": record["unit"],
                    "sub_table": record.get("sub_table"),
                    "product": record.get("product"),
                    "region": record.get("region"),
                    "state": record.get("state"),
                    "data_item_id": record.get("data_item_id"),
                }
                pivoted[key] = row
            observations[key][str(record["date"])] = record["value"]
        ordered = sorted(pivoted.items(), key=lambda item: item[1]["_order"])
        dates = sorted({date for values in observations.values() for date in values})
        return [
            DairyDataData.model_validate(
                {
                    **{k: v for k, v in row.items() if k != "_order"},
                    **{date: observations[key].get(date) for date in dates},
                }
            )
            for key, row in ordered
        ]
