import matplotlib.pyplot as plt


def display_beta(ref_ticker, stock_ticker, rr, sr, beta, alpha):
    """Display the beta scatterplot + linear regression.

    Parameters
    ----------
    ref_ticker : str
    stock_ticker : str
    rr : pd.Series
        ref_ticker returns
    sr : pd.Series
        stock_ticker returns
    beta : float
    alpha : float
    """
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
