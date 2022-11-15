""" Finviz Model """
__docformat__ = "numpy"

import logging
from typing import Any, List

import finviz
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_news(symbol: str) -> List[Any]:
    """Get news from Finviz

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    List[Any]
        News
    """
    return finviz.get_news(symbol)


@log_start_end(log=logger)
def get_analyst_data(symbol: str) -> pd.DataFrame:
    """Get analyst data. [Source: Finviz]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    df_fa: DataFrame
        Analyst price targets
    """
    d_finviz_analyst_price = finviz.get_analyst_price_targets(symbol)
    df_fa = pd.DataFrame.from_dict(d_finviz_analyst_price)
    df_fa.set_index("date", inplace=True)

    return df_fa
