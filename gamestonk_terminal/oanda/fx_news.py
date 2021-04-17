import requests
import pandas as pd
from bs4 import BeautifulSoup
from gamestonk_terminal.helper_funcs import get_user_agent


def daily_fx_news():
    daily_fx_url = "https://www.dailyfx.com/market-news/articles"
    daily_fx_soup = BeautifulSoup(
        requests.get(daily_fx_url, headers={"User-Agent": get_user_agent()}).text,
          "lxml",
      )
    daily_fx_news_header_list = list()
    for daily_fx_news_header in daily_fx_soup.findAll("a", {"class": "dfx-articleListItem jsdfx-articleListItem d-flex mb-3"}):
        daily_fx_news_header_list.append(
        daily_fx_news_header.text.strip("\n").split("\n"))
    print(daily_fx_news_header)


