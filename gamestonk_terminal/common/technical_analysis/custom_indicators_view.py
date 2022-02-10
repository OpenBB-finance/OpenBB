"""Custom TA indicators"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union, List

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.common.technical_analysis import custom_indicators_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    reindex_dates,
    is_intraday,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def fibonacci_retracement(
    ohlc: pd.DataFrame,
    period: int = 120,
    start_date: Optional[Union[str, None]] = None,
    end_date: Optional[Union[str, None]] = None,
    s_ticker: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Calculate fibonacci retracement levels

    Parameters
    ----------
    ohlc: pd.DataFrame
        Stock data
    period: int
        Days to lookback
    start_date: Optional[str, None]
        User picked date for starting retracement
    end_date: Optional[str, None]
        User picked date for ending retracement
    s_ticker:str
        Stock ticker
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None
    """
    (
        df_fib,
        min_date,
        max_date,
        min_pr,
        max_pr,
    ) = custom_indicators_model.calculate_fib_levels(ohlc, period, start_date, end_date)

    levels = df_fib.Price

    plot_data = reindex_dates(ohlc)

    # This plot has 1 axes
    if external_axes is None:
        _, ax1 = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax2 = ax1.twinx()
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of 1 axis item./n[/red]")
            return
        ax1, ax2 = external_axes

    ax1.plot(plot_data["Adj Close"])

    if is_intraday(ohlc):
        date_format = "%b %d %H:%M"
    else:
        date_format = "%Y-%m-%d"
    min_date_index = plot_data[
        plot_data["date"] == min_date.strftime(date_format)
    ].index
    max_date_index = plot_data[
        plot_data["date"] == max_date.strftime(date_format)
    ].index
    ax1.plot(
        [min_date_index, max_date_index],
        [min_pr, max_pr],
    )

    for i in levels:
        ax1.axhline(y=i, alpha=0.5)

    for i in range(5):
        ax1.fill_between(plot_data.index, levels[i], levels[i + 1], alpha=0.15)

    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_title(f"Fibonacci Support for {s_ticker.upper()}")
    ax1.set_yticks(levels)
    ax1.set_yticklabels([0, 0.235, 0.382, 0.5, 0.618, 1])
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.set_ylim(ax1.get_ylim())
    ax2.set_ylabel("Price")
    theme.style_primary_axis(ax2)

    if external_axes is None:
        theme.visualize_output()
        print_rich_table(
            df_fib,
            headers=["Fib Level", "Price"],
            show_index=False,
            title="Fibonacci retracement levels",
        )
        console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "fib",
        df_fib,
    )
