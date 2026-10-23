"""Views for the Quantitative Extension."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


class QuantitativeViews:
    """Quantitative Views."""

    @staticmethod
    def quantitative_factors(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Factor Regression Coefficient / P-Value Heatmap."""
        # pylint: disable=import-outside-toplevel
        from openbb_quantitative.views.factors_heatmap import factors_heatmap

        return factors_heatmap(**kwargs)

    @staticmethod
    def quantitative_risk_decomposition(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Variance-Share Decomposition Stacked Bar."""
        # pylint: disable=import-outside-toplevel
        from openbb_quantitative.views.risk_decomposition_bar import (
            risk_decomposition_bar,
        )

        return risk_decomposition_bar(**kwargs)

    @staticmethod
    def quantitative_attribution(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Return Attribution Stacked Bar."""
        # pylint: disable=import-outside-toplevel
        from openbb_quantitative.views.attribution_bar import attribution_bar

        return attribution_bar(**kwargs)

    @staticmethod
    def quantitative_rolling_factors(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Rolling Factor Beta Line Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_quantitative.views.rolling_factors_line import (
            rolling_factors_line,
        )

        return rolling_factors_line(**kwargs)
