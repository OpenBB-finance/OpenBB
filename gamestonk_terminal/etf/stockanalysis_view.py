"""StockAnalysis.com view functions"""
__docformat__ = "numpy"

from typing import List
from tabulate import tabulate

from gamestonk_terminal.etf import stockanalysis_model


def view_overview(symbol: str):
    """Print etf overview information

    Parameters
    ----------
    symbol:str
        ETF symbols to display overview for
    """

    data = stockanalysis_model.get_etf_overview(symbol)

    print(tabulate(data, headers=data.columns, tablefmt="fancy_grid"))
    print("")


def view_holdings(symbol: str, num_to_show: int):
    """

    Parameters
    ----------
    symbol: str
        ETF symbol to show holdings for
    num_to_show: int
        Number of holdings to show

    """

    df = stockanalysis_model.get_etf_holdings(symbol)
    print(
        tabulate(
            df[:num_to_show],
            headers=["Ticker", "% of ETF", "Shares"],
            tablefmt="fancy_grid",
        )
    )
    print("")


def view_comparisons(symbols: List[str]):
    """Show ETF comparisons

    Parameters
    ----------
    symbols: List[str]
        List of ETF symbols
    """
    df = stockanalysis_model.compare_etfs(symbols)
    print(tabulate(df, headers=df.columns, tablefmt="fancy_grid"))
    print("")
