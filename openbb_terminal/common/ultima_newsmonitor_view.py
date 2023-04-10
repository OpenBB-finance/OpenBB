""" News View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.common import feedparser_model, ultima_newsmonitor_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_news(
    term: str,
    sources: str = "",
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    sort: str = "articlePublishedDate",
):
    """Plots news for a given term and source. [Source: Ultima Insights]

    Parameters
    ----------
    term : str
        term to search on the news articles
    sources : str
        sources to exclusively show news from
    limit : int
        number of articles to display
    export : str
        Export dataframe data to csv,json,xlsx file
    sort: str
        the column to sort by
    """
    console.print()
    if term not in ultima_newsmonitor_model.supported_terms():
        console.print(f"[red]Unsupported ticker: {term}[/red]")
        return
    company_info = ultima_newsmonitor_model.get_company_info(term)
    company_name = company_info.get("companyShortName", term)
    # TODO: calling them all together does not work with feedparser
    bbg = feedparser_model.get_news(
        company_name, sources="bloomberg", sort="published", display_message=False
    )
    wsj = feedparser_model.get_news(
        company_name, sources="wsj", sort="published", display_message=False
    )
    reuters = feedparser_model.get_news(
        company_name, sources="reuters", sort="published", display_message=False
    )
    cnbc = feedparser_model.get_news(
        company_name, sources="cnbc", sort="published", display_message=False
    )
    breaking_news = pd.concat([bbg, wsj, reuters, cnbc])
    if len(breaking_news) > 0:
        breaking_news = breaking_news.sort_values(by="Date", ascending=False)
        breaking_news["DateNorm"] = (
            pd.to_datetime(breaking_news["Date"]).dt.tz_convert(None).dt.normalize()
        )
        today = pd.to_datetime("today").normalize()
        breaking_news = breaking_news[breaking_news["DateNorm"] == today]
        if len(breaking_news) > 0:
            console.print(
                "Uncategorized Breaking News (Bloomberg, Reuters, WSJ, CNBC):"
            )
            for _, row in breaking_news.head(limit).iterrows():
                console.print(f"> {row['Date']} - {row['Description']}")
                console.print(row["URL"] + "\n")
            console.print("------------------------")

    articles = ultima_newsmonitor_model.get_news(term, sort)
    articles = articles.head(limit).sort_values(by="relevancyScore", ascending=False)
    # console.print(f"News Powered by [purple]Ultima Insights[/purple].\nFor more info: https://www.ultimainsights.ai\n")
    for _, row in articles.iterrows():
        console.print(
            f"> {row['articlePublishedDate']} - {row['articleHeadline']}\n"
            f"[purple]Relevancy score: {round(row['relevancyScore'], 2) if row['relevancyScore'] < 5 else 5}"
            f"/5 Stars[/purple]\n[green]{row['riskCategory']}[/green] "
            f"(\x1B[3m{row['riskElaboratedDescription']}\x1B[0m)"
        )
        console.print(f"Read more: {row['articleURL']}\n")
    # console.print("[purple]To report any issues, please visit https://beta.ultimainsights.ai/my-account/support[/purple]\n")
    console.print()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"news_{'_'.join(term)}_{'_'.join(sources)}",
        articles,
        sheet_name,
    )


@log_start_end(log=logger)
def supported_terms() -> list:
    """Returns supported terms for news"""
    return ultima_newsmonitor_model.supported_terms()
