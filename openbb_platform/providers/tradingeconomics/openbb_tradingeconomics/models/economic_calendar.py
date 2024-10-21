"""Trading Economics Economic Calendar Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_tradingeconomics.utils.countries import COUNTRIES
from pydantic import Field, field_validator, model_validator

IMPORTANCE_CHOICES = ["low", "medium", "high"]

IMPORTANCE = Literal["low", "medium", "high"]

GROUPS_CHOICES = [
    "interest_rate",
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

GROUPS = Literal[
    "interest_rate",
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

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": sorted(COUNTRIES),
        },
        "calendar_id": {
            "multiple_items_allowed": True,
        },
        "importance": {
            "multiple_items_allowed": False,
            "choices": IMPORTANCE_CHOICES,
        },
        "group": {
            "multiple_items_allowed": False,
            "choices": GROUPS_CHOICES,
        },
    }
    country: Optional[str] = Field(
        default=None,
        description="Country of the event.",
    )
    importance: Optional[IMPORTANCE] = Field(
        default=None,
        description="Importance of the event.",
    )
    group: Optional[GROUPS] = Field(
        default=None,
        description="Grouping of events.",
    )
    calendar_id: Union[None, int, str] = Field(
        default=None, description="Get events by TradingEconomics Calendar ID."
    )
    _number_of_countries: int = 0

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import check_item

        result: list = []
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

    @field_validator("importance", mode="after", check_fields=False)
    @classmethod
    def importance_to_number(cls, v):
        """Convert importance to number."""
        string_to_value = {"low": 1, "medium": 2, "high": 3}
        return string_to_value.get(v.lower(), None) if v else None


class TEEconomicCalendarData(EconomicCalendarData):
    """Trading Economics Economic Calendar Data."""

    __alias_dict__ = {
        "date": "Date",
        "country": "Country",
        "category": "Category",
        "event": "Event",
        "reference": "Reference",
        "reference_date": "ReferenceDate",
        "source": "Source",
        "source_url": "SourceURL",
        "actual": "Actual",
        "consensus": "Forecast",
        "forecast": "TEForecast",
        "te_url": "URL",
        "importance": "Importance",
        "currency": "Currency",
        "unit": "Unit",
        "ticker": "Ticker",
        "symbol": "Symbol",
        "previous": "Previous",
        "revised": "Revised",
        "last_updated": "LastUpdate",
        "calendar_id": "CalendarId",
        "date_span": "DateSpan",
    }
    forecast: Optional[Union[str, float]] = Field(
        default=None, description="TradingEconomics projections."
    )
    reference: Optional[str] = Field(
        default=None,
        description="Abbreviated period for which released data refers to.",
    )
    reference_date: Optional[dateType] = Field(
        default=None, description="Date for the reference period."
    )
    calendar_id: Optional[int] = Field(
        default=None, description="TradingEconomics Calendar ID."
    )
    date_span: Optional[int] = Field(
        default=None, description="Date span of the event."
    )
    symbol: Optional[str] = Field(default=None, description="TradingEconomics Symbol.")
    ticker: Optional[str] = Field(
        default=None, description="TradingEconomics Ticker symbol."
    )
    te_url: Optional[str] = Field(
        default=None, description="TradingEconomics URL path."
    )
    source_url: Optional[str] = Field(default=None, description="Source URL.")
    last_updated: Optional[datetime] = Field(
        default=None, description="Last update of the data."
    )

    @field_validator("importance", mode="before", check_fields=False)
    @classmethod
    def importance_to_number(cls, v):
        """Convert importance to number."""
        value_to_string = {1: "Low", 2: "Medium", 3: "High"}
        return value_to_string.get(v) if v else None

    @field_validator("date", "last_updated", mode="before", check_fields=False)
    @classmethod
    def validate_datetime(cls, v: str) -> datetime:
        """Validate the datetime values."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        dt = to_datetime(v, utc=True)
        return dt.replace(microsecond=0)

    @field_validator("reference_date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Validate the date."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        return to_datetime(v, utc=True).date() if v else None

    @model_validator(mode="before")
    @classmethod
    def empty_strings(cls, values):  # pylint: disable=no-self-argument
        """Replace empty strings with None."""
        return (
            {
                k: None if isinstance(v, str) and v == "" else v
                for k, v in values.items()
            }
            if isinstance(values, dict)
            else values
        )


class TEEconomicCalendarFetcher(
    Fetcher[
        TEEconomicCalendarQueryParams,
        list[TEEconomicCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the Trading Economics endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TEEconomicCalendarQueryParams:
        """Transform the query params."""
        return TEEconomicCalendarQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TEEconomicCalendarQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> Union[dict, list[dict]]:
        """Return the raw data from the TE endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_tradingeconomics.utils import url_generator
        from openbb_tradingeconomics.utils.helpers import response_callback

        api_key = credentials.get("tradingeconomics_api_key") if credentials else ""

        if query.group is not None:
            query.group = query.group.replace("_", " ")  # type: ignore

        url = url_generator.generate_url(query)

        if not url:
            raise OpenBBError(
                "No url generated. Check combination of input parameters."
            )

        url = f"{url}{api_key}"

        return await amake_request(url, response_callback=response_callback, **kwargs)

    @staticmethod
    def transform_data(
        query: TEEconomicCalendarQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TEEconomicCalendarData]:
        """Return the transformed data."""
        return [TEEconomicCalendarData.model_validate(d) for d in data]
