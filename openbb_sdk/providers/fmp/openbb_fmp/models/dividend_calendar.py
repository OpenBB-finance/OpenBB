"""FMP Dividend Calendar fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_fmp.utils.helpers import get_data_many, get_querystring
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.dividend_calendar import (
    DividendCalendarData,
    DividendCalendarQueryParams,
)
from pydantic import validator


class FMPDividendCalendarQueryParams(DividendCalendarQueryParams):
    """FMP Dividend Calendar Query.

    Source: https://site.financialmodelingprep.com/developer/docs/dividend-calendar-api/

    The maximum time interval between the start and end date can be 3 months.
    Default value for time interval is 1 month.
    """


class FMPDividendCalendarData(DividendCalendarData):
    """FMP Dividend Calendar Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("recordDate", pre=True, check_fields=False)
    def record_date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the record date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("paymentDate", pre=True, check_fields=False)
    def payment_date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the payment date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None

    @validator("declarationDate", pre=True, check_fields=False)
    def declaration_date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the declaration date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPDividendCalendarFetcher(
    Fetcher[
        FMPDividendCalendarQueryParams,
        List[FMPDividendCalendarData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPDividendCalendarQueryParams:
        """Transform the query params. Start and end dates are set to 1 1 year interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPDividendCalendarQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FMPDividendCalendarQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(by_alias=True), [])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}/stock_dividend_calendar?{query_str}&apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPDividendCalendarData]:
        """Return the transformed data."""
        return [FMPDividendCalendarData.parse_obj(d) for d in data]
