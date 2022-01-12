"""Factors view"""
__docformat__ = "numpy"

from gamestonk_terminal.stocks.quantitative_analysis.factors_model import (
    capm_information,
)


def capm_view(ticker: str) -> None:
    """Displays information for the CAPM model.

    Parameters
    ----------
    ticker : str
        Selected ticker
    """
    beta, sy = capm_information(ticker)
    print(f"Beta:\t\t\t{beta:.2f}")
    print(f"Systematic Risk:\t{sy*100:.2f}%")
    print(f"Unsystematic Risk:\t{(1-sy)*100:.2f}%\n")
