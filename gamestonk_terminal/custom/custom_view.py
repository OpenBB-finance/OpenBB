"""Custom Controller View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def custom_plot(
    data: pd.DataFrame,
    y_col: str,
    x_col: str = "",
    kind: str = "scatter",
    export: str = "",
):
    """Plot custom data

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of custom data
    y_col: str
        Column for y data
    x_col: str
        Column for x data.  Uses index if not supplied.
    kind : str
        Kind of plot to pass to pandas plot function
    export: str
        Format to export image
    """
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    if x_col:
        data.plot(x=x_col, y=y_col, kind=kind, ax=ax)
    else:
        data.reset_index().plot(x="index", y=y_col, kind=kind, ax=ax)

    if x_col in ["date", "time", "timestamp"]:
        fig.autofmt_xdate()

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
