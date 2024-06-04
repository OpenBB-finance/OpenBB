"""Views for the index Extension."""

from typing import Any, Dict, Tuple

from openbb_charting import Charting
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.utils.price_historical import price_historical
from openbb_core.app.model.extension import Extension

ext = Extension(
    name="index_views",
    description="Create custom charts from OBBject data for the index extension.",
)


@ext.charting_accessor
class IndexViews:
    """Index Views."""

    def __init__(self, charting: Charting) -> None:
        """Initialize the index Views."""
        self._charting = charting

    @staticmethod
    def index_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> Tuple[OpenBBFigure, Dict[str, Any]]:
        """Index Price Historical Chart."""
        return price_historical(**kwargs)
