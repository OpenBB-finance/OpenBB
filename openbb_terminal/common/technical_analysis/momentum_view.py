"""Momentum View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.common.technical_analysis import momentum_model, ta_helpers
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_cci(
    data: pd.DataFrame,
    window: int = 14,
    scalar: float = 0.0015,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots CCI Indicator

    Parameters
    ----------

    data : pd.DataFrame
        Dataframe of OHLC
    window : int
        Length of window
    scalar : float
        Scalar variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(cci=dict(length=window, scalar=scalar)),
        f"{symbol.upper()} CCI",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cci",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_macd(
    data: pd.Series,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots MACD signal

    Parameters
    ----------
    data : pd.Series
        Values to input
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(macd=dict(fast=n_fast, slow=n_slow, signal=n_signal)),
        f"{symbol.upper()} MACD",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "macd",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_rsi(
    data: pd.Series,
    window: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots RSI Indicator

    Parameters
    ----------
    data : pd.Series
        Values to input
    window : int
        Length of window
    scalar : float
        Scalar variable
    drift : int
        Drift variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if isinstance(data, pd.DataFrame):
        return console.print("[red]Please send a series and not a dataframe[/red]\n")

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(rsi=dict(length=window, scalar=scalar, drift=drift)),
        f"{symbol.upper()} RSI {window}",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rsi",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_stoch(
    data: pd.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots stochastic oscillator signal

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    symbol : str
        Stock ticker symbol
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return None

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(stoch=dict(k=fastkperiod, d=slowdperiod, smooth_k=slowkperiod)),
        f"Stochastic Relative Strength Index (STOCH RSI) on {symbol}",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "stoch",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_fisher(
    data: pd.DataFrame,
    window: int = 14,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots Fisher Indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    window : int
        Length of window
    symbol : str
        Ticker string
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(fisher=dict(length=window)),
        f"{symbol.upper()} Fisher Transform",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "fisher",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_cg(
    data: pd.Series,
    window: int = 14,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots center of gravity Indicator

    Parameters
    ----------
    data : pd.Series
        Series of values
    window : int
        Length of window
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(cg=dict(length=window)),
        f"{symbol.upper()} Centre of Gravity",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cg",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_clenow_momentum(
    data: pd.Series,
    symbol: str = "",
    window: int = 90,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Prints table and plots clenow momentum

    Parameters
    ----------
    data : pd.Series
        Series of values
    symbol : str
        Symbol that the data corresponds to
    window : int
        Length of window
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.clenow_chart(df["Close"])
    """
    fig = PlotlyTA.plot(
        data,
        dict(clenow=dict(window=window)),
        f"Clenow Momentum Exponential Regression on {symbol}",
        False,
        volume=False,
    )

    r2, coef, _ = momentum_model.clenow_momentum(data, window)

    df_ta = pd.DataFrame.from_dict(
        {
            "R^2": f"{r2:.5f}",
            "Fit Coef": f"{coef:.5f}",
            "Factor": f"{coef * r2:.5f}",
        },
        orient="index",
    )

    print_rich_table(
        df_ta,
        show_index=True,
        headers=[""],
        title=f"Clenow Exponential Regression Factor on {symbol}",
        show_header=False,
        export=bool(export),
        print_to_console=True,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "clenow",
        df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


def display_demark(
    data: pd.DataFrame,
    symbol: str = "",
    min_to_show: int = 5,
    export: str = "",
    sheet_name: Optional[str] = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plot demark sequential indicator

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame of values
    symbol : str
        Symbol that the data corresponds to
    min_to_show: int
        Minimum value to show
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.demark_chart(df)
    """
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return None

    fig = PlotlyTA.plot(
        data,
        dict(demark=dict(min_val=min_to_show)),
        f"{symbol.upper()} Demark Sequential",
        volume=False,
    )

    demark_df = momentum_model.demark_seq(data[close_col])
    demark_df.index = data.index

    stock_data = data.copy()
    stock_data["up"] = demark_df.TD_SEQ_UPa
    stock_data["down"] = demark_df.TD_SEQ_DNa

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "demark",
        stock_data,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


# pylint: disable=too-many-arguments,R0913
@log_start_end(log=logger)
def display_ichimoku(
    data: pd.DataFrame,
    symbol: str = "",
    conversion_period: int = 9,
    base_period: int = 26,
    lagging_line_period: int = 52,
    displacement: int = 26,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots Ichimoku clouds

    Parameters
    ----------
    data: pd.DataFrame
        OHLC data
    conversion_period: int
        Conversion line period
    base_period: int
        Base line period
    lagging_line_period: int
        Lagging line period
    displacement: int
        Displacement variable
    symbol: str
        Ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load(symbol="aapl")
    >>> openbb.ta.ichimoku_clouds(data=df)
    """

    data = pd.DataFrame(data)
    data.index.name = "date"

    if ta_helpers.check_columns(data) is None:
        return None

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(
            ichimoku=dict(
                conversion_period=conversion_period,
                base_period=base_period,
                lagging_line_period=lagging_line_period,
                displacement=displacement,
            )
        ),
        f"Ichimoku Clouds for {symbol.upper()}",
        True,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "ichimoku",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
