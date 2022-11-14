"""CoinPaprika model"""
__docformat__ = "numpy"

import logging
from typing import Any, Optional

import pandas as pd

from openbb_terminal.cryptocurrency.coinpaprika_helpers import PaprikaSession
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

CATEGORIES = [
    "currencies",
    "exchanges",
    "icos",
    "people",
    "tags",
    "all",
]

FILTERS = ["category", "id", "name"]


@log_start_end(log=logger)
def get_search_results(
    query: str,
    category: Optional[Any] = None,
    modifier: Optional[Any] = None,
    sortby: str = "id",
    ascend: bool = True,
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
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get)
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
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
    df = pd.DataFrame(results)
    df = df.sort_values(by=sortby, ascending=ascend)
    return df
