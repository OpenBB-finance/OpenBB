import importlib
import inspect
import os
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.plots.plotly_ta.base import PltTA
from openbb_terminal.core.plots.plotly_ta.data_classes import (
    ChartIndicators,
    ProcessTA_Data,
)
from openbb_terminal.stocks.stocks_helper import display_candle


class PlotlyTA(PltTA):
    ma_mode = ["sma", "ema", "wma", "hma", "zlma"]
    inchart = ["bbands", "kc", "vwap", "clenow", "denmark", "donchian"]
    inchart_colors = theme.get_colors()
    plugins = []
    subplots = [
        "obv",
        "rsi",
        "macd",
        "stoch",
        "adx",
        "cci",
        "aroon",
        "fisher",
        "adosc",
        "ad",
    ]
    show_volume = True

    def __new__(cls, *args, **kwargs):  # Singleton
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        indicators: Union[ChartIndicators, Dict[str, Dict[str, Any]]],
        df_stock: pd.DataFrame = pd.DataFrame(),
    ):
        if not isinstance(indicators, ChartIndicators):
            indicators = self.process_indicators_kwargs(indicators)

        self.indicators = indicators
        self.intraday = df_stock.index[-2].time() != df_stock.index[-1].time()
        self.df_stock = df_stock
        self.args = self.indicators.get_args()

        self.check_ma = [
            ma for ma in self.ma_mode if ma in self.indicators.get_active_ids()
        ]

        self.bar_opacity = 0.8 if len(df_stock.index) > 500 else 0.7

        if issubclass(type(self), PlotlyTA):
            self.load_plugins()

    def process_indicators_kwargs(
        self,
        ta_kwargs: Dict[str, Dict[str, Any]],
    ) -> ChartIndicators:
        data = {"indicators": []}
        for indicator in ta_kwargs:
            args = []
            for arg in ta_kwargs[indicator]:
                args.append({"label": arg, "values": ta_kwargs[indicator][arg]})
            data["indicators"].append({"name": indicator, "args": args})

        return ChartIndicators(**data)

    def calculate_indicators(self):
        """Returns dataframe with all indicators"""
        df_ta = self.df_stock.copy()
        df_ta = ProcessTA_Data(df_ta, self.indicators).get_indicators()

        return df_ta

    def get_float_precision(self) -> str:
        """Returns f-string precision format"""
        price = self.df_stock.Close.tail(1).values[0]
        float_precision = (
            ",.2f" if price > 1.10 else "" if len(str(price)) < 8 else ".6f"
        )
        return float_precision

    def get_subplot(self, subplot: str) -> bool:
        """Returns True if subplots will be able to be plotted with current data"""
        output = False
        for indicator in self.indicators.get_indicators():
            if indicator.name == subplot:
                try:
                    df_ta = self.df_stock.copy()
                    output = ProcessTA_Data(df_ta, self.indicators).get_indicator_data(
                        indicator,
                        **self.indicators.get_options_dict(indicator.name)
                        if indicator.name
                        in self.indicators.get_arg_names(indicator.name)
                        else {},
                    )
                    if not isinstance(output, bool):
                        output.dropna(inplace=True)

                        if output is None or output.empty:
                            output = False

                    return True

                except Exception:
                    output = False

        return output

    def check_subplots(self, subplots: list) -> list:
        """Returns list of subplots that can be plotted with current data"""
        output = []
        for subplot in subplots:
            if self.get_subplot(subplot):
                output.append(subplot)

        return output

    def get_fig_settings_dict(self):
        """Returns dictionary with settings for plotly figure"""
        check_active = self.indicators.get_active_ids()
        subplots = [subplot for subplot in self.subplots if subplot in check_active]

        check_rows = len(self.check_subplots(subplots))

        if check_rows == 0:
            rows = 2
            row_width = [0.2, 0.7]
        elif check_rows == 1:
            rows = 3
            row_width = [0.15, 0.15, 0.7]
        elif check_rows == 2:
            rows = 4
            row_width = [0.2, 0.2, 0.2, 0.4]
        elif check_rows == 3:
            rows = 5
            row_width = [0.15, 0.15, 0.15, 0.15, 0.4]

        if not self.show_volume:
            rows -= 1
            row_width = row_width[1:]

        output = {
            "rows": rows,
            "cols": 1,
            "row_width": row_width,
            "vertical_spacing": 0.06,
        }
        return output

    def _locate_plugins(self):
        """Locates plugins in plugins folder"""

        for plugin in Path(__file__).parent.glob("plugins/*_plugin.py"):
            python_path = plugin.relative_to(Path(os.getcwd())).with_suffix("")
            module = importlib.import_module(
                ".".join(python_path.with_suffix("").parts)
            )
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, (self.__class__))
                    and obj != self.__class__
                ):
                    print(f"Plugin {obj.__name__} loaded")
                    if obj not in self.plugins:
                        self.plugins.append(obj)

    def load_plugins(self):
        """Loads plugins into PlotlyTA class"""
        self._locate_plugins()
        self.add_plugins(self.plugins)

    def plot_candle(self):
        """Returns candle plotly figure"""
        fig = display_candle("", self.df_stock, external_axes=True)
        return fig

    def plot_line(self):
        """Returns line plotly figure"""
        fig = OpenBBFigure.create_subplots(2, 1)
        fig.add_scatter(
            x=self.df_stock.index,
            y=self.df_stock["Close"],
            connectgaps=True,
            row=1,
            col=1,
        )
        colors = [
            theme.down_color if row.Open < row["Close"] else theme.up_color
            for _, row in self.df_stock.iterrows()
        ]
        fig.add_bar(
            x=self.df_stock.index,
            y=self.df_stock["Volume"],
            name="Volume",
            marker_color=colors,
            row=2,
            col=1,
        )
        return fig

    def plot_fig(
        self,
        fig: OpenBBFigure = None,
        candlestick: bool = True,
        volume: bool = True,
    ) -> OpenBBFigure:
        """Takes candle plotly fig and adds users active indicators"""

        df_ta = self.calculate_indicators()
        print(df_ta.loc["2022-10-08":"2022-10-14"])

        if candlestick:
            fig = self.plot_candle()
        else:
            fig = self.plot_line()
            self.inchart_colors = theme.get_colors()[1:]

        fig_new = {}
        inchart_index, ma_done = 0, False
        self.show_volume = volume

        fig, subplot_row = self.process_fig(fig, 3, volume)

        for indicator in self.indicators.get_active_ids():
            try:
                if indicator in self.subplots:

                    fig, subplot_row = getattr(self, f"plot_{indicator}")(
                        fig, df_ta, subplot_row
                    )
                elif indicator in self.ma_mode or indicator in self.inchart:

                    if indicator in self.ma_mode:
                        if ma_done:
                            continue
                        indicator, ma_done = "ma", True

                    fig, inchart_index = getattr(self, f"plot_{indicator}")(
                        fig, df_ta, inchart_index
                    )
                elif indicator in ["fib", "srlines"]:
                    fig = getattr(self, f"plot_{indicator}")(fig, df_ta)
                else:
                    raise ValueError(f"Unknown indicator: {indicator}")

                fig_new.update(fig.to_plotly_json())
            except Exception as e:
                print(f"Error plotting {indicator}: {e}")
                continue

        fig.update(fig_new)
        fig.update_layout(showlegend=False)
        fig.hide_holidays(df_ta.index)

        # We remove xaxis labels from all but bottom subplot, and we make sure
        # they all match the bottom one
        xbottom = list(fig.select_xaxes())[-1].anchor
        for xa in fig.select_xaxes():
            if not volume and subplot_row == 2:
                xa.showticklabels = True
                break
            if not xa.showticklabels and xa.anchor != xbottom:
                xa.showticklabels = False
            if xa.anchor != xbottom:
                xa.matches = xbottom.replace("y", "x")

        return fig

    def process_fig(
        self, fig: OpenBBFigure, subplot_row: int, volume: bool
    ) -> Tuple[OpenBBFigure, int]:
        new_subplot = OpenBBFigure.create_subplots(
            shared_xaxes=True,
            **self.get_fig_settings_dict(),
        )
        subplots = {}
        grid_ref = fig._validate_get_grid_ref()  # pylint: disable=protected-access
        for r, plot_row in enumerate(grid_ref):
            for c, plot_refs in enumerate(plot_row):
                if not plot_refs:
                    continue
                for subplot_ref in plot_refs:
                    if subplot_ref.subplot_type == "xy":
                        xaxis, yaxis = subplot_ref.layout_keys
                        xref = xaxis.replace("axis", "")
                        yref = yaxis.replace("axis", "")
                        row = r + 1
                        col = c + 1
                        subplots.setdefault(xref, {}).setdefault(yref, []).append(
                            (row, col)
                        )

        for trace in fig.select_traces():
            xref, yref = trace.xaxis, trace.yaxis
            row, col = subplots[xref][yref][0]
            if trace.name == "Volume" and not volume:
                continue
            if trace.name == "Volume":
                fig.add_annotation(
                    xref=f"x{row} domain",
                    yref=f"y{row} domain",
                    text="<b>Volume</b>",
                    x=0,
                    xanchor="right",
                    xshift=-8,
                    y=0.96,
                    font_size=16,
                    font_color="#e0b700",
                    showarrow=False,
                )
            new_subplot.add_trace(trace, row=row, col=col)
        if volume:
            for annotation in fig.layout.annotations:
                if annotation.text == "Volume":
                    # We remove the volume annotation from the original figure
                    annotation.text = ""
                    break

        if row < subplot_row - 1:
            subplot_row = row

        fig_json = fig.to_plotly_json()["layout"]
        for layout in fig_json:
            if layout in ["xaxis2", "yaxis2"] and not volume:
                continue
            if (
                isinstance(fig_json[layout], dict)
                and "domain" in fig_json[layout]
                and any(x in layout for x in ["xaxis", "yaxis"])
            ):
                fig_json[layout]["domain"] = new_subplot.to_plotly_json()["layout"][
                    layout
                ]["domain"]

            fig.layout.update({layout: fig_json[layout]})
            new_subplot.layout.update({layout: fig.layout[layout]})

        return new_subplot, subplot_row
