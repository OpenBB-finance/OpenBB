"""CoinPaprika model"""
__docformat__ = "numpy"

from typing import Optional, Any
import pandas as pd
from gamestonk_terminal.cryptocurrency.coinpaprika_helpers import PaprikaSession


def get_search_results(
    query: str, category: Optional[Any] = None, modifier: Optional[Any] = None
) -> pd.DataFrame:
    """Search CoinPaprika. [Source: CoinPaprika]

    Parameters
    ----------
    query:  str
        phrase for search
    category:  Optional[Any]
        one or more categories (comma separated) to search.
        Available options: currencies|exchanges|icos|people|tags
        Default: currencies,exchanges,icos,people,tags
    modifier: Optional[Any]
        set modifier for search results. Available options: symbol_search -
        search only by symbol (works for currencies only)

    Returns
    -------
    pandas.DataFrame
        Search Results
        Columns: Metric, Value
    """

    session = PaprikaSession()
    if category is None:
        category = "currencies,exchanges,icos,people,tags"
    data = session.make_request(
        session.ENDPOINTS["search"], q=query, c=category, modifier=modifier, limit=100
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
