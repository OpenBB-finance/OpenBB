"Polygon Model"
__docformat__ = "numpy"

from typing import List, Tuple

import requests
from gamestonk_terminal import config_terminal as cfg


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
    else:
        print(result.json()["error"])
        similar = [""]
        source = "Error"
    return similar, source
