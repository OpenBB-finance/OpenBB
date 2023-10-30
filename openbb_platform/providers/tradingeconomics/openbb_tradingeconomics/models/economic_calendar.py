"""Trading Economics Earnings Calendar fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from dateutil import parser
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_provider.utils.countries import country_list
from openbb_provider.utils.helpers import make_request
from openbb_tradingeconomics.utils import url_generator
from pydantic import Field, field_validator


class TEEarningsCalendarQueryParams(EconomicCalendarQueryParams):
    """TE Economic Calendar Query.

    Source: https://docs.tradingeconomics.com/economic_calendar/
    """

    importance: Literal["low", "medium", "high"] = Field(
        default="high",
        description="Importance of the event.",
    )
    group: Optional[
        Literal[
            "interest rate",
            "inflation",
            "bonds",
            "consumer",
            "gdp",
            "government",
            "housing",
            "labour",
            "markets",
            "money",
            "prices",
            "trade",
            "business",
        ]
    ] = Field(default=None, description="Grouping of events")

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(
        cls, country: Optional[Union[str, List[str]]]
    ) -> Optional[List[str]]:
        if country is None:
            return None
        if isinstance(country, str):
            country = [country]
        countries = list(map(lambda x: x.lower(), country))
        if any(c not in country_list for c in countries):
            raise ValueError(f"'{country}' is not a valid country")
        return countries


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

    category: Optional[str] = Field(default=None, description="Category of event.")
    reference: Optional[str] = Field(
        default=None,
        description="Abbreviated period for which released data refers to.",
    )
    source: Optional[str] = Field(default=None, description="Source of the data.")
    sourceurl: Optional[str] = Field(default=None, description="Source URL.")
    forecast: Optional[str] = Field(
        default=None, description="Trading Economics projections"
    )
    url: Optional[str] = Field(default=None, description="Trading Economics URL")
    importance: Optional[Literal["Low", "Medium", "High"]] = Field(
        default=None, description="Importance of the event."
    )
    currency: Optional[str] = Field(default=None, description="Currency of the data.")
    unit: Optional[str] = Field(default=None, description="Unit of the data.")

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
    def transform_data(
        query: TEEarningsCalendarQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TEEarningsCalendarData]:
        """Return the transformed data."""
        return [TEEarningsCalendarData.model_validate(d) for d in data]
