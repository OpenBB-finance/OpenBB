"""TMX Earnings Calendar Model"""

import concurrent.futures
import json
from datetime import (
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.earnings_calendar import (
    EarningsCalendarData,
    EarningsCalendarQueryParams,
)
from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent
from pydantic import Field


class TmxEarningsCalendarQueryParams(EarningsCalendarQueryParams):
    """TMX Earnings Calendar Query."""


class TmxEarningsCalendarData(EarningsCalendarData):
    """TMX Earnings Calendar Data."""

    __alias_dict__ = {
        "eps_estimated": "estimatedEPS",
        "eps_actual": "actualEPS",
    }

    name: str = Field(description="The company's name.", alias="companyName")
    eps_surprise: Optional[float] = Field(
        description="The EPS surprise in dollars.",
        default=None,
        alias="epsSurpriseDollar",
    )
    eps_surprise_percent: Optional[float] = Field(
        description="The EPS surprise as a percent.",
        default=None,
        alias="epsSurprisePercent",
    )


class TmxEarningsCalendarFetcher(
    Fetcher[TmxEarningsCalendarQueryParams, List[TmxEarningsCalendarData]]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEarningsCalendarQueryParams:
        """Transform the query."""
        return TmxEarningsCalendarQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxEarningsCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        results = []
        date = query.date
        date_range = []

        if not date and not query.start_date:
            query.start_date = datetime.today().date()
            query.end_date = datetime.today().date() + timedelta(days=1)
        if date:
            date = datetime.fromisoformat(date) if isinstance(date, str) else date
            date = date_range.append(date)
        if query.start_date and query.end_date:
            date_range = pd.date_range(query.start_date, end=query.end_date)

        def get_calendar_date(date):
            data = []
            date = pd.to_datetime(date)
            # Checks if the date is a weekday, if not makes it next Monday.
            if date.weekday() > 4:
                return data

            date = date.strftime("%Y-%m-%d")

            payload = GQL.get_earnings_date_payload.copy()
            payload["variables"]["date"] = date

            data = []
            url = "https://app-money.tmx.com/graphql"
            r = requests.post(
                url,
                data=json.dumps(payload),
                headers={
                    "Host": "app-money.tmx.com",
                    "Referer": "https://money.tmx.com/",
                    "locale": "en",
                    "Content-Type": "application/json",
                    "User-Agent": get_random_agent(),
                    "Accept": "*/*",
                },
                timeout=3,
            )
            try:
                if r.status_code == 403:
                    raise RuntimeError(f"HTTP error - > {r.text}")
                else:
                    data = r.json()["data"]["getEnhancedEarningsForDate"]
            except Exception as e:
                raise (e)
            data = pd.DataFrame(data).replace("N/A", None)
            if len(data) > 0:
                data["date"] = date

            return data.to_dict("records")

        def get_one(date):
            data = get_calendar_date(date)
            if len(data) > 0:
                results.extend(data)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, date_range)

        return sorted(results, key=lambda x: x["date"], reverse=False)

    @staticmethod
    def transform_data(
        data: List[Dict], **kwargs: Any
    ) -> List[TmxEarningsCalendarData]:
        """Return the transformed data."""
        return [TmxEarningsCalendarData.model_validate(d) for d in data]
