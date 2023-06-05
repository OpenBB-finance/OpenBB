""" Quandl Model """
__docformat__ = "numpy"

import logging
from multiprocessing import AuthenticationError

import pandas as pd
import quandl

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def get_short_interest(symbol: str, nyse: bool = False) -> pd.DataFrame:
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    symbol : str
        ticker to get short interest from
    nyse : bool
        data from NYSE if true, otherwise NASDAQ

    Returns
    -------
    pd.DataFrame
        short interest volume data
    """
    quandl.ApiConfig.api_key = get_current_user().credentials.API_KEY_QUANDL

    df = pd.DataFrame()

    try:
        df = (
            quandl.get(f"FINRA/FNYX_{symbol}")
            if nyse
            else quandl.get(f"FINRA/FNSQ_{symbol}")
        )

    except AuthenticationError:
        console.print("[red]Invalid API Key[/red]\n")
    # Catch invalid symbol
    except Exception as e:
        console.print(e)

    return df
