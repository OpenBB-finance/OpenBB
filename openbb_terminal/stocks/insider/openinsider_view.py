import itertools
import logging
import os
from typing import List, Optional

import numpy as np
import pandas as pd

from openbb_terminal import rich_config
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    patch_pandas_text_adjustment,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.insider.openinsider_model import (
    get_open_insider_data,
    get_open_insider_link,
    get_print_insider_data,
)

logger = logging.getLogger(__name__)

d_notes = {
    "A": "A: Amended filing",
    "D": "D: Derivative transaction in filing (usually option exercise)",
    "E": "E: Error detected in filing",
    "M": "M: Multiple transactions in filing; earliest reported transaction date & weighted average transaction price",
}

d_trade_types = {
    "S - Sale": "[red]S - Sale: Sale of securities on an exchange or to another person[/red]",
    "S - Sale+OE": "[yellow]S - Sale+OE: Sale of securities "
    "on an exchange or to another person (after option exercise)[/yellow]",
    "F - Tax": "[magenta]F - Tax: Payment of exercise price or "
    "tax liability using portion of securities received from the company[/magenta]",
    "P - Purchase": "[green]P - Purchase: Purchase of securities on "
    "an exchange or from another person[/green]",
}


def lambda_red_highlight(values) -> List[str]:
    """Red highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    -------
    List[str]
        colored dataframes values
    """
    return [f"[red]{val}[/red]" for val in values]


def lambda_yellow_highlight(values) -> List[str]:
    """Yellow highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    -------
    List[str]
        colored dataframes values
    """
    return [f"[yellow]{val}[/yellow]" for val in values]


def lambda_magenta_highlight(values):
    """Magenta highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    -------
    List[str]
        colored dataframes values
    """
    return [f"[magenta]{val}[/magenta]" for val in values]


def lambda_green_highlight(values):
    """Green highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    -------
    List[str]
        colored dataframes values
    """
    return [f"[green]{val}[/green]" for val in values]


@log_start_end(log=logger)
def print_insider_data(
    type_insider: str = "lcb",
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Print insider data

    Parameters
    ----------
    type_insider: str
        Insider type of data. Available types can be accessed through get_insider_types().
    limit: int
        Limit of data rows to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export data format
    """
    df = get_print_insider_data(type_insider)

    if not df.empty:
        print_rich_table(
            df,
            headers=[x.title() for x in df.columns],
            show_index=False,
            title="Insider Data",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            type_insider,
            df,
            sheet_name,
        )

        if df.shape[1] == 13:
            l_chars = [list(chars) for chars in df["X"].values if chars != "-"]
            l_uchars = np.unique(list(itertools.chain(*l_chars)))

            for char in l_uchars:
                console.print(d_notes[char])


@log_start_end(log=logger)
def print_insider_filter(
    preset: str,
    symbol: str,
    limit: int = 10,
    links: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Print insider filter based on loaded preset. [Source: OpenInsider]

    Parameters
    ----------
    preset : str
        Loaded preset filter
    symbol : str
        Stock ticker symbol
    limit : int
        Limit of rows of data to display
    links : bool
        Flag to show hyperlinks
    export : str
        Format to export data
    """
    link = (
        f"http://openinsider.com/screener?s={symbol}"
        if symbol
        else get_open_insider_link(preset)
    )

    if not link:
        return

    df_insider = get_open_insider_data(link, has_company_name=bool(not symbol))
    df_insider_orig = df_insider.copy()

    if df_insider.empty:
        console.print("No insider data found\n")
        return

    if links:
        df_insider = df_insider[
            ["Ticker Link", "Insider Link", "Filing Link", "Filing Date"]
        ].head(limit)
    else:
        df_insider = df_insider.drop(
            columns=["Filing Link", "Ticker Link", "Insider Link"]
        ).head(limit)

    if (
        rich_config.USE_COLOR
        and not links
        and not get_current_user().preferences.USE_INTERACTIVE_DF
    ):
        new_df_insider = df_insider.copy()
        if not new_df_insider[new_df_insider["Trade Type"] == "S - Sale"].empty:
            new_df_insider[new_df_insider["Trade Type"] == "S - Sale"] = new_df_insider[
                new_df_insider["Trade Type"] == "S - Sale"
            ].apply(lambda_red_highlight)
        if not new_df_insider[new_df_insider["Trade Type"] == "S - Sale+OE"].empty:
            new_df_insider[
                new_df_insider["Trade Type"] == "S - Sale+OE"
            ] = new_df_insider[new_df_insider["Trade Type"] == "S - Sale+OE"].apply(
                lambda_yellow_highlight
            )
        if not new_df_insider[new_df_insider["Trade Type"] == "F - Tax"].empty:
            new_df_insider[new_df_insider["Trade Type"] == "F - Tax"] = new_df_insider[
                new_df_insider["Trade Type"] == "F - Tax"
            ].apply(lambda_magenta_highlight)
        if not new_df_insider[new_df_insider["Trade Type"] == "P - Purchase"].empty:
            new_df_insider[
                new_df_insider["Trade Type"] == "P - Purchase"
            ] = new_df_insider[new_df_insider["Trade Type"] == "P - Purchase"].apply(
                lambda_green_highlight
            )

        patch_pandas_text_adjustment()
        pd.set_option("display.max_colwidth", 0)
        pd.set_option("display.max_rows", None)

        # needs to be done because table is too large :(
        new_df_insider = new_df_insider.drop(columns=["Filing Date", "Trade Type"])

    else:
        # needs to be done because table is too large :(
        new_df_insider = df_insider.drop(columns=["Filing Date"], axis=1)

    print_rich_table(
        new_df_insider,
        headers=[x.title() for x in new_df_insider.columns],
        title="Insider filtered",
        export=bool(export),
    )

    if not links:
        l_chars = [list(chars) for chars in df_insider_orig["X"].values]
        l_uchars = np.unique(list(itertools.chain(*l_chars)))

        for char in l_uchars:
            console.print(d_notes[char])

        l_tradetype = df_insider_orig["Trade Type"].values
        l_utradetype = np.unique(l_tradetype)

        for tradetype in l_utradetype:
            console.print(d_trade_types[tradetype])

    if export:
        cmd = "stats" if symbol else "filter"

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            cmd,
            df_insider,
            sheet_name,
        )
