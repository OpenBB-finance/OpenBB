"""FMP Calendar Splits Model."""

from datetime import date
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.calendar_splits import (
    CalendarSplitsData,
    CalendarSplitsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many


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
    async def aextract_data(
        query: FMPCalendarSplitsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query_str = f"from={query.start_date}&to={query.end_date}"
        url = create_url(3, f"stock_split_calendar?{query_str}", api_key)

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCalendarSplitsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCalendarSplitsData]:
        """Return the transformed data."""
        return [FMPCalendarSplitsData.model_validate(d) for d in data]
