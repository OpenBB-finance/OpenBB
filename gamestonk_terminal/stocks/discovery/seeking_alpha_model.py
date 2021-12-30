""" Seeking Alpha Model """
__docformat__ = "numpy"

from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame

from gamestonk_terminal.helper_funcs import get_user_agent


def get_earnings_html(url_next_earnings: str) -> str:
    """Wraps HTTP requests.get for testibility

    Parameters
    ----------
    url_next_earnings : str
        Next earnings URL

    Returns
    -------
    str
        HTML page of next earnings
    """
    earnings_html = requests.get(
        url_next_earnings, headers={"User-Agent": get_user_agent()}
    ).text

    return earnings_html


def get_next_earnings(pages: int) -> DataFrame:
    """Returns a DataFrame with upcoming earnings

    Parameters
    ----------
    pages : int
        Number of pages

    Returns
    -------
    DataFrame
        Upcoming earnings DataFrame
    """
    earnings = []
    url_next_earnings = "https://seekingalpha.com/earnings/earnings-calendar"

    for idx in range(0, pages):
        text_soup_earnings = BeautifulSoup(
            get_earnings_html(url_next_earnings),
            "lxml",
        )

        for stock_rows in text_soup_earnings.findAll("tr", {"data-exchange": "NASDAQ"}):
            stocks = []
            for a_stock in stock_rows.contents[:3]:
                stocks.append(a_stock.text)
            earnings.append(stocks)

        url_next_earnings = (
            f"https://seekingalpha.com/earnings/earnings-calendar/{idx+1}"
        )

    df_earnings = pd.DataFrame(earnings, columns=["Ticker", "Name", "Date"])
    df_earnings["Date"] = pd.to_datetime(df_earnings["Date"])
    df_earnings = df_earnings.set_index("Date")

    return df_earnings


def get_articles_html(url_articles: str) -> str:
    """Wraps HTTP requests.get for testibility

    Parameters
    ----------
    url_articles : str
        Articles URL

    Returns
    -------
    str
        HTML page of articles
    """
    articles_html = requests.get(
        url_articles, headers={"User-Agent": get_user_agent()}
    ).text

    return articles_html


def get_trending_list(num: int) -> list:
    """Returns a list of trending articles

    Parameters
    ----------
    pages : int
        Number of articles

    Returns
    -------
    list
        Trending articles list
    """

    articles = []
    url_articles = "https://seekingalpha.com/news/trending_news"
    response = requests.get(url_articles, headers={"User-Agent": get_user_agent()})

    # Check that the API response was successful
    if response.status_code != 200:
        print("Invalid response\n")
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

    return articles[:num]


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
    response = requests.get(article_url, headers={"User-Agent": get_user_agent()})
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

    articles_html = requests.get(
        sa_url, headers={"User-Agent": get_user_agent()}
    ).json()

    return articles_html


def get_news(news_type: str = "Top-News", num: int = 5) -> List:
    """Gets news. [Source: SeekingAlpha]

    Parameters
    ----------
    news_type : str
        From: Top-News, On-The-Move, Market-Pulse, Notable-Calls, Buybacks, Commodities, Crypto, Issuance, Global,
        Guidance, IPOs, SPACs, Politics, M-A, Consumer, Energy, Financials, Healthcare, MLPs, REITs, Technology
    num : int
        Number of news to display

    Returns
    -------
    List[dict]
        List of dict news
    """
    news_articles: Dict = get_news_html(news_type)
    news_to_display = list()

    if news_articles:
        for idx, news in enumerate(news_articles["data"]):
            if idx > num:
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
