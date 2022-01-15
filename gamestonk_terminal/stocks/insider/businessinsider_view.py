""" Business Insider View """
__docformat__ = "numpy"

import os
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import (
    export_data,
    get_next_stock_market_days,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.stocks.insider import businessinsider_model
from gamestonk_terminal.rich_config import console

register_matplotlib_converters()


def insider_activity(
    stock: pd.DataFrame,
    ticker: str,
    start: str,
    interval: str,
    num: int,
    raw: bool,
    export: str = "",
):
    """Display insider activity. [Source: Business Insider]

    Parameters
    ----------
    stock : pd.DataFrame
        Stock dataframe
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    num : int
        Number of latest days of inside activity
    raw: bool
        Print to console
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_ins = businessinsider_model.get_insider_activity(ticker)

    if start:
        df_insider = df_ins[start:].copy()  # type: ignore
    else:
        df_insider = df_ins.copy()

    if raw:
        df_insider.index = pd.to_datetime(df_insider.index).date

        print(
            tabulate(
                df_insider.sort_index(ascending=False)
                .head(n=num)
                .applymap(lambda x: x.replace(".00", "").replace(",", "")),
                headers=df_insider.columns,
                showindex=True,
                tablefmt="fancy_grid",
            )
        )

    else:
        _, ax = plt.subplots()

        if interval == "1440min":
            plt.plot(stock.index, stock["Adj Close"].values, lw=3)
        else:  # Intraday
            plt.plot(stock.index, stock["Close"].values, lw=3)

        plt.title(f"{ticker.upper()} (Time Series) and Price Target")

        plt.xlabel("Time")
        plt.ylabel("Share Price")

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
        plt.gcf().autofmt_xdate()

        if gtff.USE_ION:
            plt.ion()

        plt.show()

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "act",
        df_insider,
    )
