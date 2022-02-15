""" Comparison Analysis FinBrain View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.comparison_analysis import finbrain_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_sentiment_compare(
    similar: List[str],
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display sentiment for all ticker. [Source: FinBrain]

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_sentiment = finbrain_model.get_sentiments(similar)
    if df_sentiment.empty:
        console.print("No sentiments found.")

    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        for idx, tick in enumerate(similar):
            offset = 2 * idx
            ax.axhline(y=offset, color="white", linestyle="--", lw=1)
            ax.axhline(y=offset + 1, color="white", linestyle="--", lw=1)

            senValues = np.array(pd.to_numeric(df_sentiment[tick].values))
            senNone = np.array(0 * len(df_sentiment))
            ax.fill_between(
                df_sentiment.index,
                pd.to_numeric(df_sentiment[tick].values) + offset,
                offset,
                where=(senValues < senNone),
                color=theme.down_color,
                interpolate=True,
            )

            ax.fill_between(
                df_sentiment.index,
                pd.to_numeric(df_sentiment[tick].values) + offset,
                offset,
                where=(senValues >= senNone),
                color=theme.up_color,
                interpolate=True,
            )

        ax.set_ylabel("Sentiment")

        ax.axhline(y=-1, color="white", linestyle="--", lw=1)
        ax.set_yticks(np.arange(len(similar)) * 2)
        ax.set_yticklabels(similar)
        ax.set_xlim(df_sentiment.index[0], df_sentiment.index[-1])
        ax.set_title(f"FinBrain's Sentiment Analysis since {df_sentiment.index[0]}")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

        if raw:
            print_rich_table(
                df_sentiment,
                headers=list(df_sentiment.columns),
                title="Ticker Sentiment",
            )
            console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "sentiment",
            df_sentiment,
        )
    console.print("")


@log_start_end(log=logger)
def display_sentiment_correlation(
    similar: List[str],
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot correlation sentiments heatmap across similar companies. [Source: FinBrain]

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_sentiment = finbrain_model.get_sentiments(similar)
    corrs = df_sentiment.corr()

    if df_sentiment.empty:
        console.print("No sentiments found.")

    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        mask = np.zeros((len(similar), len(similar)), dtype=bool)
        mask[np.triu_indices(len(mask))] = True

        sns.heatmap(
            corrs,
            cbar_kws={"ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
            cmap="RdYlGn",
            linewidths=1,
            annot=True,
            vmin=-1,
            vmax=1,
            mask=mask,
            ax=ax,
        )
        similar_string = ",".join(similar)
        ax.set_title(
            f"Sentiment correlation heatmap across \n{similar_string}", fontsize=11
        )

        if not external_axes:
            theme.visualize_output()

        if raw:
            print_rich_table(
                corrs,
                headers=list(corrs.columns),
                show_index=True,
                title="Correlation Sentiments",
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "scorr",
            corrs,
        )

    console.print("")
