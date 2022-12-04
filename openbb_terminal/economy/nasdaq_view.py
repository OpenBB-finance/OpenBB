"""NASDAQ Data Link View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt

from openbb_terminal.decorators import check_api_key
from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import nasdaq_model
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_economic_calendar(
    country: str, start_date: str, end_date: str, limit: int = 10, export: str = ""
) -> None:
    """Display economic calendar for specified country between start and end dates

    Parameters
    ----------
    country : str
        Country to display calendar for
    start_date : str
        Start date for calendar
    end_date : str
        End date for calendar
    limit : int
        Limit number of rows to display
    export : str
        Export data to csv or excel file
    """
    df = nasdaq_model.get_economic_calendar(country, start_date, end_date)
    if df.empty:
        return
    print_rich_table(
        df.head(limit),
        title="Economic Calendar",
        show_index=False,
        headers=df.columns,
    )
    console.print()
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "events", df)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def display_big_mac_index(
    country_codes: List[str] = None,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display Big Mac Index for given countries

    Parameters
    ----------
    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    big_mac = nasdaq_model.get_big_mac_indices(country_codes)

    if not big_mac.empty:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        big_mac.plot(ax=ax, marker="o")
        ax.legend()
        ax.set_title("Big Mac Index (USD)")
        ax.set_ylabel("Price of Big Mac in USD")
        theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

        if raw:
            print_rich_table(
                big_mac,
                headers=list(big_mac.columns),
                title="Big Mac Index",
                show_index=True,
            )

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "bigmac", big_mac
        )
    else:
        logger.error("Unable to get big mac data")
        console.print("[red]Unable to get big mac data[/red]\n")
