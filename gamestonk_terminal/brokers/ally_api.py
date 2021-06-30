import pandas as pd
import numpy as np
import ally
import yfinance as yf
from termcolor import colored
from gamestonk_terminal.brokers.brokers_helpers import ally_positions_to_df

# pylint: disable=no-member


def login():
    try:
        ally.Ally()
    except Exception as e:
        print(e)
        print("")


def show_holdings():

    a = ally.Ally()
    hold = a.holdings()
    stonks = list(hold.sym)
    last_prices = np.asarray(list(hold.lastprice.astype(float))).round(2)
    equity = list(round(hold.marketvalue.astype(float), 2))
    # Loop to get previous close (ally api does not provide that)
    tickers = yf.Tickers(" ".join(stonks))
    prev_closes = np.array([t.info["previousClose"] for t in tickers.tickers])
    pct_changes = ((last_prices - prev_closes) / prev_closes).round(3)

    print("Stonk\t last price \t prev close \t equity \t % Change")

    for stonk, last_price, prev_close, eq, pct_change in zip(
        stonks, last_prices, prev_closes, equity, pct_changes
    ):

        to_print = f"{stonk}\t {last_price}\t\t {prev_close}\t\t {eq}\t\t {pct_change}"
        if last_price >= prev_close:
            print(colored(to_print, "green"))
        else:
            print(colored(to_print, "red"))

    print("")


def return_holdings() -> pd.DataFrame:
    a = ally.Ally()
    hold = a.holdings()
    return ally_positions_to_df(hold)
