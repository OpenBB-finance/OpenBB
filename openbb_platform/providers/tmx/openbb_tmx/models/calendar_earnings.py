"""TMX Earnings Calendar Model."""

# pylint: disable=unused-argument
import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_earnings import (
    CalendarEarningsData,
    CalendarEarningsQueryParams,
)
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pandas import date_range
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
    }

    name: str = Field(description="The company's name.", alias="companyName")
    eps_consensus: Optional[float] = Field(
        default=None, description="The consensus estimated EPS in dollars."
    )
    eps_actual: Optional[float] = Field(
        default=None, description="The actual EPS in dollars."
    )
    eps_surprise: Optional[float] = Field(
        default=None, description="The EPS surprise in dollars."
    )
    surprise_percent: Optional[float] = Field(
        default=None,
        description="The EPS surprise as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    reporting_time: Optional[str] = Field(
        default=None,
        description="The time of the report - i.e., before or after market.",
    )

    @field_validator("surprise_percent", mode="before", check_fields=False)
    @classmethod
    def percent_validate(cls, v):  # pylint: disable=E0213
        """Return the percent as a normalized value."""
        return float(v) / 100 if v else None


class TmxCalendarEarningsFetcher(
    Fetcher[TmxCalendarEarningsQueryParams, List[TmxCalendarEarningsData]]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxCalendarEarningsQueryParams:
        """Transform the query."""
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
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        results: List[Dict] = []
        user_agent = get_random_agent()
        dates = date_range(query.start_date, end=query.end_date)

        async def create_task(date, results):
            """Create a task for a single date in the range."""
            data = []
            date = date.strftime("%Y-%m-%d")
            payload = gql.get_earnings_date_payload.copy()
            payload["variables"]["date"] = date
            url = "https://app-money.tmx.com/graphql"
            r = await get_data_from_gql(
                method="POST",
                url=url,
                data=json.dumps(payload),
                headers={
                    "Host": "app-money.tmx.com",
                    "Referer": "https://money.tmx.com/",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                },
                timeout=3,
            )
            try:
                if (
                    "data" in r
                    and r["data"].get("getEnhancedEarningsForDate") is not None
                ):
                    data = r["data"].get("getEnhancedEarningsForDate")
                    data = [{"report_date": date, **d} for d in data]
            except Exception as e:
                raise RuntimeError(e) from e
            if len(data) > 0:
                results.extend(data)
            return results

        tasks = [create_task(date, results) for date in dates if date.weekday() < 5]

        await asyncio.gather(*tasks)

        return sorted(results, key=lambda x: x["report_date"])

    @staticmethod
    def transform_data(
        query: TmxCalendarEarningsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxCalendarEarningsData]:
        """Return the transformed data."""
        results = [{k: (None if v == "N/A" else v) for k, v in d.items()} for d in data]
        return [TmxCalendarEarningsData.model_validate(d) for d in results]
