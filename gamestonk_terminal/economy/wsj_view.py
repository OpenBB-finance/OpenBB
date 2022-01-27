"""WSJ view """
__docformat__ = "numpy"

import os

from gamestonk_terminal.economy import wsj_model
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console


def display_overview(export: str):
    """Market overview. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.market_overview()
    if df_data.empty:
        console.print("No overview data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="Market Overview",
    )

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "overview",
        df_data,
    )


def display_indices(export: str):
    """US indices. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.us_indices()
    if df_data.empty:
        console.print("No indices data available\n")
        return

    print_rich_table(
        df_data, show_index=False, headers=list(df_data.columns), title="US Indices"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "indices",
        df_data,
    )


def display_futures(export: str):
    """Futures/Commodities. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.top_commodities()
    if df_data.empty:
        console.print("No futures/commodities data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="Futures/Commodities",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "futures",
        df_data,
    )


def display_usbonds(export: str):
    """US bonds. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.us_bonds()
    if df_data.empty:
        console.print("No US bonds data available\n")
        return

    print_rich_table(
        df_data, show_index=False, headers=list(df_data.columns), title="US Bonds"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "usbonds",
        df_data,
    )


def display_glbonds(export: str):
    """Global bonds. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.global_bonds()
    if df_data.empty:
        console.print("No global bonds data available\n")
        return

    print_rich_table(
        df_data, show_index=False, headers=list(df_data.columns), title="Global Bonds"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "glbonds",
        df_data,
    )


def display_currencies(export: str):
    """Display currencies. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.global_currencies()
    if df_data.empty:
        console.print("No currencies data available\n")
        return

    print_rich_table(
        df_data, show_index=False, headers=list(df_data.columns), title="Currencies"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "currencies",
        df_data,
    )
