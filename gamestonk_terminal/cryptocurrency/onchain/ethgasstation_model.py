"""ETH Gas Station model"""
import pandas as pd
import requests


def get_gwei_fees() -> pd.DataFrame:
    """Returns the most recent Ethereum gas fees in gwei
    [Source: https://ethgasstation.info]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        four gas fees and durations
            (fees for slow, average, fast and
            fastest transactions in gwei and
            its average durations in seconds)
    """

    r = requests.get("https://ethgasstation.info/json/ethgasAPI.json")

    try:
        if r.status_code == 200:
            apiData = r.json()
            return pd.DataFrame(
                data=[
                    [
                        "Fastest",
                        int(apiData["fastest"] / 10),
                        round(apiData["fastestWait"], 1),
                    ],
                    ["Fast", int(apiData["fast"] / 10), round(apiData["fastWait"], 1)],
                    [
                        "Average",
                        int(apiData["average"] / 10),
                        round(apiData["avgWait"], 1),
                    ],
                    [
                        "Slow",
                        int(apiData["safeLow"] / 10),
                        round(apiData["safeLowWait"], 1),
                    ],
                ],
                columns=["Tx Type", "Fee (gwei)", "Duration (min)"],
            )
        return pd.DataFrame()
    except TypeError:
        return pd.DataFrame()
    except requests.exceptions.RequestException:
        return pd.DataFrame()
