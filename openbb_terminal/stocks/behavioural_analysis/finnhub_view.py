""" Finnhub View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd
import yfinance as yf

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.stocks.behavioural_analysis import finnhub_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def display_stock_price_headlines_sentiment(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Display stock price and headlines sentiment using VADER model over time. [Source: Finnhub]

    Parameters
    ----------
    symbol : str
        Ticker of company
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    sentiment = finnhub_model.get_headlines_sentiment(symbol)

    if not sentiment.empty:
        sentiment_data = [item for sublist in sentiment.values for item in sublist]

        df_stock: pd.DataFrame = yf.download(
            symbol,
            start=min(sentiment.index).to_pydatetime().date(),
            interval="15m",
            prepost=True,
            progress=False,
        )

        if not df_stock.empty:
            fig = OpenBBFigure.create_subplots(2, 1, row_heights=[1, 0.5])

            fig.add_scatter(
                x=df_stock.index,
                y=df_stock["Adj Close"].values,
                name="Price",
                line_color="#FCED00",
                connectgaps=True,
                row=1,
                col=1,
                showlegend=False,
            )

            fig.add_scatter(
                x=sentiment.index,
                y=pd.Series(sentiment_data)
                .rolling(window=5, min_periods=1)
                .mean()
                .values,
                name="Sentiment",
                connectgaps=True,
                row=2,
                col=1,
            )

            fig.add_bar(
                x=sentiment[sentiment.values >= 0].index,
                y=[
                    item
                    for sublist in sentiment[sentiment.values >= 0].values
                    for item in sublist
                ],
                name="Positive",
                marker=dict(color=theme.up_color, line=dict(color=theme.up_color)),
                row=2,
                col=1,
            )

            fig.add_bar(
                x=sentiment[sentiment.values < 0].index,
                y=[
                    item
                    for sublist in sentiment[sentiment.values < 0].values
                    for item in sublist
                ],
                name="Negative",
                marker=dict(color=theme.down_color, line=dict(color=theme.down_color)),
                row=2,
                col=1,
            )

            fig.update_layout(
                title=f"Headlines sentiment and {symbol} price",
                xaxis2_title="Date",
                yaxis_title="Stock Price",
                yaxis2_title="Headline Sentiment",
            )
            fig.bar_width = 5

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "snews",
                sentiment,
                sheet_name,
                fig,
            )

            return fig.show(external=external_axes)

    return None
