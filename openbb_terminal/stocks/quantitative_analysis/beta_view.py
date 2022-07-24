"""Beta view"""
__docformat__ = "numpy"

import logging

import matplotlib.pyplot as plt
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.quantitative_analysis.beta_model import beta_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def beta_view(stock_ticker, ref_ticker, stock=None, ref=None):
    """Display the beta scatterplot + linear regression.

    Parameters
    ----------
    stock_ticker : str
    ref_ticker : str
    stock : pd.DataFrame
        stock_ticker price data
    ref : pd.DataFrame
        ref_ticker price data
    """
    sr, rr, beta, alpha = beta_model(stock_ticker, ref_ticker, stock, ref)

    fig, ax = plt.subplots()
    ax.scatter(rr, sr)  # plot returns
    ax.plot(ax.get_xlim(), [x * beta + alpha for x in ax.get_xlim()])  # plot lin reg
    ax.set(
        xlabel=f"{ref_ticker} Returns (%)",
        ylabel=f"{stock_ticker} Returns (%)",
        title=f"Beta of {stock_ticker} with respect to {ref_ticker}",
    )
    beta_text = f"Raw Beta={round(beta, 2)}\nAlpha={round(alpha, 2)}"
    ax.text(0.9, 0.1, beta_text, horizontalalignment="right", transform=ax.transAxes)
    fig.show()
