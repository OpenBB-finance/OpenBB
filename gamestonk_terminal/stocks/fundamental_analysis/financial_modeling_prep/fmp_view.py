""" Financial Modeling Prep View """
__docformat__ = "numpy"

import logging
import os

import pandas as pd

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_model,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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
    console.print(f"Score: {score:.2f}".rstrip("0").rstrip(".") + " %")
    console.print("")


@log_start_end(log=logger)
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
    if not profile.empty:
        print_rich_table(
            profile.drop(index=["description", "image"]),
            headers=[],
            title="Ticker Profile",
        )

        console.print(f"\nImage: {profile.loc['image'][0]}")
        console.print(f"\nDescription: {profile.loc['description'][0]}")
    else:
        console.print("[red]Unable to get data[/red]")
    console.print("")


@log_start_end(log=logger)
def display_quote(ticker: str):
    """Financial Modeling Prep ticker quote

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """

    quote = fmp_model.get_quote(ticker)
    print_rich_table(quote, headers=[], title="Ticker Quote")
    console.print("")


@log_start_end(log=logger)
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
    print_rich_table(df_fa, headers=list(df_fa.columns), title="Ticker Enterprise")
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "enterprise", df_fa)


@log_start_end(log=logger)
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
    print_rich_table(dcf, headers=[], title="Discounted Cash Flow")

    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dcf", dcf)


@log_start_end(log=logger)
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
    if not income.empty:
        income = income[income.columns[::-1]]
        print_rich_table(
            income.drop(index=["Final link", "Link"]),
            headers=list(income.columns),
            title="Ticker Income Statement",
        )

        pd.set_option("display.max_colwidth", None)
        console.print("")
        console.print(income.loc["Final link"].to_frame().to_string())
        console.print("")
        console.print(income.loc["Link"].to_frame().to_string())
        console.print("")
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "income", income
        )
    else:
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
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
    if not balance.empty:
        balance = balance[balance.columns[::-1]]
        print_rich_table(
            balance.drop(index=["Final link", "Link"]),
            headers=list(balance.columns),
            title="Ticker Balance SHeet",
        )

        pd.set_option("display.max_colwidth", None)
        console.print("")
        console.print(balance.loc["Final link"].to_frame().to_string())
        console.print("")
        console.print(balance.loc["Link"].to_frame().to_string())
        console.print("")
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "balance", balance
        )
    else:
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
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
    if not cash.empty:
        cash = cash[cash.columns[::-1]]
        print_rich_table(
            cash.drop(index=["Final link", "Link"]),
            headers=list(cash.columns),
            title="Ticker Cash Flow",
        )

        pd.set_option("display.max_colwidth", None)
        console.print("")
        console.print(cash.loc["Final link"].to_frame().to_string())
        console.print("")
        console.print(cash.loc["Link"].to_frame().to_string())
        console.print("")
        export_data(export, os.path.dirname(os.path.abspath(__file__)), "cash", cash)
    else:
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
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
    if not key_metrics.empty:
        key_metrics = key_metrics[key_metrics.columns[::-1]]
        print_rich_table(
            key_metrics, headers=list(key_metrics.columns), title="Ticker Key Metrics"
        )
        console.print("")
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "metrics", key_metrics
        )
    else:
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
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
    if not ratios.empty:
        ratios = ratios[ratios.columns[::-1]]
        print_rich_table(ratios, headers=list(ratios.columns), title="Ticker Ratios")
        console.print("")
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "grratiosowth", ratios
        )
    else:
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
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
    if not growth.empty:
        growth = growth[growth.columns[::-1]]
        print_rich_table(growth, headers=list(growth.columns), title="Ticker Growth")
        console.print("")
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "growth", growth
        )
    else:
        console.print("[red]Could not get data[/red]\n")
