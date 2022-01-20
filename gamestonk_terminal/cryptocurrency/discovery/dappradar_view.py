"""DappRadar view"""
__docformat__ = "numpy"

import os
from gamestonk_terminal.cryptocurrency.discovery import dappradar_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    rich_table_from_df,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console


def display_top_nfts(top: int = 10, export: str = "") -> None:
    """Display information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_nfts()
    if gtff.USE_TABULATE_DF:
        rich_table_from_df(
            df.head(top),
            headers=list(df.columns),
            floatfmt=".2f",
            show_index=False,
            title="Top NFT collections",
        )
        console.print("")
    else:
        console.print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drnft",
        df,
    )


def display_top_games(top: int = 10, export: str = "") -> None:
    """Display information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_games()
    if gtff.USE_TABULATE_DF:
        rich_table_from_df(
            df.head(top),
            headers=list(df.columns),
            floatfmt=".2f",
            show_index=False,
        )
        console.print("")
    else:
        console.print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drgames",
        df,
    )


def display_top_dexes(top: int = 10, export: str = "") -> None:
    """Display information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_dexes()
    if gtff.USE_TABULATE_DF:
        rich_table_from_df(
            df.head(top),
            headers=list(df.columns),
            floatfmt=".2f",
            show_index=False,
        )
        console.print("")
    else:
        console.print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdex",
        df,
    )


def display_top_dapps(top: int = 10, export: str = "") -> None:
    """Display information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_dapps()
    if gtff.USE_TABULATE_DF:
        rich_table_from_df(
            df.head(top),
            headers=list(df.columns),
            floatfmt=".2f",
            show_index=False,
        )
        console.print("")
    else:
        console.print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdapps",
        df,
    )
