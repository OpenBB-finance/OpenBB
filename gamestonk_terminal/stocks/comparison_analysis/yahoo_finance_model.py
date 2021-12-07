"""Yahoo Finance Comparison Model"""
__docformat__ = "numpy"

from datetime import datetime, timedelta
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from sklearn.manifold import TSNE
from sklearn.preprocessing import normalize

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
    "v": "Volume",
}


def get_historical(
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
) -> pd.DataFrame:
    """Get historical prices for all comparison stocks

    Parameters
    ----------
    similar_tickers : List[str]
        List of similar tickers
    start : str, optional
        Start date of comparison.  Defaults to 1 year previously
    candle_type : str, optional
        Candle variable to compare, by default "a" for Adjusted Close

    Returns
    -------
    pd.DataFrame
        Dataframe containing candle type variable for each ticker
    """
    # To avoid having to recursively append, just do a single yfinance call.  This will give dataframe
    # where all tickers are columns.
    return yf.download(similar_tickers, start=start, progress=False, threads=False)[
        d_candle_types[candle_type]
    ][similar_tickers]


def get_1y_sp500() -> pd.DataFrame:
    """
    Gets the last year of Adj Close prices for all current SP 500 stocks.
    They are scraped daily using yfinance at https://github.com/jmaslek/daily_sp_500

    Returns
    -------
    pd.DataFrame
        DataFrame containing last 1 year of closes for all SP500 stocks.
    """
    return pd.read_csv(
        "https://raw.githubusercontent.com/jmaslek/daily_sp_500/main/SP500_prices_1yr.csv",
        index_col=0,
    )


# pylint:disable=E1137,E1101


def get_sp500_comps_tsne(
    ticker: str, lr: int = 200, no_plot: bool = False, num_tickers: int = 10
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
    num_tickers : int
        Number of tickers to return

    Returns
    -------
    List[str]
        List of the 10 closest stocks due to TSNE
    """
    # Adding the type makes pylint stop yelling
    close_vals: pd.DataFrame = get_1y_sp500()
    if ticker not in close_vals.columns:
        df_ticker = yf.download(ticker, start=close_vals.index[0], progress=False)[
            "Adj Close"
        ].to_frame()
        df_ticker.columns = [ticker]
        close_vals = close_vals.join(df_ticker, how="inner")

    close_vals = close_vals.dropna(how="all").fillna(method="bfill")
    rets = close_vals.pct_change()[1:].T

    model = TSNE(learning_rate=lr)
    tsne_features = model.fit_transform(normalize(rets))
    xs = tsne_features[:, 0]
    ys = tsne_features[:, 1]
    if not no_plot:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.scatter(xs, ys, alpha=0.5)
        for x, y, company in zip(xs, ys, rets.index):
            if company != ticker:
                ax.annotate(company, (x, y), fontsize=9, alpha=0.75)
            else:
                ax.scatter(x, y, s=50, c="r")
                ax.annotate(company, (x, y), fontsize=9, alpha=1)
        fig.tight_layout()
        plt.show()
    data = pd.DataFrame({"X": xs, "Y": ys}, index=rets.index)
    x0, y0 = data.loc[ticker]
    data["dist"] = (data.X - x0) ** 2 + (data.Y - y0) ** 2
    data = data.sort_values(by="dist")
    return data.iloc[1 : num_tickers + 1].index.to_list()
