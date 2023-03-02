""" Seeking Alpha View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.discovery import seeking_alpha_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def upcoming_earning_release_dates(
    num_pages: int = 5,
    limit: int = 1,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Displays upcoming earnings release dates

    Parameters
    ----------
    num_pages: int
        Number of pages to scrap
    limit: int
        Number of upcoming earnings release dates
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    # TODO: Check why there are repeated companies
    # TODO: Create a similar command that returns not only upcoming, but antecipated earnings
    # i.e. companies where expectation on their returns are high

    df_earnings = seeking_alpha_model.get_next_earnings(num_pages)

    if df_earnings.empty:
        console.print("No upcoming earnings release dates found")

    pd.set_option("display.max_colwidth", None)
    if export:
        l_earnings = []
        l_earnings_dates = []

    for n_days, earning_date in enumerate(df_earnings.index.unique()):
        if n_days > (limit - 1):
            break

        # TODO: Potentially extract Market Cap for each Ticker, and sort
        # by Market Cap. Then cut the number of tickers shown to 10 with
        # bigger market cap. Didier attempted this with yfinance, but
        # the computational time involved wasn't worth pursuing that solution.

        df_earn = (
            df_earnings[earning_date == df_earnings.index][["Ticker", "Name"]]
            .dropna()
            .drop_duplicates()
        )

        if export:
            l_earnings_dates.append(earning_date.date())
            l_earnings.append(df_earn)

        df_earn.index = df_earn["Ticker"].values
        df_earn.drop(columns=["Ticker"], inplace=True)

        print_rich_table(
            df_earn,
            show_index=True,
            headers=[f"Earnings on {earning_date.date()}"],
            title="Upcoming Earnings Releases",
            export=bool(export),
        )

    if export:
        for item in l_earnings:
            item.reset_index(drop=True, inplace=True)
        df_data = pd.concat(l_earnings, axis=1, ignore_index=True)
        df_data.columns = l_earnings_dates

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "upcoming",
            df_data,
            sheet_name,
        )


@log_start_end(log=logger)
def news(
    article_id: int = -1,
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Prints the latest news article list. [Source: Seeking Alpha]

    Parameters
    ----------
    article_id: int
        Article ID. If -1, none is selected
    limit: int
        Number of articles to display. Only used if article_id is -1.
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    # User wants to see all latest news
    if article_id == -1:
        articles = seeking_alpha_model.get_trending_list(limit)

        if export:
            df_articles = pd.DataFrame(articles)

        for idx, article in enumerate(articles):
            console.print(
                article["publishedAt"].replace("T", " ").replace("Z", ""),
                "-",
                article["id"],
                "-",
                article["title"],
            )
            console.print(article["url"])
            console.print("\n")

            if idx >= limit - 1:
                break

    # User wants to access specific article
    else:
        article = seeking_alpha_model.get_article_data(article_id)

        if export:
            df_articles = pd.DataFrame(article)

        console.print(
            article["publishedAt"][: article["publishedAt"].rfind(":") - 3].replace(
                "T", " "
            ),
            " ",
            article["title"],
        )
        console.print(article["url"])
        console.print("\n")
        console.print(article["content"])

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "trending",
            df_articles,
            sheet_name,
        )


@log_start_end(log=logger)
def display_news(
    news_type: str = "Top-News",
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display news. [Source: SeekingAlpha]

    Parameters
    ----------
    news_type : str
        From: Top-News, On-The-Move, Market-Pulse, Notable-Calls, Buybacks, Commodities, Crypto, Issuance, Global,
        Guidance, IPOs, SPACs, Politics, M-A, Consumer, Energy, Financials, Healthcare, MLPs, REITs, Technology
    limit : int
        Number of news to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    news_to_display: List = seeking_alpha_model.get_news(news_type, limit)

    if not news:
        console.print("No news found.", "\n")

    else:
        for news_element in news_to_display:
            console.print(
                news_element["publishOn"]
                + " - "
                + news_element["id"]
                + " - "
                + news_element["title"]
            )
            console.print(news_element["url"])
            console.print("\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cnews : " + news_type,
            pd.DataFrame(news_to_display),
            sheet_name,
        )
