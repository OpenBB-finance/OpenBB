""" Plot Controller """
import os
from typing import Optional, List, Dict, Any
from textwrap import fill

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.helper_funcs import (
    plot_autoscale,
    export_data,
    print_rich_table,
)


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
    -------
    Plots the data.
    """
    if external_axes is None:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    else:
        ax1, ax2 = external_axes

    color_palette = theme.get_colors()
    ax_1_coloring = 0
    ax_2_coloring = -1

    dataset_yaxis_1 = dataset_yaxis_1.dropna()
    dataset_yaxis_1.index = pd.to_datetime(dataset_yaxis_1.index)

    for column in dataset_yaxis_1:
        ax1.plot(
            dataset_yaxis_1[column],
            label=column.replace("_", " "),
            color=color_palette[ax_1_coloring],
        )
        ax_1_coloring += 1

    ax1.legend(
        [fill(column, 45) for column in dataset_yaxis_1.columns],
        bbox_to_anchor=(0, 0.40, 1, -0.52),
        loc="upper right",
        mode="expand",
        borderaxespad=0,
        prop={"size": 9},
    )

    theme.style_primary_axis(ax1)

    if not dataset_yaxis_2.empty:
        ax2 = ax1.twinx()

        dataset_yaxis_2 = dataset_yaxis_2.dropna()
        dataset_yaxis_2.index = pd.to_datetime(dataset_yaxis_2.index)

        for column in dataset_yaxis_2:
            ax2.plot(
                dataset_yaxis_2[column],
                label=column,
                color=color_palette[ax_2_coloring],
            )
            ax_2_coloring += -1

        theme.style_twin_axis(ax2)

        ax2.legend(
            [fill(column, 45) for column in dataset_yaxis_2.columns],
            bbox_to_anchor=(0.55, 0.40, 1, -0.52),
            loc="upper left",
            mode="expand",
            borderaxespad=0,
            prop={"size": 9},
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


def show_options(
    datasets: Dict[Any, pd.DataFrame], raw: str = "", limit: int = 10, export: str = ""
):
    """
    The ability to plot any data coming from EconDB, FRED or Yahoo Finance.

    Parameters
    ----------
    datasets: Dict[Any, pd.DataFrame]
        A dictionary with the format {command: data}.
    raw : bool
        Whether you wish to show the data available.
    limit: int
        The amount of rows you wish to show.
    export: bool
        Whether you want to export the data.

    Returns
    -------
    Plots the data.
    """
    if raw or export:
        df = pd.DataFrame()
        for _, data in datasets.items():
            df = pd.concat([df, data], axis=1)

        if raw:
            print_rich_table(
                df.tail(limit),
                show_index=True,
                headers=list(df.columns),
                title="Macro data",
            )
        if export:
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "dataset",
                df,
            )
    else:
        options = {
            command: ", ".join(values.keys()) for command, values in datasets.items()
        }
        print_rich_table(
            pd.DataFrame.from_dict(options, orient="index", columns=["Options"]),
            show_index=True,
            index_name="Command",
            title="Options available to plot",
        )
