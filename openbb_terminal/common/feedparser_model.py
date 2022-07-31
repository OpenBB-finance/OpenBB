""" Feedparser Model """
__docformat__ = "numpy"

import feedparser
import pandas as pd


def get_news(
    term: str,
    sources: str = "bloomberg.com",
) -> pd.DataFrame:
    """Get news for a given term and source. [Source: Feedparser]

    Parameters
    ----------
    term : str
        term to search on the news articles
    sources: str
        sources to exclusively show news from

    Returns
    ----------
    articles : dict
        term to search on the news articles
    """
    if term:
        if sources:
            data = feedparser.parse(
                f"https://news.google.com/rss/search?q={term}&hl=en-US&gl=US&ceid=US:en&when:24h+allinurl"
                f':{sources.replace(" ", "%20")}'
            )
        else:
            data = feedparser.parse(
                f"https://news.google.com/rss/search?q={term}&when:24h&hl=en-US&gl=US&ceid=US:en"
            )
    else:
        if sources:
            data = feedparser.parse(
                f'https://news.google.com/rss/search?q=when:24h+allinurl:{sources.replace(" ", "%20")}'
                "&hl=en-US&gl=US&ceid=US:en"
            )
        else:
            data = feedparser.parse(
                "https://news.google.com/rss/search?q=when:24h&hl=en-US&gl=US&ceid=US:en"
            )

    return pd.DataFrame(data.entries, columns=["title", "link", "published"])
