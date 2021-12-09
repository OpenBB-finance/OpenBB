""" Finviz Model """
__docformat__ = "numpy"

from typing import List, Any
import finviz
import pandas as pd
from pandas.core.frame import DataFrame


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
