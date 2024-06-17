"""Views for the crypto Extension."""

from typing import Any, Dict, Tuple

from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.utils.price_historical import price_historical


class CryptoViews:
    """Crypto Views."""

    @staticmethod
    def crypto_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """Crypto Price Historical Chart."""
        return price_historical(**kwargs)
