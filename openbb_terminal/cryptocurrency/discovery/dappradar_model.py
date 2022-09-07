"""DappRadar model"""
__docformat__ = "numpy"

# pylint: disable=C0301,E1137
from typing import Optional
import logging

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent
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
    "Daily Users",
    "Daily Volume [$]",
]


@log_start_end(log=logger)
def _make_request(url: str) -> Optional[dict]:
    """Helper method handles dappradar api requests. [Source: https://dappradar.com/]

    Parameters
    ----------
    url: str
        endpoint url
    Returns
    -------
    dict:
        dictionary with response data
    """

    headers = {
        "Accept": "application/json",
        "User-Agent": get_user_agent(),
        "referer": "https://dappradar.com/",
    }
    response = requests.get(url, headers=headers)
    if not 200 <= response.status_code < 300:
        console.print(f"[red]dappradar api exception: {response.text}[/red]")
        return None
    try:
        return response.json()
    except Exception as e:  # noqa: F841
        logger.exception("Invalid Response: %s", str(e))
        console.print(f"[red]Invalid Response:: {response.text}[/red]")
        return None


@log_start_end(log=logger)
def get_top_nfts(sortby: str = "") -> pd.DataFrame:
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
            inplace=False,
        )
        df["Protocols"] = df["Protocols"].apply(lambda x: ",".join(x))
        return df
    if sortby in NFT_COLUMNS:
        df = df.sort_values(by=sortby, ascending=False)
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_dexes(sortby: str = "") -> pd.DataFrame:
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
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXR"
        "ZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV1Y0WTJ"
        "oaGJtZGxjeVp6YjNKMFBYUnZkR0ZzVm05c2RXMWxTVzVHYVdGMEptOXlaR1Z5UFdSbGMyTW1iR2x0YVhROU1qWT0="
    )
    if data:
        arr = []
        for dex in data["dapps"]:
            arr.append(
                [
                    dex["name"],
                    dex["statistic"]["userActivity"],
                    dex["statistic"]["totalVolumeInFiat"],
                ]
            )
        df = pd.DataFrame(arr, columns=DEX_COLUMNS)
        if sortby in DEX_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        return df
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_games() -> pd.DataFrame:
    """Get top blockchain games by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        Top blockchain games. Columns: Name, Daily Users, Daily Volume [$]
    """
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMX"
        "RZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV2R"
        "oYldWekpuTnZjblE5ZFhObGNpWnZjbVJsY2oxa1pYTmpKbXhwYldsMFBUSTI="
    )
    if data:
        arr = []
        for dex in data["dapps"]:
            arr.append(
                [
                    dex["name"],
                    dex["statistic"]["userActivity"],
                    dex["statistic"]["totalVolumeInFiat"],
                ]
            )
        df = pd.DataFrame(
            arr,
            columns=DEX_COLUMNS,
        ).sort_values("Daily Users", ascending=False)
        return df
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_dapps(sortby: str = "") -> pd.DataFrame:
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
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMX"
        "RZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbk52Y25ROWRYTmxjaVp"
        "2Y21SbGNqMWtaWE5qSm14cGJXbDBQVEky"
    )
    if data:
        arr = []
        for dex in data["dapps"]:
            arr.append(
                [
                    dex["name"],
                    dex["category"],
                    dex["activeProtocols"],
                    dex["statistic"]["userActivity"],
                    dex["statistic"]["totalVolumeInFiat"],
                ]
            )
        df = pd.DataFrame(
            arr,
            columns=DAPPS_COLUMNS,
        ).sort_values("Daily Users", ascending=False)
        df["Protocols"] = df["Protocols"].apply(lambda x: ",".join(x))
        if sortby in DAPPS_COLUMNS:
            df = df.sort_values(by=sortby, ascending=False)
        return df
    return pd.DataFrame()
