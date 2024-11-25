"""Views for the Empty Extension."""

# pylint: disable=unused-import
# flake8: noqa: F401

from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure

# If `openbb-charting` was installed, this will be used to create a chart.
# Process the data by accessing, "kwargs["obbject_item"]", the function results.
# The return is a Tuple of the OpenBBFigure and a Dict of the data, so it can be
# returned to the Fast API endpoint. Use `fig.to_plotly_json()` to convert the
# OpenBBFigure to a JSON serializable object.


class EmptyViews:
    """Empty Views."""

    # @staticmethod
    # def empty_hello(  # noqa: PLR0912
    #    **kwargs,
    # ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    #    """Get Derivatives Price Historical Chart."""
    # pylint: disable=import-outside-toplevel
    # from openbb_charting.charts.price_historical import price_historical

    # return price_historical(**kwargs)
