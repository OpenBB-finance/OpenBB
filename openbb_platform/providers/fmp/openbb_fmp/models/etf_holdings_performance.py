"""FMP ETF Holdings Performance Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_fmp.models.etf_holdings import FMPEtfHoldingsFetcher
from openbb_fmp.models.price_performance import (
    FMPPricePerformanceData,
    FMPPricePerformanceFetcher,
    FMPPricePerformanceQueryParams,
)
from pandas import DataFrame


class FMPEtfHoldingsPerformanceQueryParams(FMPPricePerformanceQueryParams):
    """FMP ETF Holdings Performance Query."""


class FMPEtfHoldingsPerformanceData(FMPPricePerformanceData):
    """FMP ETF Holdings Performance Data."""


class FMPEtfHoldingsPerformanceFetcher(
    Fetcher[
        FMPEtfHoldingsPerformanceQueryParams,
        List[FMPEtfHoldingsPerformanceData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfHoldingsPerformanceQueryParams:
        """Transform the query."""
        return FMPEtfHoldingsPerformanceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfHoldingsPerformanceQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # Get the holdings data
        holdings = await FMPEtfHoldingsFetcher().aextract_data(
            FMPEtfHoldingsFetcher.transform_query({"symbol": query.symbol}),
            credentials,
            **kwargs,
        )
        if holdings is None:
            raise RuntimeError(f"No holdings data found for {query.symbol}.")
        holdings_list = DataFrame(holdings).asset.unique().tolist()
        # Split into chunks of 500
        chunks = [holdings_list[i : i + 500] for i in range(0, len(holdings_list), 500)]
        # Get price performance for the holdings
        holdings_performance: list = []
        for holding_chunk in chunks:
            holdings_str = (
                ",".join(holding_chunk) if len(holding_chunk) > 1 else holding_chunk[0]
            )
            _performance = await FMPPricePerformanceFetcher().aextract_data(
                FMPPricePerformanceFetcher.transform_query({"symbol": holdings_str}),
                credentials,
                **kwargs,
            )
            holdings_performance.extend(_performance)
        return holdings_performance

    @staticmethod
    def transform_data(
        query: FMPEtfHoldingsPerformanceQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEtfHoldingsPerformanceData]:
        """Return the transformed data."""
        return [FMPEtfHoldingsPerformanceData.model_validate(d) for d in data]
