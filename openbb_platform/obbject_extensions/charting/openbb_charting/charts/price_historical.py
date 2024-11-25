"""Price historical charting utility."""

# pylint: disable=too-many-branches, too-many-locals, unused-argument


from typing import TYPE_CHECKING, Any, Dict, Tuple

from openbb_charting.styles.colors import LARGE_CYCLER

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


def price_historical(  # noqa: PLR0912
    **kwargs,
) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Equity Price Historical Chart."""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame  # noqa
    from openbb_core.app.utils import basemodel_to_df  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa
    from openbb_charting.core.plotly_ta.ta_class import PlotlyTA  # noqa
    from openbb_charting.core.chart_style import ChartStyle  # noqa
    from openbb_charting.charts.helpers import (  # noqa
        calculate_returns,
        heikin_ashi,
        should_share_axis,
        z_score_standardization,
    )

    if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
        data = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))  # type: ignore
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "date")  # type: ignore
        )

    if "date" in data.columns:
        data = data.set_index("date")

    target = str(kwargs.get("target"))
    normalize = kwargs.get("normalize") is True
    returns = kwargs.get("returns") is True
    same_axis = kwargs.get("same_axis") is True
    text_color = "black" if ChartStyle().plt_style == "light" else "white"
    title = f"{kwargs.get('title')}" if "title" in kwargs else "Historical Prices"
    y1title = ""
    y2title = ""
    candles = True
    multi_symbol = (
        bool(kwargs.get("multi_symbol") is True)
        or (
            "symbol" in data.columns
            and target in data.columns
            and len(data.symbol.unique()) > 1
        )
        or ("target" in kwargs and kwargs.get("target") is not None)
        or "symbol" in data.columns
        or (
            "symbol" not in data.columns
            and bool(data.columns.isin(["open", "high", "low", "close"]).all())
        )
    )
    target = "close" if target is None or target == "None" or target == "" else target

    if multi_symbol is True:
        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]
            y1title = target.title()
        if "symbol" in data.columns and target in data.columns:
            data = data.pivot(columns="symbol", values=target)
            y1title = target
            title = f"Historical {target.title()}"

    indicators = kwargs.get("indicators", {})
    candles = bool(~data.columns.isin(["open", "high", "low", "close"]).all())
    candles = candles if kwargs.get("candles", True) else False
    volume = kwargs.get("volume", True) if "volume" in data.columns else False

    if normalize is True:
        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]
        multi_symbol = True
        candles = False
        volume = False

    if returns is True:
        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]
        multi_symbol = True
        candles = False
        volume = False
    if (  # pylint: disable = R0916
        multi_symbol is False
        and normalize is False
        and returns is False
        and candles is True
    ) or (indicators and multi_symbol is False):
        if (
            "heikin_ashi" in kwargs
            and kwargs["heikin_ashi"] is True
            and candles is True
        ):
            data = heikin_ashi(data)
            title = f"{title} - Heikin Ashi"
        _volume = False
        if "atr" in indicators:  # type: ignore
            _volume = volume
            volume = False
        ta = PlotlyTA()
        fig = ta.plot(  # type: ignore
            data,
            indicators=indicators if indicators else {},  # type: ignore
            symbol=target if candles is False else "",
            candles=candles,
            volume=volume,  # type: ignore
        )
        if _volume is True and "atr" in indicators:  # type: ignore
            fig.add_inchart_volume(data)
        fig.update_layout(
            paper_bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
            plot_bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
            font=dict(color=text_color),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                xanchor="right",
                y=0.95,
                x=-0.01,
                xref="paper",
                font=dict(size=12),
                bgcolor=(
                    "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
                ),
            ),
            xaxis=dict(
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                zeroline=True,
                mirror=True,
                showline=True,
            ),
            xaxis2=dict(
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                zeroline=True,
                mirror=True,
                showline=True,
            ),
            yaxis=dict(
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                zeroline=True,
                mirror=True,
                showline=True,
                tickfont=dict(size=14),
            ),
            yaxis2=dict(
                ticklen=0,
                gridcolor="rgba(128,128,128,0.3)",
            ),
            yaxis3=dict(
                ticklen=0,
                gridcolor="rgba(128,128,128,0.3)",
            ),
            dragmode="pan",
            hovermode="x",
        )

        if kwargs.get("title"):
            title = kwargs["title"]
        fig.update_layout(title=dict(text=title, x=0.5))

        content = fig.to_plotly_json()

        return fig, content

    if multi_symbol is True or candles is False:

        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]

        if "symbol" in data.columns:
            data = data.pivot(columns="symbol", values=target)

        title: str = kwargs.get("title", "Historical Prices")  # type: ignore

        y1title = data.iloc[:, 0].name
        y2title = ""

        if len(data.columns) > 2 or normalize is True or returns is True:
            if returns is True or (len(data.columns) > 2 and normalize is False):
                data = data.apply(calculate_returns)
                title = f"{title} - Cumulative Returns"
                y1title = "Percent"
            if normalize is True:
                if returns is True:
                    title = f"{title.replace(' - Cumulative Returns', '')} - Normalized Cumulative Returns"
                else:
                    title = title + " - Normalized"
                data = data.apply(z_score_standardization)
                y1title = None  # type: ignore
                y2title = None  # type: ignore

        fig = OpenBBFigure()
        fig.update_layout(ChartStyle().plotly_template.get("layout", {}))
        text_color = "white" if ChartStyle().plt_style == "dark" else "black"

        for i, col in enumerate(data.columns):

            hovertemplate = f"{data[col].name}: %{{y}}<extra></extra>"
            yaxis = "y1"
            if y1title and y1title != "Percent":
                yaxis = (
                    (
                        "y1"
                        if should_share_axis(data, col, y1title)  # type: ignore
                        or col == y1title
                        or normalize is True
                        or returns is True
                        else "y2"
                    )
                    if same_axis is False
                    else "y1"
                )

            if yaxis == "y2":
                y2title = data[col].name

            fig.add_scatter(
                x=data.index,
                y=data[col],
                name=data[col].name,
                mode="lines",
                hovertemplate=hovertemplate,
                line=dict(width=2, color=LARGE_CYCLER[i % len(LARGE_CYCLER)]),
                yaxis=yaxis,
            )

    if normalize is True or returns is True:
        y1title = "Percent" if returns is True else None  # type: ignore
        y2title = None  # type: ignore

    if same_axis is True:
        y1title = None  # type: ignore
        y2title = None  # type: ignore

    fig.update_layout(
        paper_bgcolor=(
            "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
        ),
        plot_bgcolor=(
            "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
        ),
        legend=(
            dict(
                orientation="v",
                yanchor="top",
                xanchor="right",
                y=0.95,
                x=-0.01,
                bgcolor=(
                    "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
                ),
            )
            if len(data.columns) > 2
            else dict(
                orientation="h",
                yanchor="bottom",
                xanchor="right",
                y=1.02,
                x=0.98,
                bgcolor=(
                    "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
                ),
            )
        ),
        yaxis1=(
            dict(
                side="right",
                ticklen=0,
                showgrid=True,
                showline=True,
                mirror=True,
                gridcolor="rgba(128,128,128,0.3)",
                title=dict(
                    text=y1title if y1title else None, standoff=20, font=dict(size=20)
                ),
                tickfont=dict(size=14),
                anchor="x",
            )
        ),
        yaxis2=(
            dict(
                overlaying="y",
                side="left",
                ticklen=0,
                showgrid=False,
                title=dict(
                    text=y2title if y2title else None, standoff=10, font=dict(size=20)
                ),
                tickfont=dict(size=14),
                anchor="x",
            )
            if y2title
            else None
        ),
        xaxis=dict(
            ticklen=0,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            showline=True,
            mirror=True,
        ),
        margin=dict(l=20, r=20, b=20, t=20),
        dragmode="pan",
        hovermode="x",
    )
    if kwargs.get("title"):
        title = kwargs["title"]
    fig.update_layout(title=dict(text=title, x=0.5))

    content = fig.show(external=True).to_plotly_json()

    return fig, content
