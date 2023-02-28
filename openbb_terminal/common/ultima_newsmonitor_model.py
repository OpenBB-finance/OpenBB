""" Feedparser Model """
__docformat__ = "numpy"

import os
from typing import List
from urllib.parse import quote

import certifi
import requests
import pandas as pd

from openbb_terminal.rich_config import console


def get_news(
    term: str = "", sources: str = "", sort: str = "articlePublishedDate"
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
    console.print("[yellow]Fetching data. Please be patient\n[/yellow]")
    limit = 0

    while not have_data:
        if term:
            term = quote(term)
            data = requests.get(f'https://api.ultimainsights.ai/v1/getNewsArticles/{term}')
        else:
            data = requests.get('https://api.ultimainsights.ai/v1/getNewsArticles/FCX')

        if (
            hasattr(data, "status") and data.status_code == 200
        ):  # Checking if data has status attribute and if data request succeeded
            if data.content:
                have_data = True
            elif limit == 60:  # Breaking if 60 successful requests return no data
                console.print("[red]Timeout occurred. Please try again\n[/red]")
                break
            limit = limit + 1

        elif hasattr(data, "status") and data.status_code != 200:  # If data request failed
            console.print("[red]Status code not 200. Unable to retrieve data\n[/red]")
            break
        else:
            # console.print("[red]Could not retrieve data\n[/red]")
            break

    # Filter based on data sources
    if sources:
        newdata: List = []
        for entry in list(data.json()):
            # check if sources specified
            if "," in sources:
                if entry["articlePublisher"].lower().find(sources.lower()) != -1:
                    newdata.append(entry)
            else:
                for s in sources.split(","):
                    if entry["articlePublisher"].lower().find(s.lower()) != -1:
                        newdata.append(entry)

        if newdata:
            df = pd.DataFrame(newdata, columns=["articleHeadline", "articleURL", "articlePublishedDate",
                                                "riskCategory", "riskExtDescription", "relevancyScore"])
        else:
            return pd.DataFrame()
    else:
        df = pd.DataFrame(data.json(), columns=["articleHeadline", "articleURL", "articlePublishedDate",
                                                "riskCategory", "riskExtDescription", "relevancyScore"])
    df = df[df['relevancyScore'] < 5]
    df['riskExtDescription'] = df['riskExtDescription'].str.replace('\n', '')
    df["articlePublishedDate"] = pd.to_datetime(df["articlePublishedDate"])
    df = df.sort_values(by=[sort], ascending=False)

    return df
