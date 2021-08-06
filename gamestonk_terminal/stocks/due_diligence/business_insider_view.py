""" Business Insider View """
__docformat__ = "numpy"

import argparse
from typing import List
import json
import re
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


def price_target_from_analysts(
    other_args: List[str], stock: DataFrame, ticker: str, start: str, interval: str
):
    """Display analysts' price targets for a given stock

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
        prog="pt",
        description="""Prints price target from analysts. [Source: Business Insider]""",
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of latest price targets from analysts to print.",
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

        d_analyst_data = None
        for script in text_soup_market_business_insider.find_all("script"):
            # Get Analyst data
            if "window.analyseChartConfigs.push" in str(script):
                # Extract config data:
                s_analyst_data = (
                    str(script).split("config: ", 1)[1].split(",\r\n", 1)[0]
                )
                d_analyst_data = json.loads(s_analyst_data)
                break

        df_analyst_data = pd.DataFrame.from_dict(d_analyst_data["Markers"])  # type: ignore
        df_analyst_data = df_analyst_data[
            ["DateLabel", "Company", "InternalRating", "PriceTarget"]
        ]
        df_analyst_data.columns = ["Date", "Company", "Rating", "Price Target"]
        # df_analyst_data
        df_analyst_data["Rating"].replace(
            {"gut": "BUY", "neutral": "HOLD", "schlecht": "SELL"}, inplace=True
        )
        df_analyst_data["Date"] = pd.to_datetime(df_analyst_data["Date"])
        df_analyst_data = df_analyst_data.set_index("Date")

        # Slice start of ratings
        if start:
            df_analyst_data = df_analyst_data[start:]  # type: ignore

        if interval == "1440min":
            plt.plot(stock.index, stock["Adj Close"].values, lw=3)
        # Intraday
        else:
            plt.plot(stock.index, stock["Close"].values, lw=3)

        if start:
            plt.plot(df_analyst_data.groupby(by=["Date"]).mean()[start:])  # type: ignore
        else:
            plt.plot(df_analyst_data.groupby(by=["Date"]).mean())

        plt.scatter(df_analyst_data.index, df_analyst_data["Price Target"], c="r", s=40)

        plt.legend(["Closing Price", "Average Price Target", "Price Target"])

        plt.title(f"{ticker} (Time Series) and Price Target")
        plt.xlim(stock.index[0], stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

        pd.set_option("display.max_colwidth", None)
        print(
            df_analyst_data.sort_index(ascending=False)
            .head(ns_parser.n_num)
            .to_string()
        )
        print("")

    except Exception as e:
        print(e)
        print("")
        return


def estimates(other_args: List[str], ticker: str):
    """Display analysts' estimates for a given ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Due diligence ticker symbol
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="est",
        description="""Yearly estimates and quarter earnings/revenues [Source: Business Insider]""",
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

        l_estimates_year_header = list()
        l_estimates_quarter_header = list()
        for estimates_header in text_soup_market_business_insider.findAll(
            "th", {"class": "table__th text-right"}
        ):
            s_estimates_header = estimates_header.text.strip()
            if s_estimates_header.isdigit():
                l_estimates_year_header.append(s_estimates_header)
            elif ("in %" not in s_estimates_header) and (
                "Job" not in s_estimates_header
            ):
                l_estimates_quarter_header.append(s_estimates_header)

        l_estimates_year_metric = list()
        for estimates_year_metric in text_soup_market_business_insider.findAll(
            "td", {"class": "table__td black"}
        ):
            l_estimates_year_metric.append(estimates_year_metric.text)

        l_estimates_quarter_metric = list()
        for estimates_quarter_metric in text_soup_market_business_insider.findAll(
            "td", {"class": "table__td font-color-dim-gray"}
        ):
            l_estimates_quarter_metric.append(estimates_quarter_metric.text)

        d_metric_year = dict()
        d_metric_quarter_earnings = dict()
        d_metric_quarter_revenues = dict()
        l_metrics = list()
        n_metrics = 0
        b_year = True
        for idx, metric_value in enumerate(
            text_soup_market_business_insider.findAll(
                "td", {"class": "table__td text-right"}
            )
        ):

            if b_year:
                # YEAR metrics
                l_metrics.append(metric_value.text.strip())

                # Check if we have processed all year metrics
                if n_metrics > len(l_estimates_year_metric) - 1:
                    b_year = False
                    n_metrics = 0
                    l_metrics = list()
                    idx_y = idx

                # Add value to dictionary
                if (idx + 1) % len(l_estimates_year_header) == 0:
                    d_metric_year[l_estimates_year_metric[n_metrics]] = l_metrics
                    l_metrics = list()
                    n_metrics += 1

            if not b_year:
                # QUARTER metrics
                l_metrics.append(metric_value.text.strip())

                # Check if we have processed all quarter metrics
                if n_metrics > len(l_estimates_quarter_metric) - 1:
                    break

                # Add value to dictionary
                if (idx - idx_y + 1) % len(l_estimates_quarter_header) == 0:
                    if n_metrics < 4:
                        d_metric_quarter_earnings[
                            l_estimates_quarter_metric[n_metrics]
                        ] = l_metrics
                    else:
                        d_metric_quarter_revenues[
                            l_estimates_quarter_metric[n_metrics - 4]
                        ] = l_metrics
                    l_metrics = list()
                    n_metrics += 1

        df_year_estimates = pd.DataFrame.from_dict(
            d_metric_year, orient="index", columns=l_estimates_year_header
        )
        df_year_estimates.index.name = "YEARLY ESTIMATES"
        df_quarter_earnings = pd.DataFrame.from_dict(
            d_metric_quarter_earnings,
            orient="index",
            columns=l_estimates_quarter_header,
        )
        # df_quarter_earnings.index.name = 'Earnings'
        df_quarter_revenues = pd.DataFrame.from_dict(
            d_metric_quarter_revenues,
            orient="index",
            columns=l_estimates_quarter_header,
        )
        # df_quarter_revenues.index.name = 'Revenues'

        l_quarter = list()
        l_date = list()
        for quarter_title in df_quarter_earnings.columns:
            l_quarter.append(re.split("  ending", quarter_title)[0])
            if len(re.split("  ending", quarter_title)) == 2:
                l_date.append(
                    "ending " + re.split("  ending", quarter_title)[1].strip()
                )
            else:
                l_date.append("-")

        df_quarter_earnings.columns = l_quarter
        df_quarter_earnings.loc["Date"] = l_date
        df_quarter_earnings = df_quarter_earnings.reindex(
            ["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"]
        )

        df_quarter_revenues.columns = l_quarter
        df_quarter_revenues.loc["Date"] = l_date
        df_quarter_revenues = df_quarter_revenues.reindex(
            ["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"]
        )

        print(df_year_estimates.to_string())
        print("")
        print("QUARTER ESTIMATES EARNINGS")
        print(df_quarter_earnings.to_string())
        print("")
        print("QUARTER ESTIMATES REVENUES")
        print(df_quarter_revenues.to_string())
        print("")

        print(
            text_soup_market_business_insider.find(
                "div", {"class": "text_right instrument-description"}
            ).text.strip()
        )
        print("")

    except Exception as e:
        print(e)
        print("")
        return


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
