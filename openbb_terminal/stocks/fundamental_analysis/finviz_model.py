"""Finviz Model"""
__docformat__ = "numpy"

import logging

import finviz
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_data(ticker: str) -> pd.DataFrame:
    """Get fundamental data from finviz

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        DataFrame of fundamental data
    """
    d_finviz_stock = finviz.get_stock(ticker)
    df_fa = pd.DataFrame.from_dict(d_finviz_stock, orient="index", columns=["Values"])
    return df_fa[df_fa.Values != "-"]
