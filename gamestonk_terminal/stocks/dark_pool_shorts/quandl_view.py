""" Quandl View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.ticker
import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
    plot_autoscale,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.dark_pool_shorts import quandl_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_short_interest(
    ticker: str,
    nyse: bool,
    df_short_interest: pd.DataFrame,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    ticker : str
        ticker to get short interest from
    start : str
        start date to start displaying short interest volume
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    df_short_interest: pd.DataFrame
        Short interest dataframe
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None

    """

    # This plot has 2 axis
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax2 = ax1.twinx()
    else:
        if len(external_axes) != 2:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax1, ax2) = external_axes

    ax1.bar(
        df_short_interest.index,
        df_short_interest["Short Volume"],
        0.3,
        color=theme.down_color,
    )
    ax1.bar(
        df_short_interest.index,
        df_short_interest["Total Volume"] - df_short_interest["Short Volume"],
        0.3,
        bottom=df_short_interest["Short Volume"],
        color=theme.up_color,
    )
    ax1.set_ylabel("Shares")
    ax1.set_title(f"{('NASDAQ', 'NYSE')[nyse]} Short Interest on {ticker}")

    ax1.legend(labels=["Short Volume", "Total Volume"], loc="best")
    ax1.yaxis.set_major_formatter(matplotlib.ticker.EngFormatter())

    ax2.tick_params(axis="y")
    ax2.set_ylabel("Percentage of Volume Shorted")
    ax2.plot(
        df_short_interest.index,
        df_short_interest["% of Volume Shorted"],
    )
    ax2.tick_params(axis="y", which="major")
    ax2.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.0f%%"))

    theme.style_twin_axes(ax1, ax2)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def short_interest(ticker: str, nyse: bool, days: int, raw: bool, export: str):
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    ticker : str
        ticker to get short interest from
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    days : int
        Number of past days to show short interest
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_short_interest = quandl_model.get_short_interest(ticker, nyse)

    df_short_interest = df_short_interest.tail(days)

    df_short_interest.columns = [
        "".join(" " + char if char.isupper() else char.strip() for char in idx).strip()
        for idx in df_short_interest.columns.tolist()
    ]
    pd.options.mode.chained_assignment = None

    vol_pct = (
        100
        * df_short_interest["Short Volume"].values
        / df_short_interest["Total Volume"].values
    )
    df_short_interest["% of Volume Shorted"] = [round(pct, 2) for pct in vol_pct]

    if raw:
        df_short_interest["% of Volume Shorted"] = df_short_interest[
            "% of Volume Shorted"
        ].apply(lambda x: f"{x/100:.2%}")
        df_short_interest = df_short_interest.applymap(
            lambda x: lambda_long_number_format(x)
        ).sort_index(ascending=False)

        df_short_interest.index = df_short_interest.index.date

        print_rich_table(
            df_short_interest,
            headers=list(df_short_interest.columns),
            show_index=True,
            title="Short Interest of Stock",
        )

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "psi(quandl)",
        df_short_interest,
    )
