""" Plot Controller """
import os
from typing import Any, Dict, Optional

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.helper_funcs import export_data, print_rich_table


def show_plot(
    dataset_yaxis_1,
    dataset_yaxis_2,
    export: str = "",
    sheet_name: Optional[str] = "",
    external_axes: bool = False,
):
    """
    The ability to plot any data coming from EconDB, FRED or Yahoo Finance.

    Parameters
    ----------
    dataset_yaxis_1: pd.DataFrame
        Data you wish to plot on the first y-axis.
    dataset_yaxis_2 : pd.DataFrame
        Data you wish to plot on the second y-axis.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Plots the data.
    """
    fig = OpenBBFigure.create_subplots(
        1, 1, shared_xaxes=True, shared_yaxes=False, specs=[[{"secondary_y": True}]]
    )

    dataset_yaxis_1 = dataset_yaxis_1.dropna()
    dataset_yaxis_1.index = pd.to_datetime(dataset_yaxis_1.index)

    for column in dataset_yaxis_1:
        fig.add_scatter(
            x=dataset_yaxis_1.index,
            y=dataset_yaxis_1[column],
            name=column.replace("_", " "),
            mode="lines",
            yaxis="y1",
            secondary_y=False,
        )

    if not dataset_yaxis_2.empty:
        dataset_yaxis_2 = dataset_yaxis_2.dropna()
        dataset_yaxis_2.index = pd.to_datetime(dataset_yaxis_2.index)

        for column in dataset_yaxis_2:
            fig.add_scatter(
                x=dataset_yaxis_2.index,
                y=dataset_yaxis_2[column],
                name=column,
                mode="lines",
                yaxis="y2",
                secondary_y=True,
            )

    fig.update_yaxes(side="left", secondary_y=False)

    if export:
        df = pd.concat([dataset_yaxis_1, dataset_yaxis_2], axis=1)
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "plot_macro_data",
            df,
            sheet_name,
            fig,
        )

    return fig.show(external=external_axes)


def show_options(
    datasets: Dict[Any, pd.DataFrame],
    raw: str = "",
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
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
            df = df.sort_index(ascending=False)
            print_rich_table(
                df,
                show_index=True,
                headers=list(df.columns),
                title="Macro data",
                export=bool(export),
                limit=limit,
            )
        if export:
            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "dataset",
                df,
                sheet_name,
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
