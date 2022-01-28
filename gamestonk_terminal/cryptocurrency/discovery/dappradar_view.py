"""DappRadar view"""
__docformat__ = "numpy"

import os
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    very_long_number_formatter,
)
from gamestonk_terminal.cryptocurrency.discovery import dappradar_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console


def display_top_nfts(top: int = 10, sortby: str = "", export: str = "") -> None:
    """Displays top nft collections [Source: https://dappradar.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_nfts()
    if df.empty:
        console.print("Failed to fetch data from DappRadar\n")
    else:
        if sortby in dappradar_model.NFT_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        for col in ["Floor Price [$]", "Avg Price [$]", "Market Cap [$]", "Volume [$]"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: very_long_number_formatter(x))
        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Top NFT collections",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "drnft",
            df,
        )


def display_top_games(top: int = 10, export: str = "", sortby: str = "") -> None:
    """Displays top blockchain games [Source: https://dappradar.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_games()
    if df.empty:
        console.print("Failed to fetch data from DappRadar\n")
        return
    if sortby in dappradar_model.DEX_COLUMNS:
        df = df.sort_values(by=sortby, ascending=False)
    for col in ["Daily Users", "Daily Volume [$]"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: very_long_number_formatter(x))
    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Top Blockchain Games",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drgames",
        df,
    )


def display_top_dexes(top: int = 10, export: str = "", sortby: str = "") -> None:
    """Displays top decentralized exchanges [Source: https://dappradar.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_dexes()
    if df.empty:
        console.print("Failed to fetch data from DappRadar\n")
        return
    if sortby in dappradar_model.DEX_COLUMNS:
        df = df.sort_values(by=sortby, ascending=False)
    for col in ["Daily Users", "Daily Volume [$]"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: very_long_number_formatter(x))
    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Top Decentralized Exchanges",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdex",
        df,
    )


def display_top_dapps(top: int = 10, export: str = "", sortby: str = "") -> None:
    """Displays top decentralized exchanges [Source: https://dappradar.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = dappradar_model.get_top_dapps()
    if df.empty:
        console.print("Failed to fetch data from DappRadar\n")
        return
    if sortby in dappradar_model.DAPPS_COLUMNS:
        df = df.sort_values(by=sortby, ascending=False)
    for col in ["Daily Users", "Daily Volume [$]"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: very_long_number_formatter(x))
    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Top Decentralized Applications",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "drdapps",
        df,
    )
