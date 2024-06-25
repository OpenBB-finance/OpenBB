"""Views for the Equity Extension."""

from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class EquityViews:
    """Equity Views."""

    @staticmethod
    def equity_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Equity Price Historical Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)

    @staticmethod
    def equity_price_performance(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Equity Price Performance Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_performance import price_performance

        return price_performance(**kwargs)
