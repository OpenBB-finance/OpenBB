"""USDA ERS Normalized Prices Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_normalized_prices import (
    DEFAULT_TABLE,
    NORMALIZED_PRICES_TABLES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

TABLE_OPTIONS = [
    {"label": config["label"], "value": key}
    for key, config in NORMALIZED_PRICES_TABLES.items()
]


class NormalizedPricesQueryParams(QueryParams):
    """USDA ERS Normalized Prices Query Parameters.

    Source: https://www.ers.usda.gov/data-products/normalized-prices
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": TABLE_OPTIONS,
                "style": {"popupWidth": 520},
            },
        },
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table to retrieve. 'table1_national_prices' spreads the"
        + " report years into columns with one row per commodity;"
        + " 'table2_national_indices' spreads the index years into columns with"
        + " one row per national price index series;"
        + " 'table3_state_prices' spreads the States into columns with one row"
        + " per commodity for the current report year. Valid tables are:\n    "
        + ", ".join(NORMALIZED_PRICES_TABLES)
        + "\n",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v[0] if isinstance(v, (list, tuple)) else v
        table = str(table).strip()
        if table not in NORMALIZED_PRICES_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(NORMALIZED_PRICES_TABLES)
            )
        return table


class NormalizedPricesData(NullTokenMixin, Data):
    """USDA ERS Normalized Prices Data.

    One selected table pivoted to a wide layout: each row is a commodity or
    price-index series with its unit, and the report years, index years, or
    States spread into the value columns, whose set varies by table. Values
    are the raw published normalized prices; suppressed State cells are None.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Normalized Prices",
                "$.description": "National and State-level normalized prices for"
                " crops, livestock, milk, poultry, eggs, and wool, plus national"
                " prices-received and prices-paid indices, published by the USDA"
                " Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    commodity: str = Field(
        description="Commodity (national and State price tables) or national"
        + " price index series (the index table), as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "pinned": "left"}
        },
    )
    units: str | None = Field(
        default=None,
        description="Unit of the row's prices, as published, e.g. '$ / bu',"
        + " '$ / cwt', or 'Index, 2011=100' for the price index table.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Units",
                "pinned": "left",
                "maxWidth": 150,
            }
        },
    )
    description: str | None = Field(
        default=None,
        description="Commodity qualifier, as published, e.g. 'for grain' or"
        + " 'lint, upland'. Absent for the price index table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Description", "hide": True}
        },
    )


class NormalizedPricesFetcher(
    Fetcher[
        NormalizedPricesQueryParams,
        list[NormalizedPricesData],
    ]
):
    """Fetch USDA ERS Normalized Prices."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NormalizedPricesQueryParams:
        """Transform the query params."""
        return NormalizedPricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NormalizedPricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_normalized_prices

        return await ers_normalized_prices.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: NormalizedPricesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NormalizedPricesData]:
        """Pivot the long-format rows into the wide layout for the table.

        The report or index years spread into ascending-ordered columns, or
        the States into alphabetically-ordered columns, one row per commodity
        or price-index series in published order.
        """
        dimension = NORMALIZED_PRICES_TABLES[query.table]["dimension"]
        pivoted: dict[tuple, dict] = {}
        column_keys: set[str] = set()
        for record in data:
            key = (record["commodity"], record["description"], record["units"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_order": record["order"],
                    "commodity": record["commodity"],
                    "units": record["units"],
                    "description": record["description"],
                }
                pivoted[key] = row
            column = str(record["column"])
            column_keys.add(column)
            row[column] = record["value"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        populated = {
            column
            for column in column_keys
            if any(row.get(column) is not None for row in pivoted.values())
        }
        ordered_columns = (
            sorted(populated, key=int) if dimension == "year" else sorted(populated)
        )
        results = sorted(pivoted.values(), key=lambda row: row["_order"])
        validated: list[NormalizedPricesData] = []
        for row in results:
            dimensions = {
                "commodity": row["commodity"],
                "units": row["units"],
                "description": row["description"],
            }
            columns = {column: row.get(column) for column in ordered_columns}
            validated.append(
                NormalizedPricesData.model_validate({**dimensions, **columns})
            )
        return validated
