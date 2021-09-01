"""Playground for ML models for finding similar stocks"""
__docformat__ = "numpy"

from typing import List
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
from sklearn.manifold import TSNE
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.comparison_analysis import yahoo_finance_model

# pylint:disable=no-member
# pylint:disable=unsupported-assignment-operation


def get_sp500_comps_tsne(
    ticker: str, lr: int = 200, no_plot: bool = False
) -> List[str]:
    """
    Runs TSNE on SP500 tickers (along with ticker if not in SP500).
    TSNE is a method of visualing higher dimensional data
    https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
    Note that the TSNE numbers are meaningless and will be arbitrary if run again.

    Parameters
    ----------
    ticker : str
        Ticker to get comparisons to
    lr : int
        Learning rate for TSNE
    no_plot : bool
        Flag to hold off on plotting

    Returns
    -------
    List[str]
        List of the 10 closest stocks due to TSNE
    """
    close_vals = yahoo_finance_model.get_1y_sp500()
    if ticker not in close_vals.columns:
        close_vals[ticker] = yf.download(
            ticker, start=close_vals.index[0], progress=False
        )["Adj Close"]
    rets = (
        close_vals.fillna(method="ffill").fillna(method="bfill").pct_change().dropna().T
    )
    normalized_movements = normalize(rets)
    companies = rets.index
    model = TSNE(learning_rate=lr)
    tsne_features = model.fit_transform(normalized_movements)
    xs = tsne_features[:, 0]
    ys = tsne_features[:, 1]
    if not no_plot:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.scatter(xs, ys, alpha=0.5)
        for x, y, company in zip(xs, ys, companies):
            if company != ticker:
                ax.annotate(company, (x, y), fontsize=9, alpha=0.75)
            else:
                ax.scatter(x, y, s=20, c="r")
                ax.annotate(company, (x, y), fontsize=9, alpha=1)
        fig.tight_layout()
        plt.show()
    data = pd.DataFrame({"X": xs, "Y": ys}, index=rets.index)
    x0, y0 = data.loc[ticker]
    data["dist"] = (data.X - x0) ** 2 + (data.Y - y0) ** 2
    data = data.sort_values(by="dist")
    return data.iloc[1:11].index.to_list()
