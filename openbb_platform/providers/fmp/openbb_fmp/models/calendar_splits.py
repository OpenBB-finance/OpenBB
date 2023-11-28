"""FMP Calendar Splits Model."""

from datetime import date
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_splits import (
    CalendarSplitsData,
    CalendarSplitsQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.helpers import get_data_many


class FMPCalendarSplitsQueryParams(CalendarSplitsQueryParams):
    """FMP Calendar Splits Query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-split-calendar-api/
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}


class FMPCalendarSplitsData(CalendarSplitsData):
    """FMP Calendar Splits Data."""


class FMPCalendarSplitsFetcher(
    Fetcher[
        FMPCalendarSplitsQueryParams,
        List[FMPCalendarSplitsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCalendarSplitsQueryParams:
        """Transform the query params. Start and end dates are set to a 1 year interval."""
        transformed_params = params

        now = date.today()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now

        if params.get("end_date") is None:
            transformed_params["end_date"] = now + relativedelta(days=30)

        return FMPCalendarSplitsQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FMPCalendarSplitsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = "https://financialmodelingprep.com/api/v3/stock_split_calendar"
        query_str = get_querystring(query.model_dump(by_alias=True), [])
        url = f"{base_url}?{query_str}&apikey={api_key}"
        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCalendarSplitsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCalendarSplitsData]:
        """Return the transformed data."""
        return [FMPCalendarSplitsData.model_validate(d) for d in data]
