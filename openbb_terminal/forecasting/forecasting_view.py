"""Forecasting View"""
__docformat__ = "numpy"

import logging
import os
from typing import Dict, Optional, List

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from openbb_terminal.helper_funcs import (
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.forecasting import forecasting_model
from openbb_terminal.config_terminal import theme

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def show_options(
    datasets: Dict[str, pd.DataFrame],
    dataset_name: str = None,
    export: str = "",
):
    """Plot custom data

    Parameters
    ----------
    datasets: dict
        The loaded in datasets
    dataset_name: str
        The name of the dataset you wish to show options for
    export: str
        Format to export image
    """
    if not datasets:
        console.print(
            "Please load in a dataset by using the 'load' command before using this feature."
        )
    else:
        option_tables = forecasting_model.get_options(datasets, dataset_name)

        for dataset, data_values in option_tables.items():
            print_rich_table(
                data_values,
                headers=list(data_values.columns),
                show_index=False,
                title=f"Options for dataset: '{dataset}'",
            )

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{dataset}_options",
                data_values.set_index("column"),
            )


@log_start_end(log=logger)
def display_plot(
    data: Dict[str, pd.DataFrame],
    export: str = "",
    external_axes: Optional[List[plt.axes]] = None,
):
    """Plot data from a dataset

    Parameters
    ----------
    data: Dict[str: pd.DataFrame]
        Dictionary with key being dataset.column and dataframes being values
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
    """

    for dataset_col in data:
        if isinstance(data[dataset_col].index, pd.MultiIndex):
            console.print(
                "The index appears to be a multi-index. "
                "Therefore, it is not possible to plot the data."
            )
            del data[dataset_col]

    # Check that there's at least a valid dataframe
    if data:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes[0]

        for dataset_col in data:
            if isinstance(data[dataset_col], pd.Series):
                ax.plot(data[dataset_col].index, data[dataset_col].values)
            elif isinstance(data[dataset_col], pd.DataFrame):
                ax.plot(data[dataset_col])

            theme.style_primary_axis(ax)

            if external_axes is None:
                theme.visualize_output()

        ax.legend(list(data.keys()))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "plot",
    )
