"""Yahoo Finance Comparison Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from sklearn.manifold import TSNE
from sklearn.preprocessing import normalize

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.rich_config import console


logger = logging.getLogger(__name__)

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
    "v": "Volume",
}


@log_start_end(log=logger)
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
    similar_tickers_dataframe = yf.download(
        similar_tickers, start=start, progress=False, threads=False
    )[d_candle_types[candle_type]]
    return (
        similar_tickers_dataframe
        if similar_tickers_dataframe.empty
        else similar_tickers_dataframe[similar_tickers]
    )


@log_start_end(log=logger)
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


@log_start_end(log=logger)
def get_sp500_comps_tsne(
    ticker: str,
    lr: int = 200,
    no_plot: bool = False,
    num_tickers: int = 10,
    external_axes: Optional[List[plt.Axes]] = None,
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
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return []
            (ax,) = external_axes

        data = pd.DataFrame({"X": xs, "Y": ys}, index=rets.index)
        x0, y0 = data.loc[ticker]
        data["dist"] = (data.X - x0) ** 2 + (data.Y - y0) ** 2
        data = data.sort_values(by="dist")
        ticker_df = data[data.index == ticker]

        top_n = data.iloc[1 : (num_tickers + 1)]
        top_n_name = top_n.index.to_list()

        top_100 = data[(num_tickers + 1) : 101]

        ax.scatter(
            top_n.X,
            top_n.Y,
            alpha=0.8,
            c=theme.up_color,
            label=f"Top {num_tickers} closest tickers",
        )
        ax.scatter(
            top_100.X, top_100.Y, alpha=0.5, c="grey", label="Top 100 closest tickers"
        )

        for x, y, company in zip(top_n.X, top_n.Y, top_n.index):
            ax.annotate(company, (x, y), fontsize=9, alpha=0.9)

        for x, y, company in zip(top_100.X, top_100.Y, top_100.index):
            ax.annotate(company, (x, y), fontsize=9, alpha=0.75)

        ax.scatter(
            ticker_df.X,
            ticker_df.Y,
            s=50,
            c=theme.down_color,
        )
        ax.annotate(ticker, (ticker_df.X, ticker_df.Y), fontsize=9, alpha=1)
        ax.legend()

        ax.set_title(
            f"Top 100 closest stocks on S&P500 to {ticker} using TSNE algorithm",
            fontsize=11,
        )
        ax.set_xlabel("Dimension 1")
        ax.set_ylabel("Dimension 2")
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    return top_n_name
