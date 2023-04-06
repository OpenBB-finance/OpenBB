"""Finnhub model"""
__docformat__ = "numpy"

import logging
from typing import List

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def get_similar_companies(symbol: str) -> List[str]:
    """Get similar companies from Finhub.

    Parameters
    ----------
    symbol : str
        Ticker to find comparisons for

    Returns
    -------
    List[str]
        List of similar companies
    """

    response = request(
        f"https://finnhub.io/api/v1/stock/peers?symbol={symbol}&token={get_current_user().credentials.API_FINNHUB_KEY}"
    )

    similar = []

    if response.status_code == 200:
        similar = response.json()

        if not similar:
            console.print("Similar companies not found.")
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return similar
