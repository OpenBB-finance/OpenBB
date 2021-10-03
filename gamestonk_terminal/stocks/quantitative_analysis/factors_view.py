"""Factors view"""
__docformat__ = "numpy"

from gamestonk_terminal.stocks.quantitative_analysis.factors_model import (
    capm_information,
)


def capm_view(ticker):
    """A view that displays information for the CAPM model."""
    beta, m_variance, sy, us = capm_information(ticker)
    print(f"Beta:\t\t\t{beta:.2f}")
    print(f"Market Variance:\t{m_variance:.4f}")
    print(f"Systematic Risk:\t{sy:.2f}%")
    print(f"Unsystematic Risk:\t{us:.2f}%\n")
