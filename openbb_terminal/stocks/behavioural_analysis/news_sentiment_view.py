"""Onclusive Data Model"""
__docformat__ = "numpy"


import os
from typing import Optional

from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.behavioural_analysis import news_sentiment_model


def display_articles_data(
    ticker: str = "",
    start_date: str = "",
    end_date: str = "",
    date: str = "",
    limit: int = 100,
    offset: int = 0,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display Onclusive Data. [Source: Invisage Plotform]

    Parameters
    ----------
    ticker : str
        Stock ticker
    start_date : str
        Records are coming from this day (Start date in YYYY-MM-DD format)
    end_date : str
        Records will get upto this day (End date in YYYY-MM-DD format)
    date : str
        Show that the records on this day (date in YYYY-MM-DD format)
    limit: int
        The number of records to get
    offset : int
        The number of records to offset
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = news_sentiment_model.get_data(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        date=date,
        limit=limit,
        offset=offset,
    )
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")
    if df.empty:
        console.print("No data found.")
    else:
        for row in df.itertuples():
            console.print()
            console.print("Date : ", row.published_on)
            console.print("Ticker : ", row.ticker)
            console.print("Article Name : ", row.article_title)
            console.print("Article URL : ", row.article_url)
            console.print("Article Sentiment : ", row.raw_sentiment)
            console.print("Article Adjusted Sentiment : ", row.adjusted_sentiment)
            console.print()
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "News Sentiment",
        df,
        sheet_name,
    )
