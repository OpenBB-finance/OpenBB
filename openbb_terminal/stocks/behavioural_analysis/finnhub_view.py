""" Finnhub View """
__docformat__ = "numpy"

import logging

import os
from datetime import datetime, timedelta
from typing import Optional, List
import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt
from openbb_terminal.stocks.behavioural_analysis import finnhub_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from openbb_terminal.rich_config import console
from openbb_terminal.decorators import check_api_key

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def display_stock_price_headlines_sentiment(
    ticker: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display stock price and headlines sentiment using VADER model over time. [Source: Finnhub]

    Parameters
    ----------
    ticker : str
        Ticker of company
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    start = datetime.now() - timedelta(days=30)
    articles = finnhub_model.get_company_news(
        ticker.upper(),
        s_start=start.strftime("%Y-%m-%d"),
        s_end=datetime.now().strftime("%Y-%m-%d"),
    )
    sentiment = finnhub_model.process_news_headlines_sentiment(articles)

    if not sentiment.empty:
        sentiment_data = [item for sublist in sentiment.values for item in sublist]

        df_stock = yf.download(
            ticker,
            start=min(sentiment.index).to_pydatetime().date(),
            interval="15m",
            prepost=True,
            progress=False,
        )

        if not df_stock.empty:

            # This plot has 1 axis
            if external_axes is None:
                _, ax = plt.subplots(
                    figsize=plot_autoscale(),
                    dpi=PLOT_DPI,
                    nrows=2,
                    ncols=1,
                    sharex=True,
                    gridspec_kw={"height_ratios": [2, 1]},
                )
            else:
                if len(external_axes) != 1:
                    logger.error("Expected list of one axis item.")
                    console.print("[red]Expected list of one axis item./n[/red]")
                    return
                (ax,) = external_axes

            ax[0].set_title(f"Headlines sentiment and {ticker} price")
            for uniquedate in np.unique(df_stock.index.date):
                ax[0].plot(
                    df_stock[df_stock.index.date == uniquedate].index,
                    df_stock[df_stock.index.date == uniquedate]["Adj Close"].values,
                    c="#FCED00",
                )

            ax[0].set_ylabel("Stock Price")
            theme.style_primary_axis(ax[0])
            theme.style_primary_axis(ax[1])

            ax[1].plot(
                sentiment.index,
                pd.Series(sentiment_data)
                .rolling(window=5, min_periods=1)
                .mean()
                .values,
                c="#FCED00",
            )
            ax[1].bar(
                sentiment[sentiment.values >= 0].index,
                [
                    item
                    for sublist in sentiment[sentiment.values >= 0].values
                    for item in sublist
                ],
                color=theme.up_color,
                width=0.01,
            )
            ax[1].bar(
                sentiment[sentiment.values < 0].index,
                [
                    item
                    for sublist in sentiment[sentiment.values < 0].values
                    for item in sublist
                ],
                color=theme.down_color,
                width=0.01,
            )
            ax[1].yaxis.set_label_position("right")
            ax[1].set_ylabel("Headline Sentiment")

            if external_axes is None:
                theme.visualize_output()

            export_data(
                export, os.path.dirname(os.path.abspath(__file__)), "snews", sentiment
            )
