"""Views for the currency Extension."""

from typing import Any, Dict, Tuple

from openbb_charting import Charting
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.utils.price_historical import price_historical
from openbb_core.app.model.extension import Extension

ext = Extension(
    name="currency_views",
    description="Create custom charts from OBBject data for the currency extension.",
)


@ext.charting_accessor
class CurrencyViews:
    """Currency Views."""

    def __init__(self, charting: Charting) -> None:
        """Initialize the Currency Views."""
        self._charting = charting

    @staticmethod
    def currency_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """Currency Price Historical Chart."""
        return price_historical(**kwargs)
