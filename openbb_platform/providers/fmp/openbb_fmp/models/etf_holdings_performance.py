"""FMP ETF Holdings fetcher."""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher

from .etf_holdings import FMPEtfHoldingsFetcher
from .etf_holdings_date import FMPEtfHoldingsDateFetcher
from .price_performance import (
    FMPPricePerformanceData,
    FMPPricePerformanceFetcher,
    FMPPricePerformanceQueryParams,
)


class FMPEtfHoldingsPerformanceQueryParams(FMPPricePerformanceQueryParams):
    """FMP ETF Holdings Performance query."""


class FMPEtfHoldingsPerformanceData(FMPPricePerformanceData):
    """FMP ETF Holdings Data."""


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
    def extract_data(
        query: FMPEtfHoldingsPerformanceQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # Get latest available holdings filing date
        dates = FMPEtfHoldingsDateFetcher().extract_data(
            FMPEtfHoldingsDateFetcher.transform_query(query.model_dump()),
            credentials,
            **kwargs,
        )
        if dates is None:
            return []

        # Get holdings for that date
        holdings = FMPEtfHoldingsFetcher().extract_data(
            FMPEtfHoldingsFetcher.transform_query(
                {"symbol": query.symbol, "date": max([d["date"] for d in dates])}
            ),
            credentials,
            **kwargs,
        )
        if holdings is None:
            return []

        # # Get price performance for the holdings
        holdings_str = ",".join(
            [holding["symbol"] for holding in holdings if holding["symbol"] is not None]
        )
        _performance = FMPPricePerformanceFetcher().extract_data(
            FMPPricePerformanceFetcher.transform_query({"symbol": holdings_str}),
            credentials,
            **kwargs,
        )
        return _performance

    @staticmethod
    def transform_data(
        query: FMPEtfHoldingsPerformanceQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEtfHoldingsPerformanceData]:
        """Return the transformed data."""
        return [FMPEtfHoldingsPerformanceData.model_validate(data[d]) for d in data]
