""" Seeking Alpha Model """
__docformat__ = "numpy"

import logging
from typing import Dict, List

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


@log_start_end(log=logger)
def get_next_earnings(limit: int = 10) -> DataFrame:
    """Returns a DataFrame with upcoming earnings

    Parameters
    ----------
    limit : int
        Number of pages

    Returns
    -------
    DataFrame
        Upcoming earnings DataFrame
    """
    earnings = []
    url_next_earnings = "https://seekingalpha.com/earnings/earnings-calendar"

    for idx in range(0, limit):
        text_soup_earnings = BeautifulSoup(
            get_earnings_html(url_next_earnings),
            "lxml",
        )

        for stock_rows in text_soup_earnings.findAll("tr", {"data-exchange": "NASDAQ"}):
            stocks = [a_stock.text for a_stock in stock_rows.contents[:3]]
            earnings.append(stocks)

        url_next_earnings = (
            f"https://seekingalpha.com/earnings/earnings-calendar/{idx+1}"
        )

    df_earnings = pd.DataFrame(earnings, columns=["Ticker", "Name", "Date"])
    df_earnings["Date"] = pd.to_datetime(df_earnings["Date"])
    df_earnings = df_earnings.set_index("Date")

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


@log_start_end(log=logger)
def get_news(news_type: str = "Top-News", limit: int = 5) -> List:
    """Gets news. [Source: SeekingAlpha]

    Parameters
    ----------
    news_type : str
        From: Top-News, On-The-Move, Market-Pulse, Notable-Calls, Buybacks, Commodities, Crypto, Issuance, Global,
        Guidance, IPOs, SPACs, Politics, M-A, Consumer, Energy, Financials, Healthcare, MLPs, REITs, Technology
    limit : int
        Number of news to display

    Returns
    -------
    List[dict]
        List of dict news
    """
    news_articles: Dict = get_news_html(news_type)
    news_to_display = list()

    if "data" in news_articles:
        for idx, news in enumerate(news_articles["data"]):
            if idx > limit:
                break

            news_to_display.append(
                {
                    "publishOn": news["attributes"]["publishOn"].replace("T", " ")[:-6],
                    "id": news["id"],
                    "title": news["attributes"]["title"],
                    "url": news["links"]["canonical"],
                }
            )

    return news_to_display
