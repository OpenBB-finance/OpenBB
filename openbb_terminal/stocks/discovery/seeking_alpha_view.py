""" Seeking Alpha View """
__docformat__ = "numpy"

import logging
import os
from datetime import date
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.discovery import seeking_alpha_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def upcoming_earning_release_dates(
    limit: int = 5,
    start_date: date = date.today(),
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Displays upcoming earnings release dates

    Parameters
    ----------
    num_pages: int
        Number of pages to scrape, each page is one day
    limit: int
        Number of upcoming earnings release dates
    start_date: Optional[date]
        The day to start looking at earnings releases from
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_earnings = seeking_alpha_model.get_next_earnings(limit, start_date)

    if df_earnings.empty:
        console.print("No upcoming earnings release dates found")
        return

    print_rich_table(
        df_earnings,
        show_index=False,
        headers=df_earnings.columns,
        title="Upcoming Earnings Releases",
        export=bool(export),
    )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "upcoming",
            df_earnings,
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

        df_articles = pd.DataFrame(articles)

        df_articles["publishedAt"] = pd.to_datetime(df_articles["publishedAt"])

        df_news = pd.DataFrame(
            df_articles, columns=["publishedAt", "id", "title", "url"]
        )

        # We look for a date name in the column to assume its a date on frontend side for filtering etc
        df_news.rename(columns={"publishedAt": "publishedAtDate"}, inplace=True)

        df_news = df_news.drop("id", axis=1)
        print_rich_table(
            df_news,
            show_index=False,
            export=bool(export),
            limit=limit,
        )

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
