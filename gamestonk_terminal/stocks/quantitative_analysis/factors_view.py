"""Factors view"""
__docformat__ = "numpy"

from gamestonk_terminal.stocks.quantitative_analysis.factors_model import (
    capm_information,
)
from gamestonk_terminal.rich_config import console


def capm_view(ticker: str) -> None:
    """Displays information for the CAPM model.

    Parameters
    ----------
    ticker : str
        Selected ticker
    """
    beta, sy = capm_information(ticker)
    console.print(f"Beta:\t\t\t{beta:.2f}")
    console.print(f"Systematic Risk:\t{sy*100:.2f}%")
    console.print(f"Unsystematic Risk:\t{(1-sy)*100:.2f}%\n")
