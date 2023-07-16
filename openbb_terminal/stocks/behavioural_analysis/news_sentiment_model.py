"""Onclusive Data Model"""

import datetime

import pandas as pd
import requests

from openbb_terminal.rich_config import console


def get_data(
    ticker: str = "",
    start_date: str = "",
    end_date: str = "",
    date: str = "",
    limit: int = 100,
    offset: int = 0,
) -> pd.DataFrame:
    """Getting Onclusive Data. [Source: Invisage Platform]

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
    """

    headers = {"accept": "application/json"}

    df = pd.DataFrame(data=None)

    query_params = {
        "all_feilds": "False",
        "ordering": "-published_on,-share_of_article,-pagerank",
    }
    if ticker:
        query_params["ticker"] = ticker
    if start_date:
        query_params["published_on__gte"] = start_date
    if end_date:
        query_params["published_on__lte"] = end_date

    if start_date and end_date and not date and start_date > end_date:
        console.print("start_date must be less than end_date")
        return df

    if date:
        dtdate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        query_params["published_on"] = str(dtdate)
        if start_date:
            if str(dtdate) < start_date:
                console.print("date must be grater than or equal to start_date")
                return df
            del query_params["published_on__gte"]
        if end_date:
            del query_params["published_on__lte"]

    if limit:
        query_params["limit"] = limit  # type:ignore
    if offset:
        query_params["offset"] = offset  # type:ignore

    response = requests.get(
        "https://althub-backend.invisagealpha.com/api/OnclusiveSentiment/",
        headers=headers,
        params=query_params,
        timeout=5,
    ).json()
    df = pd.DataFrame(data=response["results"])
    if not df.empty:
        df["adjusted_sentiment"] = df["adjusted_sentiment"].astype(float)

    def condition(x):
        if x >= 250:
            return "Super Positive"
        if 0 < x < 250:
            return "Positive"
        if x == 0:
            return "Neutral"
        if -250 < x < 0:
            return "Negative"
        return "Super Negative"

    sentiment = {50: "Positive", -50: "Negative", 0: "Neutral", None: "Neutral"}

    if not df.empty:
        df["raw_sentiment"] = df["raw_sentiment"].map(sentiment)
        df["adjusted_sentiment"] = df["adjusted_sentiment"].apply(condition)
    return df
