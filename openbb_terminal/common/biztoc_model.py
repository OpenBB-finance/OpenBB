""" BizToc Model """
__docformat__ = "numpy"

import os

import certifi
import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

# Necessary for installer so that it can locate the correct certificates for
# API calls and https
# https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()


def get_sources() -> pd.DataFrame:
    """Get list of source ids to query for individual news articles via get_news. [Source: BizToc]

    Parameters
    ----------

    Returns
    -------
    sources: pd.DataFrame
        list of sources
    """

    req_headers = {
        "X-RapidAPI-Key": get_current_user().credentials.API_BIZTOC_TOKEN,
        "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
    }

    req = request(
        "https://biztoc.p.rapidapi.com/sources",
        headers=req_headers,
    )

    if hasattr(req, "status_code") and req.status_code == 200:
        df = pd.DataFrame(req.json(), columns=["id", "title", "web"])
    elif hasattr(req, "status_code") and req.status_code != 200:
        # If data request failed
        console.print("[red]Status code not 200. Unable to retrieve data\n[/red]")
        df = pd.DataFrame()

    df = df.sort_values(by=["title"], ascending=True)
    df = df[["id", "title", "web"]]
    df.columns = ["id", "Title", "URL"]
    return df


def get_tags() -> pd.DataFrame:
    """Get list of trending tags to query for individual news articles via get_news. [Source: BizToc]

    Parameters
    ----------

    Returns
    -------
    tags: pd.DataFrame
        list of tags
    """

    req_headers = {
        "X-RapidAPI-Key": get_current_user().credentials.API_BIZTOC_TOKEN,
        "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
    }

    req = request(
        "https://biztoc.p.rapidapi.com/tags/main",
        headers=req_headers,
    )

    if hasattr(req, "status_code") and req.status_code == 200:
        df = pd.DataFrame(req.json(), columns=["tag"])
    elif hasattr(req, "status_code") and req.status_code != 200:
        # If data request failed
        df = pd.DataFrame()

    return df


@check_api_key(["API_BIZTOC_TOKEN"])
def get_news(
    term: str = "",
    tag: str = "",
    source: str = "",
    sort: str = "created",
    limit: int = 100,
    display_message: bool = True,
) -> pd.DataFrame:
    """Get news for a given term and source. [Source: BizToc]

    Parameters
    ----------
    term : str
        term to search on the news articles
    tag : str
        display news articles for an individual tag
    source: str
        source to exclusively show news from
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
    """

    have_data = False

    if display_message:
        console.print("[yellow]Fetching news. Please be patient\n[/yellow]")

    req_headers = {
        "X-RapidAPI-Key": get_current_user().credentials.API_BIZTOC_TOKEN,
        "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
    }

    while not have_data:
        if term:
            req = request(
                # term=quote(term)
                "https://biztoc.p.rapidapi.com/search",
                params={"q": term},
                headers=req_headers,
            )
        elif tag:
            req = request(
                f"https://biztoc.p.rapidapi.com/tag/{tag}",
                headers=req_headers,
            )
        elif source:
            req = request(
                f"https://biztoc.p.rapidapi.com/news/source/{source}",
                headers=req_headers,
            )
        else:
            req = request(
                "https://biztoc.p.rapidapi.com/news/latest/main", headers=req_headers
            )

        if hasattr(req, "status_code") and req.status_code == 200:
            have_data = True
        elif (
            hasattr(req, "status_code") and req.status_code != 200
        ):  # If data request failed
            console.print("[red]Status code not 200. Unable to retrieve data\n[/red]")
            break

        df = pd.DataFrame(req.json(), columns=["title", "body", "url", "created"])

    df["created"] = pd.to_datetime(df["created"])

    df = df.sort_values(by=[sort], ascending=False)
    df = df[["created", "title", "body", "url"]]
    df.columns = ["Date", "Title", "Body", "URL"]
    df = df[:limit]
    return df


# Define for auto-completion
try:
    BIZTOC_TAGS = get_tags().tag.tolist()


except Exception:
    # If key not defined or there is an issue
    BIZTOC_TAGS = []
