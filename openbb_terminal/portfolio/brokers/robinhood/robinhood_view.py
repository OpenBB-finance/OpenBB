"""Robinhood View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
import mplfinance as mpf

from openbb_terminal.config_terminal import theme
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.portfolio.brokers.robinhood import robinhood_model
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

span_title_dict = {
    "day": "Day",
    "week": "Week",
    "month": "Month",
    "3month": "3 Months",
    "year": "Year",
    "5year": "5 Years",
    "all": "All Time",
}


@log_start_end(log=logger)
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

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "rh_holdings",
        holdings,
    )


@log_start_end(log=logger)
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
        style=theme.mpf_style,
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
    if obbff.USE_ION:
        plt.ion()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "rh_hist",
        hist,
    )
