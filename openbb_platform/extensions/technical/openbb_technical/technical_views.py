"""Views for the technical Extension."""

# pylint: disable=too-many-locals,use-dict-literal

from typing import TYPE_CHECKING, Any, Dict, Tuple

from openbb_charting.core.to_chart import to_chart
from openbb_charting.styles.colors import LARGE_CYCLER

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


class TechnicalViews:
    """Technical Views."""

    @staticmethod
    def technical_sma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Plot simple moving average chart."""
        if "ma_type" not in kwargs:
            kwargs["ma_type"] = "sma"
        return _ta_ma(**kwargs)

    @staticmethod
    def technical_ema(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Exponential moving average chart."""
        if "ma_type" not in kwargs:
            kwargs["ma_type"] = "ema"
        return _ta_ma(**kwargs)

    @staticmethod
    def technical_hma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Hull moving average chart."""
        if "ma_type" not in kwargs:
            kwargs["ma_type"] = "hma"
        return _ta_ma(**kwargs)

    @staticmethod
    def technical_wma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Weighted moving average chart."""
        if "ma_type" not in kwargs:
            kwargs["ma_type"] = "wma"
        return _ta_ma(**kwargs)

    @staticmethod
    def technical_zlma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Zero lag moving average chart."""
        if "ma_type" not in kwargs:
            kwargs["ma_type"] = "zlma"
        return _ta_ma(**kwargs)

    @staticmethod
    def technical_aroon(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Technical Aroon Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
            data = kwargs["data"]
        else:
            data = basemodel_to_df(
                kwargs["obbject_item"], index=kwargs.get("index", "date")
            )

        if "date" in data.columns:
            data = data.set_index("date")

        if "symbol" in data.columns and len(data.symbol.unique()) > 1:
            raise ValueError(
                "Please provide data with only one symbol and columns for OHLC."
            )

        symbol = kwargs.get("symbol", "")

        volume = kwargs.get("volume") is True
        title = f"Aroon Indicator & Oscillator {symbol}"

        length = kwargs.get("length", 25)
        scalar = kwargs.get("scalar", 100)
        symbol = kwargs.get("symbol", "")

        ta = PlotlyTA()
        fig = ta.plot(  # type: ignore
            data,
            dict(aroon=dict(length=length, scalar=scalar)),
            title,
            False,
            volume=volume,
        )

        content = fig.show(external=True).to_plotly_json()

        return fig, content

    @staticmethod
    def technical_macd(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Plot moving average convergence divergence chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
            data = kwargs["data"]
        else:
            data = basemodel_to_df(
                kwargs["obbject_item"], index=kwargs.get("index", "date")
            )

        if "date" in data.columns:
            data = data.set_index("date")

        if "symbol" in data.columns and len(data.symbol.unique()) > 1:
            raise ValueError(
                "Please provide data with only one symbol and columns for OHLC."
            )

        fast = kwargs.get("fast", 12)
        slow = kwargs.get("slow", 26)
        signal = kwargs.get("signal", 9)
        symbol = kwargs.get("symbol", "")

        title = f"{symbol.upper()} MACD"
        volume = kwargs.get("volume") is True

        ta = PlotlyTA()
        fig = ta.plot(  # type: ignore
            data,
            dict(macd=dict(fast=fast, slow=slow, signal=signal)),
            title,
            False,
            volume=volume,
        )
        content = fig.show(external=True).to_plotly_json()

        return fig, content

    @staticmethod
    def technical_adx(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Average directional movement index chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
            data = kwargs["data"]
        else:
            data = basemodel_to_df(
                kwargs["obbject_item"], index=kwargs.get("index", "date")
            )

        if "date" in data.columns:
            data = data.set_index("date")

        if "symbol" in data.columns and len(data.symbol.unique()) > 1:
            raise ValueError(
                "Please provide data with only one symbol and columns for OHLC."
            )

        length = kwargs.get("length", 14)
        scalar = kwargs.get("scalar", 100.0)
        drift = kwargs.get("drift", 1)
        symbol = kwargs.get("symbol", "")

        ta = PlotlyTA()
        fig = ta.plot(  # type: ignore
            data,
            dict(adx=dict(length=length, scalar=scalar, drift=drift)),
            f"Average Directional Movement Index (ADX) {symbol}",
            False,
            volume=False,
        )
        content = fig.show(external=True).to_plotly_json()

        return fig, content

    @staticmethod
    def technical_rsi(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Relative strength index chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        if "data" in kwargs and isinstance(kwargs["data"], DataFrame):
            data = kwargs["data"]
        else:
            data = basemodel_to_df(
                kwargs["obbject_item"], index=kwargs.get("index", "date")
            )

        if "date" in data.columns:
            data = data.set_index("date")

        if "symbol" in data.columns and len(data.symbol.unique()) > 1:
            raise ValueError(
                "Please provide data with only one symbol and columns for OHLC."
            )

        window = kwargs.get("window", 14)
        scalar = kwargs.get("scalar", 100.0)
        drift = kwargs.get("drift", 1)
        symbol = kwargs.get("symbol", "")

        ta = PlotlyTA()
        fig = ta.plot(  # type: ignore
            data,
            dict(rsi=dict(length=window, scalar=scalar, drift=drift)),
            f"{symbol.upper()} RSI {window}",
            False,
            volume=False,
        )
        content = fig.show(external=True).to_plotly_json()

        return fig, content

    @staticmethod
    def technical_cones(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Volatility Cones Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.core.chart_style import ChartStyle
        from openbb_charting.core.openbb_figure import OpenBBFigure
        from openbb_core.app.utils import basemodel_to_df
        from pandas import DataFrame

        data = kwargs.get("data")

        if isinstance(data, DataFrame) and not data.empty and "window" in data.columns:
            df_ta = data.set_index("window")
        else:
            df_ta = basemodel_to_df(kwargs["obbject_item"], index="window")  # type: ignore

        df_ta.columns = [col.title().replace("_", " ") for col in df_ta.columns]

        # Check if the data is formatted as expected.
        if not all(
            col in df_ta.columns for col in ["Realized", "Min", "Median", "Max"]
        ):
            raise ValueError("Data supplied does not match the expected format.")

        model = (
            str(kwargs.get("model"))
            .replace("std", "Standard Deviation")
            .replace("_", "-")
            .title()
            if kwargs.get("model")
            else "Standard Deviation"
        )

        symbol = str(kwargs.get("symbol")) + " - " if kwargs.get("symbol") else ""

        title = (
            str(kwargs.get("title"))
            if kwargs.get("title")
            else f"{symbol}Realized Volatility Cones - {model} Model"
        )

        colors = [
            "green",
            "red",
            "burlywood",
            "grey",
            "orange",
            "blue",
        ]

        fig = OpenBBFigure()

        fig.update_layout(ChartStyle().plotly_template.get("layout", {}))

        text_color = "black" if ChartStyle().plt_style == "light" else "white"

        for i, col in enumerate(df_ta.columns):
            fig.add_scatter(
                x=df_ta.index,
                y=df_ta[col],
                name=col,
                mode="lines+markers",
                hovertemplate=f"{col}: %{{y}}<extra></extra>",
                marker=dict(
                    color=colors[i],
                    size=11,
                ),
            )

        fig.set_title(title)

        fig.update_layout(
            paper_bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
            plot_bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
            font=dict(color=text_color),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                xanchor="right",
                y=1.02,
                x=1,
                bgcolor=(
                    "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
                ),
            ),
            yaxis=dict(
                ticklen=0,
                showgrid=True,
                showline=True,
                mirror=True,
                zeroline=False,
                gridcolor="rgba(128,128,128,0.3)",
            ),
            xaxis=dict(
                type="category",
                tickmode="array",
                ticklen=0,
                tickvals=df_ta.index,
                ticktext=df_ta.index,
                title_text="Period",
                showgrid=False,
                showline=True,
                mirror=True,
                zeroline=False,
            ),
            margin=dict(l=20, r=20, b=20),
            dragmode="pan",
        )

        content = fig.to_plotly_json()

        return fig, content

    @staticmethod
    def technical_relative_rotation(
        **kwargs: Any,
    ) -> Tuple["OpenBBFigure", Dict[str, Any]]:
        """Relative Rotation Chart."""
        # pylint: disable=import-outside-toplevel
        from openbb_charting.charts import relative_rotation  # noqa
        from openbb_charting.core.chart_style import ChartStyle  # noqa
        from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa
        from openbb_core.app.utils import basemodel_to_df  # noqa

        ratios_df = basemodel_to_df(kwargs["obbject_item"].rs_ratios, index="date")  # type: ignore
        momentum_df = basemodel_to_df(kwargs["obbject_item"].rs_momentum, index="date")  # type: ignore
        benchmark_symbol = kwargs["obbject_item"].benchmark  # type: ignore
        study = kwargs.get("study", None)
        study = str(kwargs["obbject_item"].study) if study is None else str(study)
        show_tails = kwargs.get("show_tails")
        show_tails = True if show_tails is None else show_tails
        tail_periods = int(kwargs.get("tail_periods")) if "tail_periods" in kwargs else 16  # type: ignore
        tail_interval = str(kwargs.get("tail_interval")) if "tail_interval" in kwargs else "week"  # type: ignore
        date = kwargs.get("date") if "date" in kwargs else None  # type: ignore
        show_tails = False if date is not None else show_tails
        if ratios_df.empty or momentum_df.empty:
            raise RuntimeError("Error: No data to plot.")

        if show_tails is True:
            fig = relative_rotation.create_rrg_with_tails(
                ratios_df, momentum_df, study, benchmark_symbol, tail_periods, tail_interval  # type: ignore
            )

        if show_tails is False:
            fig = relative_rotation.create_rrg_without_tails(
                ratios_df, momentum_df, benchmark_symbol, study, date  # type: ignore
            )

        figure = OpenBBFigure(fig)  # pylint: disable=E0606
        font_color = "black" if ChartStyle().plt_style == "light" else "white"
        figure.update_layout(
            paper_bgcolor=(
                "rgba(0,0,0,0)" if font_color == "white" else "rgba(255,255,255,255)"
            ),
            plot_bgcolor="rgba(255,255,255,1)",
            font=dict(color=font_color),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                side="left",
                showline=True,
                zeroline=True,
                mirror=True,
                ticklen=0,
                tickfont=dict(size=14),
                titlefont=dict(size=16),
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                showline=True,
                zeroline=True,
                mirror=True,
                ticklen=0,
                tickfont=dict(size=14),
                titlefont=dict(size=16),
                hoverformat="",
            ),
            hoverlabel=dict(
                font_size=12,
            ),
            hovermode="x",
            hoverdistance=50,
        )
        if kwargs.get("title") is not None:
            figure.set_title(str(kwargs.get("title")))
        content = figure.to_plotly_json()

        return figure, content


def _ta_ma(**kwargs):
    """Plot moving average helper."""
    # pylint: disable=import-outside-toplevel
    from openbb_charting.core.chart_style import ChartStyle
    from openbb_charting.core.openbb_figure import OpenBBFigure
    from openbb_core.app.utils import basemodel_to_df
    from pandas import DataFrame

    index = (
        kwargs.get("index")
        if "index" in kwargs and kwargs.get("index") is not None
        else "date"
    )
    data = kwargs.get("data")
    ma_type = (
        kwargs["ma_type"]
        if "ma_type" in kwargs and kwargs.get("ma_type") is not None
        else "sma"
    )
    ma_types = ma_type.split(",") if isinstance(ma_type, str) else ma_type

    if isinstance(data, DataFrame) and not data.empty:
        data = data.set_index(index) if index in data.columns else data

    if data is None:
        data = basemodel_to_df(kwargs["obbject_item"], index=index)

    if isinstance(data, list):
        data = basemodel_to_df(data, index=index)

    window = (
        kwargs.get("length", [])
        if "length" in kwargs and kwargs.get("length") is not None
        else [50]
    )
    offset = kwargs.get("offset", 0)
    target = (
        kwargs.get("target")
        if "target" in kwargs and kwargs.get("target") is not None
        else "close"
    )

    if target not in data.columns and "close" in data.columns:
        target = "close"

    if target not in data.columns and "close" not in data.columns:
        raise ValueError(f"Column '{target}', or 'close', not found in the data.")

    df = data.copy()
    if target in data.columns:
        df = df[[target]]
        df.columns = ["close"]
    title = (
        kwargs.get("title")
        if "title" in kwargs and kwargs.get("title") is not None
        else f"{ma_type.upper()}"
    )

    fig = OpenBBFigure()
    fig = fig.create_subplots(
        1,
        1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        horizontal_spacing=0.01,
        row_width=[1],
        specs=[[{"secondary_y": True}]],
    )
    fig.update_layout(ChartStyle().plotly_template.get("layout", {}))
    font_color = "black" if ChartStyle().plt_style == "light" else "white"
    ma_df = DataFrame()
    window = [window] if isinstance(window, int) else window
    for w in window:
        for ma_type in ma_types:
            ma_df[f"{ma_type.upper()} {w}"] = getattr(df.ta, ma_type)(
                length=w, offset=offset
            )

    if kwargs.get("dropnan") is True:
        ma_df = ma_df.dropna()
        data = data.iloc[-len(ma_df) :]

    if (
        "candles" in kwargs
        and kwargs.get("candles") is True
        and kwargs.get("target") is None
    ):
        volume = kwargs.get("volume") is True
        fig, _ = to_chart(data, candles=True, volume=volume)

    else:
        ma_df[f"{target}".title()] = data[target]

    for i, col in enumerate(ma_df.columns):
        name = col.replace("_", " ")
        fig.add_scatter(
            x=ma_df.index,
            y=ma_df[col],
            name=name,
            mode="lines",
            hovertemplate=f"{name}: %{{y}}<extra></extra>",
            line=dict(width=1, color=LARGE_CYCLER[i]),
            showlegend=True,
        )

    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        paper_bgcolor=(
            "rgba(0,0,0,0)" if font_color == "white" else "rgba(255,255,255,255)"
        ),
        plot_bgcolor=(
            "rgba(0,0,0,0)" if font_color == "white" else "rgba(255,255,255,0)"
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            y=1.02,
            x=0.95,
            bgcolor="rgba(0,0,0,0)" if font_color == "white" else "rgba(255,255,255,0)",
        ),
        xaxis=dict(
            ticklen=0,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            zeroline=True,
            mirror=True,
        ),
        yaxis=dict(
            ticklen=0,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            zeroline=True,
            mirror=True,
            autorange=True,
        ),
        font=dict(color=font_color),
    )

    content = fig.show(external=True).to_plotly_json()

    return fig, content
