"""Ethplorer view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
)
from openbb_terminal.cryptocurrency.onchain import ethplorer_model
from openbb_terminal.decorators import check_api_key
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_address_info(
    address: str,
    top: int = 15,
    sortby: str = "index",
    descend: bool = True,
    export: str = "",
) -> None:
    """Display info about tokens for given ethereum blockchain balance e.g. ETH balance, balance of all tokens with
    name and symbol. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Ethereum balance.
    top: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    descend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_address_info(address)
    df_data = df.copy()
    df = df.sort_values(by=sortby, ascending=descend)
    df["balance"] = df["balance"].apply(
        lambda x: lambda_very_long_number_formatter(x)
        if x >= 10000
        else round(float(x), 4)
    )

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Blockchain Token Information",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "balance",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_top_tokens(
    top: int = 15,
    sortby: str = "rank",
    descend: bool = True,
    export: str = "",
) -> None:
    """Display top ERC20 tokens [Source: Ethplorer]

    Parameters
    ----------
    top: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    descend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_top_tokens()
    df_data = df.copy()
    df.fillna("", inplace=True)
    df = df.sort_values(by=sortby, ascending=descend)
    for col in ["txsCount", "transfersCount", "holdersCount"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: lambda_very_long_number_formatter(x))

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Top ERC20 Tokens",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "top",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_top_token_holders(
    address: str,
    top: int = 10,
    sortby: str = "balance",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display info about top ERC20 token holders. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    top: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    descend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_top_token_holders(address)
    df_data = df.copy()
    df = df.sort_values(by=sortby, ascending=descend)
    df["balance"] = df["balance"].apply(lambda x: lambda_very_long_number_formatter(x))

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="ERC20 Token Holder Info",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "holders",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_address_history(
    address: str,
    top: int = 10,
    sortby: str = "timestamp",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display information about balance historical transactions. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Ethereum blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    top: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    descend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_address_history(address)
    df_data = df.copy()
    df = df.sort_values(by=sortby, ascending=descend)
    df["value"] = df["value"].apply(
        lambda x: lambda_very_long_number_formatter(x)
        if x >= 10000
        else round(float(x), 4)
    )

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Historical Transactions Information",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hist",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_token_info(
    address: str,
    social: bool = False,
    export: str = "",
) -> None:
    """Display info about ERC20 token. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    social: bool
        Flag to display social media links
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_token_info(address)
    df_data = df.copy()
    df.loc[:, "Value"] = df["Value"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )

    socials = ["website", "telegram", "reddit", "twitter", "coingecko"]
    if social:
        df = df[df["Metric"].isin(["balance", "name", "symbol"] + socials)]
    else:
        df = df[~df["Metric"].isin(socials)]

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="ERC20 Token Information"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_tx_info(
    tx_hash: str,
    export: str = "",
) -> None:
    """Display info about transaction. [Source: Ethplorer]

    Parameters
    ----------
    tx_hash: str
        Transaction hash e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_tx_info(tx_hash)
    df_data = df.copy()
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Information About Transactions",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tx",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_token_history(
    address: str,
    top: int = 10,
    sortby: str = "timestamp",
    hash_: bool = False,
    descend: bool = False,
    export: str = "",
) -> None:
    """Display info about token history. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    top: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    descend: str
        Sort in descending order.
    hash_: bool,
        Flag to show transaction hash.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_token_history(address)
    df_data = df.copy()
    if df.empty:
        console.print(f"No results found for balance: {address}\n")
        return

    df.loc[:, "value"] = df["value"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df = df.sort_values(by=sortby, ascending=descend)

    if hash_:
        df.drop(["from", "to"], axis=1, inplace=True)
    else:
        df.drop("transactionHash", inplace=True, axis=1)

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Token History Information",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "th",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_token_historical_prices(
    address: str,
    top: int = 30,
    sortby: str = "date",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display token historical prices with volume and market cap, and average price. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    top: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    descend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_token_historical_price(address)
    df_data = df.copy()

    if df.empty:
        console.print(f"No results found for balance: {address}\n")
        return

    df["volumeConverted"] = df["volumeConverted"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df.loc[:, "cap"] = df["cap"].apply(lambda x: lambda_very_long_number_formatter(x))
    df = df.sort_values(by=sortby, ascending=descend)

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Historical Token Prices",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "prices",
        df_data,
    )
