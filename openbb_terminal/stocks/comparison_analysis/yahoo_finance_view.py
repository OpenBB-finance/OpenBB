""" Comparison Analysis Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.comparison_analysis import yahoo_finance_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
    "v": "Volume",
    "r": "Returns",
}


@log_start_end(log=logger)
def display_historical(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    candle_type: str = "a",
    normalize: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display historical stock prices. [Source: Yahoo Finance]

    Parameters
    ----------
    similar: List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date: Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date: Optional[str], optional
        End date (e.g., 2023-01-01)
    candle_type: str, optional
        OHLCA column to use or R to use daily returns calculated from Adjusted Close, by default "a" for Adjusted Close
    normalize: bool, optional
        Boolean to normalize all stock prices using MinMax defaults True
    export: str, optional
        Format to export historical prices, by default ""
    external_axes: bool, optional
        Whether to return the figure object or not, by default False
    """
    df_similar = yahoo_finance_model.get_historical(
        similar, start_date, end_date, candle_type
    )

    # This puts everything on 0-1 scale for visualizing
    if normalize:
        mm_scale = MinMaxScaler()
        df_similar = pd.DataFrame(
            mm_scale.fit_transform(df_similar),
            columns=df_similar.columns,
            index=df_similar.index,
        )

    fig = OpenBBFigure(
        yaxis_title=f"{['','Normalized'][normalize]} Share Price {['($)',''][normalize]}"
    )
    fig.set_title("Historical price of similar companies")

    for ticker in df_similar.columns:
        fig.add_scatter(
            x=df_similar.index,
            y=df_similar[ticker],
            name=ticker,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "historical",
        df_similar,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_volume(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display stock volume. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date : Optional[str], optional
        End date (e.g., 2023-01-01). Defaults to today
    export : str, optional
        Format to export historical prices, by default ""
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_similar = yahoo_finance_model.get_volume(similar, start_date, end_date)

    fig = OpenBBFigure(yaxis_title="Volume").set_title(
        "Historical volume of similar companies"
    )
    for ticker in df_similar.columns:
        fig.add_scatter(
            x=df_similar.index,
            y=df_similar[ticker],
            name=ticker,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "volume",
        df_similar,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_correlation(
    similar: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    candle_type: str = "a",
    display_full_matrix: bool = False,
    raw: bool = False,
    external_axes: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> Union[OpenBBFigure, None]:
    """
    Correlation heatmap based on historical price comparison
    between similar companies. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : Optional[str], optional
        Initial date (e.g., 2021-10-01). Defaults to 1 year back
    end_date : Optional[str], optional
        End date (e.g., 2023-01-01)
    candle_type : str, optional
        OHLCA column to use for candles or R for returns, by default "a" for Adjusted Close
    display_full_matrix : bool, optional
        Optionally display all values in the matrix, rather than masking off half, by default False
    raw: bool, optional
        Whether to display raw data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    export : str, optional
        Format to export correlation prices, by default ""
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")

    correlations, df_similar = yahoo_finance_model.get_correlation(
        similar, start_date, end_date, candle_type
    )

    df_corr = correlations
    if not display_full_matrix:
        mask = np.zeros((df_similar.shape[1], df_similar.shape[1]), dtype=bool)
        mask[np.triu_indices(len(mask))] = True
        df_corr = correlations.mask(mask)

    df_corr.fillna("", inplace=True)

    fig = OpenBBFigure()
    fig.set_title(f"Correlation Heatmap of similar companies from {start_date}")
    fig.add_heatmap(
        x=df_corr.columns,
        y=df_corr.index,
        z=df_corr.values.tolist(),
        zmin=-1,
        zmax=1,
        hoverongaps=False,
        showscale=True,
        colorscale="RdYlGn",
        text=df_corr.to_numpy(),
        textfont=dict(color="black"),
        texttemplate="%{text:.2f}",
        colorbar=dict(
            thickness=10,
            thicknessmode="pixels",
            x=1.2,
            y=1,
            xanchor="right",
            yanchor="top",
            xpad=10,
        ),
        xgap=1,
        ygap=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=120, t=0, b=0), yaxis=dict(autorange="reversed")
    )

    if raw:
        print_rich_table(
            correlations,
            headers=[x.title().upper() for x in correlations.columns],
            show_index=True,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hcorr",
        df_similar,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_sp500_comps_tsne(
    symbol: str,
    lr: int = 200,
    no_plot: bool = False,
    limit: int = 10,
    external_axes: bool = False,
) -> Union[List[str], Tuple[List[str], Optional[OpenBBFigure]]]:
    """Runs TSNE on SP500 tickers (along with ticker if not in SP500).
    TSNE is a method of visualing higher dimensional data
    https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
    Note that the TSNE numbers are meaningless and will be arbitrary if run again.

    Parameters
    ----------
    symbol: str
        Ticker to get comparisons to
    lr: int
        Learning rate for TSNE
    no_plot: bool
        Flag to hold off on plotting
    limit: int
        Number of tickers to return
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    List[str]
        List of the 10 closest stocks due to TSNE
    """
    data = yahoo_finance_model.get_sp500_comps_tsne(symbol=symbol, lr=lr)

    top_n = data.iloc[1 : (limit + 1)]
    top_n_name = top_n.index.to_list()

    if not no_plot:
        fig = OpenBBFigure(xaxis_title="Dimension 1", yaxis_title="Dimension 2")
        fig.set_title(
            f"Top 100 closest stocks on S&P500 to {symbol} using TSNE algorithm"
        )

        top_100 = data[(limit + 1) : 101]
        symbol_df = data[data.index == symbol]

        fig.add_scatter(
            x=top_n.X,
            y=top_n.Y,
            text=top_n.index,
            textfont=dict(color=theme.up_color),
            textposition="top center",
            texttemplate="%{text}",
            mode="markers+text",
            marker=dict(size=10, color=theme.up_color),
            name=f"Top {limit} closest tickers",
        )
        fig.add_scatter(
            x=top_100.X,
            y=top_100.Y,
            text=top_100.index,
            textfont=dict(color="grey"),
            textposition="top center",
            texttemplate="%{text}",
            mode="markers+text",
            marker=dict(size=10, color="grey"),
            name="Top 100 closest tickers",
        )

        fig.add_scatter(
            x=symbol_df.X,
            y=symbol_df.Y,
            mode="markers+text",
            name=symbol,
            text=symbol_df.index,
            textfont=dict(color=theme.down_color),
            textposition="top center",
            texttemplate="%{text}",
            marker=dict(size=12, color=theme.down_color),
        )
        if external_axes:
            return top_n_name, fig.show(external=external_axes)

        fig.show()

    return top_n_name
