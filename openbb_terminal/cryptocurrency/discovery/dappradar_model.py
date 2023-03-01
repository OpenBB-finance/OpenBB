"""DappRadar model"""
__docformat__ = "numpy"

# pylint: disable=C0301,E1137
import logging
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

NFT_COLUMNS = [
    "Name",
    "Protocols",
    "Floor Price [$]",
    "Avg Price [$]",
    "Market Cap [$]",
    "Volume [$]",
]

DAPPS_COLUMNS = [
    "Name",
    "Category",
    "Protocols",
    "Daily Users",
    "Daily Volume [$]",
]

DEX_COLUMNS = [
    "Name",
    "Category",
    "Daily Users",
    "Daily Volume [$]",
]


@log_start_end(log=logger)
def _make_request(url: str, verbose: bool = False) -> Optional[dict]:
    """Helper method handles dappradar api requests. [Source: https://dappradar.com/]

    Parameters
    ----------
    url: str
        endpoint url
    verbose: bool
        whether to print the text from the response

    Returns
    -------
    Optional[dict]:
        dictionary with response data
    """

    headers = {
        "Accept": "application/json",
        "User-Agent": get_user_agent(),
        "referer": "https://dappradar.com/",
    }
    response = request(url, headers=headers)
    if not 200 <= response.status_code < 300:
        if verbose:
            console.print(f"[red]dappradar api exception: {response.text}[/red]")
        return None
    try:
        return response.json()
    except Exception as e:  # noqa: F841
        logger.exception("Invalid Response: %s", str(e))
        if verbose:
            console.print(f"[red]Invalid Response:: {response.text}[/red]")
        return None


@log_start_end(log=logger)
def get_top_nfts(sortby: str = "", limit: int = 10) -> pd.DataFrame:
    """Get top nft collections [Source: https://dappradar.com/]

    Parameters
    ----------
    sortby: str
        Key by which to sort data

    Returns
    -------
    pd.DataFrame
        NFTs Columns: Name, Protocols, Floor Price [$], Avg Price [$], Market Cap [$], Volume [$]
    """

    sortby = sortby.replace("_", " ").title()

    response = _make_request(
        "https://nft-sales-service.dappradar.com/v2/collection/day?limit=20&p"
        "age=1&currency=USD&sort=marketCapInFiat&order=desc"
    )
    if response:
        data = response.get("results")
        df = pd.DataFrame(
            data,
            columns=[
                "name",
                "activeProtocols",
                "floorPriceInFiat",
                "avgPriceInFiat",
                "marketCapInFiat",
                "volumeInFiat",
            ],
        )

        df = df.set_axis(
            NFT_COLUMNS,
            axis=1,
            copy=False,
        )
        df["Protocols"] = df["Protocols"].apply(lambda x: ",".join(x))
    if response and sortby in NFT_COLUMNS:
        df = df.sort_values(by=sortby, ascending=False)
        return df.head(limit)
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_dexes(sortby: str = "", limit: int = 10) -> pd.DataFrame:
    """Get top dexes by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------
    sortby: str
        Key by which to sort data

    Returns
    -------
    pd.DataFrame
        Top decentralized exchanges. Columns: Name, Daily Users, Daily Volume [$]
    """

    sortby = sortby.replace("_", " ").title()

    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXR"
        # pragma: allowlist nextline secret
        "ZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV1Y0WTJ"
        # pragma: allowlist nextline secret
        "oaGJtZGxjeVp6YjNKMFBYUnZkR0ZzVm05c2RXMWxTVzVHYVdGMEptOXlaR1Z5UFdSbGMyTW1iR2x0YVhROU1qWT0="
    )
    if data:
        arr = [
            [
                dex["name"],
                dex["category"],
                dex["statistic"]["userActivity"],
                dex["statistic"]["totalVolumeInFiat"],
            ]
            for dex in data["dapps"]
        ]

        df = pd.DataFrame(arr, columns=DEX_COLUMNS)
        if sortby in DEX_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        df = df[df["Category"] == "exchanges"]
        if df.empty:
            return pd.DataFrame()
        df.drop("Category", axis=1, inplace=True)
        return df.head(limit)
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_games(sortby: str = "", limit: int = 10) -> pd.DataFrame:
    """Get top blockchain games by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data

    Returns
    -------
    pd.DataFrame
        Top blockchain games. Columns: Name, Daily Users, Daily Volume [$]
    """

    sortby = sortby.replace("_", " ").title()

    data = _make_request(
        # pragma: allowlist nextline secret
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMX"
        # pragma: allowlist nextline secret
        "RZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV2R"
        # pragma: allowlist nextline secret
        "oYldWekpuTnZjblE5ZFhObGNpWnZjbVJsY2oxa1pYTmpKbXhwYldsMFBUSTI="
    )
    if data:
        arr = [
            [
                dex["name"],
                dex["category"],
                dex["statistic"]["userActivity"],
                dex["statistic"]["totalVolumeInFiat"],
            ]
            for dex in data["dapps"]
        ]

        df = pd.DataFrame(
            arr,
            columns=DEX_COLUMNS,
        ).sort_values("Daily Users", ascending=False)
        if sortby in df.columns:
            df = df.sort_values(by=sortby, ascending=False)
        df = df[df["Category"] == "games"]
        df.drop("Category", axis=1, inplace=True)
        return df.head(limit)
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_dapps(sortby: str = "", limit: int = 10) -> pd.DataFrame:
    """Get top decentralized applications by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------
    sortby: str
        Key by which to sort data

    Returns
    -------
    pd.DataFrame
        Top decentralized exchanges.
        Columns: Name, Category, Protocols, Daily Users, Daily Volume [$]
    """

    sortby = sortby.replace("_", " ").title()

    data = _make_request(
        # pragma: allowlist nextline secret
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMX"
        # pragma: allowlist nextline secret
        "RZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbk52Y25ROWRYTmxjaVp"
        # pragma: allowlist nextline secret
        "2Y21SbGNqMWtaWE5qSm14cGJXbDBQVEky",
        False,
    )
    if data:
        arr = [
            [
                dex["name"],
                dex["category"],
                dex["activeProtocols"],
                dex["statistic"]["userActivity"],
                dex["statistic"]["totalVolumeInFiat"],
            ]
            for dex in data["dapps"]
        ]

        df = pd.DataFrame(
            arr,
            columns=DAPPS_COLUMNS,
        ).sort_values("Daily Users", ascending=False)
        df["Protocols"] = df["Protocols"].apply(lambda x: ",".join(x))
        if sortby in DAPPS_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        return df.head(limit)
    return pd.DataFrame()
