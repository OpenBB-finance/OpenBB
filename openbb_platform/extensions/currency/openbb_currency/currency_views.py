"""Views for the Currency Extension."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class CurrencyViews:
    """Currency Views."""

    @staticmethod
    def currency_price_historical(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Currency Price Historical Chart."""
        price_historical = import_module(
            "openbb_charting.charts.price_historical"
        ).price_historical

        return price_historical(**kwargs)
