"""指数扩展的视图。"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class IndexViews:
    """指数视图。"""

    @staticmethod
    def index_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """指数历史价格图表。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)
