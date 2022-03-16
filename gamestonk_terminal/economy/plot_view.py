""" Plot Controller """
import os
from typing import Optional, List

import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data


def show_plot(
    dataset_yaxis_1,
    dataset_yaxis_2,
    export,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """
    The ability to plot any data coming from EconDB, FRED or Yahoo Finance.

    Parameters
    ----------
    dataset_yaxis_1: pd.DataFrame
        Data you wish to plot on the first y-axis.
    dataset_yaxis_2 : pd.DataFrame
        Data you wish to plot on the second y-axis.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on

    Returns
    ----------
    Plots the data.
    """
    if external_axes is None:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    else:
        ax1, ax2 = external_axes

    color_palette = theme.get_colors()
    ax_1_coloring = 0
    ax_2_coloring = -1

    for column in dataset_yaxis_1:
        ax1.plot(
            dataset_yaxis_1[column],
            label=column.replace("_", " "),
            color=color_palette[ax_1_coloring],
        )
        ax_1_coloring += 1

    theme.style_primary_axis(ax1)

    if not dataset_yaxis_2.empty:
        ax2 = ax1.twinx()

        for column in dataset_yaxis_2:
            ax2.plot(
                dataset_yaxis_2[column],
                label=column,
                color=color_palette[ax_2_coloring],
            )
            ax_2_coloring += -1

        theme.style_twin_axis(ax2)

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()

        ax1.legend(
            h1 + h2,
            l1 + l2,
            bbox_to_anchor=(0, 0.40, 1, -0.52),
            loc="upper right",
            mode="expand",
            borderaxespad=0,
            prop={"size": 9},
            ncol=2,
        )
    else:
        ax1.legend(
            bbox_to_anchor=(0, 0.40, 1, -0.52),
            loc="upper right",
            mode="expand",
            borderaxespad=0,
            prop={"size": 9},
            ncol=2,
        )

    if external_axes is None:
        theme.visualize_output()

    if export:
        df = pd.concat([dataset_yaxis_1, dataset_yaxis_2], axis=1)
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "plot_macro_data",
            df,
        )
