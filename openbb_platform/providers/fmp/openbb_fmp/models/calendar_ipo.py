"""FMP Earnings Calendar Model."""

# pylint: disable=unused-argument

from datetime import (
    datetime,
    timedelta,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_ipo import (
    CalendarIpoData,
    CalendarIpoQueryParams,
)
from pydantic import Field


class FMPCalendarIpoQueryParams(CalendarIpoQueryParams):
    """FMP IPO Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs#ipos-calendar
    """

    __alias_dict__ = {
        "start_date": "from",
        "end_date": "to",
    }


class FMPCalendarIpoData(CalendarIpoData):
    """FMP Earnings Calendar Data."""

    __alias_dict__ = {
        "ipo_date": "date",
        "exchange_date": "daa",
        "name": "company",
    }

    exchange_date: datetime | None = Field(
        default=None,
        description="Timezone information for the exchange and date of the IPO.",
    )
    name: str | None = Field(
        default=None,
        description="The name of the entity going public.",
    )
    exchange: str | None = Field(
        default=None,
        description="The exchange where the IPO is listed.",
    )
    actions: str | None = Field(
        default=None,
        description="Actions related to the IPO, such as, Expected, Priced, Filed, Amended.",
    )
    shares: int | float | None = Field(
        default=None,
        description="The number of shares being offered in the IPO.",
    )
    price_range: str | None = Field(
        default=None,
        description="The expected price range for the IPO shares.",
    )
    market_cap: int | float | None = Field(
        default=None,
        description="The estimated market capitalization of the company at the time of the IPO.",
    )


class FMPCalendarIpoFetcher(
    Fetcher[
        FMPCalendarIpoQueryParams,
        list[FMPCalendarIpoData],
    ]
):
    """FMP IPO Calendar Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCalendarIpoQueryParams:
        """FMP IPO Calendar Query Params."""
        now = datetime.today().date()
        transformed_params = params

        if params.get("start_date") is None:
            transformed_params["start_date"] = now

        if params.get("end_date") is None:
            transformed_params["end_date"] = now + timedelta(days=3)

        return FMPCalendarIpoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCalendarIpoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_requests  # noqa
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/stable/ipos-calendar?"
        start_date = query.start_date or datetime.now().date() - timedelta(days=7)
        end_date = query.end_date or datetime.now().date() + timedelta(days=7)

        # Create 90-day chunks between start_date and end_date
        urls: list = []
        current_start = start_date

        while current_start <= end_date:
            chunk_end = min(current_start + timedelta(days=89), end_date)
            url = f"{base_url}from={current_start}&to={chunk_end}&apikey={api_key}"
            urls.append(url)
            current_start = chunk_end + timedelta(days=1)

        # Get data from all URLs
        all_data: list = await amake_requests(
            urls, response_callback=response_callback, **kwargs
        )

        return all_data

    @staticmethod
    def transform_data(
        query: FMPCalendarIpoQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCalendarIpoData]:
        """Return the transformed data."""
        return [
            FMPCalendarIpoData.model_validate(d)
            for d in sorted(data, key=lambda x: x["date"], reverse=True)
        ]
