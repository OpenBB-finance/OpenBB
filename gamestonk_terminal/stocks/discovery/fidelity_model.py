""" Fidelity Model """
__docformat__ = "numpy"

from typing import Tuple
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame

from gamestonk_terminal.helper_funcs import get_user_agent


def get_orders() -> Tuple[str, DataFrame]:
    """Returns Fidelity orders in a Dataframe

    Returns
    -------
    Tuple[str, DataFrame]
        First value in the tuple is a Fidelity orders header
        Fidelity orders Dataframe with the following columns:
        Symbol, Buy / Sell Ratio, Price Change, Company, # Buy Orders, # Sell Orders
    """

    url_orders = (
        "https://eresearch.fidelity.com/eresearch/gotoBL/fidelityTopOrders.jhtml"
    )

    text_soup_url_orders = BeautifulSoup(
        requests.get(url_orders, headers={"User-Agent": get_user_agent()}).text, "lxml"
    )

    l_orders = list()
    l_orders_vals = list()
    idx = 0
    order_list = text_soup_url_orders.findAll(
        "td",
        {"class": ["second", "third", "fourth", "fifth", "sixth", "seventh", "eight"]},
    )
    for an_order in order_list:
        if ((idx + 1) % 3 == 0) or ((idx + 1) % 4 == 0) or ((idx + 1) % 6 == 0):
            if not an_order:
                l_orders_vals.append("")
            else:
                try:
                    l_orders_vals.append(an_order.contents[1])
                except IndexError:
                    l_orders_vals.append("0")
        elif (idx + 1) % 5 == 0:
            s_orders = str(an_order)
            l_orders_vals.append(
                s_orders[
                    s_orders.find('title="') + len('title="') : s_orders.find('"/>')
                ]
            )
        else:
            l_orders_vals.append(an_order.text.strip())

        idx += 1

        # Add value to dictionary
        if (idx + 1) % 8 == 0:
            l_orders.append(l_orders_vals)
            l_orders_vals = list()
            idx = 0

    df_orders = pd.DataFrame(
        l_orders,
        columns=[
            "Symbol",
            "Company",
            "Price Change",
            "# Buy Orders",
            "Buy / Sell Ratio",
            "# Sell Orders",
            "Latest News",
        ],
    )

    df_orders = df_orders[
        [
            "Symbol",
            "Buy / Sell Ratio",
            "Price Change",
            "Company",
            "# Buy Orders",
            "# Sell Orders",
            "Latest News",
        ]
    ]

    order_header = text_soup_url_orders.findAll("span", {"class": "source"})[
        0
    ].text.capitalize()

    return order_header, df_orders
