"""TA Overlap View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import pandas as pd

from openbb_terminal.common.technical_analysis import overlap_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.plots_core.plotly_helper import OpenBBFigure
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_ma(
    data: pd.Series,
    window: List[int] = None,
    offset: int = 0,
    ma_type: str = "EMA",
    symbol: str = "",
    export: str = "",
    external_axes: bool = False,
) -> None:
    """Plots MA technical indicator

    Parameters
    ----------
    data: pd.Series
        Series of prices
    window: List[int]
        Length of EMA window
    offset: int
        Offset variable
    ma_type: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    symbol: str
        Ticker
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.ma_chart(data=df["Adj Close"], symbol="AAPL", ma_type="EMA", window=[20, 50, 100])


    >>> from openbb_terminal.sdk import openbb
    >>> spuk_index = openbb.economy.index(indices = ["^SPUK"])
    >>> openbb.ta.ma_chart(data = spuk_index["^SPUK"], symbol = "S&P UK Index", ma_type = "EMA", window = [20, 50, 100])
    """
    # Define a dataframe for adding EMA series to it
    price_df = pd.DataFrame(data)
    price_df.index.name = "date"

    l_legend = [symbol]
    if not window:
        window = [20, 50]

    for win in window:
        if ma_type == "EMA":
            df_ta = overlap_model.ema(data, win, offset)
            l_legend.append(f"EMA {win}")
        elif ma_type == "SMA":
            df_ta = overlap_model.sma(data, win, offset)
            l_legend.append(f"SMA {win}")
        elif ma_type == "WMA":
            df_ta = overlap_model.wma(data, win, offset)
            l_legend.append(f"WMA {win}")
        elif ma_type == "HMA":
            df_ta = overlap_model.hma(data, win, offset)
            l_legend.append(f"HMA {win}")
        elif ma_type == "ZLMA":
            df_ta = overlap_model.zlma(data, win, offset)
            l_legend.append(f"ZLMA {win}")
        price_df = price_df.join(df_ta)

    plot_data = price_df

    fig = OpenBBFigure()

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data.iloc[:, 1].values,
        name=f"{symbol} Price",
        line=dict(color="gold"),
    )
    for idx in range(2, plot_data.shape[1]):
        fig.add_scatter(
            x=plot_data.index,
            y=plot_data.iloc[:, idx].values,
            name=l_legend[idx - 1],
        )
    fig.update_layout(
        title=f"{symbol} {ma_type.upper()}",
        xaxis=dict(
            title="Date",
        ),
        yaxis_title=f"{symbol} Price",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        f"{ma_type.lower()}{'_'.join([str(win) for win in window])}",
        price_df,
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def view_vwap(
    data: pd.DataFrame,
    symbol: str = "",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    offset: int = 0,
    interval: str = "",
    export: str = "",
    external_axes: bool = False,
):
    """Plots VWMA technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    symbol : str
        Ticker
    offset : int
        Offset variable
    start_date: Optional[str]
        Initial date, format YYYY-MM-DD
    end_date: Optional[str]
        Final date, format YYYY-MM-DD
    interval : str
        Interval of data
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    data.index = data.index.tz_localize(None)

    if start_date is None:
        start = data.index[0].date()
        console.print(f"No start date specified. Start date: {start}")
    else:
        start = start_date

    if end_date is None:
        end = data.index[-1].date()
        console.print(f"No end date specified. End date: {end}")
    else:
        end = end_date

    day_df = data[(start <= data.index.date) & (data.index.date <= end)]
    if len(day_df) == 0:
        return console.print(
            f"[red]No data found between {start.strftime('%Y-%m-%d')} and {end.strftime('%Y-%m-%d')}\n[/red]"
        )

    df_vwap = overlap_model.vwap(day_df, offset)

    fig = OpenBBFigure.create_subplots(
        rows=1,
        cols=1,
        shared_xaxes=True,
    )

    fig.add_candlestick(
        x=day_df.index,
        open=day_df["Open"],
        high=day_df["High"],
        low=day_df["Low"],
        close=day_df["Close"],
        name="Candlestick",
    )
    fig.add_scatter(
        x=day_df.index,
        y=df_vwap["VWAP_D"],
        name="VWAP",
        line=dict(width=1.2),
    )

    fig.update_layout(
        title=f"{symbol} {interval} VWAP",
        xaxis=dict(
            title="Date",
            type="date",
        ),
        yaxis_title=f"{symbol} Price",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "VWAP",
        df_vwap,
    )

    return fig.show() if not external_axes else fig
