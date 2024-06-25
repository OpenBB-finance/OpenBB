"""Views for the Currency Extension."""

from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class CurrencyViews:
    """Currency Views."""

    @staticmethod
    def currency_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Currency Price Historical Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)
