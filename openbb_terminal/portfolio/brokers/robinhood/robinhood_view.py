"""Robinhood View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.portfolio.brokers.robinhood import robinhood_model

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
def display_holdings(export: str = "", sheet_name: Optional[str] = None):
    """Display stock holdings in robinhood

    Parameters
    ----------
    export : str, optional
        Format to export data, by default ""
    """
    holdings = robinhood_model.get_holdings()
    print_rich_table(
        holdings,
        headers=list(holdings.columns),
        title="Robinhood Holdings",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "rh_holdings",
        holdings,
        sheet_name,
    )


@log_start_end(log=logger)
def display_historical(
    interval: str = "day",
    window: str = "3month",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Display historical portfolio

    Parameters
    ----------
    interval : str
        Interval to look at (candle width), default="day"
    window : str
        How long to look back, default="3month"
    export : str, optional
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    hist = robinhood_model.get_historical(interval, window)

    fig = OpenBBFigure(xaxis_title="Date", yaxis_title="Equity ($)")
    fig.set_title(f"Portfolio for {span_title_dict[window]}")

    fig.add_candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"],
        name="Equity",
    )

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "rh_hist",
        hist,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
