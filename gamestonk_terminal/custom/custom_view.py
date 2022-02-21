"""Custom Controller View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.config_terminal import theme

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def custom_plot(
    data: pd.DataFrame,
    y_col: str,
    x_col: str = "",
    kind: str = "line",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes: Optional[List[plt.Axes]]:
        External axes for plot
    """
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    if x_col:
        data.plot(x=x_col, y=y_col, kind=kind, ax=ax)
    else:
        data.reset_index().plot(x=data.index.name, y=y_col, kind=kind, ax=ax)

    if kind in ["scatter", "line"]:
        theme.style_primary_axis(ax)
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "custom_plot",
    )
