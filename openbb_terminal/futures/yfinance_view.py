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
def display_historical(
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
    tickers_validated = list()
    for ticker in tickers:
        if ticker in yfinance_model.FUTURES_DATA["Ticker"].unique().tolist():
            tickers_validated.append(ticker)
        else:
            console.print(f"[red]{ticker} is not a valid ticker[/red]")

    tickers = tickers_validated

    if not tickers:
        console.print("No ticker was provided.\n")
        return

    historicals = yfinance_model.get_historical_futures([t + "=F" for t in tickers])
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

        if len(tickers) > 1:
            name = list()
            for tick in tickers:
                name.append(
                    yfinance_model.FUTURES_DATA[
                        yfinance_model.FUTURES_DATA["Ticker"] == tick
                    ]["Description"].values[0]
                )
                ax.plot(
                    historicals["Adj Close"][tick + "=F"].dropna().index,
                    historicals["Adj Close"][tick + "=F"].dropna().values,
                )
                ax.legend(name)
        else:
            name = yfinance_model.FUTURES_DATA[
                yfinance_model.FUTURES_DATA["Ticker"] == tickers[0]
            ]["Description"].values[0]
            ax.plot(
                historicals["Adj Close"].dropna().index,
                historicals["Adj Close"].dropna().values,
            )
            ax.set_title(name)

        first = datetime.strptime(start_date, "%Y-%m-%d")
        if historicals.index[0] > first:
            first = historicals.index[0]
        ax.set_xlim(first, historicals.index[-1])

        if external_axes is None:
            theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "historical",
            historicals,
        )
