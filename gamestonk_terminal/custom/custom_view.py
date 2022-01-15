"""Custom Controller View"""
__docformat__ = "numpy"

import os

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console


def custom_plot(data: pd.DataFrame, y_col: str, x_col: str = "", export: str = ""):
    """Plot custom data

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of custom data
    y_col: str
        Column for y data
    x_col: str
        Column for x data.  Uses index if not supplied.
    export: str
        Format to export image
    """
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    if x_col:
        ax.scatter(data[x_col], data[y_col])
    else:
        ax.scatter(data.index, data[y_col])
    fig.tight_layout(pad=2)
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    console.print()
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "custom_plot",
    )
