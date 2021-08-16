""" Finviz Model """
__docformat__ = "numpy"

from typing import Dict
from colorama import Fore, Style
import finviz
import pandas as pd
from pandas.core.frame import DataFrame


def category_color_red_green(val: str) -> str:
    """Add color to analyst rating

    Parameters
    ----------
    val : str
        Analyst rating - Upgrade/Downgrade

    Returns
    -------
    str
        Analyst rating with color
    """
    if val == "Upgrade":
        return Fore.GREEN + val + Style.RESET_ALL
    if val == "Downgrade":
        return Fore.RED + val + Style.RESET_ALL
    return val


def get_news(ticker: str) -> Dict:
    """Get news from Finviz

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    Dict
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
