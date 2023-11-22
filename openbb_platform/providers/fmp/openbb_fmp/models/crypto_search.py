"""FMP Crypto Search Model."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_search import (
    CryptoSearchData,
    CryptoSearchQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field


class FMPCryptoSearchQueryParams(CryptoSearchQueryParams):
    """FMP Crypto Search Query."""


class FMPCryptoSearchData(CryptoSearchData):
    """FMP Crypto Search Data."""

    currency: Optional[str] = Field(
        description="The currency the crypto trades for.", default=None
    )
    exchange: Optional[str] = Field(
        description="The exchange code the crypto trades on.",
        alias="stockExchange",
        default=None,
    )
    exchange_name: Optional[str] = Field(
        description="The short name of the exchange the crypto trades on.",
        alias="exchangeShortName",
        default=None,
    )


class FMPCryptoSearchFetcher(
    Fetcher[
        FMPCryptoSearchQueryParams,
        List[FMPCryptoSearchData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCryptoSearchQueryParams:
        """Transform the query."""
        return FMPCryptoSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCryptoSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=3,
            endpoint="symbol/available-cryptocurrencies",
            api_key=api_key,
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCryptoSearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCryptoSearchData]:
        """Return the transformed data."""
        cryptos = pd.DataFrame(data)
        if query.query:
            cryptos = cryptos[
                cryptos["symbol"].str.contains(query.query, case=False)
                | cryptos["name"].str.contains(query.query, case=False)
                | cryptos["currency"].str.contains(query.query, case=False)
                | cryptos["stockExchange"].str.contains(query.query, case=False)
                | cryptos["exchangeShortName"].str.contains(query.query, case=False)
            ]
        for col in cryptos:
            if cryptos[col].dtype in ("int", "float"):
                cryptos[col] = cryptos[col].fillna(0)
        return [
            FMPCryptoSearchData.model_validate(d) for d in cryptos.to_dict("records")
        ]
