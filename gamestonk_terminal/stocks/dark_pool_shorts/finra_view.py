""" FINRA View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.dark_pool_shorts import finra_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_dark_pools(
    ticker: str,
    ats: pd.DataFrame,
    otc: pd.DataFrame,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots ATS and NON-ATS data

    Parameters
    ----------
    ticker : str
        Stock ticker to get data from
    ats : pd.DataFrame
        Dark Pools (ATS) Data
    otc : pd.DataFrame
        OTC (Non-ATS) Data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None

    """

    # This plot has 1 axis
    if not external_axes:
        _, (ax1, ax2) = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax1, ax2) = external_axes

    if not ats.empty and not otc.empty:
        ax1.bar(
            ats.index,
            (ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"])
            / 1_000_000,
            color=theme.down_color,
        )
        ax1.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color=theme.up_color
        )
        ax1.legend(["ATS", "OTC"])

    elif not ats.empty:
        ax1.bar(
            ats.index,
            ats["totalWeeklyShareQuantity"] / 1_000_000,
            color=theme.down_color,
        )
        ax1.legend(["ATS"])

    elif not otc.empty:
        ax1.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color=theme.up_color
        )
        ax1.legend(["OTC"])

    ax1.set_ylabel("Total Weekly Shares [Million]")
    ax1.set_title(f"Dark Pools (ATS) vs OTC (Non-ATS) Data for {ticker}")

    if not ats.empty:
        ax2.plot(
            ats.index,
            ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
            color=theme.down_color,
        )
        ax2.legend(["ATS"])

        if not otc.empty:
            ax2.plot(
                otc.index,
                otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                color=theme.up_color,
            )
            ax2.legend(["ATS", "OTC"])

    else:
        ax2.plot(
            otc.index,
            otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
            color=theme.up_color,
        )
        ax2.legend(["OTC"])

    ax2.set_ylabel("Shares per Trade")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax2.set_xlim(otc.index[0], otc.index[-1])
    ax2.set_xlabel("Weeks")

    theme.style_primary_axis(ax1)
    theme.style_primary_axis(ax2)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def darkpool_ats_otc(ticker: str, export: str):
    """Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]

    Parameters
    ----------
    ticker : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_ats, df_otc = finra_model.getTickerFINRAdata(ticker)

    if df_ats.empty and df_otc.empty:
        console.print("No ticker data found!")

    plot_dark_pools(ticker, df_ats, df_otc)
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dpotc_ats",
        df_ats,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dpotc_otc",
        df_otc,
    )


@log_start_end(log=logger)
def plot_dark_pools_ats(
    ats: pd.DataFrame,
    top_ats_tickers: List,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots promising tickers based on growing ATS data

    Parameters
    ----------
    ats : pd.DataFrame
        Dark Pools (ATS) Data
    top_ats_tickers : List
        List of tickers from most promising with better linear regression slope
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    for symbol in top_ats_tickers:
        ax.plot(
            pd.to_datetime(
                ats[ats["issueSymbolIdentifier"] == symbol]["weekStartDate"]
            ),
            ats[ats["issueSymbolIdentifier"] == symbol]["totalWeeklyShareQuantity"]
            / 1_000_000,
        )

    ax.legend(top_ats_tickers)
    ax.set_ylabel("Total Weekly Shares [Million]")
    ax.set_title("Dark Pool (ATS) growing tickers")
    ax.set_xlabel("Weeks")
    ax.set_xlim(ats["weekStartDate"][0], ats["weekStartDate"][-1])
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def darkpool_otc(
    num: int,
    promising: int,
    tier: str,
    export: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]

    Parameters
    ----------
    num : int
        Number of tickers to filter from entire ATS data based on
        the sum of the total weekly shares quantity
    promising : int
        Number of tickers to display from most promising with
        better linear regression slope
    tier : int
        Tier to process data from
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # TODO: Improve command logic to be faster and more useful
    df_ats, d_ats_reg = finra_model.getATSdata(num, tier)

    top_ats_tickers = list(
        dict(sorted(d_ats_reg.items(), key=lambda item: item[1], reverse=True)).keys()
    )[:promising]

    plot_dark_pools_ats(df_ats, top_ats_tickers, external_axes)
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "prom",
        df_ats,
    )
