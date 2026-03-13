"""Views for the crypto Extension."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class CryptoViews:
    """Crypto Views."""

    @staticmethod
    def crypto_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Crypto Price Historical Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)
