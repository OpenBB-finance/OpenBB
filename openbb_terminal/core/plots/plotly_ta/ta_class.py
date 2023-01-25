import importlib
import inspect
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import pandas as pd

from openbb_terminal.base_helpers import console
from openbb_terminal.config_terminal import theme
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.plots.plotly_ta.base import PltTA
from openbb_terminal.core.plots.plotly_ta.data_classes import (
    ChartIndicators,
    ProcessTA_Data,
)
from openbb_terminal.stocks.stocks_helper import display_candle


class PlotlyTA(PltTA):
    inchart_colors = theme.get_colors()
    plugins = []
    show_volume = True

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
        self.params = self.indicators.get_params()

        if type(self) is PlotlyTA:
            self.load_plugins()

    @property
    def ma_mode(self) -> List[str]:
        return list(set(self.__ma_mode__))

    @ma_mode.setter
    def ma_mode(self, value: List[str]):
        self.__ma_mode__ = value

    @property
    def inchart(self) -> List[str]:
        return list(set(self.__inchart__))

    @inchart.setter
    def inchart(self, value: List[str]):
        self.__inchart__ = value

    @property
    def subplots(self) -> List[str]:
        return list(set(self.__subplots__))

    @subplots.setter
    def subplots(self, value: List[str]):
        self.__subplots__ = value

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

        check_rows = min(len(self.check_subplots(subplots)), 3)

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

        if not self.show_volume and len(self.check_subplots(subplots)) > 3:
            rows = 4
            row_width = [0.2, 0.2, 0.2, 0.4]

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
                    and issubclass(obj, (PltTA))
                    and obj != self.__class__
                ):
                    if obj not in self.plugins:
                        self.plugins.append(obj)

    def load_plugins(self):
        """Loads plugins into PlotlyTA class"""
        self._locate_plugins()
        self.add_plugins(self.plugins)

    def plot_candle(self, symbol: str = ""):
        """Returns candle plotly figure"""
        fig = display_candle(symbol, self.df_stock, external_axes=True)
        return fig

    def plot_line(self, symbol: str = ""):
        """Returns line plotly figure"""
        fig = OpenBBFigure.create_subplots(
            2,
            1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            subplot_titles=(f"{symbol}", "Volume"),
            row_width=[0.2, 0.7],
        )
        fig.add_scatter(
            x=self.df_stock.index,
            y=self.df_stock["Close"],
            connectgaps=True,
            row=1,
            col=1,
        )
        if self.show_volume:
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
        fig.update_layout(yaxis_title="Stock Price ($)", bargap=0, bargroupgap=0)
        fig.add_logscale_menus()
        return fig

    def plot_fig(
        self,
        fig: OpenBBFigure = None,
        symbol: str = "",
        candlestick: bool = True,
        volume: bool = True,
    ) -> OpenBBFigure:
        """Takes candle plotly fig and adds users active indicators"""

        df_ta = self.calculate_indicators()
        self.show_volume = volume

        if hasattr(self.df_stock, "name"):
            symbol = self.df_stock.name

        if not fig:
            if candlestick:
                fig = self.plot_candle(symbol)
            else:
                fig = self.plot_line(symbol)
                self.inchart_colors = theme.get_colors()[1:]

        fig_new = {}
        inchart_index, ma_done = 0, False

        fig, subplot_row = self.process_fig(fig)

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

                if (
                    subplot_row > 5
                    and indicator != self.indicators.get_active_ids()[-1]
                ):
                    remaining = self.indicators.get_active_ids()[
                        self.indicators.get_active_ids().index(indicator) + 1 :
                    ]
                    console.print(
                        f"[bold red]Reached max number of subplots, skipping {', '.join(remaining)}[/]"
                    )
                    break
            except Exception as e:
                console.print(f"[bold red]Error plotting {indicator}: {e}[/]")
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

    def process_fig(self, fig: OpenBBFigure) -> Tuple[OpenBBFigure, int]:
        """Processes fig to add subplots and volume"""

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
            if trace.name == "Volume":
                try:
                    list(fig.select_annotations(selector=dict(text="Volume")))[
                        0
                    ].text = ""
                except IndexError:
                    pass
                if not self.show_volume:
                    row -= 1
                    continue
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
                fig.update_yaxes(nticks=5, row=row, col=col)

            new_subplot.add_trace(trace, row=row, col=col)

        subplot_row = row + 1

        fig_json = fig.to_plotly_json()["layout"]
        for layout in fig_json:
            if layout in ["xaxis2", "yaxis2"] and not self.show_volume:
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
