"""ETF Holdings Performance Standard Model."""

from .recent_performance import (
    RecentPerformanceData,
    RecentPerformanceQueryParams,
)


class ETFHoldingsPerformanceQueryParams(RecentPerformanceQueryParams):
    """ETF Holdings Performance Query."""


class ETFHoldingsPerformanceData(RecentPerformanceData):
    """ETF Holdings Performance Data."""
