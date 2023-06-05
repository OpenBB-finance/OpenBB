""" Feedparser Model """
__docformat__ = "numpy"

import os
from typing import List
from urllib.parse import quote

import certifi
import feedparser
import pandas as pd

from openbb_terminal.rich_config import console


def get_news(
    term: str = "",
    sources: str = "",
    sort: str = "published",
    limit: int = 10,
    display_message: bool = True,
) -> pd.DataFrame:
    """Get news for a given term and source. [Source: Feedparser]

    Parameters
    ----------
    term : str
        term to search on the news articles
    sources: str
        sources to exclusively show news from (separated by commas)
    sort: str
        the column to sort by
    limit : int
        number of articles to display
    display_message: bool
        whether to display a message to the user

    Returns
    -------
    articles: pd.DataFrame
        term to search on the news articles

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.news()
    """
    # Necessary for installer so that it can locate the correct certificates for
    # API calls and https
    # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    os.environ["SSL_CERT_FILE"] = certifi.where()

    have_data = False
    if display_message:
        console.print("[yellow]Fetching data. Please be patient\n[/yellow]")
    n = 0

    while not have_data:
        if term:
            term = quote(term)
            data = feedparser.parse(
                f"https://news.google.com/rss/search?q={term}&hl=en-US&gl=US&ceid=US:en&when:24h+allinurl"
                f':{sources.replace(" ", "%20")}'
            )
        else:
            data = feedparser.parse(
                f'https://news.google.com/rss/search?q=when:24h+allinurl:{sources.replace(" ", "%20")}'
                "&hl=en-US&gl=US&ceid=US:en"
            )

        if (
            hasattr(data, "status") and data.status == 200
        ):  # Checking if data has status attribute and if data request succeeded
            if data.entries:
                have_data = True
            elif n == 60:  # Breaking if 60 successful requests return no data
                console.print("[red]Timeout occurred. Please try again\n[/red]")
                break
            n += 1

        elif hasattr(data, "status") and data.status != 200:  # If data request failed
            console.print("[red]Status code not 200. Unable to retrieve data\n[/red]")
            break
        else:
            console.print("[red]Could not retrieve data\n[/red]")
            break

    # Filter based on data sources
    if sources:
        newdata: List = []
        for entry in list(data.entries):
            # check if sources specified
            if "," in sources:
                if entry["source"]["title"].lower().find(sources.lower()) != -1:
                    newdata.append(entry)
            else:
                for s in sources.split(","):
                    if entry["source"]["title"].lower().find(s.lower()) != -1:
                        newdata.append(entry)

        if newdata:
            df = pd.DataFrame(newdata, columns=["title", "link", "published"])
        else:
            return pd.DataFrame()
    else:
        df = pd.DataFrame(data.entries, columns=["title", "link", "published"])
    df["published"] = pd.to_datetime(df["published"])
    df = df.sort_values(by=[sort], ascending=False)
    df = df[["published", "title", "link"]]
    df.columns = ["Date", "Description", "URL"]
    df = df[:limit]
    return df
