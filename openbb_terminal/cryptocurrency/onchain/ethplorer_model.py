"""Ethplorer model"""
__docformat__ = "numpy"

import logging
import textwrap
from datetime import datetime
from time import sleep
from typing import Any, Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.dataframe_helpers import create_df_index
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

PRICES_FILTERS = [
    "date",
    "cap",
    "volumeConverted",
    "open",
    "high",
    "close",
    "low",
]

TOP_FILTERS = [
    "rank",
    "name",
    "symbol",
    "price",
    "txsCount",
    "transfersCount",
    "holdersCount",
]

TH_FILTERS = [
    "value",
]

BALANCE_FILTERS = [
    "index",
    "balance",
    "tokenName",
    "tokenSymbol",
]

HIST_FILTERS = ["timestamp", "transactionHash", "token", "value"]

HOLDERS_FILTERS = [
    "balance",
    "share",
]


@log_start_end(log=logger)
def split_cols_with_dot(column: str) -> str:
    """Split column name in data frame columns whenever there is a dot between 2 words.
    E.g. price.availableSupply -> priceAvailableSupply.

    Parameters
    ----------
    column: str
        Pandas dataframe column value

    Returns
    -------
    str
        Value of column with replaced format.
    """

    @log_start_end(log=logger)
    def replace(string: str, char: str, index: int) -> str:
        """Helper method which replaces values with dot as a separator and converts it to camelCase format

        Parameters
        ----------
        string: str
            String in which we remove dots and convert it to camelcase format.
        char: str
            First letter of given word.
        index:
            Index of string element.

        Returns
        ----------
        str
            Camel case string with no dots. E.g. price.availableSupply -> priceAvailableSupply.
        """

        return string[:index] + char + string[index + 1 :]

    if "." in column:
        part1, part2 = column.split(".")
        part2 = replace(part2, part2[0].upper(), 0)
        return part1 + part2
    return column


@log_start_end(log=logger)
def enrich_social_media(dct: dict) -> None:
    """Searching inside dictionary if there are any information about twitter, reddit or coingecko.
    If yes it updates dictionary with url to given social media site.

    Parameters
    ----------
    dct: dict
        Dictionary in which we search for coingecko, twitter or reddit url.
    """

    social_media = {
        "twitter": "https://www.twitter.com/",
        "reddit": "https://www.reddit.com/r/",
        "coingecko": "https://www.coingecko.com/en/coins/",
    }

    for k, v in social_media.items():
        if k in dct:
            dct[k] = v + dct[k]


@log_start_end(log=logger)
def make_request(
    endpoint: str, address: Optional[str] = None, **kwargs: Any
) -> Optional[dict]:
    """Helper method that handles request for Ethplorer API [Source: https://ethplorer.io/]

    Parameters
    ----------
    endpoint: str
        endpoint we want to query e.g. https://api.ethplorer.io/<endpoint><arg>?=apiKey=freekey
    address: str
        balance argument for given endpoint. In most cases it's tx hash, or eth balance.
    kwargs: Any
        Additional keywords arguments e.g. limit of transactions

    Returns
    -------
    Optional[dict]
        dictionary with response data
    """

    base_url = "https://api.ethplorer.io/"
    url = f"{base_url}{endpoint}"

    if address:
        url = url + "/" + address

    url += f"?apiKey={get_current_user().credentials.API_ETHPLORER_KEY}"

    if "limit" in kwargs:
        url += f"&limit={kwargs['limit']}"

    sleep(0.5)  # Limit is 2 API calls per 1 sec.
    response = request(url)
    result = {}

    if response.status_code == 200:
        result = response.json()

        if not result:
            console.print("No data found")

    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(response.json()["error"]["message"])

    return result


@log_start_end(log=logger)
def get_token_decimals(address: str) -> Optional[int]:
    """Helper methods that gets token decimals number. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Blockchain balance e.g. 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984

    Returns
    -------
    Optional[int]
        Number of decimals for given token.
    """
    response = make_request("getTokenInfo", address)
    if response and "decimals" in response:
        return 10 ** int(response["decimals"])
    return None


@log_start_end(log=logger)
def get_address_info(
    address: str, sortby: str = "index", ascend: bool = False
) -> pd.DataFrame:
    """Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which
    have name and symbol. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame
        DataFrame with list of tokens and their balances.
    """

    response = make_request("getAddressInfo", address)
    tokens = []
    if "tokens" in response:
        tokens = response.pop("tokens")
        for token in tokens:
            token_info = token.pop("tokenInfo")
            token.update(
                {
                    "tokenName": token_info.get("name"),
                    "tokenSymbol": token_info.get("symbol"),
                    "tokenAddress": token_info.get("balance"),
                    "balance": token.get("balance")
                    / (10 ** int(token_info.get("decimals"))),
                }
            )
    elif "token_info" in response:
        token_info = response.get("tokenInfo") or {}
        tokens = [
            {
                "tokenName": token_info.get("name"),
                "tokenSymbol": token_info.get("symbol"),
                "tokenAddress": token_info.get("balance"),
                "balance": token_info.get("balance")
                / (10 ** int(token_info.get("decimals"))),
            }
        ]

    eth = response.get("ETH") or {}
    eth_balance = eth.get("balance")
    eth_row = [
        "Ethereum",
        "ETH",
        "0x0000000000000000000000000000000000000000",
        eth_balance,
    ]
    cols = [
        "tokenName",
        "tokenSymbol",
        "tokenAddress",
        "balance",
    ]
    df = pd.DataFrame(tokens)
    eth_row_df = pd.DataFrame([eth_row], columns=cols)
    df = pd.concat([eth_row_df, df], ignore_index=True)
    df = df[df["tokenName"].notna()][cols]
    create_df_index(df, "index")
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_top_tokens(sortby: str = "rank", ascend: bool = False) -> pd.DataFrame:
    """Get top 50 tokens. [Source: Ethplorer]

    Parameters
    ----------
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame
        DataFrame with list of top 50 tokens.
    """

    response = make_request("getTopTokens")
    tokens = response["tokens"]
    df = pd.DataFrame(tokens)[
        [
            "name",
            "symbol",
            "price",
            "txsCount",
            "transfersCount",
            "holdersCount",
            "twitter",
            "coingecko",
        ]
    ]
    df["price"] = df["price"].apply(lambda x: x["rate"] if x and "rate" in x else None)
    create_df_index(df, "rank")
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_top_token_holders(
    address: str, sortby: str = "balance", ascend: bool = True
) -> pd.DataFrame:
    """Get info about top token holders. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame
        DataFrame with list of top token holders.
    """

    response = make_request("getTopTokenHolders", address, limit=100)
    df = pd.DataFrame(response["holders"])
    sleep(0.5)
    token_decimals_divider = get_token_decimals(address)
    if token_decimals_divider:
        df["balance"] = df["balance"] / token_decimals_divider
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_address_history(
    address: str, sortby: str = "timestamp", ascend: bool = True
) -> pd.DataFrame:
    """Get information about balance historical transactions. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.

    Returns
    -------
    pd.DataFrame
        DataFrame with balance historical transactions (last 100)
    """
    response = make_request("getAddressHistory", address, limit=100)
    operations = response.pop("operations")
    if operations:
        for operation in operations:
            token = operation.pop("tokenInfo")
            if token:
                operation["token"] = token["name"]
                operation["tokenAddress"] = token["address"]
                operation["decimals"] = int(token["decimals"])
            operation["timestamp"] = datetime.fromtimestamp(operation["timestamp"])

    df = pd.DataFrame(operations)
    cols = ["timestamp", "transactionHash", "token", "value"]
    df["value"] = df["value"].astype(float) / (10 ** df["decimals"])

    if df.empty:
        console.print(f"No historical transaction found for {address}")
        return pd.DataFrame(columns=cols)

    df = df[cols]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_token_info(address) -> pd.DataFrame:
    """Get info about ERC20 token. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984

    Returns
    -------
    pd.DataFrame
        DataFrame with information about provided ERC20 token.
    """

    response = make_request("getTokenInfo", address)
    decimals = response.pop("decimals") if "decimals" in response else None

    for name in [
        "issuancesCount",
        "lastUpdated",
        "image",
        "transfersCount",
        "ethTransfersCount",
    ]:
        try:
            response.pop(name)
        except KeyError as e:
            logger.exception(str(e))
            continue

    enrich_social_media(response)
    df = pd.json_normalize(response)
    df.columns = [split_cols_with_dot(x) for x in df.columns.tolist()]
    if "priceTs" in df:
        df.drop("priceTs", axis=1, inplace=True)

    for col in [
        "owner",
        "slot",
        "facebook",
        "priceDiff",
        "priceDiff7d",
        "priceDiff30d",
        "priceVolDiff1",
        "priceVolDiff7",
        "priceVolDiff30",
        "priceCurrency",
    ]:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

    df["totalSupply"] = df["totalSupply"].astype(float) / (10 ** int(decimals))

    df = df.T.reset_index()
    df.columns = ["Metric", "Value"]
    # pylint: disable=unsupported-assignment-operation
    df["Value"] = df["Value"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=70)) if isinstance(x, str) else x
    )

    return df


@log_start_end(log=logger)
def get_tx_info(tx_hash: str) -> pd.DataFrame:
    """Get info about transaction. [Source: Ethplorer]

    Parameters
    ----------
    tx_hash: str
        Transaction hash e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6

    Returns
    -------
    pd.DataFrame
        DataFrame with information about ERC20 token transaction.
    """
    decimals = None
    response = make_request("getTxInfo", tx_hash)

    try:
        response.pop("logs")
        operations = response.pop("operations")[0]
        if operations:
            operations.pop("addresses")
            token = operations.pop("tokenInfo")
            decimals = token.get("decimals")
            if token:
                operations["token"] = token["name"]
                operations["tokenAddress"] = token["address"]
            operations["timestamp"] = datetime.fromtimestamp(operations["timestamp"])
        response.update(operations)
        response.pop("input")

        df = pd.Series(response)

        if decimals:
            for col in ["intValue", "value"]:
                df[col] = float(df[col]) // (10 ** int(decimals))

        df = df.to_frame().reset_index()
        df.columns = ["Metric", "Value"]
    except KeyError as e:
        logger.exception(str(e))
        return pd.DataFrame()
    return df


@log_start_end(log=logger)
def get_token_history(
    address: str, sortby: str = "timestamp", ascend: bool = False
) -> pd.DataFrame:
    """Get info about token historical transactions. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame
        DataFrame with token historical transactions.
    """

    response = make_request("getTokenHistory", address, limit=1000)
    all_operations = []
    operations = response["operations"]
    try:
        first_row = operations[0]["tokenInfo"]
        name, symbol, _ = (
            first_row.get("name"),
            first_row.get("symbol"),
            first_row.get("balance"),
        )
        decimals = first_row.get("decimals")
    except Exception as e:
        logger.exception(str(e))
        name, symbol = "", ""
        decimals = None

    for operation in operations:
        operation.pop("type")
        operation.pop("tokenInfo")
        operation["timestamp"] = datetime.fromtimestamp(operation["timestamp"])
        all_operations.append(operation)

    df = pd.DataFrame(all_operations)

    if df.empty:
        console.print(f"No historical transaction found for {address}")
        return df

    df[["name", "symbol"]] = name, symbol
    df["value"] = df["value"].astype(float) / (10 ** int(decimals))
    df = df[["timestamp", "name", "symbol", "value", "from", "to", "transactionHash"]]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_token_historical_price(
    address: str,
    sortby: str = "date",
    ascend: bool = False,
) -> pd.DataFrame:
    """Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame
        DataFrame with token historical prices.
    """

    response = make_request("getTokenPriceHistoryGrouped", address)
    data = response["history"]
    data.pop("current")
    prices = data.get("prices")

    if not prices:
        console.print(f"No historical price found for {address}")

        return pd.DataFrame()

    prices_df = pd.DataFrame(prices)
    prices_df["ts"] = prices_df["ts"].apply(lambda x: datetime.fromtimestamp(x))
    if "tmp" in prices_df.columns:
        prices_df.drop("tmp", axis=1, inplace=True)

    df = prices_df[
        ["date", "open", "close", "high", "low", "volumeConverted", "cap", "average"]
    ]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df
