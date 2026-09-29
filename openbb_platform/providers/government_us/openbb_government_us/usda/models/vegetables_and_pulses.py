"""USDA ERS Vegetables and Pulses Yearbook Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_vegetables_and_pulses import (
    DEFAULT_TABLE,
    TABLE_LABELS,
)
from openbb_government_us.utils.serializers import NullTokenMixin


class VegetablesAndPulsesQueryParams(QueryParams):
    """USDA ERS Vegetables and Pulses Yearbook Query Parameters.

    Source: https://www.ers.usda.gov/data-products/vegetables-and-pulses-data/vegetables-and-pulses-yearbook-tables
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in TABLE_LABELS.items()
                ],
                "style": {"popupWidth": 520},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Yearbook table to retrieve. Each table is a supply,"
        + " availability, price, cash-receipts, or world-production series"
        + " for one commodity or aggregate; the data elements (production,"
        + " supply, imports, exports, availability, price) become the wide"
        + " columns while year, commodity, and location stay as rows."
        + " Valid tables are:\n    "
        + ", ".join(TABLE_LABELS)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " observation year. If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " observation year. If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v[0] if isinstance(v, (list, tuple)) else v
        table = str(table).strip()
        if table not in TABLE_LABELS:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(TABLE_LABELS)
            )
        return table


class VegetablesAndPulsesData(NullTokenMixin, Data):
    """USDA ERS Vegetables and Pulses Yearbook Data.

    One selected yearbook table pivoted to a wide layout: year, commodity, and
    location stay in the rows while the table's data elements spread into value
    columns, whose set and units vary by table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Vegetables & Pulses Yearbook",
                "$.description": "U.S. and world vegetable and pulse-crop"
                " production, supply, use, trade, per capita availability,"
                " prices, and cash receipts from the annual Vegetables and"
                " Pulses Yearbook, published by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Year of the observation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    commodity: str | None = Field(
        default=None,
        description="Vegetable or pulse commodity, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "pinned": "left"}
        },
    )
    location: str | None = Field(
        default=None,
        description="Location of the observation: a country for the"
        + " world-production table, a state or the United States for the"
        + " cash-receipts table, and the United States for the commodity"
        + " supply tables.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Location", "pinned": "left"}
        },
    )
    end_use: str | None = Field(
        default=None,
        description="Market of the observation, as published, e.g. 'Fresh',"
        + " 'Processing', 'Dry', 'Canning', 'Freezing', or 'All uses'.",
        json_schema_extra={"x-widget_config": {"headerName": "End use", "hide": True}},
    )
    geographical_level: str | None = Field(
        default=None,
        description="Geographical level of the location, 'Country' or 'State'.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Geographic level", "hide": True}
        },
    )


class VegetablesAndPulsesFetcher(
    Fetcher[
        VegetablesAndPulsesQueryParams,
        list[VegetablesAndPulsesData],
    ]
):
    """Fetch USDA ERS Vegetables and Pulses Yearbook Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> VegetablesAndPulsesQueryParams:
        """Transform the query params."""
        return VegetablesAndPulsesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: VegetablesAndPulsesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_vegetables_and_pulses

        return await ers_vegetables_and_pulses.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: VegetablesAndPulsesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[VegetablesAndPulsesData]:
        """Pivot the long-format rows into the wide layout, item into columns."""
        pivoted: dict[tuple, dict] = {}
        item_order: list[str] = []
        seen_items: set[str] = set()
        for record in data:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            item = record["item"]
            if item not in seen_items:
                seen_items.add(item)
                item_order.append(item)
            key = (
                record["commodity"],
                record["end_use"],
                record["location"],
                year,
            )
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_commodity": record["commodity"] or "",
                    "_location": record["location"] or "",
                    "_end_use": record["end_use"] or "",
                    "_year": year,
                    "year": year,
                    "commodity": record["commodity"],
                    "location": record["location"],
                    "end_use": record["end_use"],
                    "geographical_level": record["geographical_level"],
                }
                pivoted[key] = row
            row[item] = record["value"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        results = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_commodity"],
                row["_location"],
                row["_end_use"],
                row["_year"],
            ),
        )
        validated: list[VegetablesAndPulsesData] = []
        for row in results:
            ordered = {
                "year": row["year"],
                "commodity": row["commodity"],
                "location": row["location"],
                "end_use": row["end_use"],
                "geographical_level": row["geographical_level"],
            }
            for item in item_order:
                if item in row:
                    ordered[item] = row[item]
            validated.append(VegetablesAndPulsesData.model_validate(ordered))
        return validated
