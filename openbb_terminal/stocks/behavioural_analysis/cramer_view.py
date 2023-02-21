"""Cramer View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import List, Optional

import matplotlib.pyplot as plt
import yfinance
from matplotlib.dates import DateFormatter

import openbb_terminal.config_plot as cfp
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.behavioural_analysis import cramer_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_cramer_daily(
    inverse: bool = True, export: str = "", sheet_name: Optional[str] = None
):
    """Display Jim Cramer daily recommendations

    Parameters
    ----------
    inverse: bool
        Include inverse recommendation
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """

    recs = cramer_model.get_cramer_daily(inverse)
    if recs.empty:
        console.print("[red]Error getting request.\n[/red]")
        return
    date = recs.Date[0]
    recs = recs.drop(columns=["Date"])

    if datetime.today().strftime("%m-%d") != datetime.strptime(
        date.replace("/", "-"), "%m-%d"
    ):
        console.print(
            """
        \n[yellow]Warning[/yellow]: We noticed Jim Crammer recommendation data has not been updated for a while, \
and we're investigating on finding a replacement.
        """,
        )

    print_rich_table(recs, title=f"Jim Cramer Recommendations for {date}")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cramer",
        recs,
        sheet_name,
    )


@log_start_end(log=logger)
def display_cramer_ticker(
    symbol: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display ticker close with Cramer recommendations

    Parameters
    ----------
    symbol: str
        Stock ticker
    raw: bool
        Display raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]] = None,
        External axes to plot on
    """

    df = cramer_model.get_cramer_ticker(symbol)
    if df.empty:
        console.print(f"No recommendations found for {symbol}.\n")
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    close_prices = yfinance.download(symbol, start="2022-01-01", progress=False)[
        "Adj Close"
    ]

    ax.plot(close_prices)
    color_map = {"Buy": theme.up_color, "Sell": theme.down_color}
    for name, group in df.groupby("Recommendation"):
        ax.scatter(group.Date, group.Price, color=color_map[name], s=150, label=name)

    ax.set_title(f"{symbol.upper()} Close With Cramer Recommendations")
    theme.style_primary_axis(ax)
    ax.legend(loc="best", scatterpoints=1)

    # Overwrite default dote formatting
    ax.xaxis.set_major_formatter(DateFormatter("%m/%d"))
    ax.set_xlabel("Date")

    if external_axes is None:
        theme.visualize_output()

    if raw:
        df["Date"] = df["Date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        print_rich_table(df, title=f"Jim Cramer Recommendations for {symbol}")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        df,
        "jctr",
        sheet_name,
    )
