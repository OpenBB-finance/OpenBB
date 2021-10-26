""" Financial Modeling Prep View """
__docformat__ = "numpy"

import os

import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_model,
)
import gamestonk_terminal.feature_flags as gtff


def valinvest_score(ticker: str):
    """Value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: FMP]

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    score = fmp_model.get_score(ticker)
    print(f"Score: {score:.2f}".rstrip("0").rstrip(".") + " %")
    print("")


def display_profile(ticker: str):
    """Financial Modeling Prep ticker profile

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    profile = fmp_model.get_profile(ticker)
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                profile.drop(index=["description", "image"]),
                headers=[],
                tablefmt="fancy_grid",
            )
        )
    else:
        print(profile.drop(index=["description", "image"]).to_string(header=False))

    print(f"\nImage: {profile.loc['image'][0]}")
    print(f"\nDescription: {profile.loc['description'][0]}")
    print("")


def display_quote(ticker: str):
    """Financial Modeling Prep ticker quote

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """

    quote = fmp_model.get_quote(ticker)
    if gtff.USE_TABULATE_DF:
        print(tabulate(quote, headers=[], tablefmt="fancy_grid"))
    else:
        print(quote.to_string(header=False))
    print("")


def display_enterprise(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    df_fa = fmp_model.get_enterprise(ticker, number, quarterly)
    df_fa = df_fa[df_fa.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(tabulate(df_fa, headers=df_fa.columns, tablefmt="fancy_grid"))
    else:
        print(df_fa.to_string())
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "enterprise", df_fa)


def display_discounted_cash_flow(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker discounted cash flow

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    dcf = fmp_model.get_dcf(ticker, number, quarterly)
    dcf = dcf[dcf.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(tabulate(dcf, headers=[], tablefmt="fancy_grid"))
    else:
        print(dcf.to_string())

    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dcf", dcf)


def display_income_statement(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    income = fmp_model.get_income(ticker, number, quarterly)
    income = income[income.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                income.drop(index=["Final link", "Link"]),
                headers=income.columns,
                tablefmt="fancy_grid",
            )
        )

    else:

        print(income.drop(index=["Final link", "Link"]).to_string())

    pd.set_option("display.max_colwidth", None)
    print("")
    print(income.loc["Final link"].to_frame().to_string())
    print("")
    print(income.loc["Link"].to_frame().to_string())
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "income", income)


def display_balance_sheet(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker balance sheet

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    balance = fmp_model.get_balance(ticker, number, quarterly)
    balance = balance[balance.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                balance.drop(index=["Final link", "Link"]),
                headers=balance.columns,
                tablefmt="fancy_grid",
            )
        )

    else:
        print(balance.drop(index=["Final link", "Link"]).to_string())

    pd.set_option("display.max_colwidth", None)
    print("")
    print(balance.loc["Final link"].to_frame().to_string())
    print("")
    print(balance.loc["Link"].to_frame().to_string())
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "balance", balance)


def display_cash_flow(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker cash flow

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    cash = fmp_model.get_cash(ticker, number, quarterly)
    cash = cash[cash.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                cash.drop(index=["Final link", "Link"]),
                headers=cash.columns,
                tablefmt="fancy_grid",
            )
        )
    else:
        print(cash.drop(index=["Final link", "Link"]).to_string())

    pd.set_option("display.max_colwidth", None)
    print("")
    print(cash.loc["Final link"].to_frame().to_string())
    print("")
    print(cash.loc["Link"].to_frame().to_string())
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "cash", cash)


def display_key_metrics(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker key metrics

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    key_metrics = fmp_model.get_key_metrics(ticker, number, quarterly)
    key_metrics = key_metrics[key_metrics.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(tabulate(key_metrics, headers=key_metrics.columns, tablefmt="fancy_grid"))
    else:
        print(key_metrics.to_string())
    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metrics", key_metrics
    )


def display_financial_ratios(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker ratios

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    ratios = fmp_model.get_key_ratios(ticker, number, quarterly)
    ratios = ratios[ratios.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(tabulate(ratios, headers=ratios.columns, tablefmt="fancy_grid"))
    else:

        print(ratios.to_string())
    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "grratiosowth", ratios
    )


def display_financial_statement_growth(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker growth

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    growth = fmp_model.get_financial_growth(ticker, number, quarterly)
    growth = growth[growth.columns[::-1]]
    if gtff.USE_TABULATE_DF:
        print(tabulate(growth, headers=growth.columns, tablefmt="fancy_grid"))
    else:

        print(growth.to_string())
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "growth", growth)
