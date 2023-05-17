"""Volatility Technical Indicators View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.common.technical_analysis import ta_helpers, volatility_model
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
)

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_bbands(
    data: pd.DataFrame,
    symbol: str = "",
    window: int = 15,
    n_std: float = 2,
    mamode: str = "sma",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots bollinger bands

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    export : str
        Format of export file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(bbands=dict(length=window, std=n_std, mamode=mamode)),
        f"{symbol.upper()} Bollinger Bands",
        False,
        volume=False,
    )

    if ta_helpers.check_columns(data, high=False, low=False) is None:
        return None

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "bbands",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_donchian(
    data: pd.DataFrame,
    symbol: str = "",
    upper_length: int = 20,
    lower_length: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots donchian channels

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    export : str
        Format of export file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(donchian=dict(upper_length=upper_length, lower_length=lower_length)),
        f"{symbol.upper()} Donchian Channels",
        False,
        volume=False,
    )

    if ta_helpers.check_columns(data) is None:
        return None

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "donchian",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def view_kc(
    data: pd.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots Keltner Channels Indicator

    Parameters
    ----------

    data: pd.DataFrame
        Dataframe of ohlc prices
    window: int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset: int
        Offset value
    symbol: str
        Ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(kc=dict(length=window, scalar=scalar, mamode=mamode, offset=offset)),
        f"{symbol.upper()} Keltner Channels",
        False,
        volume=False,
    )

    if ta_helpers.check_columns(data) is None:
        return None

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "kc",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_atr(
    data: pd.DataFrame,
    symbol: str = "",
    window: int = 14,
    mamode: str = "sma",
    offset: int = 0,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots ATR

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate upper channel
    export : str
        Format of export file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(atr=dict(length=window, mamode=mamode, offset=offset)),
        f"{symbol.upper()} Average True Range",
        False,
        volume=False,
    )

    if ta_helpers.check_columns(data) is None:
        return None

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "atr",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_cones(
    data: pd.DataFrame,
    symbol: str = "",
    lower_q: float = 0.25,
    upper_q: float = 0.75,
    model: str = "STD",
    is_crypto: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots the realized volatility quantiles for the loaded ticker.
    The model used to calculate the volatility is selectable.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame of OHLC prices.
    symbol: str (default = "")
        The ticker symbol.
    lower_q: float (default = 0.25)
        The lower quantile to calculate for.
    upper_q: float (default = 0.75)
        The upper quantile to for.
    is_crypto: bool (default = False)
        If true, volatility is calculated for 365 days instead of 252.
    model: str (default = "STD")
        The model to use for volatility calculation. Choices are:
        ["STD", "Parkinson", "Garman-Klass", "Hodges-Tompkins", "Rogers-Satchell", "Yang-Zhang"]

            Standard deviation measures how widely returns are dispersed from the average return.
            It is the most common (and biased) estimator of volatility.

            Parkinson volatility uses the high and low price of the day rather than just close to close prices.
            It is useful for capturing large price movements during the day.

            Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.
            As markets are most active during the opening and closing of a trading session;
            it makes volatility estimation more accurate.

            Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
            It produces unbiased estimates and a substantial gain in efficiency.

            Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.
            Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term,
            mean return not equal to zero.

            Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
            It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility.
    export : str
        Format of export file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    df_ta = openbb.stocks.load('XLY')
    openbb.ta.cones_chart(data = df_ta, symbol = 'XLY')

    df_ta = openbb.stocks.load('XLE')
    openbb.ta.cones_chart(data = df_ta, symbol = "XLE", lower_q = 0.10, upper_q = 0.90)

    openbb.ta.cones_chart(data = df_ta, symbol = "XLE", model = "Garman-Klass")
    """

    if lower_q > upper_q:
        lower_q, upper_q = upper_q, lower_q

    df_ta = volatility_model.cones(
        data, lower_q=lower_q, upper_q=upper_q, is_crypto=is_crypto, model=model
    )
    lower_q_label = str(int(lower_q * 100))
    upper_q_label = str(int(upper_q * 100))

    if df_ta.empty:
        return None

    fig = OpenBBFigure(xaxis_title="Window of Time (in days)")
    fig.set_title(f"{symbol} - Realized Volatility Cones - {model} Model", x=0.5)

    fig.add_scatter(x=df_ta.index, y=df_ta.Min, name="Min")
    fig.add_scatter(x=df_ta.index, y=df_ta.Max, name="Max")
    fig.add_scatter(x=df_ta.index, y=df_ta.Median, name="Median")
    fig.add_scatter(
        x=df_ta.index,
        y=df_ta["Upper " f"{upper_q_label}" "%"],
        name="Upper " f"{upper_q_label}" "%",
    )
    fig.add_scatter(
        x=df_ta.index,
        y=df_ta["Lower " f"{lower_q_label}" "%"],
        name="Lower " f"{lower_q_label}" "%",
    )
    fig.add_scatter(x=df_ta.index, y=df_ta.Realized, name="Realized")

    fig.update_xaxes(tickmode="array", tickvals=df_ta.index, ticktext=df_ta.index)
    fig.horizontal_legend(x=1, y=1, yanchor="top")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cones",
        df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
