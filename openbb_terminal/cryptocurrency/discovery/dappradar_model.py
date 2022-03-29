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

    response = requests.get(
        url, headers={"Accept": "application/json", "User-Agent": get_user_agent()}
    )
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
def get_top_nfts() -> pd.DataFrame:
    """Get top nft collections [Source: https://dappradar.com/]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        NFT collections. Columns: Name, Protocols, Floor Price [$], Avg Price [$], Market Cap [$], Volume [$]
    """

    response = _make_request(
        "https://nft-sales-service.dappradar.com/v2/collection/day?limit=20&page=1&currency=USD&sort=marketCapInFiat&order=desc"  # noqa
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
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_dexes() -> pd.DataFrame:
    """Get top dexes by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        Top decentralized exchanges. Columns: Name, Daily Users, Daily Volume [$]
    """
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXRZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV1Y0WTJoaGJtZGxjeVp6YjNKMFBYUnZkR0ZzVm05c2RXMWxTVzVHYVdGMEptOXlaR1Z5UFdSbGMyTW1iR2x0YVhROU1qWT0="  # noqa
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
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXRZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV2RoYldWekpuTnZjblE5ZFhObGNpWnZjbVJsY2oxa1pYTmpKbXhwYldsMFBUSTI="  # noqa
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
def get_top_dapps() -> pd.DataFrame:
    """Get top decentralized applications by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        Top decentralized exchanges. Columns: Name, Category, Protocols, Daily Users, Daily Volume [$]
    """
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXRZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbk52Y25ROWRYTmxjaVp2Y21SbGNqMWtaWE5qSm14cGJXbDBQVEky"  # noqa
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
        return df
    return pd.DataFrame()
