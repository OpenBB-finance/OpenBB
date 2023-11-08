"""CFTC Commitment of Traders Reports Search fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_nasdaq.utils.series_ids import CFTC
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cot_search import (
    CotSearchData,
    CotSearchQueryParams,
)


class NasdaqCotSearchQueryParams(CotSearchQueryParams):
    """CFTC Commitment of Traders Reports Search query parameters.

    Source: https://data.nasdaq.com/data/CFTC-commodity-futures-trading-commission-reports/documentation
    """


class NasdaqCotSearchData(CotSearchData):
    """Nasdaq CFTC Commitment of Traders Reports Search data."""


class NasdaqCotSearchFetcher(Fetcher[CotSearchQueryParams, List[NasdaqCotSearchData]]):
    """Nasdaq CFTC Commitment of Traders Reports Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqCotSearchQueryParams:
        return NasdaqCotSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqCotSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Search a curated list of CFTC Commitment of Traders Reports."""
        query_string = query.query  # noqa
        available_cot = pd.DataFrame(CFTC).transpose()
        available_cot.columns = available_cot.columns.str.lower()
        return (
            available_cot[
                available_cot["name"].str.contains(query_string, case=False)
                | available_cot["category"].str.contains(query_string, case=False)
                | available_cot["subcategory"].str.contains(query_string, case=False)
                | available_cot["symbol"].str.contains(query_string, case=False)
            ]
            .reset_index(drop=True)
            .to_dict("records")
        )

    @staticmethod
    def transform_data(
        query: CotSearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqCotSearchData]:
        return [NasdaqCotSearchData.model_validate(d) for d in data]
