"""Trading Economics Economic Calendar Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_core.provider.utils.helpers import ClientResponse, amake_request, check_item
from openbb_tradingeconomics.utils import url_generator
from openbb_tradingeconomics.utils.countries import COUNTRIES
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
TE_COUNTRY_LIMIT = 28


class TEEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """Trading Economics Economic Calendar Query.

    Source: https://docs.tradingeconomics.com/economic_calendar/
    """

    __json_schema_extra__ = {"country": ["multiple_items_allowed"]}

    # TODO: Probably want to figure out the list we can use.
    country: Optional[str] = Field(default=None, description="Country of the event.")
    importance: Optional[IMPORTANCE] = Field(
        default=None, description="Importance of the event."
    )
    group: Optional[GROUPS] = Field(default=None, description="Grouping of events")

    _number_of_countries: int = 0

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c: str):  # pylint: disable=E0213
        """Validate country."""
        result = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            check_item(v.lower(), COUNTRIES)
            result.append(v.lower())

        cls._number_of_countries = len(result)
        if cls._number_of_countries >= TE_COUNTRY_LIMIT:
            warn(
                f"Trading Economics API tend to fail if the number of countries is above {TE_COUNTRY_LIMIT}."
            )

        return ",".join(result)

    @field_validator("importance")
    @classmethod
    def importance_to_number(cls, v):
        """Convert importance to number."""
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
        """Validate the date."""
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
    async def aextract_data(
        query: TEEconomicCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Union[dict, List[dict]]:
        """Return the raw data from the TE endpoint."""
        api_key = credentials.get("tradingeconomics_api_key") if credentials else ""

        url = url_generator.generate_url(query)
        if not url:
            raise RuntimeError(
                "No url generated. Check combination of input parameters."
            )
        url = f"{url}{api_key}"

        async def callback(response: ClientResponse, _: Any) -> Union[dict, List[dict]]:
            """Return the response."""
            if response.status != 200:
                raise RuntimeError(
                    f"Error in TE request: \n{await response.text()}"
                    f"\nInfo -> TE API tend to fail if the number of countries is above {TE_COUNTRY_LIMIT}."
                )
            return await response.json()

        return await amake_request(url, response_callback=callback, **kwargs)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TEEconomicCalendarQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TEEconomicCalendarData]:
        """Return the transformed data."""
        return [TEEconomicCalendarData.model_validate(d) for d in data]
