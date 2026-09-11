"""Farm Income and Wealth Statistics Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_farm_income_and_wealth_statistics import (
    STATE_LABELS,
    TABLE_LABELS,
    TABLE_PREFIXES,
    allowed_states,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "income_statement"
DEFAULT_STATE = "US"


class FarmIncomeAndWealthStatisticsQueryParams(QueryParams):
    """Farm Income and Wealth Statistics Query Parameters.

    Source: https://www.ers.usda.gov/data-products/farm-income-and-wealth-statistics
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
                "style": {"popupWidth": 360},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "value": DEFAULT_STATE,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/farm_income_states",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 280},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Statement to retrieve. Each table is a set of line items"
        + " keyed by year; the years become the wide columns while the line"
        + " item and its unit stay as pinned row columns. The balance sheet,"
        + " financial ratios, and farm business income tables are published"
        + " for the United States only. Valid tables are:\n    "
        + ", ".join(TABLE_PREFIXES)
        + "\n",
    )
    state: str = Field(
        default=DEFAULT_STATE,
        description="State to retrieve, as a two-letter code, or 'US' for the"
        + " national aggregate. State detail is published for the income"
        + " statement, production expenses, cash receipts, government payments,"
        + " farm-related income, home consumption, and inventory change tables;"
        + " the U.S.-only tables accept 'US'. Forecast years are published for"
        + " 'US' only.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from the first published year.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent forecast year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in TABLE_PREFIXES:
            raise OpenBBError(
                f"Invalid table: {value}. Valid tables are: "
                + ", ".join(TABLE_PREFIXES)
            )
        return value

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate state."""
        if not v:
            return DEFAULT_STATE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        if value not in STATE_LABELS:
            raise OpenBBError(
                f"Invalid state: {value}. Valid states are: " + ", ".join(STATE_LABELS)
            )
        return value

    @model_validator(mode="after")
    def _validate_state_for_table(self):
        """Validate that the state is published for the selected table."""
        codes = allowed_states(self.table)
        if self.state not in codes:
            raise OpenBBError(
                f"Invalid state '{self.state}' for table '{self.table}'."
                f" This table is published for: " + ", ".join(codes)
            )
        return self


class FarmIncomeAndWealthStatisticsData(NullTokenMixin, Data):
    """Farm Income and Wealth Statistics Data.

    One selected statement pivoted to a wide layout: each row is a published
    line item and its unit, with one value column per year. Amounts are the
    raw published values; year columns are dynamic and vary by table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Farm Income and Wealth Statistics",
                "$.description": "U.S. and State-level farm sector income"
                " statements, production expenses, cash receipts, government"
                " payments, balance sheets, financial ratios, and farm business"
                " income, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    line_item: str = Field(
        description="Published line item of the statement, as the full"
        + " variable description.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Line item", "pinned": "left"}
        },
    )
    unit: str = Field(
        description="Unit of the line's values, as published, e.g. '$1,000',"
        + " '$1,000 per farm', 'Ratio', 'Percent', or '1,000 acres'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Unit",
                "pinned": "left",
                "maxWidth": 130,
            }
        },
    )
    state: str = Field(
        description="State of the observation, or 'United States' for the"
        + " national aggregate.",
        json_schema_extra={"x-widget_config": {"headerName": "State", "hide": True}},
    )
    part_1: str | None = Field(
        default=None,
        description="First component of the line-item description, as"
        + " published, when the item is broken out.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Component", "hide": True}
        },
    )
    part_2: str | None = Field(
        default=None,
        description="Second component of the line-item description, as"
        + " published, when the item is broken out.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Subcomponent", "hide": True}
        },
    )


class FarmIncomeAndWealthStatisticsFetcher(
    Fetcher[
        FarmIncomeAndWealthStatisticsQueryParams,
        list[FarmIncomeAndWealthStatisticsData],
    ]
):
    """Fetch USDA ERS Farm Income and Wealth Statistics."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FarmIncomeAndWealthStatisticsQueryParams:
        """Transform the query params."""
        return FarmIncomeAndWealthStatisticsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FarmIncomeAndWealthStatisticsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's rows for the selected state."""
        from openbb_government_us.usda.utils import (
            ers_farm_income_and_wealth_statistics,
        )

        return await ers_farm_income_and_wealth_statistics.afetch_table(
            query.table, query.state
        )

    @staticmethod
    def transform_data(
        query: FarmIncomeAndWealthStatisticsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FarmIncomeAndWealthStatisticsData]:
        """Pivot each line item's years into columns, oldest year first."""
        prefix_rank = {
            prefix: rank for rank, prefix in enumerate(TABLE_PREFIXES[query.table])
        }
        pivoted: dict[tuple, dict] = {}
        for record in data:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            key = (record["line_item"], record["unit"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_rank": prefix_rank.get(record["prefix"], len(prefix_rank)),
                    "_order": record["order"],
                    "line_item": record["line_item"],
                    "unit": record["unit"],
                    "state": STATE_LABELS.get(record["state"], record["state"]),
                    "part_1": record["part_1"],
                    "part_2": record["part_2"],
                }
                pivoted[key] = row
            elif record["order"] < row["_order"]:
                row["_order"] = record["order"]
            row[str(year)] = record["amount"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        results = sorted(
            pivoted.values(), key=lambda row: (row["_rank"], row["_order"])
        )
        validated: list[FarmIncomeAndWealthStatisticsData] = []
        for row in results:
            dimensions = {
                k: v
                for k, v in row.items()
                if not k.startswith("_") and not k.isdigit()
            }
            years = {
                year: row[year]
                for year in sorted((k for k in row if k.isdigit()), key=int)
            }
            validated.append(
                FarmIncomeAndWealthStatisticsData.model_validate(
                    {**dimensions, **years}
                )
            )
        return validated
