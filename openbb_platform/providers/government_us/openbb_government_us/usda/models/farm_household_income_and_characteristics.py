"""Farm Household Income and Characteristics Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_farm_household_income_and_characteristics import (
    DEFAULT_TABLE,
    TABLE_CONFIG,
    TABLE_LABELS,
    YEAR_TABLES,
    parse_year,
    year_sort_key,
)
from openbb_government_us.utils.serializers import NullTokenMixin


class FarmHouseholdIncomeAndCharacteristicsQueryParams(QueryParams):
    """Farm Household Income and Characteristics Query Parameters.

    Source: https://www.ers.usda.gov/data-products/farm-household-income-and-characteristics
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
        description="Table to retrieve. Each table is a set of line items pivoted"
        + " to a wide layout: the item stays as the pinned row column while the"
        + " time-series tables spread years into value columns and the"
        + " cross-tab tables spread a category into value columns. Valid tables"
        + " are:\n    "
        + ", ".join(TABLE_CONFIG)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data. Applies only to the"
        + " time-series tables ("
        + ", ".join(sorted(YEAR_TABLES))
        + "). If None, returns from the first published year.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data. Applies only to the"
        + " time-series tables. If None, returns up to the most recent year"
        + " or forecast year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in TABLE_CONFIG:
            raise OpenBBError(
                f"Invalid table: {value}. Valid tables are: " + ", ".join(TABLE_CONFIG)
            )
        return value


class FarmHouseholdIncomeAndCharacteristicsData(NullTokenMixin, Data):
    """Farm Household Income and Characteristics Data.

    One selected table pivoted to a wide layout: each row is a published line
    item, with one value column per year for the time-series tables or per
    category for the cross-tab tables. The value columns are dynamic and vary
    by table; amounts are the raw published values.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Farm Household Income and Characteristics",
                "$.description": "Income, finances, and characteristics of U.S."
                " farm operator households, by year, farm type, occupation, age,"
                " experience, management team, limited-resource status, and sex,"
                " published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    item: str = Field(
        description="Published line item of the selected table.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Item",
                "pinned": "left",
                "minWidth": 340,
            }
        },
    )


class FarmHouseholdIncomeAndCharacteristicsFetcher(
    Fetcher[
        FarmHouseholdIncomeAndCharacteristicsQueryParams,
        list[FarmHouseholdIncomeAndCharacteristicsData],
    ]
):
    """Fetch USDA ERS Farm Household Income and Characteristics."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FarmHouseholdIncomeAndCharacteristicsQueryParams:
        """Transform the query params."""
        return FarmHouseholdIncomeAndCharacteristicsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FarmHouseholdIncomeAndCharacteristicsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import (
            ers_farm_household_income_and_characteristics,
        )

        return await ers_farm_household_income_and_characteristics.afetch_table(
            query.table
        )

    @staticmethod
    def transform_data(
        query: FarmHouseholdIncomeAndCharacteristicsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FarmHouseholdIncomeAndCharacteristicsData]:
        """Pivot each item's series into columns, years chronological."""
        shape = TABLE_CONFIG[query.table]["shape"]
        item_order: dict[str, int] = {}
        column_order: dict[str, int] = {}
        grid: dict[tuple[str, str], Any] = {}
        for record in data:
            column = record["column"]
            if shape == "year":
                year = parse_year(column)
                if query.start_year is not None and year < query.start_year:
                    continue
                if query.end_year is not None and year > query.end_year:
                    continue
            item_order.setdefault(record["item"], len(item_order))
            column_order.setdefault(column, len(column_order))
            grid[(record["item"], column)] = record["value"]
        if shape == "year":
            columns = sorted(column_order, key=year_sort_key)
        else:
            columns = list(column_order)
        live_columns = [
            column
            for column in columns
            if any(grid.get((item, column)) is not None for item in item_order)
        ]
        if not item_order or not live_columns:
            raise EmptyDataError("No records match the given filters.")
        results: list[FarmHouseholdIncomeAndCharacteristicsData] = []
        for item in item_order:
            row = {"item": item}
            for column in live_columns:
                row[column] = grid.get((item, column))
            results.append(
                FarmHouseholdIncomeAndCharacteristicsData.model_validate(row)
            )
        return results
