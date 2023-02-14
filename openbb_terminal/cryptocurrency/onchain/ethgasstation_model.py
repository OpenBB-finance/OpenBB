"""ETH Gas Station model"""
import logging

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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

    r = request("https://ethgasstation.info/json/ethgasAPI.json")

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
    except TypeError as terr:
        logger.exception(str(terr))
        return pd.DataFrame()
    except requests.exceptions.RequestException as re:
        logger.exception(str(re))
        return pd.DataFrame()
