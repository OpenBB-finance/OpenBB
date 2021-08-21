""" MarketBeat Model """
__docformat__ = "numpy"

from typing import List
import requests
from bs4 import BeautifulSoup

from gamestonk_terminal.helper_funcs import get_user_agent


def get_ratings_html(url_ratings: str) -> str:
    """Wraps HTTP requests.get for testibility

    Parameters
    ----------
    url_ratings : str
        Ratings URL

    Returns
    -------
    str
        HTML page of ratings
    """
    ratings_html = requests.get(
        url_ratings, headers={"User-Agent": get_user_agent()}
    ).text

    return ratings_html


def get_ratings() -> List[dict]:
    """Returns a list of ratings

    Parameters
    ----------
    None

    Returns
    -------
    list
        Ratings list
    """

    ratings = []
    url_ratings = "https://www.marketbeat.com/ratings/"

    text_soup_ratings = BeautifulSoup(
        get_ratings_html(url_ratings),
        "lxml",
    )

    for stock_rows in text_soup_ratings.findAll("tr"):
        tds = stock_rows.findAll("td")
        if len(tds) == 8:
            rating = {}
            # company
            td = tds[0]
            company = td.find("div", {"class": "title-area"}).text
            ticker = td.find("div", {"class": "ticker-area"}).text
            rating["company"] = company
            rating["ticker"] = ticker
            # action
            td = tds[1]
            action = td.text
            rating["action"] = action
            # brokerage
            td = tds[2]
            brokerage = td.find("a").text
            rating["brokerage"] = brokerage
            # current price
            td = tds[3]
            if td.find("span"):
                td.span.extract()
            analyst = td.text
            rating["analyst"] = analyst
            # target price
            td = tds[4]
            current_price = td.text
            rating["current_price"] = current_price
            # new rating
            td = tds[5]
            target_price = td.text
            rating["target_price"] = target_price
            # impact on price
            td = tds[6]
            if td.find("a"):
                rate = td.find("a").text
            else:
                rate = td.text
            rating["rate"] = rate
            ratings.append(rating)

    return ratings
