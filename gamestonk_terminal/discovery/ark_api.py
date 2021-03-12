import argparse
from datetime import timedelta
import json
import requests
from colorama import Fore, Style
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
import yfinance as yf

from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_user_agent,
    patch_pandas_text_adjustment,
    parse_known_args_and_warn,
)
from gamestonk_terminal import feature_flags as gtff


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


def add_order_total(df_orders: DataFrame) -> DataFrame:
    start_date = df_orders["date"].iloc[-1] - timedelta(days=1)

    tickers = " ".join(df_orders["ticker"].unique())

    print("")

    prices = yf.download(tickers, start=start_date, progress=False)

    for i, candle in enumerate(["Volume", "Open", "Close", "High", "Low", "Total"]):
        df_orders.insert(i + 3, candle.lower(), 0)

    for i, _ in df_orders.iterrows():
        if np.isnan(
            prices["Open"][df_orders.loc[i, "ticker"]][
                df_orders.loc[i, "date"].strftime("%Y-%m-%d")
            ]
        ):
            for candle in ["Volume", "Open", "Close", "High", "Low", "Total"]:
                df_orders.loc[i, candle.lower()] = 0
            continue

        for candle in ["Volume", "Open", "Close", "High", "Low"]:
            df_orders.loc[i, candle.lower()] = prices[candle][
                df_orders.loc[i, "ticker"]
            ][df_orders.loc[i, "date"].strftime("%Y-%m-%d")]

        df_orders.loc[i, "total"] = (
            df_orders.loc[i, "close"] * df_orders.loc[i, "shares"]
        )

    return df_orders


def ark_orders(l_args):
    parser = argparse.ArgumentParser(
        add_help=False,
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
    if not ns_parser:
        return

    df_orders = get_ark_orders()

    pd.set_option("mode.chained_assignment", None)
    df_orders = add_order_total(df_orders.head(ns_parser.n_num))

    if gtff.USE_COLOR:
        df_orders["direction"] = df_orders["direction"].apply(direction_color_red_green)

        patch_pandas_text_adjustment()

    df_orders["link"] = "https://finviz.com/quote.ashx?t=" + df_orders["ticker"]

    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.float_format", "{:,.2f}".format)
    print("")
    print("Orders by ARK Investment Management LLC")
    print("")
    print(df_orders.to_string(index=False))
    print("")
