""" Finviz Model """
__docformat__ = "numpy"

import logging

import finviz
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_last_insider_activity(symbol: str) -> pd.DataFrame:
    """Get last insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Latest insider trading activity
    """
    activity_dict = finviz.get_insider(symbol)
    df = pd.DataFrame.from_dict(activity_dict)

    if df.empty:
        console.print(f"[red]No insider information found for {symbol}.\n[/red]")
    else:
        df.set_index("Date", inplace=True)
        df = df[
            [
                "Relationship",
                "Transaction",
                "#Shares",
                "Cost",
                "Value ($)",
                "#Shares Total",
                "Insider Trading",
                "SEC Form 4",
            ]
        ]

    return df
