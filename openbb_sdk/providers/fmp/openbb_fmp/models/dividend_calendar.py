"""FMP Dividend Calendar fetcher."""

from datetime import datetime
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.dividend_calendar import (
    DividendCalendarData,
    DividendCalendarQueryParams,
)


from pydantic import validator

from openbb_fmp.utils.helpers import get_data_many, get_querystring


class FMPDividendCalendarQueryParams(DividendCalendarQueryParams):
    """FMP Dividend Calendar query.

    Source: https://site.financialmodelingprep.com/developer/docs/dividend-calendar-api/

    The maximum time interval between the start and end date can be 3 months.
    Default value for time interval is 1 month.

    Parameter
    ---------
    start_date : date
        The starting date to fetch the dividend calendar from. Default value is the
        previous day from the last month.
    end_date : date
        The ending date to fetch the dividend calendar till. Default value is the
        previous day from the current month.
    """


class FMPDividendCalendarData(DividendCalendarData):
    """FMP Dividend Calendar data."""

    @validator("date", pre=True)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("recordDate", pre=True)
    def record_date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("paymentDate", pre=True)
    def payment_date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("declarationDate", pre=True)
    def declaration_date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPDividendCalendarFetcher(
    Fetcher[
        DividendCalendarQueryParams,
        DividendCalendarData,
        FMPDividendCalendarQueryParams,
        FMPDividendCalendarData,
    ]
):
    @staticmethod
    def transform_query(
        query: DividendCalendarQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPDividendCalendarQueryParams:
        return FMPDividendCalendarQueryParams(
            start_date=query.start_date,
            end_date=query.end_date,
            **extra_params or {},
        )

    @staticmethod
    def extract_data(
        query: FMPDividendCalendarQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPDividendCalendarData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(), [])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}/stock_dividend_calendar?{query_str}&apikey={api_key}"
        return get_data_many(url, FMPDividendCalendarData)

    @staticmethod
    def transform_data(
        data: List[FMPDividendCalendarData],
    ) -> List[DividendCalendarData]:
        return data_transformer(data, DividendCalendarData)
