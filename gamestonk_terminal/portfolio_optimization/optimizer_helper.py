""" Portfolio Optimization Helper Functions """
__docformat__ = "numpy"

import argparse
from typing import List
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import plot_autoscale

l_valid_property_infos = [
    "previousClose",
    "regularMarketOpen",
    "twoHundredDayAverage",
    "trailingAnnualDividendYield",
    "payoutRatio",
    "volume24Hr",
    "regularMarketDayHigh",
    "navPrice",
    "averageDailyVolume10Day",
    "totalAssets",
    "regularMarketPreviousClose",
    "fiftyDayAverage",
    "trailingAnnualDividendRate",
    "open",
    "toCurrency",
    "averageVolume10days",
    "expireDate",
    "yield",
    "algorithm",
    "dividendRate",
    "exDividendDate",
    "beta",
    "circulatingSupply",
    "regularMarketDayLow",
    "priceHint",
    "currency",
    "trailingPE",
    "regularMarketVolume",
    "lastMarket",
    "maxSupply",
    "openInterest",
    "marketCap",
    "volumeAllCurrencies",
    "strikePrice",
    "averageVolume",
    "priceToSalesTrailing12Months",
    "dayLow",
    "ask",
    "ytdReturn",
    "askSize",
    "volume",
    "fiftyTwoWeekHigh",
    "forwardPE",
    "fromCurrency",
    "fiveYearAvgDividendYield",
    "fiftyTwoWeekLow",
    "bid",
    "dividendYield",
    "bidSize",
    "dayHigh",
    "annualHoldingsTurnover",
    "enterpriseToRevenue",
    "beta3Year",
    "profitMargins",
    "enterpriseToEbitda",
    "52WeekChange",
    "morningStarRiskRating",
    "forwardEps",
    "revenueQuarterlyGrowth",
    "sharesOutstanding",
    "fundInceptionDate",
    "annualReportExpenseRatio",
    "bookValue",
    "sharesShort",
    "sharesPercentSharesOut",
    "fundFamily",
    "lastFiscalYearEnd",
    "heldPercentInstitutions",
    "netIncomeToCommon",
    "trailingEps",
    "lastDividendValue",
    "SandP52WeekChange",
    "priceToBook",
    "heldPercentInsiders",
    "shortRatio",
    "sharesShortPreviousMonthDate",
    "floatShares",
    "enterpriseValue",
    "threeYearAverageReturn",
    "lastSplitFactor",
    "legalType",
    "lastDividendDate",
    "morningStarOverallRating",
    "earningsQuarterlyGrowth",
    "pegRatio",
    "lastCapGain",
    "shortPercentOfFloat",
    "sharesShortPriorMonth",
    "impliedSharesOutstanding",
    "fiveYearAverageReturn",
    "regularMarketPrice",
]


def check_valid_property_type(aproperty: str) -> str:
    """Check that the property selected is valid"""
    if aproperty in l_valid_property_infos:
        return aproperty

    raise argparse.ArgumentTypeError(f"{aproperty} is not a valid info")


def process_stocks(list_of_stocks: List[str], period: str = "3mo") -> pd.DataFrame:
    """Get adjusted closing price for each stock in the list

    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to get historical data for
    period: str
        Period to get data from yfinance

    Returns
    -------
    stock_closes: DataFrame
        DataFrame containing daily (adjusted) close prices for each stock in list
    """

    stock_prices = yf.download(
        list_of_stocks, period=period, progress=False, group_by="ticker"
    )
    stock_closes = pd.DataFrame(index=stock_prices.index)
    for stock in list_of_stocks:
        stock_closes[stock] = stock_prices[stock]["Adj Close"]
    return stock_closes


def prepare_efficient_frontier(stock_prices: pd.DataFrame):
    """Take in a dataframe of prices and return an efficient frontier object

    Parameters
    ----------
    stock_prices : DataFrame
        DataFrame where indices are DateTime and columns are stocks

    Returns
    -------
    ef: EfficientFrontier
        EfficientFrontier object
    """

    mu = expected_returns.mean_historical_return(stock_prices)
    S = risk_models.sample_cov(stock_prices)
    ef = EfficientFrontier(mu, S)
    return ef


def display_weights(weights: dict):
    """Print weights in a nice format

    Parameters
    ----------
    weights: dict
        weights to display.  Keys are stocks.  Values are either weights or values if -v specified
    """

    if not weights:
        return
    weight_df = pd.DataFrame.from_dict(data=weights, orient="index", columns=["value"])
    if math.isclose(weight_df.sum()["value"], 1, rel_tol=0.1):
        weight_df["weight"] = (weight_df["value"] * 100).astype(str).apply(
            lambda s: " " + s[:4] if s.find(".") == 1 else "" + s[:5]
        ) + " %"
        print(pd.DataFrame(weight_df["weight"]).to_string(header=False))
    else:
        print(weight_df.to_string(header=False))


def my_autopct(x):
    """Function for autopct of plt.pie.  This results in values not being printed in the pie if they are 'too small'"""
    if x > 4:
        return f"{x:.2f} %"

    return ""


def pie_chart_weights(weights: dict, title_opt: str):
    """Show a pie chart of holdings

    Parameters
    ----------
    weights: dict
        Weights to display, where keys are tickers, and values are either weights or values if -v specified
    title: str
        Title to be used on the plot title
    """
    if not weights:
        return

    init_stocks = list(weights.keys())
    init_sizes = list(weights.values())
    stocks = []
    sizes = []
    for stock, size in zip(init_stocks, init_sizes):
        if size > 0:
            stocks.append(stock)
            sizes.append(size)

    total_size = np.sum(sizes)

    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    if math.isclose(sum(sizes), 1, rel_tol=0.1):
        wedges, _, autotexts = plt.pie(
            sizes,
            labels=stocks,
            autopct=my_autopct,
            textprops=dict(color="k"),
            wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
            normalize=True,
        )
        plt.setp(autotexts, color="white", fontweight="bold")
    else:
        wedges, _, autotexts = plt.pie(
            sizes,
            labels=stocks,
            autopct="",
            textprops=dict(color="k"),
            wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
            normalize=True,
        )
        plt.setp(autotexts, color="white", fontweight="bold")
        for i, a in enumerate(autotexts):
            if sizes[i] / total_size > 0.05:
                a.set_text(f"{sizes[i]:.2f}")
            else:
                a.set_text("")

    plt.axis("equal")

    leg1 = plt.legend(
        wedges,
        [str(s) for s in stocks],
        title="  Ticker",
        loc="upper left",
        bbox_to_anchor=(0.80, 0, 0.5, 1),
        frameon=False,
    )
    leg2 = plt.legend(
        wedges,
        [
            f"{' ' if ((100*s/total_size) < 10) else ''}{100*s/total_size:.2f}%"
            for s in sizes
        ],
        title=" ",
        loc="upper left",
        handlelength=0,
        bbox_to_anchor=(0.91, 0, 0.5, 1),
        frameon=False,
    )
    plt.gca().add_artist(leg1)
    plt.gca().add_artist(leg2)

    plt.setp(autotexts, size=8, weight="bold")

    plt.gca().set_title(title_opt, pad=20)

    if gtff.USE_ION:
        plt.ion()

    plt.tight_layout()

    plt.show()
    print("")
