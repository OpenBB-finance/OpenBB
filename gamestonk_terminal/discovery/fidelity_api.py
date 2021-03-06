import argparse
import re
import requests
from colorama import Fore, Style
from bs4 import BeautifulSoup
import pandas as pd

from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_user_agent,
    patch_pandas_text_adjustment,
    parse_known_args_and_warn,
)
from gamestonk_terminal.config_terminal import USE_COLOR


def buy_sell_ratio_color_red_green(val: str) -> str:
    buy_sell_match = re.match(r"(\d+)% Buys, (\d+)% Sells", val, re.M | re.I)

    if not buy_sell_match:
        return val

    buys = int(buy_sell_match.group(1))
    sells = int(buy_sell_match.group(2))

    if buys >= sells:
        return "{}{}%{} Buys, {}% Sells".format(
            Fore.GREEN, buys, Style.RESET_ALL, sells
        )

    return f"{buys}% Buys, {Fore.RED}{sells}%{Style.RESET_ALL} Sells"


def price_change_color_red_green(val: str) -> str:
    val_float = float(val.split(" ")[0])
    if val_float > 0:
        color = Fore.GREEN
    else:
        color = Fore.RED
    return color + val + Style.RESET_ALL


def orders(l_args):
    parser = argparse.ArgumentParser(
        prog="orders",
        description="""
            Orders by Fidelity customers. Information shown in the table below
            is based on the volume of orders entered on the "as of" date shown. Securities
            identified are not recommended or endorsed by Fidelity and are displayed for
            informational purposes only. [Source: Fidelity]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of top ordered stocks to be printed.",
    )

    ns_parser = parse_known_args_and_warn(parser, l_args)

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
                l_orders_vals.append(an_order.contents[1])
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

    print(
        text_soup_url_orders.findAll("span", {"class": "source"})[0].text.capitalize()
        + ":"
    )

    pd.set_option("display.max_colwidth", -1)

    if USE_COLOR:
        df_orders["Buy / Sell Ratio"] = df_orders["Buy / Sell Ratio"].apply(
            buy_sell_ratio_color_red_green
        )
        df_orders["Price Change"] = df_orders["Price Change"].apply(
            price_change_color_red_green
        )

        patch_pandas_text_adjustment()

    print(df_orders.head(n=ns_parser.n_num).iloc[:, :-1].to_string(index=False))
    print("")
