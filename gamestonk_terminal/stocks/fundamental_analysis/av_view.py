""" Alpha Vantage View """
__docformat__ = "numpy"

import os

from tabulate import tabulate
import numpy as np

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.fundamental_analysis import av_model


def display_overview(ticker: str):
    """Alpha Vantage stock ticker overview

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    df_fa = av_model.get_overview(ticker)
    if df_fa.empty:
        print(f"No data found from alphavantage for {ticker}.\n")
        return
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_fa.drop(index=["Description"]), headers=[], tablefmt="fancy_grid"
            )
        )
    else:
        print(df_fa.drop(index=["Description"]).to_string(header=False))

    print(f"\nCompany Description:\n\n{df_fa.loc['Description'][0]}")
    print("")


def display_key(ticker: str):
    """Alpha Vantage key metrics

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    df_key = av_model.get_key_metrics(ticker)

    if df_key.empty:
        print("Issue getting key metrics from alpha vantage.")
        return

    if gtff.USE_TABULATE_DF:
        print(tabulate(df_key, headers=[], tablefmt="fancy_grid"))
    else:
        print(df_key.to_string(header=False))

    print("")


def display_income_statement(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Alpha Vantage income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number of past statements
    quarterly: bool
        Flag to get quarterly instead of annual
    export: str
        Format to export data
    """
    df_income = av_model.get_income_statements(ticker, number, quarterly)

    if gtff.USE_TABULATE_DF:
        print(tabulate(df_income, headers=df_income.columns, tablefmt="fancy_grid"))
    else:
        print(df_income.to_string())

    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "income", df_income)


def display_balance_sheet(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Alpha Vantage income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number of past statements
    quarterly: bool
        Flag to get quarterly instead of annual
    export: str
        Format to export data
    """
    df_balance = av_model.get_balance_sheet(ticker, number, quarterly)

    if gtff.USE_TABULATE_DF:
        print(tabulate(df_balance, headers=df_balance.columns, tablefmt="fancy_grid"))
    else:
        print(df_balance.to_string())

    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "balance", df_balance
    )


def display_cash_flow(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Alpha Vantage income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number of past statements
    quarterly: bool
        Flag to get quarterly instead of annual
    export: str
        Format to export data
    """
    df_cash = av_model.get_cash_flow(ticker, number, quarterly)

    if gtff.USE_TABULATE_DF:
        print(tabulate(df_cash, headers=df_cash.columns, tablefmt="fancy_grid"))
    else:
        print(df_cash.to_string())

    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "cash", df_cash)


def display_earnings(ticker: str, number: int, quarterly: bool = False):
    """Alpha Vantage earnings

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number:int
        Number of events to show
    quarterly: bool
        Flag to show quarterly instead of annual
    """
    df_fa = av_model.get_earnings(ticker, quarterly)
    if df_fa.empty:
        print("Error getting earnings data.\n")
        return
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_fa.head(number),
                headers=df_fa.columns,
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df_fa.head(n=number).T.to_string(header=False))

    print("")


def display_fraud(ticker: str):
    """Fraud indicators for given ticker
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    ratios, zscore = av_model.get_fraud_ratios(ticker)

    if ratios["MSCORE"] > -1.78:
        chanceM = "high"
    elif ratios["MSCORE"] > -2.22:
        chanceM = "moderate"
    else:
        chanceM = "low"

    if zscore < 0.5:
        chanceZ = "high"
    else:
        chanceZ = "low"

    if np.isnan(ratios["MSCORE"]) or np.isnan(zscore):
        print("Data incomplete for this ticker. Unable to calculate risk")
        return

    print("Mscore Sub Stats:")
    for rkey, value in ratios.items():
        if rkey != "MSCORE":
            print("  ", f"{rkey} : {value:.2f}")

    print(
        "\n" + "MSCORE: ",
        f"{ratios['MSCORE']:.2f} ({chanceM} chance of fraud)",
    )

    print("ZSCORE: ", f"{zscore:.2f} ({chanceZ} chance of bankruptcy)", "\n")
    return
