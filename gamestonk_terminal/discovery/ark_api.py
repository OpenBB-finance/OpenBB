import argparse
import json
from pandas.core.base import DataError
from pandas.core.frame import DataFrame
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


def direction_color_red_green(val: str) -> str:
    if val == "Buy":
        ret = Fore.GREEN + val + Style.RESET_ALL
    elif val == "Sell":
        ret = Fore.RED + val + Style.RESET_ALL
    else:
        ret = val

    return ret


def get_ark_orders() -> DataFrame:
    url_orders = "https://cathiesark.com/ark-funds-combined/trades"

    raw_page = requests.get(url_orders, headers={"User-Agent": get_user_agent()}).text

    parsed_script = BeautifulSoup(raw_page, "lxml").find(
        "script", {"id": "__NEXT_DATA__"}
    )

    parsed_json = json.loads(parsed_script.string)

    df_orders = pd.json_normalize(parsed_json["props"]["pageProps"]["arkTrades"])
    df_orders.drop(
        [
            "everything",
            "everything.profile.customThumbnail",
            "hidden",
            "images.thumbnail",
        ],
        axis=1,
        inplace=True,
    )

    df_orders["date"] = pd.to_datetime(df_orders["date"], format="%Y-%m-%dZ").dt.date

    return df_orders


def ark_orders(l_args):
    parser = argparse.ArgumentParser(
        prog="ARK Orders",
        description="""
            Orders by ARK Investment Management LLC - https://ark-funds.com/. [Source: https://cathiesark.com]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=20,
        help="Last N orders.",
    )

    ns_parser = parse_known_args_and_warn(parser, l_args)

    df_orders = get_ark_orders()

    if USE_COLOR:
        df_orders["direction"] = df_orders["direction"].apply(direction_color_red_green)

        patch_pandas_text_adjustment()

    df_orders["link"] = "https://finviz.com/quote.ashx?t=" + df_orders["ticker"]

    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_rows", None)
    print("")
    print("Orders by ARK Investment Management LLC")
    print("")
    print(df_orders.head(ns_parser.n_num))
    print("")
