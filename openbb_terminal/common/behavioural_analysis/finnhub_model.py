"""Finnhub Model"""
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
def get_sentiment_stats(ticker: str) -> pd.DataFrame:
    """Get sentiment stats [Source: finnhub].

    Parameters
    ----------
    ticker : str
        Ticker to get sentiment stats

    Returns
    -------
    pd.DataFrame
        Get sentiment stats
    """
    response = request(
        f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={get_current_user().credentials.API_FINNHUB_KEY}"
    )

    df = pd.DataFrame()
    if response.status_code == 200:
        df = response.json()

        if df.empty:
            console.print(f"No sentiment stats found for {ticker}.\n")

    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df
