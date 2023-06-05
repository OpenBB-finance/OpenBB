""" Comparison Analysis FinBrain View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.comparison_analysis import finbrain_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_sentiment_compare(
    similar: List[str],
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Display sentiment for all ticker. [Source: FinBrain].

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finviz_peers(), finnhub_peers() or polygon_peers().
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_sentiment = finbrain_model.get_sentiments(similar)
    if df_sentiment.empty:
        return console.print("No sentiments found.")

    fig = OpenBBFigure(yaxis_title="Sentiment")
    fig.set_title(f"FinBrain's Sentiment Analysis since {df_sentiment.index[0]}")

    # we need to remove the tickers that are not in the df_sentiment dataframe
    similar = [tick for tick in similar if tick in df_sentiment.columns]

    for idx, tick in enumerate(similar):
        offset = 2 * idx
        fig.add_hline(y=offset + 1, line=dict(color="white", dash="dash"))

        senValues = np.array(pd.to_numeric(df_sentiment[tick].values))
        senNone = np.array(0 * len(df_sentiment))
        negative_yloc = np.where(senValues < senNone)[0]
        positive_yloc = np.where(senValues > senNone)[0]

        fig.add_scatter(
            x=df_sentiment.index[positive_yloc],
            y=pd.to_numeric(df_sentiment[tick].values)[positive_yloc] + offset,
            mode="lines",
            line_width=0,
            name=tick,
        )
        fig.add_scatter(
            x=[df_sentiment.index[0], df_sentiment.index[-1]],
            y=[offset, offset],
            fillcolor=theme.up_color,
            line=dict(color="white", dash="dash"),
            fill="tonexty",
            mode="lines",
            name=tick,
        )
        fig.add_scatter(
            x=df_sentiment.index[negative_yloc],
            y=pd.to_numeric(df_sentiment[tick].values)[negative_yloc] + offset,
            fill="tonexty",
            fillcolor=theme.down_color,
            line_width=0,
            mode="lines",
            name=tick,
        )

    fig.add_hline(y=-1, line=dict(color="white", dash="dash"))
    fig.update_traces(showlegend=False)
    fig.update_yaxes(ticktext=similar, tickvals=np.arange(len(similar)) * 2)

    if raw:
        print_rich_table(
            df_sentiment,
            headers=list(df_sentiment.columns),
            show_index=True,
            index_name="Date",
            title="Ticker Sentiment",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sentiment",
        df_sentiment,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_sentiment_correlation(
    similar: List[str],
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plot correlation sentiments heatmap across similar companies. [Source: FinBrain].

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finviz_peers(), finnhub_peers() or polygon_peers().
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    corrs, df_sentiment = finbrain_model.get_sentiment_correlation(similar)

    if df_sentiment.empty:
        return console.print("No sentiments found.")

    similar_string = ",".join(similar)
    fig = OpenBBFigure().set_title(
        f"Sentiment correlation heatmap across {similar_string}"
    )

    mask = np.zeros((len(similar), len(similar)), dtype=bool)
    mask[np.triu_indices(len(mask))] = True
    df_corr = corrs.mask(mask)

    df_corr.fillna("", inplace=True)

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
            thickness=20,
            thicknessmode="pixels",
            x=1.15,
            y=1,
            xanchor="right",
            yanchor="top",
            xpad=10,
        ),
        xgap=1,
        ygap=1,
    )
    fig.update_layout(
        margin=dict(l=0, r=20, t=20, b=0),
        yaxis=dict(autorange="reversed"),
    )

    if raw:
        print_rich_table(
            corrs,
            headers=list(corrs.columns),
            show_index=True,
            title="Correlation Sentiments",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "scorr",
        corrs,
        sheet_name,
        fig,
    )
    return fig.show(external=raw or external_axes)
