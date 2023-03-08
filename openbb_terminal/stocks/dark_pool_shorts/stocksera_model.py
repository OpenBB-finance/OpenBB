"""Stocksera model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import stocksera
from stocksera.exceptions import StockseraRequestException

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_cost_to_borrow(symbol: str) -> pd.DataFrame:
    """Get cost to borrow of stocks [Source: Stocksera]

    Parameters
    ----------
    symbol : str
        ticker to get cost to borrow from

    Returns
    -------
    pd.DataFrame
        Cost to borrow
    """

    df = pd.DataFrame()

    try:
        client = stocksera.Client(
            api_key=get_current_user().credentials.API_STOCKSERA_KEY
        )
        df = pd.DataFrame(client.borrowed_shares(ticker=symbol))
        df.columns = ["Ticker", "Fees", "Available", "Date"]
        df.set_index("Date", inplace=True)

    except StockseraRequestException:
        console.print("[red]Invalid API Key[/red]\n")
    except Exception as e:
        console.print(f"[red]{e}[/red]\n")
    return df
