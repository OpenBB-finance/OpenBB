"""Views for the currency Extension."""

from typing import Any, Dict, Tuple

from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.utils.price_historical import price_historical


class CurrencyViews:
    """Currency Views."""

    @staticmethod
    def currency_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """Currency Price Historical Chart."""
        return price_historical(**kwargs)
