"""Technical Analysis class for Plotly."""

# pylint: disable=R0902
import importlib
import inspect
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

import pandas as pd

from openbb_charting.core.chart_style import ChartStyle
from openbb_charting.core.openbb_figure import OpenBBFigure

from .base import PltTA
from .data_classes import ChartIndicators
from .ta_helpers import check_columns

charting_EXTENSION_PATH = Path(__file__).parent.parent.parent
CHARTING_INSTALL_PATH = charting_EXTENSION_PATH.parent
PLUGINS_PATH = Path(__file__).parent / "plugins"
PLOTLY_TA: Optional["PlotlyTA"] = None

if TYPE_CHECKING:
    from openbb_core.app.model.charts.charting_settings import ChartingSettings


class PlotlyTA(PltTA):
    """Plotly Technical Analysis class.

    This class is a singleton. It is created and then reused, to assure
    the plugins are only loaded once. This is done by overriding the __new__
    method. The __init__ method is overridden to do nothing, except to clear
    the internal data structures.

    Attributes
    ----------
    inchart_colors (List[str]):
        List of colors for inchart indicators
    show_volume (bool):
        Whether to show the volume subplot
    ma_mode (List[str]):
        List of available moving average modes
    inchart (List[str]):
        List of available inchart indicators
    subplots (List[str]):
        List of available subplots

    StaticMethods
    -------------
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
    >>> from openbb import obb
    >>> from charting.core.plotly_ta.ta_class import PlotlyTA

    >>> df = obb.equity.price.historical("SPY")
    >>> indicators = dict(
    >>>     sma=dict(length=[20, 50, 100]),
    >>>     adx=dict(length=14),
    >>>     macd=dict(fast=12, slow=26, signal=9),
    >>>     rsi=dict(length=14),
    >>> )
    >>> fig = PlotlyTA.plot(df, indicators=indicators)
    >>> fig.show()

    If you want to plot the chart with the same indicators, you can
    reuse the same instance of the class as follows:

    >>> ta = PlotlyTA()
    >>> fig = ta.plot(df, indicators=indicators)
    >>> df2 = obb.equity.price.historical("AAPL")
    >>> fig2 = ta.plot(df2)
    >>> fig.show()
    >>> fig2.show()
    """

    inchart_colors: List[str] = []
    plugins: List[Type[PltTA]] = []
    df_ta: pd.DataFrame = None
    close_column: Optional[str] = "close"
    has_volume: bool = True
    show_volume: bool = True
    prepost: bool = False
    charting_settings: Optional["ChartingSettings"] = None
    theme: Optional[ChartStyle] = None

    def __new__(cls, *args, **kwargs):
        """Method is overridden to create a singleton instance of the class."""
        cls.charting_settings = kwargs.pop("charting_settings", cls.charting_settings)
        cls.theme = cls.setup_theme(
            chart_style=getattr(cls.charting_settings, "chart_style", ""),
            user_styles_directory=getattr(
                cls.charting_settings, "user_styles_directory", ""
            ),
        )
        cls.inchart_colors = cls.theme.get_colors()

        global PLOTLY_TA  # pylint: disable=global-statement # noqa
        if PLOTLY_TA is None:
            # Creates the instance of the class and loads the plugins
            # We set the global variable to the instance of the class so that
            # the plugins are only loaded once
            PLOTLY_TA = super().__new__(cls)
            PLOTLY_TA._locate_plugins(
                getattr(cls.charting_settings, "debug_mode", False)
            )
            PLOTLY_TA.add_plugins(PLOTLY_TA.plugins)

        return PLOTLY_TA

    def __init__(self, *args, **kwargs):
        """Method is overridden to do nothing, except to clear the internal data structures."""
        if not args and not kwargs:
            self._clear_data()
        else:
            self.df_fib = None
            super().__init__(*args, **kwargs)

    @staticmethod
    def setup_theme(chart_style, user_styles_directory) -> ChartStyle:
        """Setup theme for charting."""
        return ChartStyle(chart_style, user_styles_directory)

    @property
    def ma_mode(self) -> List[str]:
        """List of available moving average modes."""
        return list(set(self.__ma_mode__))

    @ma_mode.setter
    def ma_mode(self, value: List[str]):
        """Set list of available moving average modes."""
        self.__ma_mode__ = value

    @property
    def inchart(self) -> List[str]:
        """List of available inchart indicators."""
        return list(set(self.__inchart__))

    @inchart.setter
    def inchart(self, value: List[str]):
        """Set list of available inchart indicators."""
        self.__inchart__ = value

    @property
    def subplots(self) -> List[str]:
        """List of available subplots."""
        return list(set(self.__subplots__))

    @subplots.setter
    def subplots(self, value: List[str]):
        """Set list of available subplots."""
        self.__subplots__ = value

    # pylint: disable=R0913
    def __plot__(
        self,
        df_stock: Union[pd.DataFrame, pd.Series],
        indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        prepost: bool = False,
        fig: Optional[OpenBBFigure] = None,
        volume_ticks_x: int = 7,
    ) -> OpenBBFigure:
        """Method should not be called directly. Use the PlotlyTA.plot() static method instead."""
        if isinstance(df_stock, pd.Series):
            df_stock = df_stock.to_frame()

        if not isinstance(indicators, ChartIndicators):
            indicators = ChartIndicators.from_dict(indicators or dict(dict()))

        # Apply to_datetime to the index in a way that handles daylight savings.
        df_stock.loc[:, "date"] = df_stock.index  # type: ignore
        df_stock["date"] = df_stock["date"].apply(pd.to_datetime)
        df_stock.index = df_stock["date"]  # type: ignore
        df_stock.drop(columns=["date"], inplace=True)

        self.indicators = indicators
        self.intraday = df_stock.index[-2].time() != df_stock.index[-1].time()
        self.df_stock = df_stock.sort_index(ascending=True)
        self.close_column = check_columns(self.df_stock)
        self.params = self.indicators.get_params()

        self.has_volume = "volume" in self.df_stock.columns and bool(
            self.df_stock["volume"].sum() > 0
        )
        self.show_volume = volume and self.has_volume

        self.prepost = prepost

        return self.plot_fig(
            fig=fig, symbol=symbol, candles=candles, volume_ticks_x=volume_ticks_x
        )

    @staticmethod
    def plot(
        df_stock: Union[pd.DataFrame, pd.Series],
        indicators: Optional[Union[ChartIndicators, Dict[str, Dict[str, Any]]]] = None,
        symbol: str = "",
        candles: bool = True,
        volume: bool = True,
        prepost: bool = False,
        fig: Optional[OpenBBFigure] = None,
        volume_ticks_x: int = 7,
    ) -> OpenBBFigure:
        """Plot a chart with the given indicators.

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
        volume_ticks_x : int, optional
            Number to multiply volume, by default 7
        """
        if indicators is None and PLOTLY_TA is not None:
            indicators = PLOTLY_TA.indicators

        return PlotlyTA().__plot__(
            df_stock, indicators, symbol, candles, volume, prepost, fig, volume_ticks_x
        )

    @staticmethod
    def _locate_plugins(debug: Optional[bool] = False) -> None:
        """Locate all the plugins in the plugins folder."""
        path = (
            Path(sys.executable).parent
            if hasattr(sys, "frozen")
            else CHARTING_INSTALL_PATH
        )
        if debug:
            warnings.warn(f"[bold green]Loading plugins from {path}[/]")
            warnings.warn("[bold green]Plugins found:[/]")

        for plugin in Path(__file__).parent.glob("plugins/*_plugin.py"):
            python_path = plugin.relative_to(path).with_suffix("")

            if debug:
                warnings.warn(f"    [bold red]{plugin.name}[/]")
                warnings.warn(f"        [bold yellow]{python_path}[/]")
                warnings.warn(f"        [bold bright_cyan]{__package__}[/]")
                warnings.warn(f"        [bold magenta]{python_path.parts}[/]")
                warnings.warn(
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
                ) and obj not in PlotlyTA.plugins:
                    PlotlyTA.plugins.append(obj)

    def _clear_data(self):
        """Clear and reset all data to default values."""
        self.df_stock = None
        self.indicators = {}
        self.params = None
        self.intraday = False
        self.show_volume = True

    def calculate_indicators(self):
        """Return dataframe with all indicators."""
        return self.indicators.to_dataframe(self.df_stock.copy(), self.ma_mode)

    def get_subplot(self, subplot: str) -> bool:
        """Return True if subplots will be able to be plotted with current data."""
        if subplot == "volume":
            return self.show_volume

        if subplot in ["ad", "adosc", "obv", "vwap"] and not self.has_volume:
            self.indicators.remove_indicator(subplot)
            warnings.warn(
                f"[bold red]Warning:[/] [yellow]{subplot.upper()}"
                " requires volume data to be plotted but no volume data was found."
                " Indicator will not be plotted.[/]"
            )
            return False

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
                output = output.dropna()

                if output is None or output.empty:
                    output = False

            return True

        except Exception:
            output = False

        return output

    def check_subplots(self, subplots: list) -> list:
        """Return list of subplots that can be plotted with current data."""
        output = []
        for subplot in subplots:
            if self.get_subplot(subplot):
                output.append(subplot)

        return output

    def get_fig_settings_dict(self):
        """Return dictionary with settings for plotly figure."""
        row_params = {
            "0": dict(rows=1, row_width=[1]),
            "1": dict(rows=2, row_width=[0.3, 0.7]),
            "2": dict(rows=3, row_width=[0.15, 0.15, 0.7]),
            "3": dict(rows=4, row_width=[0.2, 0.2, 0.2, 0.4]),
            "4": dict(rows=5, row_width=[0.15, 0.15, 0.15, 0.15, 0.4]),
        }

        check_active = self.indicators.get_active_ids()
        subplots = [subplot for subplot in self.subplots if subplot in check_active]

        check_rows = min(len(self.check_subplots(subplots)), 4)
        check_rows += 1 if "aroon" in subplots and (check_rows + 1) < 5 else 0

        specs = [[{"secondary_y": True}]] + [[{"secondary_y": False}]] * check_rows

        output = row_params.get(str(check_rows), dict(rows=1, row_width=[1]))
        output.update(dict(cols=1, vertical_spacing=0.04, specs=specs))

        return output

    def init_plot(self, symbol: str = "", candles: bool = True) -> OpenBBFigure:
        """Create plotly figure with subplots.

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
        fig = OpenBBFigure(charting_settings=self.charting_settings)
        fig = fig.create_subplots(
            1,
            1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            horizontal_spacing=0.01,
            row_width=[1],
            specs=[[{"secondary_y": True}]],
        )
        cc_linewidth = (
            0.8 if len(self.df_stock.index) > 500 else 0.9 if self.intraday else 1.1
        )
        if candles:
            fig.add_candlestick(
                x=self.df_stock.index,
                open=self.df_stock.open,
                high=self.df_stock.high,
                low=self.df_stock.low,
                close=self.df_stock.close,
                decreasing=dict(line=dict(width=cc_linewidth)),
                increasing=dict(line=dict(width=cc_linewidth)),
                name=f"{symbol} OHLC",
                showlegend=False,
                row=1,
                col=1,
                secondary_y=False,
            )
        else:
            fig.add_scatter(
                x=self.df_stock.index,
                y=self.df_stock[self.close_column],
                name=f"{symbol} Close",
                connectgaps=True,
                row=1,
                col=1,
                secondary_y=False,
            )
            fig.update_layout(yaxis=dict(nticks=15))
            if self.theme:
                self.inchart_colors = self.theme.get_colors()[1:]

        fig.set_title(symbol, x=0.5, y=0.98, xanchor="center", yanchor="top")
        return fig

    def plot_fig(
        self,
        fig: Optional[OpenBBFigure] = None,
        symbol: str = "",
        candles: bool = True,
        volume_ticks_x: int = 7,
    ) -> OpenBBFigure:
        """Plot indicators on plotly figure.

        Parameters
        ----------
        fig : OpenBBFigure, optional
            Plotly figure to plot indicators on, by default None
        symbol : str, optional
            Symbol to plot, by default uses the dataframe.name attribute if available or ""
        candles : bool, optional
            Plot a candlestick chart, by default True (if False, plots a line chart)
        volume_ticks_x : int, optional
            Number to multiply volume, by default 7

        Returns
        -------
        fig : OpenBBFigure
            Plotly figure with candlestick/line chart and volume bar chart (if enabled)
        """
        self.df_ta = self.calculate_indicators()

        symbol = (
            self.df_stock.name
            if hasattr(self.df_stock, "name") and not symbol
            else symbol
        )

        figure = self.init_plot(symbol, candles) if fig is None else fig

        subplot_row, fig_new = 2, {}
        inchart_index, ma_done = 0, False

        figure = self.process_fig(figure, volume_ticks_x)

        # Aroon indicator is always plotted first since it has 2 subplot rows
        plot_indicators = sorted(
            self.indicators.get_active_ids(),
            key=lambda x: 50 if x == "aroon" else 999 if x in self.subplots else 1,
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
                        indicator, ma_done = "ma", True  # noqa

                    figure, inchart_index = getattr(self, f"plot_{indicator}")(
                        figure, self.df_ta, inchart_index
                    )
                elif indicator in ["fib", "srlines", "demark", "clenow", "ichimoku"]:
                    figure = getattr(self, f"plot_{indicator}")(figure, self.df_ta)
                else:
                    raise ValueError(f"Unknown indicator: {indicator}")

                fig_new.update(figure.to_plotly_json())

                remaining_subplots = (
                    list(
                        set(plot_indicators[plot_indicators.index(indicator) + 1 :])
                        - set(self.inchart)
                    )
                    if indicator != "ma"
                    else []
                )
                if subplot_row > 5 and remaining_subplots:
                    warnings.warn(
                        f"[bold red]Reached max number of subplots.   "
                        f"Skipping {', '.join(remaining_subplots)}[/]"
                    )
                    break
            except Exception as e:
                warnings.warn(f"[bold red]Error plotting {indicator}: {e}[/]")
                continue

        figure.update(fig_new)
        figure.update_yaxes(
            row=1,
            col=1,
            secondary_y=False,
            nticks=15 if subplot_row < 3 else 10,
            tickfont=dict(size=16),
        )
        figure.update_traces(
            selector=dict(type="scatter", mode="lines"), connectgaps=True
        )
        figure.update_layout(showlegend=False)
        if hasattr(figure, "hide_holidays"):
            figure.hide_holidays(self.prepost)

        if not self.show_volume:
            figure.update_layout(margin=dict(l=20))

        # We remove xaxis labels from all but bottom subplot, and we make sure
        # they all match the bottom one
        xbottom = f"y{subplot_row+1}"
        xaxes = list(figure.select_xaxes())
        for xa in xaxes:
            if xa == xaxes[-1]:
                xa.showticklabels = True
            if not xa.showticklabels and xa.anchor != xbottom:
                xa.showticklabels = False
            if xa.anchor != xbottom:
                xa.matches = xbottom.replace("y", "x")

        return figure

    def process_fig(self, fig: OpenBBFigure, volume_ticks_x: int = 7) -> OpenBBFigure:
        """Process plotly figure before plotting indicators.

        Parameters
        ----------
        fig : OpenBBFigure
            Plotly figure to process
        volume_ticks_x : int, optional
            Number to multiply volume, by default 7

        Returns
        -------
        fig : OpenBBFigure
            Processed plotly figure
        """
        new_subplot = OpenBBFigure(charting_settings=self.charting_settings)
        new_subplot = fig.create_subplots(
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
            new_subplot.add_trace(trace, row=row, col=col, secondary_y=False)

        fig_json = fig.to_plotly_json()["layout"]
        for layout in fig_json:
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

        if self.show_volume:
            new_subplot.add_inchart_volume(
                self.df_stock, self.close_column, volume_ticks_x=volume_ticks_x
            )

        return new_subplot
