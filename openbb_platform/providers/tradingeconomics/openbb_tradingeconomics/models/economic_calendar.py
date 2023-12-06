"""Trading Economics Economic Calendar Model."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Set, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from openbb_tradingeconomics.utils import url_generator
from openbb_tradingeconomics.utils.countries import country_list
from pandas import to_datetime
from pydantic import Field, field_validator

IMPORTANCE = Literal["Low", "Medium", "High"]

GROUPS = Literal[
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


class TEEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """Trading Economics Economic Calendar Query.

    Source: https://docs.tradingeconomics.com/economic_calendar/
    """

    # TODO: Probably want to figure out the list we can use.
    country: Optional[Union[str, List[str]]] = Field(
        default=None, description="Country of the event"
    )
    importance: Optional[IMPORTANCE] = Field(
        default=None, description="Importance of the event."
    )
    group: Optional[GROUPS] = Field(default=None, description="Grouping of events")

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, v: Union[str, List[str], Set[str]]):
        """Validate the country input."""
        if isinstance(v, str):
            return v.lower().replace(" ", "_")
        return ",".join([country.lower().replace(" ", "_") for country in list(v)])

    @field_validator("importance")
    @classmethod
    def importance_to_number(cls, v):
        string_to_value = {"Low": 1, "Medium": 2, "High": 3}
        return string_to_value.get(v, None)


class TEEconomicCalendarData(EconomicCalendarData):
    """Trading Economics Economic Calendar Data."""

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
    def validate_date(cls, v: str) -> datetime:
        return to_datetime(v, utc=True)


class TEEconomicCalendarFetcher(
    Fetcher[
        TEEconomicCalendarQueryParams,
        List[TEEconomicCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the Trading Economics endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TEEconomicCalendarQueryParams:
        """Transform the query params."""
        return TEEconomicCalendarQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TEEconomicCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TE endpoint."""
        api_key = credentials.get("tradingeconomics_api_key") if credentials else ""

        if query.country is not None:
            country = (
                query.country.split(",") if "," in query.country else query.country
            )
            country = [country] if isinstance(country, str) else country

            for c in country:
                if c.replace("_", " ").lower() not in country_list:
                    raise ValueError(f"{c} is not a valid country")
            query.country = country

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
        query: TEEconomicCalendarQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TEEconomicCalendarData]:
        """Return the transformed data."""
        return [TEEconomicCalendarData.model_validate(d) for d in data]
