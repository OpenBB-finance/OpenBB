"""Views for the index Extension."""

from typing import Any, Dict, Tuple

from openbb_charting.charts.price_historical import price_historical
from openbb_charting.core.openbb_figure import OpenBBFigure


class IndexViews:
    """Index Views."""

    @staticmethod
    def index_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """Index Price Historical Chart."""
        return price_historical(**kwargs)
