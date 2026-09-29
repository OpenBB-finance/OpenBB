"""TMX Earnings Calendar Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_earnings import (
    CalendarEarningsData,
    CalendarEarningsQueryParams,
)
from pydantic import Field, field_validator


class TmxCalendarEarningsQueryParams(CalendarEarningsQueryParams):
    """TMX Calendar Earnings Query."""


class TmxCalendarEarningsData(CalendarEarningsData):
    """TMX Calendar Earnings Data."""

    __alias_dict__ = {
        "eps_actual": "actualEps",
        "reporting_time": "announceTime",
        "eps_consensus": "estimatedEps",
        "eps_surprise": "epsSurpriseDollar",
        "surprise_percent": "epsSurprisePercent",
        "name": "companyName",
    }

    name: str = Field(description="The company's name.")
    eps_consensus: float | None = Field(
        default=None, description="The consensus estimated EPS in dollars."
    )
    eps_actual: float | None = Field(
        default=None, description="The actual EPS in dollars."
    )
    eps_surprise: float | None = Field(
        default=None, description="The EPS surprise in dollars."
    )
    surprise_percent: float | None = Field(
        default=None,
        description="The EPS surprise as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    reporting_time: str | None = Field(
        default=None,
        description="The time of the report - i.e., before or after market.",
    )

    @field_validator("surprise_percent", mode="before", check_fields=False)
    @classmethod
    def percent_validate(cls, v):  # pylint: disable=E0213
        """Return the percent as a normalized value."""
        return float(v) / 100 if v else None


class TmxCalendarEarningsFetcher(
    Fetcher[TmxCalendarEarningsQueryParams, list[TmxCalendarEarningsData]]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxCalendarEarningsQueryParams:
        """Transform the query."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                datetime.now().date().strftime("%Y-%m-%d")
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = (
                (datetime.now() + timedelta(days=5)).date().strftime("%Y-%m-%d")
            )
        return TmxCalendarEarningsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: TmxCalendarEarningsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Read the earnings reported on each business day of the window.

        Raises
        ------
        EmptyDataError
            If nothing is scheduled across the whole window.
        """
        import asyncio

        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from pandas import date_range

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request

        results: list[dict] = []
        dates = date_range(query.start_date, end=query.end_date)

        async def create_task(date, results):
            """Fetch the earnings reported on a single date."""
            date = date.strftime("%Y-%m-%d")

            try:
                response = await amake_gql_request(
                    "getEnhancedEarningsForDate", gql.EARNINGS_FOR_DATE, {"date": date}
                )
            except OpenBBError as error:
                if "Cannot read properties of undefined" not in str(error):
                    raise

                return results

            data = (response or {}).get("getEnhancedEarningsForDate") or []

            if data:
                results.extend({"report_date": date, **d} for d in data)

            return results

        tasks = [create_task(date, results) for date in dates if date.weekday() < 5]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError(
                f"No earnings were reported between {query.start_date}"
                f" and {query.end_date}."
            )

        return sorted(results, key=lambda x: x["report_date"])

    @staticmethod
    def transform_data(
        query: TmxCalendarEarningsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxCalendarEarningsData]:
        """Return the transformed data."""
        results = [{k: (None if v == "N/A" else v) for k, v in d.items()} for d in data]
        return [TmxCalendarEarningsData.model_validate(d) for d in results]
