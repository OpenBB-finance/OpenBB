""" NYSE Model """
__docformat__ = "numpy"

import logging

from datetime import datetime, timedelta
import pandas as pd


# from openbb_terminal.decorators import log_start_end

# logger = logging.getLogger(__name__)


# @log_start_end(log=logger)
def get_trading_halts(ticker: str = "") -> pd.DataFrame:
    """Get stocks with highest cost to borrow [Source: Interactive Broker]

    Returns
    -------
    pd.DataFrame
        Cost to borrow
    """
    data = pd.read_csv(f"https://www.nyse.com/api/trade-halts/historical/download?haltDateFrom="
                       f"{str(datetime.utcnow().date() - timedelta(days=365))}")
    data.fillna("N/A", inplace=True)
    # data["Halt Date"] = data["Halt Date"].astype(str)
    # data["Halt Date"] = data["Halt Date"].apply(lambda x: str(x[6:] + "-" + x[:2] + "-" + x[3:5] if x != "N/A" else "N/A"))
    # data["Resume Date"] = data["Resume Date"].astype(str)
    # data["Resume Date"] = data["Resume Date"].apply(
    #     lambda x: str(x[6:] + "-" + x[:2] + "-" + x[3:5] if x != "N/A" else "N/A"))
    del data["Name"]
    data.rename(columns={"Symbol": "Ticker", "NYSE Resume Time": "Resume Time"}, inplace=True)
    if ticker:
        data = data[data["Ticker"] == ticker]
    print(data)
    return data


get_trading_halts("AMC")
