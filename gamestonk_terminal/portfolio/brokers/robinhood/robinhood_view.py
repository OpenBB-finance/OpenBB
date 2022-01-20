"""Robinhood View"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
import matplotlib.pyplot as plt
import mplfinance as mpf

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
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
    if gtff.USE_TABULATE_DF:
        print(tabulate(holdings, headers=holdings.columns, tablefmt="fancy_grid"))
    else:
        console.print(holdings.to_string())
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

    mpf.plot(
        hist,
        type="candle",
        style=cfg.style.mpf_style,
        title=f"\nPortfolio for {span_title_dict[span]}",
        ylabel="Equity ($)",
        xrotation=10,
        figratio=(10, 7),
        figscale=1.10,
        scale_padding={"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        figsize=(plot_autoscale()),
        update_width_config=dict(
            candle_linewidth=0.6,
            candle_width=0.8,
            volume_linewidth=0.8,
            volume_width=0.8,
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
