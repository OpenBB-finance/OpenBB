"""Options Smile View"""
__docformat__ = "numpy"

import matplotlib.pyplot as plt

from gamestonk_terminal.options.yfinance_model import get_option_chain


def plot_smile(ticker: str, expiration: str, put: bool) -> None:
    """Generate a graph showing the option smile for a given option chain at a given expiration"""
    chain = get_option_chain(ticker, expiration)
    values = chain.puts if put else chain.calls
    prices = values["strike"]
    iv = values["impliedVolatility"]
    _, ax = plt.subplots()
    ax.plot(prices, iv, "--bo", label="Implied Volatility")
    word = "puts" if put else "calls"
    ax.set_title(f"Volatility smile for {ticker} {word} on {expiration}")
    ax.set_ylabel("Implied Volatility")
    ax.set_xlabel("Strike Price")
    ax.xaxis.set_major_formatter("${x:.2f}")
    ax.yaxis.set_major_formatter("{x:.2f}%")
    plt.legend()
    plt.show()
