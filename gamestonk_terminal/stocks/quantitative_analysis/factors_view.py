"""Factors view"""
__docformat__ = "numpy"

from gamestonk_terminal.stocks.quantitative_analysis.factors_model import (
    capm_information,
)


def capm_view(ticker):
    """A view that displays information for the CAPM model."""
    beta, sy = capm_information(ticker)
    print(f"Beta:\t\t\t{beta:.2f}")
    print(f"Systematic Risk:\t{sy*100:.2f}%")
    print(f"Unsystematic Risk:\t{(1-sy)*100:.2f}%\n")
