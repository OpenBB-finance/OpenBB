"""Polygon Model"""
__docformat__ = "numpy"

import logging
from typing import List

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_POLYGON_KEY"])
def get_similar_companies(symbol: str, us_only: bool = False) -> List[str]:
    """Get similar companies from Polygon

    Parameters
    ----------
    symbol: str
        Ticker to get similar companies of
    us_only: bool
        Only stocks from the US stock exchanges

    Returns
    -------
    List[str]:
        List of similar tickers
    """
    result = request(
        f"https://api.polygon.io/v1/meta/symbols/{symbol.upper()}/company?&apiKey={get_current_user().credentials.API_POLYGON_KEY}"
    )

    similar = []

    if result.status_code == 200:
        similar = result.json()["similar"]
        if us_only:
            us_similar = []
            mkw_link = "https://www.marketwatch.com/investing/stock/"
            for sym in similar:
                prep_link = mkw_link + sym
                sent_req = request(prep_link)
                if prep_link == sent_req.request.url:
                    us_similar.append(sym)
                similar = us_similar
    elif result.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif result.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(result.json()["error"])

    return similar
