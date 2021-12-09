""" Comparison Analysis FinBrain View """
__docformat__ = "numpy"

import os
from typing import List

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.stocks.comparison_analysis import finbrain_model

register_matplotlib_converters()


def display_sentiment_compare(similar: List[str], raw: bool = False, export: str = ""):
    """Display sentiment for all ticker. [Source: FinBrain]

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    """
    df_sentiment = finbrain_model.get_sentiments(similar)
    if df_sentiment.empty:
        print("No sentiments found.")

    else:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        for idx, tick in enumerate(similar):
            offset = 2 * idx
            ax.axhline(y=offset, color="k", linestyle="--", lw=2)
            ax.axhline(y=offset + 1, color="k", linestyle="--", lw=1)

            senValues = np.array(pd.to_numeric(df_sentiment[tick].values))
            senNone = np.array(0 * len(df_sentiment))
            ax.fill_between(
                df_sentiment.index,
                pd.to_numeric(df_sentiment[tick].values) + offset,
                offset,
                where=(senValues < senNone),
                alpha=0.60,
                color="red",
                interpolate=True,
            )

            ax.fill_between(
                df_sentiment.index,
                pd.to_numeric(df_sentiment[tick].values) + offset,
                offset,
                where=(senValues >= senNone),
                alpha=0.60,
                color="green",
                interpolate=True,
            )

        ax.set_xlabel("Time")
        ax.set_ylabel("Sentiment")
        ax.axhline(y=-1, color="k", linestyle="--", lw=1)
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax.set_yticks(np.arange(len(similar)) * 2)
        ax.set_yticklabels(similar)
        ax.set_title(f"FinBrain's Sentiment Analysis since {df_sentiment.index[0]}")
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.gcf().autofmt_xdate()
        fig.tight_layout()
        if gtff.USE_ION:
            plt.ion()
        plt.show()

        if raw:
            if gtff.USE_TABULATE_DF:
                print(
                    tabulate(
                        df_sentiment,
                        headers=df_sentiment.columns,
                        tablefmt="fancy_grid",
                    )
                )
            else:
                print(df_sentiment.to_string())

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "sentiment",
            df_sentiment,
        )
    print("")


def display_sentiment_correlation(
    similar: List[str], raw: bool = False, export: str = ""
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
    """
    df_sentiment = finbrain_model.get_sentiments(similar)
    corrs = df_sentiment.corr()
    if df_sentiment.empty:
        print("No sentiments found.")

    else:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

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
        fig.tight_layout()
        if gtff.USE_ION:
            plt.ion()
        plt.show()

        if raw:
            if gtff.USE_TABULATE_DF:
                print(
                    tabulate(
                        corrs,
                        headers=corrs.columns,
                        showindex=True,
                        tablefmt="fancy_grid",
                    )
                )
            else:
                print(corrs.to_string())

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "scorr",
            corrs,
        )

    print("")
