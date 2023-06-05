"""Finviz Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Any, Dict, List

import finviz
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

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
    try:
        d_finviz_stock = finviz.get_stock(symbol)
    except Exception:
        return pd.DataFrame()
    df_fa = pd.DataFrame.from_dict(d_finviz_stock, orient="index", columns=["Values"])
    return df_fa[df_fa.Values != "-"]


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
    d_finviz_analyst_price = get_analyst_price_targets_workaround(symbol)
    df_fa = pd.DataFrame.from_dict(d_finviz_analyst_price)
    if not df_fa.empty:
        df_fa.set_index("date", inplace=True)

    return df_fa


# Patches finviz function while finviz is not updated
def get_analyst_price_targets_workaround(
    ticker: str, last_ratings: int = 5
) -> List[Dict]:
    """Patch the analyst price targets function from finviz

    Parameters
    ----------
    ticker: str
        Ticker symbol
    last_ratings: int
        Number to get

    """

    analyst_price_targets = []

    try:
        finviz.main_func.get_page(ticker)
        page_parsed = finviz.main_func.STOCK_PAGE[ticker]
        table = page_parsed.cssselect(
            'table[class="js-table-ratings fullview-ratings-outer"]'
        )[0]

        # skip first row of table since its the header
        for row in table[1:]:
            rating = row.xpath("td//text()")
            rating = [
                val.replace("→", "->").replace("$", "") for val in rating if val != "\n"
            ]
            rating[0] = datetime.strptime(rating[0], "%b-%d-%y").strftime("%Y-%m-%d")

            data = {
                "date": rating[0],
                "category": rating[1],
                "analyst": rating[2],
                "rating": rating[3],
            }
            if len(rating) == 5:
                if "->" in rating[4]:
                    rating.extend(rating[4].replace(" ", "").split("->"))
                    del rating[4]
                    data["target_from"] = float(rating[4])
                    data["target_to"] = float(rating[5])
                else:
                    data["target"] = float(rating[4])

            analyst_price_targets.append(data)
    except Exception:
        pass  # noqa

    return analyst_price_targets[:last_ratings]


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
    try:
        result = finviz.get_news(symbol)
    except ValueError:
        console.print(f"[red]Error getting news for {symbol}[/red]")
        result = []
    return result
