"""Yahoo Finance view"""
__docformat__ = "numpy"

from typing import Optional, List
import logging
import os

import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timedelta

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.futures import yfinance_model
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_historical_futures(
    tickers: List[str],
    start_date: str = (datetime.now() - timedelta(days=3 * 365)).strftime("%Y-%m-%d"),
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical futures [Source: Yahoo Finance]

    Parameters
    ----------
    tickers: List[str]
        List of future timeseries tickers to display
    start_date : str
        Initial date like string (e.g., 2021-10-01)
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    historicals = yfinance_model.get_historical_futures(tickers)
    if historicals.empty:
        console.print(f"No data was found for the tickers: {', '.join(tickers)}\n")
        return

    if raw:
        print_rich_table(
            historicals,
            headers=list(historicals.columns),
            show_index=True,
            title="Futures timeseries",
        )

    else:
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        ax.plot(
            plot_data.index,
            plot_data["Adj Close"].values,
        )
        ax.plot(
            plot_data.index,
            plot_data[df_ta.columns[0]].values,
            theme.down_color,
            linewidth=0.7,
        )
        ax.plot(
            plot_data.index, plot_data[df_ta.columns[1]].values, ls="--", linewidth=0.7
        )
        ax.plot(
            plot_data.index,
            plot_data[df_ta.columns[2]].values,
            theme.up_color,
            linewidth=0.7,
        )
        ax.set_title(f"{symbol} Bollinger Bands")
        ax.set_xlim(plot_data.index[0], plot_data.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.legend([symbol, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
        ax.fill_between(
            df_ta.index, df_ta.iloc[:, 0].values, df_ta.iloc[:, 2].values, alpha=0.1
        )
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
            "bbands",
            df_ta,
        )
