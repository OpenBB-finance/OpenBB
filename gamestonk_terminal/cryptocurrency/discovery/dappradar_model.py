"""DappRadar model"""
__docformat__ = "numpy"

# pylint: disable=C0301

import requests
import pandas as pd
from gamestonk_terminal.helper_funcs import get_user_agent
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    long_number_format_with_type_check,
)


def _make_request(url: str) -> dict:
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
        raise Exception(f"dappradar api exception: {response.text}")
    try:
        return response.json()
    except Exception as e:
        raise ValueError(f"Invalid Response: {response.text}") from e


def get_top_nfts() -> pd.DataFrame:
    """[Source: ]

    Parameters
    ----------
    address: str

    Returns
    -------
    Tuple[pd.DataFrame, str]:
        luna delegations and summary report for given address
    """

    response = _make_request(
        "https://nft-sales-service.dappradar.com/v2/collection/day?limit=20&page=1&currency=USD&sort=marketCapInFiat&order=desc"  # noqa
    )
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
        [
            "Name",
            "Protocols",
            "Floor Price ($)",
            "Avg Price ($)",
            "Market Cap ($)",
            "Volume ($)",
        ],
        axis=1,
        inplace=False,
    )
    df["Protocols"].apply(lambda x: ",".join(x))
    df = df.applymap(lambda x: long_number_format_with_type_check(x))
    return df


def get_top_dexes() -> pd.DataFrame:
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXRZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV1Y0WTJoaGJtZGxjeVp6YjNKMFBYUnZkR0ZzVm05c2RXMWxTVzVHYVdGMEptOXlaR1Z5UFdSbGMyTW1iR2x0YVhROU1qWT0="  # noqa
    )
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
        columns=[
            "Name",
            "Daily Users",
            "Daily Volume ($)",
        ],
    )
    df = df.applymap(lambda x: long_number_format_with_type_check(x))
    return df


def get_top_games() -> pd.DataFrame:
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXRZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbU5oZEdWbmIzSjVQV2RoYldWekpuTnZjblE5ZFhObGNpWnZjbVJsY2oxa1pYTmpKbXhwYldsMFBUSTI="  # noqa
    )
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
        columns=[
            "Name",
            "Daily Users",
            "Daily Volume ($)",
        ],
    ).sort_values("Daily Users", ascending=False)
    df = df.applymap(lambda x: long_number_format_with_type_check(x))
    return df


def get_top_dapps() -> pd.DataFrame:
    data = _make_request(
        "https://dappradar.com/v2/api/dapps?params=WkdGd2NISmhaR0Z5Y0dGblpUMHhKbk5uY205MWNEMXRZWGdtWTNWeWNtVnVZM2s5VlZORUptWmxZWFIxY21Wa1BURW1jbUZ1WjJVOVpHRjVKbk52Y25ROWRYTmxjaVp2Y21SbGNqMWtaWE5qSm14cGJXbDBQVEky"  # noqa
    )
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
        columns=[
            "Name",
            "Category",
            "Protocols",
            "Daily Users",
            "Daily Volume ($)",
        ],
    ).sort_values("Daily Users", ascending=False)
    df["Protocols"] = df["Protocols"].apply(lambda x: ",".join(x))
    df = df.applymap(lambda x: long_number_format_with_type_check(x))
    return df
