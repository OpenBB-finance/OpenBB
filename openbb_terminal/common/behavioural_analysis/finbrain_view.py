"""FinBrain View Module"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure, rich_config, theme
from openbb_terminal.common.behavioural_analysis import finbrain_model
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def lambda_sentiment_coloring(val: float, last_val: float) -> str:
    if float(val) > last_val:
        return f"[green]{val}[/green]"
    return f"[red]{val}[/red]"


@log_start_end(log=logger)
def display_sentiment_analysis(
    symbol: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots Sentiment analysis from FinBrain. Prints table if raw is True. [Source: FinBrain]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get the sentiment analysis from
    raw: False
        Display raw table data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes: bool, optional
        Whether to return the figure object or not, by default False
    """
    sentiment = finbrain_model.get_sentiment(symbol)
    if sentiment.empty:
        return console.print("No sentiment data found.\n")

    if raw:
        if (
            rich_config.USE_COLOR
            and not get_current_user().preferences.USE_INTERACTIVE_DF
        ):
            color_df = sentiment["Sentiment Analysis"].apply(
                lambda_sentiment_coloring, last_val=0
            )
            color_df = pd.DataFrame(
                data=color_df.values,
                index=pd.to_datetime(sentiment.index).strftime("%Y-%m-%d"),
            )
            print_rich_table(
                color_df,
                headers=["Sentiment"],
                title="FinBrain Ticker Sentiment",
                show_index=True,
                export=bool(export),
            )
        else:
            print_rich_table(
                pd.DataFrame(
                    data=sentiment.values,
                    index=pd.to_datetime(sentiment.index).strftime("%Y-%m-%d"),
                ),
                headers=["Sentiment"],
                title="FinBrain Ticker Sentiment",
                show_index=True,
                export=bool(export),
            )

    fig = OpenBBFigure(
        yaxis=dict(title="Sentiment", range=[-1.1, 1.1]), xaxis_title="Time"
    )

    fig.add_hline(y=0, line_dash="dash")

    start_date = sentiment.index[-1].strftime("%Y/%m/%d")

    fig.set_title(
        f"FinBrain's Sentiment Analysis for {symbol.upper()} since {start_date}"
    )
    senValues = np.array(pd.to_numeric(sentiment["Sentiment Analysis"].values))
    senNone = np.array(0 * len(sentiment))
    df_sentiment = sentiment["Sentiment Analysis"]
    negative_yloc = np.where(senValues < senNone)[0]
    positive_yloc = np.where(senValues > senNone)[0]

    fig.add_scatter(
        x=df_sentiment.index[positive_yloc],
        y=pd.to_numeric(df_sentiment.values)[positive_yloc],
        mode="lines+markers",
        marker=dict(color=theme.up_color, size=15),
        line_width=1,
        name=symbol,
    )
    fig.add_scatter(
        x=[df_sentiment.index[0], df_sentiment.index[-1]],
        y=[0, 0],
        fillcolor=theme.up_color_transparent.replace("0.5", "0.4"),
        line=dict(color="white", dash="dash"),
        fill="tonexty",
        mode="lines",
        name=symbol,
    )
    fig.add_scatter(
        x=df_sentiment.index[negative_yloc],
        y=pd.to_numeric(df_sentiment.values)[negative_yloc],
        fill="tonexty",
        fillcolor=theme.down_color_transparent.replace("0.5", "0.4"),
        line_width=1,
        mode="lines+markers",
        marker=dict(color=theme.down_color, size=15),
        name=symbol,
    )
    fig.update_traces(showlegend=False)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "headlines",
        sentiment,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
