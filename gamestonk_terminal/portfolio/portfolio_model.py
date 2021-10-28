"""Portfolio Model"""
__docformat__ = "numpy"

import os
import math
from datetime import date, timedelta

import numpy as np
import pandas as pd

from gamestonk_terminal.portfolio import portfolio_view, yfinance_model

# pylint: disable=E1136
# pylint: disable=unsupported-assignment-operation


def save_df(df: pd.DataFrame, name: str) -> None:
    """
    Saves the portfolio as a csv

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
    """
    Saves the portfolio as a csv

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


def generate_performance(portfolio: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a new df with performance results

    Parameters
    ----------
    portfolio : pd.DataFrame
        The dataframe of transactions

    Returns
    ----------
    data : pd.DataFrame
        A dataframe with performance of portfolio
    hist : pd.DataFrame
        The historical performance of tickers in portfolio
    """
    changes = portfolio.copy()
    # Transactions sorted for only stocks
    cashes = changes[changes["Type"] == "cash"]
    changes = changes[changes["Type"] == "stock"]
    uniques = list(set(changes["Name"].tolist()))
    if uniques:
        hist = yfinance_model.get_stocks(uniques)
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

    log[("Cash", "Cash")] = log[("Cash", "Cash")].cumsum()

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
        comb[("Holding", uni)] = comb[("Quantity", uni)] * comb[("Close", uni)]
        comb[("Holding", uni)] = np.where(
            comb[("Quantity", uni)] > 0,
            comb[("Holding", uni)],
            (2 * comb[("Holding", uni)][0] - comb[("Holding", uni)]),
        )
        comb[("Profit", uni)] = comb[("Profit", uni)].cumsum()

    if len(changes["Date"]) > 0:
        comb["holdings"] = comb.sum(level=0, axis=1)["Holding"]
        comb["profits"] = comb.sum(level=0, axis=1)["Profit"]
        comb["total_prof"] = comb["holdings"] + comb["profits"]
        comb["total_cost"] = comb.sum(level=0, axis=1)["Cost Basis"]
    return comb, hist
