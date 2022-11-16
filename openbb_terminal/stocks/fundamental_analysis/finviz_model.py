"""Finviz Model"""
__docformat__ = "numpy"

import logging

import finviz
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_data(symbol: str) -> pd.DataFrame:
    """Get fundamental data from finviz

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        DataFrame of fundamental data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.fa.data("IWV")
    """
    d_finviz_stock = finviz.get_stock(symbol)
    df_fa = pd.DataFrame.from_dict(d_finviz_stock, orient="index", columns=["Values"])
    return df_fa[df_fa.Values != "-"]
