"""USDA ERS Food Security in the United States Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_food_security_in_the_united_states import (
    DIM_FIELDS,
    FOOD_SECURITY_TABLES,
)
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "national_trend"


class FoodSecurityInTheUnitedStatesQueryParams(QueryParams):
    """USDA ERS Food Security in the United States Query Parameters.

    Source: https://www.ers.usda.gov/data-products/food-security-in-the-united-states
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
                    for key, config in FOOD_SECURITY_TABLES.items()
                ],
                "style": {"popupWidth": 360},
            },
        },
        "category": {
            "x-widget_config": {
                "label": "Category",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/food_security_categories",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 320},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table to retrieve. Each table pivots a set of"
        + " food-security status measures into wide columns, with the survey"
        + " year or 3-year period in the rows and the characteristic path or"
        + " State as pinned dimension columns. Valid tables are:\n    "
        + ", ".join(FOOD_SECURITY_TABLES)
        + "\n",
    )
    category: str | None = Field(
        default=None,
        description="Filter by the household characteristic category of a"
        + " table, e.g. 'Race/ethnicity of households'. If None, all"
        + " categories of the selected table are included. Ignored by the"
        + " by_state table, which has no category dimension.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " survey year or the first year of a 3-year period. If None, returns"
        + " from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " survey year or the first year of a 3-year period. If None, returns"
        + " up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in FOOD_SECURITY_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(FOOD_SECURITY_TABLES)
            )
        return table

    @field_validator("category", mode="before", check_fields=False)
    @classmethod
    def _validate_category(cls, v):
        """Normalize category to a stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None


class FoodSecurityInTheUnitedStatesData(NullTokenMixin, Data):
    """USDA ERS Food Security in the United States Data.

    One selected table pivoted to a wide layout: the food-security status
    measures spread into value columns while the survey year or 3-year period
    stays in the rows, with any varying household characteristic or State
    folded into the period label so each row is uniquely labeled.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Food Security in the United States",
                "$.description": "Prevalence of household and child food"
                " security, food insecurity, and very low food security by"
                " year, household characteristic, and State, from the USDA"
                " Economic Research Service and the Current Population Survey"
                " Food Security Supplement.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the survey year for annual"
        + " tables ('2008') or the 3-year period for the by_state table"
        + " ('2006-2008'), with any varying household characteristic or State"
        + " prefixed so each row is uniquely labeled"
        + " ('Households with children — 2008', 'CA — 2006-2008').",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 320,
            }
        },
    )


class FoodSecurityInTheUnitedStatesFetcher(
    Fetcher[
        FoodSecurityInTheUnitedStatesQueryParams,
        list[FoodSecurityInTheUnitedStatesData],
    ]
):
    """Fetch USDA ERS Food Security in the United States."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FoodSecurityInTheUnitedStatesQueryParams:
        """Transform the query params."""
        return FoodSecurityInTheUnitedStatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FoodSecurityInTheUnitedStatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import (
            ers_food_security_in_the_united_states,
        )

        return await ers_food_security_in_the_united_states.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: FoodSecurityInTheUnitedStatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FoodSecurityInTheUnitedStatesData]:
        """Pivot the long-format rows into period rows with series as columns."""
        filtered: list[tuple[int, dict]] = []
        for order, record in enumerate(data):
            year = record["sort_year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            if (
                query.category is not None
                and record["category"] is not None
                and record["category"] != query.category
            ):
                continue
            filtered.append((order, record))
        varying = {
            field: len(
                {
                    record[field]
                    for _, record in filtered
                    if record[field] is not None and not is_null_token(record[field])
                }
            )
            > 1
            for field in DIM_FIELDS
        }
        pivoted: dict[tuple, dict] = {}
        combo_order: dict[tuple, int] = {}
        col_order: list[str] = []
        for order, record in filtered:
            combo = tuple(record[field] for field in DIM_FIELDS)
            key = (record["year"], *combo)
            row = pivoted.get(key)
            if row is None:
                combo_order.setdefault(combo, len(combo_order))
                dim_values = [
                    record[field]
                    for field in DIM_FIELDS
                    if varying[field]
                    and record[field] is not None
                    and not is_null_token(record[field])
                ]
                row = {
                    "_combo": combo_order[combo],
                    "_sort_year": record["sort_year"],
                    "_order": order,
                    "period": " — ".join([*dim_values, record["year"]]),
                }
                pivoted[key] = row
            column = record["series"]
            if column not in col_order:
                col_order.append(column)
            row[column] = record["value"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["_combo"], row["_sort_year"], row["_order"]),
        )
        validated: list[FoodSecurityInTheUnitedStatesData] = []
        for row in results:
            payload: dict[str, Any] = {"period": row["period"]}
            for column in col_order:
                payload[column] = row.get(column)
            validated.append(FoodSecurityInTheUnitedStatesData.model_validate(payload))
        return validated
