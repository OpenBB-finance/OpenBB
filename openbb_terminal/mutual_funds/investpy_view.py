"""Investpy View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.mutual_funds import investpy_model
from openbb_terminal.rich_config import console

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
def display_overview(
    country: str = "united states",
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
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
        sheet_name,
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
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Display historical fund price

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing historical data
    name: str
        Fund symbol or name
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    console.print()
    if data.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Close Price", xaxis_title="Date")
    fig.set_title(f"{name.title()} Price History")
    fig.add_scatter(x=data.index, y=data.Close, name=name)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "historical",
        data,
        sheet_name,
    )

    return fig.show(external=external_axes)
