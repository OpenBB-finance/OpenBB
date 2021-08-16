""" Business Insider View """
__docformat__ = "numpy"

import argparse
from typing import List
from pandas.core.frame import DataFrame
import requests
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from bs4 import BeautifulSoup
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_next_stock_market_days,
    get_user_agent,
    parse_known_args_and_warn,
)
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def insider_activity(
    other_args: List[str], stock: DataFrame, ticker: str, start: str, interval: str
):
    """Display insider activity

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    stock : DataFrame
        Due diligence stock dataframe
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="ins",
        description="""Prints insider activity over time [Source: Business Insider]""",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of latest insider activity.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        url_market_business_insider = (
            f"https://markets.businessinsider.com/stocks/{ticker.lower()}-stock"
        )
        text_soup_market_business_insider = BeautifulSoup(
            requests.get(
                url_market_business_insider, headers={"User-Agent": get_user_agent()}
            ).text,
            "lxml",
        )

        d_insider = dict()
        l_insider_vals = list()
        for idx, insider_val in enumerate(
            text_soup_market_business_insider.findAll(
                "td", {"class": "table__td text-center"}
            )
        ):
            # print(insider_val.text.strip())

            l_insider_vals.append(insider_val.text.strip())

            # Add value to dictionary
            if (idx + 1) % 6 == 0:
                # Check if we are still parsing insider trading activity
                if "/" not in l_insider_vals[0]:
                    break
                d_insider[(idx + 1) // 6] = l_insider_vals
                l_insider_vals = list()

        df_insider = pd.DataFrame.from_dict(
            d_insider,
            orient="index",
            columns=["Date", "Shares Traded", "Shares Held", "Price", "Type", "Option"],
        )

        df_insider["Date"] = pd.to_datetime(df_insider["Date"])
        df_insider = df_insider.set_index("Date")
        df_insider = df_insider.sort_index(ascending=True)

        if start:
            df_insider = df_insider[start:]  # type: ignore

        _, ax = plt.subplots()

        if interval == "1440min":
            plt.plot(stock.index, stock["Adj Close"].values, lw=3)
        else:  # Intraday
            plt.plot(stock.index, stock["Close"].values, lw=3)

        plt.title(f"{ticker.upper()} (Time Series) and Price Target")

        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")

        df_insider["Trade"] = df_insider.apply(
            lambda row: (1, -1)[row.Type == "Sell"]
            * float(row["Shares Traded"].replace(",", "")),
            axis=1,
        )
        plt.xlim(df_insider.index[0], stock.index[-1])
        min_price, max_price = ax.get_ylim()

        price_range = max_price - min_price
        shares_range = (
            df_insider[df_insider["Type"] == "Buy"]
            .groupby(by=["Date"])
            .sum()["Trade"]
            .max()
            - df_insider[df_insider["Type"] == "Sell"]
            .groupby(by=["Date"])
            .sum()["Trade"]
            .min()
        )
        n_proportion = price_range / shares_range

        for ind in (
            df_insider[df_insider["Type"] == "Sell"].groupby(by=["Date"]).sum().index
        ):
            if ind in stock.index:
                ind_dt = ind
            else:
                ind_dt = get_next_stock_market_days(ind, 1)[0]

            n_stock_price = 0
            if interval == "1440min":
                n_stock_price = stock["Adj Close"][ind_dt]
            else:
                n_stock_price = stock["Close"][ind_dt]

            plt.vlines(
                x=ind_dt,
                ymin=n_stock_price
                + n_proportion
                * float(
                    df_insider[df_insider["Type"] == "Sell"]
                    .groupby(by=["Date"])
                    .sum()["Trade"][ind]
                ),
                ymax=n_stock_price,
                colors="red",
                ls="-",
                lw=5,
            )

        for ind in (
            df_insider[df_insider["Type"] == "Buy"].groupby(by=["Date"]).sum().index
        ):
            if ind in stock.index:
                ind_dt = ind
            else:
                ind_dt = get_next_stock_market_days(ind, 1)[0]

            n_stock_price = 0
            if interval == "1440min":
                n_stock_price = stock["Adj Close"][ind_dt]
            else:
                n_stock_price = stock["Close"][ind_dt]

            plt.vlines(
                x=ind_dt,
                ymin=n_stock_price,
                ymax=n_stock_price
                + n_proportion
                * float(
                    df_insider[df_insider["Type"] == "Buy"]
                    .groupby(by=["Date"])
                    .sum()["Trade"][ind]
                ),
                colors="green",
                ls="-",
                lw=5,
            )

        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()

        l_names = list()
        for s_name in text_soup_market_business_insider.findAll(
            "a", {"onclick": "silentTrackPI()"}
        ):
            l_names.append(s_name.text.strip())
        df_insider["Insider"] = l_names

        print(
            df_insider.sort_index(ascending=False).head(n=ns_parser.n_num).to_string()
        )
        print("")

    except Exception as e:
        print(e)
        print("")
        return
