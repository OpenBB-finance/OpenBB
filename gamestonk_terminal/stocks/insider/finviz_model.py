""" Finviz Model """
__docformat__ = "numpy"

from typing import Dict
import finviz


def get_last_insider_activity(ticker: str) -> Dict:
    """Get last insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    ticker : str
        Stock ticker

    Dict
        Latest insider trading activity
    """
    return finviz.get_insider(ticker)
