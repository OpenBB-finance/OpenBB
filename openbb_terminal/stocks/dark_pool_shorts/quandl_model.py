""" Quandl Model """
__docformat__ = "numpy"

import logging
from multiprocessing import AuthenticationError

import pandas as pd
import quandl

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_short_interest(ticker: str, nyse: bool) -> pd.DataFrame:
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    ticker : str
        ticker to get short interest from
    nyse : bool
        data from NYSE if true, otherwise NASDAQ

    Returns
    ----------
    pd.DataFrame
        short interest volume data
    """
    quandl.ApiConfig.api_key = cfg.API_KEY_QUANDL

    df = pd.DataFrame()

    try:

        if nyse:
            df = quandl.get(f"FINRA/FNYX_{ticker}")
        else:
            df = quandl.get(f"FINRA/FNSQ_{ticker}")

    except AuthenticationError:
        console.print("[red]Invalid API Key[/red]\n")
    # Catch invalid ticker
    except Exception as e:
        console.print(e)

    return df
