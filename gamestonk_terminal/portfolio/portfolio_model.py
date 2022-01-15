"""Portfolio Model"""
__docformat__ = "numpy"

import os
import math
from datetime import date, timedelta, datetime
from typing import List

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from gamestonk_terminal.portfolio import (
    portfolio_view,
    yfinance_model,
    portfolio_helper,
)
from gamestonk_terminal.rich_config import console

# pylint: disable=E1136
# pylint: disable=unsupported-assignment-operation


def save_df(df: pd.DataFrame, name: str) -> None:
    """Saves the portfolio as a csv

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be saved
    name : str
        The name of the string
    """
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(path, "portfolios", name))
    if ".csv" in name:
        df.to_csv(path, index=False)
    elif ".json" in name:
        df.to_json(path, index=False)
    elif ".xlsx" in name:
        df = df.to_excel(path, index=False, engine="openpyxl")


def load_df(name: str) -> pd.DataFrame:
    """Load the portfolio from a csv

    Parameters
    ----------
    name : str
        The name of the string

    Returns
    ----------
    data : pd.DataFrame
        A DataFrame with historical trading information
    """
    if ".csv" not in name and ".xlsx" not in name and ".json" not in name:
        console.print(
            "Please submit as 'filename.filetype' with filetype being csv, xlsx, or json\n"
        )
        return pd.DataFrame()

    try:
        if ".csv" in name:
            df = pd.read_csv(f"gamestonk_terminal/portfolio/portfolios/{name}")
        elif ".json" in name:
            df = pd.read_json(f"gamestonk_terminal/portfolio/portfolios/{name}")
        elif ".xlsx" in name:
            df = pd.read_excel(
                f"gamestonk_terminal/portfolio/portfolios/{name}", engine="openpyxl"
            )

        df.index = list(range(0, len(df.values)))
        df["Name"] = df["Name"].str.lower()
        df["Type"] = df["Type"].str.lower()
        df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d")

        for item in ["Quantity", "Price", "Fees", "Premium"]:
            result = any(df[item] < 0)
            if result:
                console.print(
                    f"The column '{item}' has a negative value. Ensure all values are positive."
                )
                return pd.DataFrame()

        if len(df[~df["Type"].isin(["cash", "stock"])].index):
            console.print(
                "Warning: 'Type' other than 'cash' and 'stock' will be ignored."
            )

        if len(
            df[
                ~df["Side"]
                .str.lower()
                .isin(["buy", "sell", "interest", "deposit", "withdrawal"])
            ].index
        ):
            console.print(
                "Warning: 'Side' must be buy, sell, interest, deposit, or withdrawal"
            )
            return pd.DataFrame()

        return df
    except FileNotFoundError:
        portfolio_view.load_info()
        return pd.DataFrame()


def add_values(
    log: pd.DataFrame, changes: pd.DataFrame, cashes: pd.DataFrame
) -> pd.DataFrame:
    """Creates a new df with performance results

    Parameters
    ----------
    log : pd.DataFrame
        The dataframe that will have daily holdings
    changes : pd.DataFrame
        Transactions that changed holdings
    cashes : pd.DataFrame
        Cash changing transactions

    Returns
    ----------
    log : pd.DataFrame
        A dataframe with daily holdings
    """
    for index, _ in log.iterrows():
        # Add stocks to dataframe
        values = changes[changes["Date"] == index]
        if len(values.index) > 0:
            for _, sub_row in values.iterrows():
                ticker = sub_row["Name"]
                quantity = sub_row["Quantity"]
                price = sub_row["Price"]
                fees = sub_row["Fees"]
                if math.isnan(fees):
                    fees = 0
                sign = -1 if sub_row["Side"].lower() == "sell" else 1
                pos1 = log.cumsum().at[index, ("Quantity", ticker)] > 0
                pos2 = (quantity * sign) > 0

                if sub_row["Side"].lower() == "interest":
                    log.at[index, ("Cost Basis", ticker)] = (
                        log.at[index, ("Cost Basis", ticker)] + quantity * price
                    )
                    log.at[index, ("Cash", "Cash")] = log.at[
                        index, ("Cash", "Cash")
                    ] - (quantity * price)

                elif (
                    pos1 == pos2
                    or log.cumsum().at[index, ("Quantity", ticker)] == 0
                    or (quantity * sign) == 0
                ):
                    log.at[index, ("Quantity", ticker)] = (
                        log.at[index, ("Quantity", ticker)] + quantity * sign
                    )
                    log.at[index, ("Cost Basis", ticker)] = (
                        log.at[index, ("Cost Basis", ticker)]
                        + fees
                        + quantity * sign * price
                    )
                    log.at[index, ("Cash", "Cash")] = log.at[
                        index, ("Cash", "Cash")
                    ] - (fees + quantity * sign * price)
                else:
                    rev = (
                        log.at[index, ("Profit", ticker)] + quantity * sign * price * -1
                    )
                    wa_cost = (
                        quantity / log.cumsum().at[index, ("Quantity", ticker)]
                    ) * log.cumsum().at[index, ("Cost Basis", ticker)]
                    log.at[index, ("Profit", ticker)] = rev - wa_cost - fees
                    log.at[index, ("Cash", "Cash")] = (
                        log.at[index, ("Cash", "Cash")] + rev - fees
                    )
                    log.at[index, ("Quantity", ticker)] = (
                        log.at[index, ("Quantity", ticker)] + quantity * sign
                    )
                    log.at[index, ("Cost Basis", ticker)] = (
                        log.at[index, ("Cost Basis", ticker)] - wa_cost
                    )
        cash_vals = cashes[cashes["Date"] == index]
        if len(cash_vals.index) > 0:
            for _, sub_row in cash_vals.iterrows():
                amount = sub_row["Price"]
                quantity = sub_row["Quantity"]
                if sub_row["Side"] == "deposit":
                    d = 1
                elif sub_row["Side"] == "withdrawal":
                    d = -1
                else:
                    raise ValueError("Cash type must be deposit or withdrawal")
                log.at[index, ("Cash", "Cash")] = (
                    log.at[index, ("Cash", "Cash")] + d * amount * quantity
                )
                log.at[index, ("Cash", "User")] = (
                    log.at[index, ("Cash", "User")] + d * amount * quantity
                )
    return log


def merge_dataframes(
    log: pd.DataFrame,
    hist: pd.DataFrame,
    changes: pd.DataFrame,
    divs: pd.DataFrame,
    uniques: List[str],
) -> pd.DataFrame:
    """Merge dataframes to create final dataframe

    Parameters
    ----------
    log : pd.DataFrame
        The new dataframe with daily holdings
    hist : pd.DataFrame
        Historical returns for stocks in portfolio
    changes : pd.DataFrame
        A log of past transactions
    divs : pd.DataFrame
        The dividend history for stocks in portfolio
    uniques: List[str]
        A list of stocks in the portfolio

    Returns
    ----------
    comb : pd.DataFrame
        Thew new aggregated dataframe
    """
    comb = pd.merge(log, hist, how="left", left_index=True, right_index=True)
    comb = comb.fillna(method="ffill")
    comb = pd.merge(comb, divs, how="left", left_index=True, right_index=True)
    comb = comb.fillna(0)

    for uni in uniques:
        comb[("Quantity", uni)] = comb[("Quantity", uni)].cumsum()
        comb[("Cost Basis", uni)] = comb[("Cost Basis", uni)].cumsum()
        comb[("Cash", "Cash")] = comb[("Cash", "Cash")] + (
            comb[("Quantity", uni)] * comb[("Dividend", uni)]
        )
        comb[("Holding", uni)] = (
            np.where(
                comb[("Quantity", uni)] > 0,
                comb[("Close", uni)],
                (2 * comb[("Close", uni)][0] - comb[("Close", uni)]),
            )
            * comb[("Quantity", uni)]
        )
        comb[("Profit", uni)] = comb[("Profit", uni)].cumsum()
    comb[("Cash", "Cash")] = comb[("Cash", "Cash")].cumsum()
    if len(changes["Date"]) > 0:
        comb["holdings"] = comb.groupby(level=0, axis=1).sum()["Holding"]
        comb["profits"] = comb.groupby(level=0, axis=1).sum()["Profit"]
        comb["total_prof"] = comb["holdings"] + comb["profits"]
        comb["total_cost"] = comb.groupby(level=0, axis=1).sum()["Cost Basis"]
    return comb


def convert_df(portfolio: pd.DataFrame) -> pd.DataFrame:
    """Converts a df from activity to daily holdings

    Parameters
    ----------
    portfolio : pd.DataFrame
        The dataframe of transactions

    Returns
    ----------
    data : pd.DataFrame
        A dataframe with daily holdings of portfolio
    hist : pd.DataFrame
        The historical performance of tickers in portfolio
    """
    changes = portfolio.copy()
    # Transactions sorted for only stocks and etfs
    cashes = changes[changes["Type"] == "cash"]
    if cashes.empty:
        raise ValueError("Brokers require cash, input cash deposits")
    changes = changes[changes["Type"] == ("stock" or "etf")]
    uniques = list(set(changes["Name"].tolist()))
    if uniques:
        hist = yfinance_model.get_stocks(uniques, min(changes["Date"]))
        divs = yfinance_model.get_dividends(uniques)
    else:
        hist, divs = pd.DataFrame(), pd.DataFrame()

    divs = divs.fillna(0)
    mini = min(cashes["Date"].to_list() + changes["Date"].to_list())
    days = pd.date_range(mini, date.today() - timedelta(days=1), freq="d")
    zeros = [0 for _ in uniques]
    data = [zeros + zeros + zeros + [0] for _ in days]
    vals = ["Quantity", "Cost Basis", "Profit"]
    arrays = [[x for _ in uniques for x in vals] + ["Cash"], uniques * 3 + ["Cash"]]
    tuples = list(zip(*arrays))
    headers = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
    log = pd.DataFrame(data, columns=headers, index=days)
    log[("Cash", "User")] = 0
    log = add_values(log, changes, cashes)
    comb = merge_dataframes(log, hist, changes, divs, uniques)

    return comb, hist


def get_return(df: pd.DataFrame, df_m: pd.DataFrame, n: int) -> pd.DataFrame:
    """Adds cumulative returns to a holdings df

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe of daily holdings
    df_m : pd.DataFrame
        The dataframe of market performance
    n : int
        The period to get returns for

    Returns
    ----------
    comb : pd.DataFrame
        Dataframe with holdings and returns
    """
    df = df.copy()
    df = df[df.index >= datetime.now() - timedelta(days=n + 1)]
    comb = pd.merge(df, df_m, how="left", left_index=True, right_index=True)
    comb = comb.fillna(method="ffill")
    comb = comb.dropna()
    comb["return"] = (
        comb[("Cash", "Cash")]
        + (0 if "holdings" not in comb.columns else comb["holdings"])
    ) / (
        comb[("Cash", "Cash")].shift(1)
        + comb[("Cash", "User")]
        + (0 if "holdings" not in comb.columns else comb["holdings"].shift(1))
    )
    comb["return"] = comb["return"].fillna(1)
    variance = np.var(comb["return"])
    comb["return"] = comb["return"].cumprod() - 1
    comb[("Market", "Return")] = (
        comb[("Market", "Close")] - comb[("Market", "Close")][0]
    ) / comb[("Market", "Close")][0]
    return comb, variance


def get_rolling_beta(
    df: pd.DataFrame, hist: pd.DataFrame, mark: pd.DataFrame, n: pd.DataFrame
) -> pd.DataFrame:
    """Turns a holdings portfolio into a rolling beta dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe of daily holdings
    hist : pd.DataFrame
        A dataframe of historical returns
    mark : pd.DataFrame
        The dataframe of market performance
    n : int
        The period to get returns for

    Returns
    ----------
    final : pd.DataFrame
        Dataframe with rolling beta
    """
    df = df["Holding"]
    uniques = df.columns.tolist()
    res = df.div(df.sum(axis=1), axis=0)
    res = res.fillna(0)
    comb = pd.merge(
        hist["Close"], mark["Market"], how="outer", left_index=True, right_index=True
    )
    comb = comb.fillna(method="ffill")
    for col in hist["Close"].columns:
        exog = sm.add_constant(comb["Close"])
        rols = RollingOLS(comb[col], exog, window=252)
        rres = rols.fit()
        res[f"beta_{col}"] = rres.params["Close"]
    final = res.fillna(method="ffill")
    for uni in uniques:
        final[f"prod_{uni}"] = final[uni] * final[f"beta_{uni}"]
    dropped = final[[f"beta_{x}" for x in uniques]].copy()
    final = final.drop(columns=[f"beta_{x}" for x in uniques] + uniques)
    final["total"] = final.sum(axis=1)
    final = final[final.index >= datetime.now() - timedelta(days=n + 1)]
    comb = pd.merge(final, dropped, how="left", left_index=True, right_index=True)
    return comb


def get_main_text(df: pd.DataFrame) -> str:
    """Get main performance summary from a dataframe with returns

    Parameters
    ----------
    df : pd.DataFrame
        Stock holdings and returns with market returns

    Returns
    ----------
    t : str
        The main summary of performance
    """
    d_debt = np.where(df[("Cash", "Cash")] > 0, 0, 1)
    bcash = 0 if df[("Cash", "Cash")][0] > 0 else abs(df[("Cash", "Cash")][0])
    ecash = 0 if df[("Cash", "Cash")][-1] > 0 else abs(df[("Cash", "Cash")][-1])
    bdte = bcash / (df["holdings"][0] - bcash)
    edte = ecash / (df["holdings"][-1] - ecash)
    if sum(d_debt) > 0:
        t_debt = (
            f"Beginning debt to equity was {bdte:.2%} and ending debt to equity was"
            f" {edte:.2%}. Debt adds risk to a portfolio by amplifying the gains and losses when"
            " equities change in value."
        )
        if bdte > 1 or edte > 1:
            t_debt += " Debt to equity ratios above one represent a significant amount of risk."
    else:
        t_debt = (
            "Margin was not used this year. This reduces this risk of the portfolio."
        )
    text = (
        f"Your portfolio's performance for the period was {df['return'][-1]:.2%}. This was"
        f" {'greater' if df['return'][-1] > df[('Market', 'Return')][-1] else 'less'} than"
        f" the market return of {df[('Market', 'Return')][-1]:.2%}. The variance for the"
        f" portfolio is {np.var(df['return']):.2%}, while the variance for the market was"
        f" {np.var(df[('Market', 'Return')]):.2%}. {t_debt} The following report details"
        f" various analytics from the portfolio. Read below to see the moving beta for a"
        f" stock."
    )
    return text


def get_beta_text(df: pd.DataFrame) -> str:
    """Get beta summary for a dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The beta history of the stock

    Returns
    ----------
    t : str
        The beta history for a ticker
    """
    betas = df[list(filter(lambda score: "beta" in score, list(df.columns)))]
    high = betas.idxmax(axis=1)
    low = betas.idxmin(axis=1)
    text = (
        "Beta is how strongly a portfolio's movements correlate with the market's movements."
        " A stock with a high beta is considered to be riskier. The beginning beta for the period"
        f" was {portfolio_helper.beta_word(df['total'][0])} at {df['total'][0]:.2f}. This went"
        f" {'up' if df['total'][-1] > df['total'][0] else 'down'} to"
        f" {portfolio_helper.beta_word(df['total'][-1])} at {df['total'][-1]:.2f} by the end"
        f" of the period. The ending beta was pulled {'up' if df['total'][-1] > 1 else 'down'} by"
        f" {portfolio_helper.clean_name(high[-1] if df['total'][-1] > 1 else low[-1])}, which had"
        f" an ending beta of {df[high[-1]][-1] if df['total'][-1] > 1 else df[low[-1]][-1]:.2f}."
    )
    return text


performance_text = (
    "The Sharpe ratio is a measure of reward to total volatility. A Sharpe ratio above one is"
    " considered acceptable. The Treynor ratio is a measure of systematic risk to reward."
    " Alpha is the average return above what CAPM predicts. This measure should be above zero"
    ". The information ratio is the excess return on systematic risk. An information ratio of"
    " 0.4 to 0.6 is considered good."
)
