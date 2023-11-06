"""ETF Holdings performance data model."""
from .recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)


class ETFHoldingsPerformanceQueryParams(RecentPerformanceQueryParams):
    """ETF Performance QueryParams."""


class ETFHoldingsPerformanceData(RecentPerformanceData):
    """ETF performance data."""
