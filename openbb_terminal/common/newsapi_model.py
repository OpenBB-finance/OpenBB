""" News Model """
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_NEWS_TOKEN"])
def get_news(
    query: str,
    limit: int = 10,
    start_date: Optional[str] = None,
    show_newest: bool = True,
    sources: str = "",
) -> pd.DataFrame:
    """Get news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    query : str
        term to search on the news articles
    start_date: Optional[str]
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from (comma separated)

    Returns
    -------
    pd.DataFrame
        DataFrame with columns Date, Description, URL
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    link = (
        f"https://newsapi.org/v2/everything?q={query}&from={start_date}&sortBy=publishedAt"
        "&language=en"
    )

    if sources:
        if "," in sources:
            sources = ".com,".join(sources.split(","))
        link += f"&domains={sources}.com"
    link += f"&apiKey={get_current_user().credentials.API_NEWS_TOKEN}"
    response = request(link)
    articles = {}

    if response.status_code == 200:
        response_json = response.json()
        articles = (
            response_json["articles"]
            if show_newest
            else response_json["articles"][::-1]
        )
    elif response.status_code == 426:
        console.print(f"Error in request: {response.json()['message']}", "\n")
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['message']}", "\n")

    if articles:
        df = pd.DataFrame(articles)
        df["publishedAt"] = pd.to_datetime(df["publishedAt"])
        df["publishedAt"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        df = df[["publishedAt", "description", "url"]]
        df.columns = ["Date", "Description", "URL"]
        df = df[:limit]
        return df

    return pd.DataFrame()
