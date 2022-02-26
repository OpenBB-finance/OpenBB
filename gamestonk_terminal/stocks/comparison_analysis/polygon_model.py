"Polygon Model"
__docformat__ = "numpy"

import logging
from typing import List, Tuple

import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_similar_companies(ticker: str, us_only: bool) -> Tuple[List[str], str]:
    """Get similar companies from Polygon

    Parameters
    ----------
    ticker : str
        Ticker to get similar companies of

    Returns
    -------
    List[str] :
        List of similar tickers
    str :
        String indicating data source
    """
    result = requests.get(
        f"https://api.polygon.io/v1/meta/symbols/{ticker.upper()}/company?&apiKey={cfg.API_POLYGON_KEY}"
    )

    similar = []
    source = "Error"

    if result.status_code == 200:
        similar = result.json()["similar"]
        source = "Polygon"
        if us_only:
            us_similar = []
            mkw_link = "https://www.marketwatch.com/investing/stock/"
            for sym in similar:
                prep_link = mkw_link + sym
                sent_req = requests.get(prep_link)
                if prep_link == sent_req.request.url:
                    us_similar.append(sym)
                similar = us_similar
    elif result.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif result.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(result.json()["error"])

    return similar, source
