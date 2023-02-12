# pylint: disable=R0902
import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.base_helpers import console
from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.config_terminal import theme
from openbb_terminal.core.plots.plotly_ta.base import PltTA
from openbb_terminal.core.plots.plotly_ta.data_classes import ChartIndicators

PLUGINS_PATH = Path(__file__).parent / "plugins"
PLOTLY_TA: Optional["PlotlyTA"] = None


class PlotlyTA(PltTA):
    """Plotly Technical Analysis class

    This class is a singleton. It is created once and then reused, so that
    the plugins are only loaded once. This is done by overriding the __new__
    method. The __init__ method is overridden to do nothing, except to clear
    the internal data structures.

    Attributes
    ----------
        inchart_colors (List[str]): List of colors for inchart indicators
        show_volume (bool): Show volume
        ma_mode (List[str]): List of moving average modes
        inchart (List[str]): List of inchart indicators
        subplots (List[str]): List of subplots

    StaticMethods
    --------------
        plot(
            df: pd.DataFrame,
            indicators: ChartIndicators,
            fig: Optional[OpenBBFigure] = None,
            symbol: Optional[str] = "",
            candles: bool = True,
            volume: bool = True,
        ) -> OpenBBFigure:
            Plots the chart with the given indicators


    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA

    >>> df = openbb.stocks.load("SPY", interval=15)
    >>> indicators = dict(
    >>>     sma=dict(length=[20, 50, 100]),
    >>>     adx=dict(length=14),
    >>>     macd=dict(fast=12, slow=26, signal=9),
    >>>     rsi=dict(length=14),
    >>> )
    >>> fig = PlotlyTA.plot(df, indicators=indicators)
    >>> fig.show()

    If you want to plot the chart with the same indicators, you can use the
    PlotlyTA.plot() static method. This will reuse the same instance of the
    PlotlyTA class, so that the plugins are only loaded once.

    >>> fig = PlotlyTA.plot(df)
    >>> fig.show()

    """

    inchart_colors = theme.get_colors()
    plugins: List[Type[PltTA]] = []
    df_ta: pd.DataFrame = None
    close_column: Optional[str] = "Close"
    show_volume = True
    prepost: bool = False

    def __new__(cls, *args, **kwargs):
        """This method is overridden to create a singleton instance of the class."""
        global PLOTLY_TA  # pylint: disable=global-statement
        if PLOTLY_TA is None:
            # Creates the instance of the class and loads the plugins
            # We set the global variable to the instance of the class so that
            # the plugins are only loaded once
            PLOTLY_TA = super().__new__(cls)
            PLOTLY_TA._locate_plugins()
            PLOTLY_TA.add_plugins(PLOTLY_TA.plugins)

        return PLOTLY_TA

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        """This method is overridden to do nothing, except to clear the internal data structures."""
        if not args and not kwargs:
            self._clear_data()
        else:
            self.df_fib = None
            super().__init__(*args, **kwargs)

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

    def __plot__(
        self,
        df_stock: Union[pd.DataFrame, pd.Series],
        indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        prepost: bool = False,
        fig: Optional[OpenBBFigure] = None,
    ) -> OpenBBFigure:
        """This method should not be called directly. Use the PlotlyTA.plot() static method instead."""
        if isinstance(df_stock, pd.Series):
            df_stock = df_stock.to_frame()

        if not isinstance(indicators, ChartIndicators):
            indicators = ChartIndicators.from_dict(indicators or dict(dict()))

        self.indicators = indicators
        self.intraday = df_stock.index[-2].time() != df_stock.index[-1].time()
        self.df_stock = df_stock
        self.close_column = ta_helpers.check_columns(self.df_stock)
        self.params = self.indicators.get_params()
        self.show_volume = volume
        self.prepost = prepost

        return self.plot_fig(fig=fig, symbol=symbol, candles=candles)

    @staticmethod
    def plot(
        df_stock: Union[pd.DataFrame, pd.Series],
        indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        prepost: bool = False,
        fig: Optional[OpenBBFigure] = None,
    ) -> OpenBBFigure:
        """Plots the chart with the given indicators

        Parameters
        ----------
        df_stock : pd.DataFrame
            Dataframe with stock data
        indicators : Union[ChartIndicators, Dict[str, Dict[str, Any]]]
            ChartIndicators object or dictionary with indicators and parameters to plot
            Example:
                dict(
                    sma=dict(length=[20, 50, 100]),
                    adx=dict(length=14),
                    macd=dict(fast=12, slow=26, signal=9),
                    rsi=dict(length=14),
                )
        symbol : str, optional
            Symbol to plot, by default uses the dataframe.name attribute if available or ""
        candles : bool, optional
            Plot a candlestick chart, by default True (if False, plots a line chart)
        volume : bool, optional
            Plot volume, by default True
        prepost : bool, optional
            Plot pre and post market data, by default False
        fig : OpenBBFigure, optional
            Plotly figure to plot on, by default None
        """
        return PlotlyTA().__plot__(
            df_stock, indicators, symbol, candles, volume, prepost, fig
        )

    @staticmethod
    def _locate_plugins() -> None:
        """Locate all the plugins in the plugins folder"""
        if hasattr(sys, "frozen"):
            path = Path(sys.executable).parent
        else:
            path = Path(os.getcwd())

        if os.environ.get("DEBUG_MODE", "False").lower() == "true":
            console.print(f"[bold green]Loading plugins from {path}[/]")
            console.print("[bold green]Plugins found:[/]")
        for plugin in Path(__file__).parent.glob("plugins/*_plugin.py"):
            python_path = plugin.relative_to(path).with_suffix("")
            if os.environ.get("DEBUG_MODE", "False").lower() == "true":
                console.print(f"    [bold red]{plugin.name}[/]")
                console.print(f"        [bold yellow]{python_path}[/]")
                console.print(f"        [bold bright_cyan]{__package__}[/]")
                console.print(f"        [bold magenta]{python_path.parts}[/]")
                console.print(
                    f"        [bold bright_magenta]{'.'.join(python_path.parts)}[/]"
                )
            module = importlib.import_module(
                ".".join(python_path.parts), package=__package__
            )
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, (PltTA))
                    and obj != PlotlyTA.__class__
                ):
                    if obj not in PlotlyTA.plugins:
                        PlotlyTA.plugins.append(obj)

    def _clear_data(self):
        """Clears and resets all data to default values"""
        self.df_stock = None
        self.indicators = {}
        self.params = None
        self.intraday = False
        self.show_volume = True

    def calculate_indicators(self):
        """Returns dataframe with all indicators"""
        return self.indicators.to_dataframe(self.df_stock.copy(), self.ma_mode)

    def get_subplot(self, subplot: str) -> bool:
        """Returns True if subplots will be able to be plotted with current data"""
        if subplot == "volume":
            return self.show_volume

        output = False

        try:
            indicator = self.indicators.get_indicator(subplot)
            if indicator is None:
                return False

            output = self.indicators.get_indicator_data(
                self.df_stock.copy(),
                indicator,
                **self.indicators.get_options_dict(indicator.name) or {},
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

        if self.show_volume:
            subplots.append("volume")

        check_rows = min(len(self.check_subplots(subplots)), 4)

        if "aroon" in subplots:
            check_rows += 1

        if check_rows == 0:
            rows = 1
            row_width = [1]
        elif check_rows == 1:
            rows = 2
            row_width = [0.3, 0.7]
        elif check_rows == 2:
            rows = 3
            row_width = [0.15, 0.15, 0.7]
        elif check_rows == 3:
            rows = 4
            row_width = [0.2, 0.2, 0.2, 0.4]
        elif check_rows == 4:
            rows = 5
            row_width = [0.15, 0.15, 0.15, 0.15, 0.4]

        output = {
            "rows": rows,
            "cols": 1,
            "row_width": row_width,
            "vertical_spacing": 0.06,
        }
        return output

    def init_plot(self, symbol: str = "", candles: bool = True) -> OpenBBFigure:
        """Creates plotly figure with subplots

        Parameters
        ----------
        symbol : str, optional
            Symbol to plot, by default uses the dataframe.name attribute if available or ""
        candles : bool, optional
            Plot a candlestick chart, by default True (if False, plots a line chart)

        Returns
        -------
        fig : OpenBBFigure
            Plotly figure with candlestick/line chart and volume bar chart (if enabled)
        """

        fig = OpenBBFigure.create_subplots(
            2,
            1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            subplot_titles=[f"{symbol}", "Volume" if self.show_volume else ""],
            row_width=[0.2, 0.7],
        )
        if candles:
            fig.add_candlestick(
                x=self.df_stock.index,
                open=self.df_stock.Open,
                high=self.df_stock.High,
                low=self.df_stock.Low,
                close=self.df_stock.Close,
                name="OHLC",
                showlegend=False,
                row=1,
                col=1,
            )
        else:
            fig.add_scatter(
                x=self.df_stock.index,
                y=self.df_stock[self.close_column],
                name=f"{symbol} Close",
                connectgaps=True,
                row=1,
                col=1,
            )
            fig.update_layout(yaxis=dict(nticks=15))
            self.inchart_colors = theme.get_colors()[1:]
        if self.show_volume and "Volume" in self.df_stock.columns:
            colors = [
                theme.down_color
                if row.Open < row[self.close_column]
                else theme.up_color
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

        fig.update_layout(yaxis_title="Price ($)")
        return fig

    def plot_fig(
        self,
        fig: Optional[OpenBBFigure] = None,
        symbol: str = "",
        candles: bool = True,
    ) -> OpenBBFigure:
        """Takes candle plotly fig and adds users active indicators"""

        self.df_ta = self.calculate_indicators()

        if hasattr(self.df_stock, "name") and not symbol:
            symbol = self.df_stock.name

        figure = self.init_plot(symbol, candles) if fig is None else fig

        subplot_row, fig_new = 2, {}
        inchart_index, ma_done = 0, False

        if self.show_volume and "Volume" in self.df_stock.columns:
            subplot_row += 1

        figure = self.process_fig(figure)

        plot_indicators = sorted(
            self.indicators.get_active_ids(), key=lambda x: x in self.subplots
        )
        for indicator in plot_indicators:
            try:
                if indicator in self.subplots:
                    figure, subplot_row = getattr(self, f"plot_{indicator}")(
                        figure, self.df_ta, subplot_row
                    )
                elif indicator in self.ma_mode or indicator in self.inchart:
                    if indicator in self.ma_mode:
                        if ma_done:
                            continue
                        indicator, ma_done = "ma", True

                    figure, inchart_index = getattr(self, f"plot_{indicator}")(
                        figure, self.df_ta, inchart_index
                    )
                elif indicator in ["fib", "srlines", "demark", "clenow"]:
                    figure = getattr(self, f"plot_{indicator}")(figure, self.df_ta)
                else:
                    raise ValueError(f"Unknown indicator: {indicator}")

                fig_new.update(figure.to_plotly_json())

                if subplot_row > 5 and indicator != plot_indicators[-1]:
                    remaining = plot_indicators[plot_indicators.index(indicator) + 1 :]
                    console.print(
                        f"[bold red]Reached max number of subplots, skipping {', '.join(remaining)}[/]"
                    )
                    break
            except Exception as e:
                console.print(f"[bold red]Error plotting {indicator}: {e}[/]")
                continue

        figure.update(fig_new)
        figure.update_traces(
            selector=dict(type="scatter", mode="lines"), connectgaps=True
        )
        figure.update_layout(showlegend=False)
        figure.hide_holidays(self.prepost)

        # We remove xaxis labels from all but bottom subplot, and we make sure
        # they all match the bottom one
        xbottom = list(figure.select_xaxes())[-1].anchor
        for xa in figure.select_xaxes():
            if not self.show_volume and subplot_row == 2:
                xa.showticklabels = True
                break
            if not xa.showticklabels and xa.anchor != xbottom:
                xa.showticklabels = False
            if xa.anchor != xbottom:
                xa.matches = xbottom.replace("y", "x")

        return figure

    def process_fig(self, fig: OpenBBFigure) -> OpenBBFigure:
        """Processes fig to add subplots and volume

        Parameters
        ----------
        fig : OpenBBFigure
            Plotly figure to process

        Returns
        -------
        fig : OpenBBFigure
            Processed plotly figure
        """

        new_subplot = OpenBBFigure.create_subplots(
            shared_xaxes=True, **self.get_fig_settings_dict()
        )

        subplots: Dict[str, Dict[str, List[Any]]] = {}
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
                )
                fig.update_yaxes(nticks=5, row=row, col=col)

            new_subplot.add_trace(trace, row=row, col=col)

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

        return new_subplot
