""" Seeking Alpha Model """
__docformat__ = "numpy"

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

    earnings = list()
    url_next_earnings = "https://seekingalpha.com/earnings/earnings-calendar"

    for idx in range(0, pages):
        text_soup_earnings = BeautifulSoup(
            get_earnings_html(url_next_earnings),
            "lxml",
        )

        for stock_rows in text_soup_earnings.findAll("tr", {"data-exchange": "NASDAQ"}):
            stocks = list()
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


def get_article_list(pages: int) -> list:
    """Returns a list of recent articles

    Parameters
    ----------
    pages : int
        Number of pages

    Returns
    -------
    list
        Latest articles list
    """

    articles = list()
    url_articles = "https://seekingalpha.com/market-news"
    for idx in range(0, pages):
        text_soup_articles = BeautifulSoup(
            get_articles_html(url_articles),
            "lxml",
        )

        for item_row in text_soup_articles.findAll("li", {"class": "item"}):
            item = item_row.find("a", {"class": "add-source-assigned"})
            if item is None:
                continue
            article_url = item['href']
            if not article_url.startswith('/news/'):
                continue
            article_id = article_url.split('/')[2].split('-')[0]
            articles.append({
                'title': item.text,
                'date': item_row['data-last-date'],
                'url': "https://seekingalpha.com"+article_url,
                'id': article_id
            })

        url_articles = (
            f"https://seekingalpha.com/market-news/{idx+1}"
        )

    return articles


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
    content = jdata['data']['attributes']['content'].replace('</li>', '</li>\n')
    content = BeautifulSoup(content, features="html.parser").get_text()

    article = {
        'title': jdata['data']['attributes']['title'],
        'date': jdata['data']['attributes']['lastModified'],
        'content': content
    }

    return article
