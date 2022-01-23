"""DeFi Rate View"""
__docformat__ = "numpy"

import os
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.cryptocurrency.defi import defirate_model
from gamestonk_terminal.rich_config import console


def display_funding_rates(top: int, current: bool = True, export: str = "") -> None:
    """Display Funding rates - transfer payments made between long and short positions on perpetual swap futures markets
    [Source: https://defirate.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    current: bool
        If true displays current funding rate values. If false displays last 30 day average of funding rates.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = defirate_model.get_funding_rates(current)

    df_data = df.copy()

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "funding",
        df_data,
    )


def display_lending_rates(top: int, current: bool = True, export: str = "") -> None:
    """Displays top DeFi lendings. Decentralized Finance lending – allows users to supply cryptocurrencies
    in exchange for earning an annualized return
    [Source: https://defirate.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    current: bool
        If true displays current funding rate values. If false displays last 30 day average of funding rates.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = defirate_model.get_lending_rates(current)
    df_data = df.copy()
    df = df.loc[:, ~df.eq("–").all()]

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Top DeFi Lendings",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lending",
        df_data,
    )


def display_borrow_rates(top: int, current: bool = True, export: str = "") -> None:
    """Displays DeFi borrow rates. By using smart contracts, borrowers are able to lock
    collateral to protect against defaults while seamlessly adding to or closing their
    loans at any time.

    [Source: https://defirate.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    current: bool
        If true displays current funding rate values. If false displays last 30 day average of funding rates.
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = defirate_model.get_borrow_rates(current)
    df_data = df.copy()
    df = df.loc[:, ~df.eq("–").all()]

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="DeFi Borrow Rates",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "borrow",
        df_data,
    )
