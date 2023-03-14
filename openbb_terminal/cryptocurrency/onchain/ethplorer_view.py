"""Ethplorer view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
)
from openbb_terminal.cryptocurrency.onchain import ethplorer_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_address_info(
    address: str,
    limit: int = 15,
    sortby: str = "index",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display info about tokens for given ethereum blockchain balance e.g. ETH balance,
    balance of all tokens with name and symbol. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Ethereum balance.
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_address_info(address, sortby=sortby, ascend=ascend)
    df_data = df.copy()
    df["balance"] = df["balance"].apply(
        lambda x: lambda_very_long_number_formatter(x)
        if x >= 10000
        else round(float(x), 4)
    )

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Blockchain Token Information",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "balance",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_top_tokens(
    limit: int = 15,
    sortby: str = "rank",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display top ERC20 tokens [Source: Ethplorer]

    Parameters
    ----------
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_top_tokens(sortby, ascend)
    df_data = df.copy()
    df.fillna("", inplace=True)
    for col in ["txsCount", "transfersCount", "holdersCount"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: lambda_very_long_number_formatter(x))

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Top ERC20 Tokens",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "top",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_top_token_holders(
    address: str,
    limit: int = 10,
    sortby: str = "balance",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display info about top ERC20 token holders. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_top_token_holders(address, sortby, ascend)
    df_data = df.copy()
    df["balance"] = df["balance"].apply(lambda x: lambda_very_long_number_formatter(x))

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="ERC20 Token Holder Info",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "holders",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_address_history(
    address: str,
    limit: int = 10,
    sortby: str = "timestamp",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display information about balance historical transactions. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Ethereum blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_address_history(address, sortby, ascend)
    df_data = df.copy()
    df["value"] = df["value"].apply(
        lambda x: lambda_very_long_number_formatter(x)
        if x >= 10000
        else round(float(x), 4)
    )

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Historical Transactions Information",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hist",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_token_info(
    address: str,
    social: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
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
    df = (
        df[df["Metric"].isin(["balance", "name", "symbol"] + socials)]
        if social
        else df[~df["Metric"].isin(socials)]
    )

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="ERC20 Token Information",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_tx_info(
    tx_hash: str,
    export: str = "",
    sheet_name: Optional[str] = None,
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
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Information About Transactions",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tx",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_token_history(
    address: str,
    limit: int = 10,
    sortby: str = "timestamp",
    ascend: bool = False,
    hash_: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display info about token history. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    hash_: bool,
        Flag to show transaction hash.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_token_history(address, sortby, ascend)
    df_data = df.copy()
    if df.empty:
        console.print(f"No results found for balance: {address}\n")
        return

    df.loc[:, "value"] = df["value"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )

    if hash_:
        df.drop(["from", "to"], axis=1, inplace=True)
    else:
        df.drop("transactionHash", inplace=True, axis=1)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Token History Information",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "th",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_ETHPLORER_KEY"])
def display_token_historical_prices(
    address: str,
    limit: int = 30,
    sortby: str = "date",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display token historical prices with volume and market cap, and average price.
    [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = ethplorer_model.get_token_historical_price(address, sortby, ascend)
    df_data = df.copy()

    if df.empty:
        console.print(f"No results found for balance: {address}\n")
        return

    df["volumeConverted"] = df["volumeConverted"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df.loc[:, "cap"] = df["cap"].apply(lambda x: lambda_very_long_number_formatter(x))

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Historical Token Prices",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "prices",
        df_data,
        sheet_name,
    )
