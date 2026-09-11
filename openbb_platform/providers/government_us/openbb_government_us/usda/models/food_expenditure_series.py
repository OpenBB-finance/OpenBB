"""USDA ERS Food Expenditure Series Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_food_expenditure_series import (
    FOOD_EXPENDITURE_FILES,
    MONTH_ORDER,
    STATES,
)
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

DEFAULT_TABLE = "food_and_alcohol"

Measure = Literal["nominal", "constant"]
Taxes = Literal["with", "without"]


class FoodExpenditureSeriesQueryParams(QueryParams):
    """USDA ERS Food Expenditure Series Query Parameters.

    Source: https://www.ers.usda.gov/data-products/food-expenditure-series
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": config["label"], "value": key}
                    for key, config in FOOD_EXPENDITURE_FILES.items()
                ],
                "style": {"popupWidth": 360},
            },
        },
        "measure": {
            "x-widget_config": {
                "label": "Measure",
                "value": "nominal",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": "Nominal dollars", "value": "nominal"},
                    {"label": "Constant dollars (2025=100)", "value": "constant"},
                ],
            },
        },
        "taxes": {
            "x-widget_config": {
                "label": "Taxes and tips",
                "value": "with",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": "With taxes and tips", "value": "with"},
                    {"label": "Without taxes and tips", "value": "without"},
                ],
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "multiSelect": False,
                "multiple": False,
                "options": [{"label": state, "value": state} for state in STATES],
                "style": {"popupWidth": 260},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Food Expenditure Series table to retrieve. Each table's"
        + " category series become the wide value columns while the year, folded"
        + " with the month or state where either varies, forms the pinned period"
        + " label. Valid tables are:\n    "
        + ", ".join(FOOD_EXPENDITURE_FILES)
        + "\n",
    )
    measure: Measure = Field(
        default="nominal",
        description="Dollar measure. 'nominal' returns current-dollar values;"
        + " 'constant' returns chained 2025-dollar values. Selects the source"
        + " file for the food_and_alcohol, state, and state_per_capita tables"
        + " and the value columns for the others. Ignored by the percentage"
        + " share columns of the normalized table.",
    )
    taxes: Taxes = Field(
        default="with",
        description="Sales-tax and tip treatment. 'with' includes taxes and"
        + " tips; 'without' excludes them. Selects the source file for the"
        + " food_and_alcohol, state, and state_per_capita tables; the other"
        + " tables publish a single treatment and ignore this.",
    )
    state: str | None = Field(
        default=None,
        description="Filter the state and state_per_capita tables to states"
        + " matching this case-insensitive substring, e.g. 'california'."
        + " If None, every state is returned. Ignored by the other tables.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from the beginning of the series.",
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
        table = v.strip() if isinstance(v, str) else v
        if table not in FOOD_EXPENDITURE_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(FOOD_EXPENDITURE_FILES)
            )
        return table


class FoodExpenditureSeriesData(NullTokenMixin, Data):
    """USDA ERS Food Expenditure Series Data, pivoted to period rows with the table's category series as value columns."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Food Expenditure Series",
                "$.description": "U.S. food and alcohol expenditures by outlet,"
                " final purchaser, month, and state, in nominal and constant"
                " dollars, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual tables"
        + " ('2020'), the year and month for monthly tables ('2020 March'), with"
        + " the state prefixed when more than one state is shown at once"
        + " ('California — 2020'), so each row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 280,
            }
        },
    )


class FoodExpenditureSeriesFetcher(
    Fetcher[
        FoodExpenditureSeriesQueryParams,
        list[FoodExpenditureSeriesData],
    ]
):
    """Fetch USDA ERS Food Expenditure Series Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FoodExpenditureSeriesQueryParams:
        """Transform the query params."""
        return FoodExpenditureSeriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FoodExpenditureSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_food_expenditure_series

        return await ers_food_expenditure_series.afetch_table(
            query.table, query.measure, query.taxes
        )

    @staticmethod
    def _period_label(year: int, month: str | None, dim_values: list[str]) -> str:
        """Fold the varying dimensions, the year, and the month into one label."""
        time_label = f"{year} {month}" if month else str(year)
        return " — ".join([*dim_values, time_label])

    @staticmethod
    def transform_data(
        query: FoodExpenditureSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FoodExpenditureSeriesData]:
        """Filter, then pivot the long-format rows into period rows."""
        state_filter = query.state.strip().casefold() if query.state else None
        filtered: list[dict] = []
        for record in data:
            measure = record["measure"]
            if measure is not None and measure != query.measure:
                continue
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            state = record["state"]
            if (
                state_filter is not None
                and state is not None
                and state_filter not in state.casefold()
            ):
                continue
            filtered.append(record)
        state_varies = (
            len(
                {
                    record["state"]
                    for record in filtered
                    if record["state"] and not is_null_token(record["state"])
                }
            )
            > 1
        )
        units = {record["unit"] for record in filtered}
        single_unit = len(units) == 1 and "" not in units
        unit_suffix = f" ({next(iter(units))})" if single_unit else ""
        pivoted: dict[tuple, dict] = {}
        col_order: list[str] = []
        seen_columns: set[str] = set()
        for record in filtered:
            year = record["year"]
            month = record["month"]
            state = record["state"]
            key = (state or "", year, month)
            row = pivoted.get(key)
            if row is None:
                dim_values = (
                    [state]
                    if state_varies and state and not is_null_token(state)
                    else []
                )
                row = {
                    "_state": state or "",
                    "_year": year,
                    "_month_order": MONTH_ORDER.get(month or "", 0),
                    "period": FoodExpenditureSeriesFetcher._period_label(
                        year, month, dim_values
                    ),
                }
                pivoted[key] = row
            column = f"{record['category']}{unit_suffix}"
            if column not in seen_columns:
                seen_columns.add(column)
                col_order.append(column)
            row[column] = record["value"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["_state"], row["_year"], row["_month_order"]),
        )
        validated: list[FoodExpenditureSeriesData] = []
        for row in results:
            payload: dict[str, Any] = {"period": row["period"]}
            for column in col_order:
                payload[column] = row.get(column)
            validated.append(FoodExpenditureSeriesData.model_validate(payload))
        return validated
