import pandas as pd
import requests


def get_gwei_fees() -> pd.DataFrame:
    """Returns the most recent Ethereum gas fees in gwei

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        gas prices
    """

    r = requests.get("https://www.gasnow.org/api/v3/gas/price").json()["data"]

    return pd.DataFrame(
        data=[
            ["Fastest", int(r["rapid"] / 1_000_000_000), "~15 sec"],
            ["Fast", int(r["fast"] / 1_000_000_000), "~1 min"],
            ["Standard", int(r["standard"] / 1_000_000_000), "~3 min"],
            ["Slow", int(r["slow"] / 1_000_000_000), ">10 min"],
        ],
        columns=["Label", "Fee (gwei)", "Duration"],
    )
