"""CFTC Commitment of Traders Reports Search fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cot_search import (
    CotSearchData,
    CotSearchQueryParams,
)
from openbb_quandl.utils.series_ids import CFTC


class QuandlCotSearchQueryParams(CotSearchQueryParams):
    """CFTC Commitment of Traders Reports Search query parameters.

    Source: https://data.nasdaq.com/data/CFTC-commodity-futures-trading-commission-reports/documentation
    """


class QuandlCotSearchData(CotSearchData):
    """Quandl CFTC Commitment of Traders Reports Search data."""


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
    ) -> List[Dict]:
        """Search a curated list of CFTC Commitment of Traders Reports."""
        query_string = query.query  # noqa
        available_cot = pd.DataFrame(CFTC).transpose()
        available_cot.columns = available_cot.columns.str.lower()
        return (
            available_cot.query(
                "name.str.contains(@query_string, case=False)"
                "| category.str.contains(@query_string, case=False)"
                "| subcategory.str.contains(@query_string, case=False)"
                "| symbol.str.contains(@query_string, case=False)"
            )
            .reset_index(drop=True)
            .to_dict("records")
        )

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[QuandlCotSearchData]:
        return [QuandlCotSearchData(**d) for d in data]
