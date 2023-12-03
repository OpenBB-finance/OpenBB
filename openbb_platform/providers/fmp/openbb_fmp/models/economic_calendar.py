"""FMP Economic Calendar Model."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import Field, field_validator


class FMPEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """FMP Economic Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/economic-calendar-api
    """


class FMPEconomicCalendarData(EconomicCalendarData):
    """FMP Economics Calendar Data.

    Source: https://site.financialmodelingprep.com/developer/docs/economic-calendar-api
    """

    __alias_dict__ = {"consensus": "estimate", "importance": "impact"}

    change: Optional[float] = Field(
        description="Value change since previous.",
        default=None,
    )
    change_percent: Optional[float] = Field(
        description="Percentage change since previous.",
        default=None,
        alias="changePercentage",
    )
    updated_at: Optional[datetime] = Field(
        description="Last updated timestamp.", default=None, alias="updatedAt"
    )
    created_at: Optional[datetime] = Field(
        description="Created at timestamp.", default=None, alias="createdAt"
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S") if v else None

    @field_validator("updatedAt", mode="before", check_fields=False)
    def updated_at_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S") if v else None

    @field_validator("createdAt", mode="before", check_fields=False)
    def created_at_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date ending as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S") if v else None


class FMPEconomicCalendarFetcher(
    Fetcher[
        FMPEconomicCalendarQueryParams,
        List[FMPEconomicCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEconomicCalendarQueryParams:
        """Transform the query."""
        if params:
            if params["start_date"] is None:
                params["start_date"] = datetime.now().strftime("%Y-%m-%d")
            if params["end_date"] is None:
                params["end_date"] = datetime.now().strftime("%Y-%m-%d")

        return FMPEconomicCalendarQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEconomicCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the data from the FMP endpoint."""
        response = []
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3/economic_calendar?"

        url = f"{base_url}from={query.start_date}&to={query.end_date}&apikey={api_key}"

        data = make_request(url)

        if data.ok:
            response = data.json()

        return response

    @staticmethod
    def transform_data(
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEconomicCalendarData]:
        """Transform the data."""
        return [FMPEconomicCalendarData.model_validate(d) for d in data]
