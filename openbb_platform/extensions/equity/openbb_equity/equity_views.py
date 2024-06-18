"""Views for the Equity Extension."""

from typing import Any, Dict, Tuple

from openbb_charting.charts.price_historical import price_historical
from openbb_charting.charts.price_performance import price_performance
from openbb_charting.core.openbb_figure import OpenBBFigure


class EquityViews:
    """Equity Views."""

    @staticmethod
    def equity_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """Equity Price Historical Chart."""
        return price_historical(**kwargs)

    @staticmethod
    def equity_price_performance(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """Equity Price Performance Chart."""
        return price_performance(**kwargs)
