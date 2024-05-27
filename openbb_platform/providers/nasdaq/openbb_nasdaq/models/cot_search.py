"""Nasdaq CFTC Commitment of Traders Reports Search Model."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot_search import (
    CotSearchData,
    CotSearchQueryParams,
)
from openbb_nasdaq.utils.series_ids import CFTC

# pylint: disable=W0613


class NasdaqCotSearchQueryParams(CotSearchQueryParams):
    """Nasdaq CFTC Commitment of Traders Reports Search Query.

    Source: https://data.nasdaq.com/data/CFTC-commodity-futures-trading-commission-reports/documentation
    """


class NasdaqCotSearchData(CotSearchData):
    """Nasdaq CFTC Commitment of Traders Reports Search Data."""


class NasdaqCotSearchFetcher(
    Fetcher[NasdaqCotSearchQueryParams, List[NasdaqCotSearchData]]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqCotSearchQueryParams:
        """Transform the query params."""
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
        """Transform the data."""
        return [NasdaqCotSearchData.model_validate(d) for d in data]
