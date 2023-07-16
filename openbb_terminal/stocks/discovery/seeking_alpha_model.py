""" Seeking Alpha Model """
__docformat__ = "numpy"

import logging
from datetime import date, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_earnings_html(url_next_earnings: str) -> str:
    """Wraps HTTP request for testibility

    Parameters
    ----------
    url_next_earnings : str
        Next earnings URL

    Returns
    -------
    str
        HTML page of next earnings
    """
    earnings_html = request(
        url_next_earnings, headers={"User-Agent": get_user_agent()}
    ).text

    return earnings_html


def get_filters(date_str: str) -> str:
    text = f"?filter[selected_date]={date_str}&filter[with_rating]=false&filter[currency]=USD"
    return text


@log_start_end(log=logger)
def get_next_earnings(limit: int = 5, start_date: date = date.today()) -> DataFrame:
    """Returns a DataFrame with upcoming earnings

    Parameters
    ----------
    limit : int
        Number of days to look ahead
    start_date: date
        Date to start from. Defaults to today

    Returns
    -------
    DataFrame
        Upcoming earnings DataFrame
    """
    base_url = "https://seekingalpha.com/api/v3/earnings_calendar/tickers"
    df_earnings = pd.DataFrame()

    for _ in range(0, limit):
        start_date = pd.to_datetime(start_date)
        date_str = str(start_date.strftime("%Y-%m-%d"))
        response = request(base_url + get_filters(date_str), timeout=10)
        json = response.json()
        try:
            data = json["data"]
            cleaned_data = [x["attributes"] for x in data]
            temp_df = pd.DataFrame.from_records(cleaned_data)
            temp_df = temp_df.drop(columns=["sector_id"])
            temp_df["Date"] = start_date  # pylint: disable=E1137
            df_earnings = pd.concat(
                [df_earnings, temp_df], join="outer", ignore_index=True
            )
            start_date = start_date + timedelta(days=1)
        except KeyError:
            pass

    df_earnings = df_earnings.rename(
        columns={
            "slug": "Ticker",
            "name": "Name",
            "release_time": "Release Time",
            "exchange": "Exchange",
        }
    )

    if df_earnings.empty:
        console.print("No earnings found. Try adjusting the date.\n")
        return pd.DataFrame()

    df_earnings = df_earnings[
        df_earnings["Date"] <= pd.to_datetime(start_date + timedelta(days=limit))
    ]

    return df_earnings


@log_start_end(log=logger)
def get_articles_html(url_articles: str) -> str:
    """Wraps HTTP request for testability

    Parameters
    ----------
    url_articles : str
        Articles URL

    Returns
    -------
    str
        HTML page of articles
    """
    articles_html = request(url_articles, headers={"User-Agent": get_user_agent()}).text

    return articles_html


@log_start_end(log=logger)
def get_trending_list(limit: int = 5) -> list:
    """Returns a list of trending articles

    Parameters
    ----------
    limit: int
        Number of articles

    Returns
    -------
    list
        Trending articles list
    """

    articles = []
    url_articles = "https://seekingalpha.com/news/trending_news"
    response = request(url_articles, headers={"User-Agent": get_user_agent()})

    # Check that the API response was successful
    if response.status_code != 200:
        console.print("Invalid response\n")
    else:
        for item in response.json():
            article_url = item["uri"]
            if not article_url.startswith("/news/"):
                continue
            article_id = article_url.split("/")[2].split("-")[0]
            articles.append(
                {
                    "title": item["title"],
                    "publishedAt": item["publish_on"][: item["publish_on"].rfind(".")],
                    "url": "https://seekingalpha.com" + article_url,
                    "id": article_id,
                }
            )

    return articles[:limit]


@log_start_end(log=logger)
def get_article_data(article_id: int) -> dict:
    """Returns an article

    Parameters
    ----------
    article_id : int
        Article ID

    Returns
    -------
    dict
        Article data
    """

    article_url = f"https://seekingalpha.com/api/v3/news/{article_id}"
    response = request(article_url, headers={"User-Agent": get_user_agent()})
    jdata = response.json()
    content = jdata["data"]["attributes"]["content"].replace("</li>", "</li>\n")
    content = BeautifulSoup(content, features="html.parser").get_text()

    article = {
        "title": jdata["data"]["attributes"]["title"],
        "publishedAt": jdata["data"]["attributes"]["lastModified"],
        "url": "https://seekingalpha.com" + jdata["data"]["links"]["self"],
        "content": content,
    }

    return article


@log_start_end(log=logger)
def get_news_html(news_type: str = "Top-News") -> dict:
    """Gets news. [Source: SeekingAlpha]

    Parameters
    ----------
    news_type : str
        From: Top-News, On-The-Move, Market-Pulse, Notable-Calls, Buybacks, Commodities, Crypto, Issuance, Global,
        Guidance, IPOs, SPACs, Politics, M-A, Consumer, Energy, Financials, Healthcare, MLPs, REITs, Technology

    Returns
    -------
    dict
        HTML page of articles
    """
    sa_url = (
        f"http://seekingalpha.com/api/v3/news?filter%5Bcategory%5D=market-news%3A%3A{news_type}"
        "&filter%5Bsince%5D=0&filter%5Buntil%5D=0&include=author%2CprimaryTickers%2CsecondaryTickers"
        "&isMounting=true&page%5Bsize%5D=25&page%5Bnumber%5D=1"
    )

    articles_html = request(sa_url, headers={"User-Agent": get_user_agent()}).json()

    return articles_html
