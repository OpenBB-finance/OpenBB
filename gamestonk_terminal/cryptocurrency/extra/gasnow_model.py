import pandas as pd
import requests


def get_gwei_fees() -> pd.DataFrame:
    """Returns the most recent Ethereum gas fees in gwei
    [Source: https://www.gasnow.org]

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

    r = requests.get("https://www.gasnow.org/api/v3/gas/price")

    if r.status_code == 200:
        try:
            data = r.json()["data"]
            return pd.DataFrame(
                data=[
                    ["Fastest", int(data["rapid"] / 1_000_000_000), "~15 sec"],
                    ["Fast", int(data["fast"] / 1_000_000_000), "~1 min"],
                    ["Standard", int(data["standard"] / 1_000_000_000), "~3 min"],
                    ["Slow", int(data["slow"] / 1_000_000_000), ">10 min"],
                ],
                columns=["Tx Type", "Fee (gwei)", "Duration"],
            )
        except TypeError:
            print("Error in gasnow JSON response.\n")
            return pd.DataFrame()
    else:
        print("Error in gasnow GET request\n")
        return pd.DataFrame()
