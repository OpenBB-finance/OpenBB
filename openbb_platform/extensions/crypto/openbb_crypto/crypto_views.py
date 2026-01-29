"""crypto 扩展及其视图。"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class CryptoViews:
    """Crypto 视图。"""

    @staticmethod
    def crypto_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """加密货币价格历史图表。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)
