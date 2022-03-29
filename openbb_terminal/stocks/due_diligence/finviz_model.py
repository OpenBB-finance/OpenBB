""" Finviz Model """
__docformat__ = "numpy"

import logging
from typing import Any, List

import finviz
import pandas as pd
from pandas.core.frame import DataFrame

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_news(ticker: str) -> List[Any]:
    """Get news from Finviz

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    List[Any]
        News
    """
    return finviz.get_news(ticker)


@log_start_end(log=logger)
def get_analyst_data(ticker: str) -> DataFrame:
    """Get analyst data. [Source: Finviz]

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    df_fa: DataFrame
        Analyst price targets
    """
    d_finviz_analyst_price = finviz.get_analyst_price_targets(ticker)
    df_fa = pd.DataFrame.from_dict(d_finviz_analyst_price)
    df_fa.set_index("date", inplace=True)

    return df_fa
