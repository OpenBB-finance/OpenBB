"""Quandl SP500 Multiples Fetcher."""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.sp500_multiples import (
    SP500MultiplesData,
    SP500MultiplesQueryParams,
)

from openbb_quandl.utils.helpers import get_sp500_multiples


class QuandlSP500MultiplesQueryParams(SP500MultiplesQueryParams):
    """SP500 Multiples query."""


class QuandlSP500MultiplesData(SP500MultiplesData):
    """SP500 Multiples data."""


class QuandlSP500MultiplesFetcher(
    Fetcher[SP500MultiplesQueryParams, SP500MultiplesData]
):
    """Quandl SP500 Multiples Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> QuandlSP500MultiplesQueryParams:
        return QuandlSP500MultiplesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: QuandlSP500MultiplesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[QuandlSP500MultiplesData]:
        api_key = credentials.get("quandl_api_key") if credentials else ""
        data = get_sp500_multiples(
            series_name=query.series_name,
            start_date=query.start_date,
            end_date=query.end_date,
            collapse=query.collapse,
            transform=query.transform,
            api_key=api_key,
        )

        return [QuandlSP500MultiplesData.parse_obj(d) for d in data.to_dict("records")]

    @staticmethod
    def transform_data(
        data: List[QuandlSP500MultiplesData],
    ) -> QuandlSP500MultiplesData:
        return data
