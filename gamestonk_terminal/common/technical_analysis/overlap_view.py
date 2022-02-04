"""TA Overlap View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.common.technical_analysis import overlap_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale, reindex_dates
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def view_ma(
    series: pd.Series,
    length: List[int] = None,
    offset: int = 0,
    ma_type: str = "EMA",
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots MA technical indicator

    Parameters
    ----------
    series : pd.Series
        Series of prices
    length : List[int]
        Length of EMA window
    ma_type: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    s_ticker : str
        Ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # Define a dataframe for adding EMA series to it
    price_df = pd.DataFrame(series)

    l_legend = [s_ticker]
    if not length:
        length = [20, 50]

    for win in length:
        if ma_type == "EMA":
            df_ta = overlap_model.ema(series, win, offset)
            l_legend.append(f"EMA {win}")
        elif ma_type == "SMA":
            df_ta = overlap_model.sma(series, win, offset)
            l_legend.append(f"SMA {win}")
        elif ma_type == "WMA":
            df_ta = overlap_model.wma(series, win, offset)
            l_legend.append(f"WMA {win}")
        elif ma_type == "HMA":
            df_ta = overlap_model.hma(series, win, offset)
            l_legend.append(f"HMA {win}")
        elif ma_type == "ZLMA":
            df_ta = overlap_model.zlma(series, win, offset)
            l_legend.append(f"ZLMA {win}")
        price_df = price_df.join(df_ta)

    plot_data = reindex_dates(price_df)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(plot_data.index, plot_data.iloc[:, 1].values)
    ax.set_xlim([plot_data.index[0], plot_data.index[-1]])
    ax.set_ylabel(f"{s_ticker} Price")
    for idx in range(2, plot_data.shape[1]):
        ax.plot(plot_data.iloc[:, idx])

    ax.set_title(f"{s_ticker} {ma_type.upper()}")
    ax.legend(l_legend)
    theme.style_primary_axis(
        ax,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        f"{ma_type.lower()}{'_'.join([str(win) for win in length])}",
        price_df,
    )


@log_start_end(log=logger)
def view_vwap(
    s_ticker: str,
    ohlc: pd.DataFrame,
    offset: int = 0,
    s_interval: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots EMA technical indicator

    Parameters
    ----------
    s_ticker : str
        Ticker
    ohlc : pd.DataFrame
        Dataframe of prices
    offset : int
        Offset variable
    s_interval : str
        Interval of data
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """

    ohlc.index = ohlc.index.tz_localize(None)
    ohlc["Day"] = [idx.date() for idx in ohlc.index]
    day_df = ohlc[ohlc.Day == ohlc.Day[-1]]
    df_vwap = overlap_model.vwap(day_df, offset)

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": True,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1.2, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
    }
    # This plot has 2 axes
    if external_axes is None:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        candle_chart_kwargs["addplot"] = mpf.make_addplot(
            df_vwap, width=theme.line_width
        )
        fig, _ = mpf.plot(day_df, **candle_chart_kwargs)
        fig.suptitle(
            f"{s_ticker} {s_interval} VWAP",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )
        theme.visualize_output(force_tight_layout=False)
    else:
        if len(external_axes) != 3:
            console.print("[red]Expected list of 3 axis items./n[/red]")
            return
        (ax1, ax2, ax3) = external_axes
        candle_chart_kwargs["ax"] = ax1
        candle_chart_kwargs["volume"] = ax2
        candle_chart_kwargs["addplot"] = mpf.make_addplot(
            df_vwap, width=theme.line_width, ax=ax3
        )
        mpf.plot(day_df, **candle_chart_kwargs)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "VWAP",
        df_vwap,
    )
