"""Views for the ETF Extension."""

from importlib import import_module
from typing import Any


class EtfViews:
    """Etf Views."""

    @staticmethod
    def etf_historical(
        **kwargs,
    ) -> tuple[Any, dict[str, Any]]:
        """Etf Price Historical Chart."""
        price_historical = import_module(
            "openbb_charting.charts.price_historical"
        ).price_historical

        return price_historical(**kwargs)

    @staticmethod
    def etf_price_performance(
        **kwargs,
    ) -> tuple[Any, dict[str, Any]]:
        """Etf Price Performance Chart."""
        price_performance = import_module(
            "openbb_charting.charts.price_performance"
        ).price_performance

        return price_performance(**kwargs)

    @staticmethod
    def etf_holdings(
        **kwargs,
    ) -> tuple[Any, dict[str, Any]]:
        """Equity Compare Groups Chart."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        bar_chart = import_module("openbb_charting.charts.generic_charts").bar_chart

        if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
            data = kwargs["data"]
        elif "data" in kwargs and isinstance(kwargs["data"], list):
            data = basemodel_to_df(kwargs["data"], index=None)
        else:
            data = basemodel_to_df(kwargs["obbject_item"], index=None)

        if "weight" not in data.columns:
            raise OpenBBError("No 'weight' column found in the data.")

        orientation = kwargs.get("orientation", "h")
        limit = kwargs.get("limit", 20)
        symbol = kwargs["standard_params"].get("symbol")
        title = kwargs.get("title", f"Top {limit} {symbol} Holdings")
        layout_kwargs = kwargs.get("layout_kwargs", {})

        data = data.sort_values("weight", ascending=False)
        limit = min(limit, len(data))
        target = data.head(limit)[["symbol", "weight"]].set_index("symbol")
        target = target.multiply(100)
        axis_title = "Weight (%)"

        fig = bar_chart(
            target.reset_index(),
            "symbol",
            ["weight"],
            title=title,
            xtitle=axis_title if orientation == "h" else None,
            ytitle=axis_title if orientation == "v" else None,
            orientation=orientation,
        )

        fig.update_layout(
            hovermode="x" if orientation == "v" else "y",
            margin=dict(r=0, l=50) if orientation == "h" else None,
        )

        fig.update_traces(
            hovertemplate=(
                "%{y:.3f}%<extra></extra>"
                if orientation == "v"
                else "%{x:.3f}%<extra></extra>"
            )
        )

        if layout_kwargs:
            fig.update_layout(**layout_kwargs)

        content = fig.show(external=True).to_plotly_json()

        return fig, content
