"""Investpy View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.mutual_funds import investpy_model
from openbb_terminal.rich_config import console
from openbb_terminal.config_terminal import theme

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_search(
    by: str = "name",
    value: str = "",
    country: str = "united states",
    limit: int = 10,
    sortby: str = "",
    ascend: bool = False,
):
    """Display results of searching for Mutual Funds

    Parameters
    ----------
    by : str
        Field to match on.  Can be name, issuer, isin or symbol
    value : str
        String that will be searched for
    country: str
        Country to filter on
    limit: int
        Number to show
    sortby: str
        Column to sort by
    ascend: bool
        Flag to sort in ascending order
    """
    searches = investpy_model.search_funds(by, value)
    if searches.empty:
        console.print("No matches found.\n")
        return
    if country:
        searches = searches[searches.country == country]
        if searches.empty:
            console.print(f"No matches found in {country}.\n")
            return
        searches = searches.drop(columns=["country", "underlying"])

    if sortby:
        searches = searches.sort_values(by=sortby, ascending=ascend)

    print_rich_table(
        searches.head(limit),
        show_index=False,
        title=f"[bold]Mutual Funds with {by} matching {value}[/bold]",
    )


@log_start_end(log=logger)
def display_overview(country: str = "united states", limit: int = 10, export: str = ""):
    """Displays an overview of the main funds from a country.

    Parameters
    ----------
    country: str
        Country to get overview for
    limit: int
        Number to show
    export : str
        Format to export data
    """
    overview = investpy_model.get_overview(country=country, limit=limit)
    if overview.empty:
        return
    overview["Assets (1B)"] = overview.total_assets / 1_000_000_000
    overview = overview.drop(columns=["country", "total_assets"])
    print_rich_table(
        overview, title=f"[bold]Fund overview for {country.title()}[/bold]"
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"overview_{country.replace(' ','_')}",
        overview,
    )


@log_start_end(log=logger)
def display_fund_info(name: str, country: str = "united states"):
    """Display fund information.  Finds name from symbol first if name is false

    Parameters
    ----------
    name: str
        Fund name to get info for
    country : str
        Country of fund
    """
    info = (
        investpy_model.get_fund_info(name, country)
        .reset_index(drop=False)
        .applymap(lambda x: np.nan if not x else x)
        .dropna()
    )
    if info.empty:
        return

    # redact inception date if it appears castable to a float
    try:
        float(info[0].loc[info["index"] == "Inception Date"].values[0])
        info.loc[info["index"] == "Inception Date", 0] = "-"
    except ValueError:
        pass

    print_rich_table(
        info,
        title=f"[bold]{name.title()} Information[/bold]",
        show_index=False,
        headers=["Info", "Value"],
    )


@log_start_end(log=logger)
def display_historical(
    data: pd.DataFrame,
    name: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical fund price

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing historical data
    name: str
        Fund symbol or name
    export: str
        Format to export data
    external_axes:Optional[List[plt.Axes]]:
        External axes to plot on
    """
    console.print()
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]
    if data.empty:
        return
    ax.plot(data.index, data.Close)
    ax.set_xlim([data.index[0], data.index[-1]])
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price")
    ax.set_title(f"{name.title()} Price History")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "historical", data)
