""" Investing.com View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import investingcom_model
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_yieldcurve(
    country: str,
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    export: str = "",
):
    """Display yield curve for specified country. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = investingcom_model.get_yieldcurve(country)

    if not df.empty:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        else:
            if len(external_axes) != 1:
                logger.error("Expected list of 3 axis items")
                console.print("[red]Expected list of 3 axis items.\n[/red]")
                return
            (ax,) = external_axes

        ax.plot(df["Tenor"], df["Current"], "-o")
        ax.set_xlabel("Maturity")
        ax.set_ylabel("Yield (%)")
        theme.style_primary_axis(ax)
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        if external_axes is None:
            ax.set_title(f"Yield Curve for {country.title()} ")
            theme.visualize_output()

        if raw:
            print_rich_table(
                df,
                headers=list(df.columns),
                show_index=False,
                title=f"{country.title()} Yield Curve",
                floatfmt=".3f",
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "ycrv",
            df,
        )


@log_start_end(log=logger)
def display_economic_calendar(
    country: str = "all",
    importance: str = "",
    category: str = "",
    start_date: datetime.date = None,
    end_date: datetime.date = None,
    limit=100,
    export: str = "",
):
    """Display economic calendar. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country selected. List of available countries is accessible through get_events_countries().
    importances: str
        Importance selected from high, medium, low or all.
    categories: str
        Event category. List of available categories is accessible through get_events_categories().
    start_date: datetime.date
        First date to get events.
    end_date: datetime.date
        Last date to get events.
    limit: int
        The maximum number of events to show, default is 100.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df, detail = investingcom_model.get_economic_calendar(
        country, importance, category, start_date, end_date, limit
    )

    if not df.empty:

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=detail,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "events",
            df,
        )
