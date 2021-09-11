"""WSJ view """
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import wsj_model
from gamestonk_terminal.helper_funcs import export_data


def display_overview(export: str):
    """Market overview. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.market_overview()
    if df_data.empty:
        print("No overview data available\n")
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_data,
                showindex=False,
                headers=df_data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df_data.to_string(index=False))
    print("")

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
        print("No indices data available\n")
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_data,
                showindex=False,
                headers=df_data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df_data.to_string(index=False))
    print("")

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
        print("No futures/commodities data available\n")
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_data,
                showindex=False,
                headers=df_data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df_data.to_string(index=False))
    print("")

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
        print("No US bonds data available\n")
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_data,
                showindex=False,
                headers=df_data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df_data.to_string(index=False))
    print("")

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
        print("No global bonds data available\n")
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_data,
                showindex=False,
                headers=df_data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df_data.to_string(index=False))
    print("")

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
        print("No currencies data available\n")
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_data,
                showindex=False,
                headers=df_data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df_data.to_string(index=False))
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "currencies",
        df_data,
    )
