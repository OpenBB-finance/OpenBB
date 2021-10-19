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

    if r.status_code == 200:
        try:
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
        except TypeError:
            print("Error in ethgasstation JSON response.\n")
            return pd.DataFrame()
    else:
        print("Error in ethgasstation GET request\n")
        return pd.DataFrame()
