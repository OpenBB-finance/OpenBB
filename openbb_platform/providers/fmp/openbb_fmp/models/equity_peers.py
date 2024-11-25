"""FMP Equity Peers Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_peers import (
    EquityPeersData,
    EquityPeersQueryParams,
)


class FMPEquityPeersQueryParams(EquityPeersQueryParams):
    """FMP Equity Peers Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Peers
    """


class FMPEquityPeersData(EquityPeersData):
    """FMP Equity Peers Data."""


class FMPEquityPeersFetcher(
    Fetcher[
        FMPEquityPeersQueryParams,
        FMPEquityPeersData,
    ]
):
    """FMP Equity Peers Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEquityPeersQueryParams:
        """Transform the query params."""
        return FMPEquityPeersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityPeersQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import create_url, get_data_one

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = create_url(4, "stock_peers", api_key, query)

        return await get_data_one(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityPeersQueryParams, data: dict, **kwargs: Any
    ) -> FMPEquityPeersData:
        """Return the transformed data."""
        _ = data.pop("symbol", None)
        peers: list = [d for d in data.get("peersList", []) if d]
        data["peersList"] = peers

        return FMPEquityPeersData.model_validate(data)
