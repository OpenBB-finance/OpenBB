"""FMP Earnings Calendar fetcher."""


from datetime import datetime
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.earnings_calendar import (
    EarningsCalendarData,
    EarningsCalendarQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPEarningsCalendarQueryParams(EarningsCalendarQueryParams):
    """FMP Earnings Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/
    """


class FMPEarningsCalendarData(EarningsCalendarData):
    """FMP Earnings Calendar Data."""

    class Config:
        fields = {
            "eps_estimated": "epsEstimated",
            "revenue_estimated": "revenueEstimated",
            "updated_from_date": "updatedFromDate",
            "fiscal_date_ending": "fiscalDateEnding",
        }

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("updatedFromDate", pre=True, check_fields=False)
    def updated_from_date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("fiscalDateEnding", pre=True, check_fields=False)
    def fiscal_date_ending_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPEarningsCalendarFetcher(
    Fetcher[
        EarningsCalendarQueryParams,
        EarningsCalendarData,
        FMPEarningsCalendarQueryParams,
        FMPEarningsCalendarData,
    ]
):
    @staticmethod
    def transform_query(
        query: EarningsCalendarQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPEarningsCalendarQueryParams:
        return FMPEarningsCalendarQueryParams(symbol=query.symbol, limit=query.limit)

    @staticmethod
    def extract_data(
        query: FMPEarningsCalendarQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPEarningsCalendarData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"historical/earning_calendar/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPEarningsCalendarData)

    @staticmethod
    def transform_data(
        data: List[FMPEarningsCalendarData],
    ) -> List[EarningsCalendarData]:
        return data_transformer(data, EarningsCalendarData)
