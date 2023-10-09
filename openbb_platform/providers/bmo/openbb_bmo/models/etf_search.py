"""BMO ETF Search fetcher."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_bmo.utils.helpers import get_all_etfs
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field


class BmoEtfSearchQueryParams(EtfSearchQueryParams):
    """BMO ETF Search Query Params"""


class BmoEtfSearchData(EtfSearchData):
    """BMO ETF Search Data."""

    symbol: str = Field(description="The ticker symbol of the asset.")
    name: str = Field(description="The name of the fund.")
    asset_class: Optional[str] = Field(
        description="The asset class of the fund.", default=None
    )
    region: Optional[str] = Field(
        description="The target region of the fund.", default=None
    )
    currency: Optional[str] = Field(
        description="The currency of the fund.", default=None
    )
    trading_currency: Optional[str] = Field(
        description="The currency the fund trades in.", default=None
    )
    fees: Optional[float] = Field(
        description="The management fee of the fund.", default=None
    )
    mer: Optional[float] = Field(
        description="The management expense ratio of the fund.", default=None
    )
    inception_date: Optional[dateType] = Field(
        description="The inception date of the fund.",
        default=None,
    )


class BmoEtfSearchFetcher(
    Fetcher[
        BmoEtfSearchQueryParams,
        List[BmoEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the BMO endpoint."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BmoEtfSearchQueryParams:
        """Transform the query."""
        return BmoEtfSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BmoEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the BMO endpoint."""

        etfs = pd.DataFrame()
        results = pd.DataFrame()
        etfs = get_all_etfs()

        results = etfs[
            etfs["name"].str.contains(query.query, case=False)  # type: ignore
            | etfs["symbol"].str.contains(query.query, case=False)  # type: ignore
            | etfs["asset_class"].str.contains(query.query, case=False)  # type: ignore
            | etfs["region"].str.contains(query.query, case=False)  # type: ignore
            | etfs["currency"].str.contains(query.query, case=False)  # type: ignore
        ]

        results = results.sort_values(by="mer", ascending=False)

        return results.to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[BmoEtfSearchData]:
        """Transform the data."""
        return [BmoEtfSearchData.model_validate(d) for d in data]
