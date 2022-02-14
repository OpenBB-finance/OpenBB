""" Business Insider View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
from pandas.core.frame import DataFrame
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.due_diligence import business_insider_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def price_target_from_analysts(
    ticker: str,
    start: str,
    interval: str,
    stock: DataFrame,
    num: int,
    raw: bool,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display analysts' price targets for a given stock. [Source: Business Insider]

    Parameters
    ----------
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    stock : DataFrame
        Due diligence stock dataframe
    num : int
        Number of latest price targets from analysts to print
    raw : bool
        Display raw data only
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_analyst_data = business_insider_model.get_price_target_from_analysts(ticker)

    if raw:
        df_analyst_data.index = df_analyst_data.index.strftime("%Y-%m-%d")
        print_rich_table(
            df_analyst_data.sort_index(ascending=False).head(num),
            headers=list(df_analyst_data.columns),
            show_index=True,
            title="Analyst Price Targets",
        )

    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        # Slice start of ratings
        if start:
            df_analyst_data = df_analyst_data[start:]  # type: ignore

        if interval == "1440min":
            ax.plot(stock.index, stock["Adj Close"].values, lw=3)
        # Intraday
        else:
            ax.plot(stock.index, stock["Close"].values, lw=3)

        if start:
            ax.plot(df_analyst_data.groupby(by=["Date"]).mean()[start:], lw=5)  # type: ignore
        else:
            ax.plot(df_analyst_data.groupby(by=["Date"]).mean(), lw=5)

        ax.scatter(
            df_analyst_data.index,
            df_analyst_data["Price Target"],
            c="red",
            s=40,
            zorder=2,
        )

        ax.legend(["Closing Price", "Average Price Target", "Price Target"])

        ax.set_title(f"{ticker} (Time Series) and Price Target")
        ax.set_xlim(stock.index[0], stock.index[-1])
        ax.set_ylabel("Share Price")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt",
        df_analyst_data,
    )


@log_start_end(log=logger)
def estimates(ticker: str, export: str):
    """Display analysts' estimates for a given ticker. [Source: Business Insider]

    Parameters
    ----------
    ticker : str
        Ticker to get analysts' estimates
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    (
        df_year_estimates,
        df_quarter_earnings,
        df_quarter_revenues,
    ) = business_insider_model.get_estimates(ticker)

    print_rich_table(
        df_year_estimates,
        headers=list(df_year_estimates.columns),
        show_index=True,
        title="Annual Earnings Estimates",
    )
    console.print("")
    print_rich_table(
        df_quarter_earnings,
        headers=list(df_quarter_earnings.columns),
        show_index=True,
        title="Quarterly Earnings Estimates",
    )
    console.print("")
    print_rich_table(
        df_quarter_revenues,
        headers=list(df_quarter_revenues.columns),
        show_index=True,
        title="Quarterly Revenue Estimates",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt_year",
        df_year_estimates,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt_qtr_earnings",
        df_quarter_earnings,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt_qtr_revenues",
        df_quarter_revenues,
    )
