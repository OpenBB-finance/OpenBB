""" Interactive Broker Model """
__docformat__ = "numpy"

import ftplib
import logging
from io import BytesIO

import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_cost_to_borrow() -> pd.DataFrame:
    """Get stocks with highest cost to borrow [Source: Interactive Broker]

    Returns
    -------
    pd.DataFrame
        Cost to borrow
    """
    ftp = ftplib.FTP("ftp3.interactivebrokers.com", "shortstock")

    flo = BytesIO()
    ftp.retrbinary("RETR usa.txt", flo.write)
    flo.seek(0)

    data = pd.read_csv(flo, sep="|", skiprows=1)
    data = data[["#SYM", "FEERATE", "AVAILABLE"]]
    data["AVAILABLE"] = data["AVAILABLE"].replace(">10000000", 10000000)
    data.fillna(0, inplace=True)
    data["AVAILABLE"] = data["AVAILABLE"].astype(int)
    data.sort_values(by=["FEERATE"], ascending=False, inplace=True)
    data["FEERATE"] = data["FEERATE"].apply(lambda x: str(x) + "%")
    data.columns = ["Symbol", "Fees", "Available"]
    data = data.reset_index(drop=True)
    return data
