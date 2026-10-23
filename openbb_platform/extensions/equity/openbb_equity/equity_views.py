"""Views for the Equity Extension."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class EquityViews:
    """Equity Views."""

    @staticmethod
    def equity_price_historical(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Equity Price Historical Chart."""
        price_historical = import_module(
            "openbb_charting.charts.price_historical"
        ).price_historical

        return price_historical(**kwargs)

    @staticmethod
    def equity_price_performance(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Equity Price Performance Chart."""
        price_performance = import_module(
            "openbb_charting.charts.price_performance"
        ).price_performance

        return price_performance(**kwargs)  # ty: ignore[invalid-return-type]

    @staticmethod
    def equity_historical_market_cap(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Equity Historical Market Cap Chart."""
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        line_chart = import_module("openbb_charting.charts.generic_charts").line_chart

        title = kwargs.pop("title", "Historical Market Cap")

        data = DataFrame()

        if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
            data = kwargs["data"]
        elif "data" in kwargs and isinstance(kwargs["data"], list):
            data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
        else:
            data = basemodel_to_df(
                kwargs["obbject_item"],
                index=kwargs.get("index", "date"),
            )

        if "date" in data.columns:
            data = data.set_index("date")

        if data.empty:
            raise ValueError("Data is empty")

        df = data.pivot(columns="symbol", values="market_cap")

        scatter_kwargs = kwargs.pop("scatter_kwargs", {})

        if "hovertemplate" not in scatter_kwargs:
            scatter_kwargs["hovertemplate"] = "%{y}"

        ytital = kwargs.pop("ytitle", "Market Cap ($)")
        y = kwargs.pop("y", df.columns.tolist())

        fig = line_chart(
            data=df,
            title=title,
            y=y,
            ytitle=ytital,
            same_axis=True,
            scatter_kwargs=scatter_kwargs,
            **kwargs,
        )
        content = fig.show(external=True).to_plotly_json()

        return fig, content  # ty: ignore[invalid-return-type]
