import pandas as pd
from gamestonk_terminal.cryptocurrency.coinpaprika_helpers import (
    ENDPOINTS,
    PaprikaSession,
)


session = PaprikaSession()


def search(q, c=None, modifier=None):
    """Search CoinPaprika
    Parameters
    ----------
    q:  phrase for search
    c:  one or more categories (comma separated) to search.
        Available options: currencies|exchanges|icos|people|tags
        Default: currencies,exchanges,icos,people,tags
    modifier: set modifier for search results. Available options: symbol_search -
        search only by symbol (works for currencies only)

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    if c is None:
        c = "currencies,exchanges,icos,people,tags"
    data = session.make_request(
        ENDPOINTS["search"], q=q, c=c, modifier=modifier, limit=100
    )
    results = []
    for item in data:
        category = data[item]
        for r in category:
            results.append(
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "category": item,
                }
            )
    return pd.DataFrame(results)
