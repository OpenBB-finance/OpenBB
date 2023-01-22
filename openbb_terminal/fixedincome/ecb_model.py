""" ECB model """
__docformat__ = "numpy"

import logging
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_series_data(
    series_id: str = "EST.B.EU000A2X2A25.WT", start_date: str = "", end_date: str = ""
):
    """Get ECB data

    Parameters
    ----------
    series_id: str
        ECB ID of data
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    start_date = start_date[0:4] + start_date[4:7] + start_date[8:9]
    end_date = end_date[0:4] + end_date[4:7] + end_date[8:9]

    df = pd.read_csv(
        f"https://sdw.ecb.europa.eu/quickviewexport.do?trans=N&start={start_date}&end={end_date}&SERIES_KEY={series_id}&type=csv",
        header=5,
        usecols=[0, 1],
        index_col=0,
        parse_dates=True,
    )
    df = df.iloc[::-1]

    return df
