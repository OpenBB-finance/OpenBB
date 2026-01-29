"""股票扩展的视图。"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (
        OpenBBFigure,
    )


class EquityViews:
    """股票视图。"""

    @staticmethod
    def equity_price_historical(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """股票历史价格图表。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)

    @staticmethod
    def equity_price_performance(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """股票价格表现图表。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.price_performance import price_performance

        return price_performance(**kwargs)  # type: ignore

    @staticmethod
    def equity_historical_market_cap(  # noqa: PLR0912
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """股票历史市值图表。"""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts.generic_charts import line_chart
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        title = kwargs.pop("title", "历史市值")

        data = DataFrame()

        if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
            data = kwargs["data"]
        elif "data" in kwargs and isinstance(kwargs["data"], list):
            data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))  # type: ignore
        else:
            data = basemodel_to_df(
                kwargs["obbject_item"],
                index=kwargs.get("index", "date"),  # type: ignore
            )

        if "date" in data.columns:
            data = data.set_index("date")

        if data.empty:
            raise ValueError("数据为空")

        df = data.pivot(columns="symbol", values="market_cap")

        scatter_kwargs = kwargs.pop("scatter_kwargs", {})

        if "hovertemplate" not in scatter_kwargs:
            scatter_kwargs["hovertemplate"] = "%{y}"

        ytital = kwargs.pop("ytitle", "市值 ($)")
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
        content = fig.show(external=True).to_plotly_json()  # type: ignore

        return fig, content  # type: ignore
