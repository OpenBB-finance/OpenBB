"""Trading Economics Earnings Calendar fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from dateutil import parser
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_provider.utils.helpers import make_request
from openbb_tradingeconomics.utils import countries, url_generator
from pydantic import field_validator


class TEEarningsCalendarQueryParams(EconomicCalendarQueryParams):
    """FMP Economic Calendar Query.

    Source: https://docs.tradingeconomics.com/economic_calendar/
    """

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(
        cls, country: Optional[Union[str, List[str]]]
    ) -> Optional[List[str]]:
        if country is None:
            return None
        if isinstance(country, str):
            country = [country]

        for c in country:
            if c not in countries.country_list:
                raise ValueError(f"{c} is not a valid country")
        return country


class TEEarningsCalendarData(EconomicCalendarData):
    """TE Earnings Calendar Data."""

    __alias_dict__ = {
        "date": "Date",
        "country": "Country",
        "category": "Category",
        "event": "Event",
        "reference": "Reference",
        "source": "Source",
        "sourceurl": "SourceURL",
        "actual": "Actual",
        "consensus": "Forecast",
        "forecast": "TEForecast",
        "url": "URL",
        "importance": "Importance",
        "currency": "Currency",
        "unit": "Unit",
        "ticker": "Ticker",
        "symbol": "Symbol",
        "previous": "Previous",
        "revised": "Revised",
    }

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, input_date: str) -> datetime:
        return parser.parse(input_date)


class TEEarningsCalendarFetcher(
    Fetcher[
        TEEarningsCalendarQueryParams,
        List[TEEarningsCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the TE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TEEarningsCalendarQueryParams:
        """Transform the query params."""
        return TEEarningsCalendarQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TEEarningsCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TE endpoint."""
        api_key = credentials.get("tradingeconomics_api_key") if credentials else ""

        url = url_generator.generate_url(query)
        if not url:
            raise RuntimeError(
                "No url generated. Check combination of input parameters."
            )
        url = f"{url}{api_key}"
        response = make_request(url, **kwargs)
        if response.status_code != 200:
            raise RuntimeError(f"Error in TE request -> {response.text}")
        return response.json()

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TEEarningsCalendarData]:
        """Return the transformed data."""
        return [TEEarningsCalendarData.model_validate(d) for d in data]
