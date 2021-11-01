"""Portfolio Model"""
__docformat__ = "numpy"

import os
import math
from datetime import date, timedelta, datetime
from typing import List

import numpy as np
import pandas as pd

from gamestonk_terminal.portfolio import portfolio_view, yfinance_model

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
        print(
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
                if sub_row["Side"] == "deposit":
                    d = 1
                elif sub_row["Side"] == "withdrawal":
                    d = -1
                else:
                    raise ValueError("Cash type must be deposit or withdrawal")
                log.at[index, ("Cash", "Cash")] = (
                    log.at[index, ("Cash", "Cash")] + d * amount
                )
                log.at[index, ("Cash", "User")] = (
                    log.at[index, ("Cash", "User")] + d * amount
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
    unqiues: List[str]
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
        comb["holdings"] = comb.sum(level=0, axis=1)["Holding"]
        comb["profits"] = comb.sum(level=0, axis=1)["Profit"]
        comb["total_prof"] = comb["holdings"] + comb["profits"]
        comb["total_cost"] = comb.sum(level=0, axis=1)["Cost Basis"]
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
    # Transactions sorted for only stocks
    cashes = changes[changes["Type"] == "cash"]
    if cashes.empty:
        raise ValueError("Brokers require cash, input cash deposits")
    changes = changes[changes["Type"] == "stock"]
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
    comb["return"] = comb["return"].cumprod() - 1
    return comb


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
        hist["Close"], mark["Market"], how="left", left_index=True, right_index=True
    )
    comb = comb.fillna(method="ffill")
    df_var = comb.rolling(252).var().unstack()["Close"].to_frame(name="var")
    for col in hist["Close"].columns:
        df1 = (
            comb.rolling(252).cov().unstack()[col]["Close"].to_frame(name=f"cov_{col}")
        )
        df_var = pd.merge(df_var, df1, how="left", left_index=True, right_index=True)
        df_var[f"beta_{col}"] = df_var[f"cov_{col}"] / df_var["var"]
    final = pd.merge(res, df_var, how="left", left_index=True, right_index=True)
    final = final.fillna(method="ffill")
    final = final.drop(columns=["var"] + [f"cov_{x}" for x in uniques])
    for uni in uniques:
        final[f"prod_{uni}"] = final[uni] * final[f"beta_{uni}"]
    final = final.drop(columns=[f"beta_{x}" for x in uniques] + uniques)
    final["total"] = final.sum(axis=1)
    final = final[final.index >= datetime.now() - timedelta(days=n + 1)]
    return final
