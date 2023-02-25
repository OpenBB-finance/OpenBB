""" Finnhub Model """
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def get_rating_over_time(symbol: str) -> pd.DataFrame:
    """Get rating over time data. [Source: Finnhub]

    Parameters
    ----------
    symbol : str
        Ticker symbol to get ratings from

    Returns
    -------
    pd.DataFrame
        Get dataframe with ratings
    """
    response = request(
        f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={get_current_user().credentials.API_FINNHUB_KEY}"
    )
    df = pd.DataFrame()

    if response.status_code == 200:
        if response.json():
            df = pd.DataFrame(response.json())
        else:
            console.print("No ratings over time found", "\n")
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df
