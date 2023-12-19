"""Helper Function for the openbb sdk function openbb.news()"""

import pandas as pd

from openbb_terminal.common import biztoc_model, feedparser_model
from openbb_terminal.core.session.current_user import get_current_user


def news(term: str = "", sources: str = "", tag="", source="") -> pd.DataFrame:
    """Access news from either feedparser or biztoc for a given term or from specified sources

    Parameters
    ----------
    term : str, optional
        Term to sort for, by default ""
    sources : str, optional
        News sources to include, by default ""
    tag : str, optional
        Biztoc only selection for searching by a given tag, by default ""
    source : str, optional
        Data provider, can be either FeedParser or BizToc.  Will default to Biztoc if key is provided

    Returns
    -------
    pd.DataFrame
        DataFrame of news
    """
    if source:
        provider = source.lower()
    else:
        # Use biztoc if token is provided
        provider = "feedparser"
        biztoc_token = get_current_user().credentials.API_BIZTOC_TOKEN
        if biztoc_token != "REPLACE_ME":  # noqa: S105
            provider = "biztoc"

    if provider == "feedparser":
        return feedparser_model.get_news(
            term=term, sources=sources, display_message=False
        )
    if provider == "biztoc":
        return biztoc_model.get_news(
            term=term, tag=tag, source=source, display_message=False
        )
    return pd.DataFrame()
