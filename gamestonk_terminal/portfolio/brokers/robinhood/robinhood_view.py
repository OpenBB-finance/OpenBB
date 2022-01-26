"""Robinhood View"""
__docformat__ = "numpy"

import os
import matplotlib.pyplot as plt
import mplfinance as mpf
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.portfolio.brokers.robinhood import robinhood_model
from gamestonk_terminal.rich_config import console


span_title_dict = {
    "day": "Day",
    "week": "Week",
    "month": "Month",
    "3month": "3 Months",
    "year": "Year",
    "5year": "5 Years",
    "all": "All Time",
}


def display_holdings(export: str = ""):
    """Display stock holdings in robinhood

    Parameters
    ----------
    export : str, optional
        Format to export data, by default ""
    """
    holdings = robinhood_model.get_holdings()
    print_rich_table(
        holdings, headers=list(holdings.columns), title="Robinhood Holdings"
    )
    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "rh_holdings",
        holdings,
    )


def display_historical(interval: str = "day", span: str = "3month", export: str = ""):
    """Display historical portfolio

    Parameters
    ----------
    interval : str
        Interval to look at (candle width), default="day"
    span : str
        How long to look back, default="3month"
    export : str, optional
        Format to export data
    """
    hist = robinhood_model.get_historical(interval, span)
    mc = mpf.make_marketcolors(
        up="green", down="red", edge="black", wick="black", ohlc="i"
    )
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=False)

    mpf.plot(
        hist,
        type="candle",
        style=s,
        title=f"\nPortfolio for {span_title_dict[span]}",
        ylabel="Equity ($)",
        figsize=(plot_autoscale()),
        update_width_config=dict(
            candle_linewidth=1.0,
            candle_width=0.8,
        ),
    )
    if gtff.USE_ION:
        plt.ion()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "rh_hist",
        hist,
    )
