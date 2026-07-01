"""Federal Reserve Bank of Cleveland Inflation Expectations Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.clevelandfed.org/-/media/files/webcharts"
    "/inflationexpectations/inflation-expectations.xlsx"
)

_TABLES = {
    "expected_inflation": "Expected Inflation",
    "real_interest_rate": "Real Interest Rate",
    "ten_year_decomposition": "Ten-year Expected Chart",
}
# The ten-year chart sheet is published in percent, not the decimal convention
# used by the other two sheets; scale it so every table is comparable.
_PERCENT_TABLES = {"ten_year_decomposition"}


class FederalReserveClevelandInflationQueryParams(QueryParams):
    """Cleveland Fed Inflation Expectations Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": sheet, "value": code} for code, sheet in _TABLES.items()
                ]
            }
        },
    }

    table: Literal[
        "expected_inflation", "real_interest_rate", "ten_year_decomposition"
    ] = Field(
        default="expected_inflation",
        description="Model-implied expected inflation by horizon, the model's real"
        " interest rate by horizon, or the ten-year decomposition into expected"
        " inflation, real risk premium, and inflation risk premium.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveClevelandInflationData(Data):
    """Cleveland Fed Inflation Expectations Data.

    One row per model output month, with one column per horizon series carrying
    that series' decimal-rate estimate (0.025 = 2.5%). The selected table's
    series are pivoted to wide, so the columns vary with the requested table.
    """

    date: dateType = Field(description="The model output month.")


class FederalReserveClevelandInflationFetcher(
    Fetcher[
        FederalReserveClevelandInflationQueryParams,
        list[FederalReserveClevelandInflationData],
    ]
):
    """Cleveland Fed Inflation Expectations Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveClevelandInflationQueryParams:
        """Transform the query params."""
        return FederalReserveClevelandInflationQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveClevelandInflationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the inflation-expectations workbook from the Cleveland Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw inflation-expectations workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "cleveland_inflation",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveClevelandInflationQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveClevelandInflationData]:
        """Melt the selected sheet, then pivot the series to wide rows."""
        from openbb_federal_reserve.utils.workbook import melt_sheet, pivot_wide

        records = melt_sheet(
            data[0]["_raw"],
            _TABLES[query.table],
            start_date=query.start_date,
            end_date=query.end_date,
        )
        if query.table in _PERCENT_TABLES:
            for record in records:
                if record.get("value") is not None:
                    record["value"] = record["value"] / 100
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveClevelandInflationData.model_validate(record)
            for record in rows
        ]
