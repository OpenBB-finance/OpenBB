"""CFTC Commitment of Traders Reports Search fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cot_search import (
    CotSearchData,
    CotSearchQueryParams,
)

from openbb_quandl.utils.helpers import search_cot


class QuandlCotSearchQueryParams(CotSearchQueryParams):
    """CFTC Commitment of Traders Reports Search query parameters.

    Source: https://data.nasdaq.com/data/CFTC-commodity-futures-trading-commission-reports/documentation
    """


class QuandlCotSearchData(CotSearchData):
    """CBOE Company Search Data."""


class QuandlCotSearchFetcher(Fetcher[CotSearchQueryParams, List[QuandlCotSearchData]]):
    """Quandl CFTC Commitment of Traders Reports Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> QuandlCotSearchQueryParams:
        return QuandlCotSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: QuandlCotSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> dict:
        return search_cot(query.query)

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[QuandlCotSearchData]:
        return [QuandlCotSearchData.parse_obj(d) for d in data]
