""" Yahoo Finance view """
__docformat__ = "numpy"

import logging
import os
from itertools import cycle
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.fixedincome import yfinance_model
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
)

logger = logging.getLogger(__name__)

TY_TO_ID = {
    "5_year": "^FVX",
    "10_year": "^TNX",
    "30_year": "^TYX",
}


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ty(
    maturity: str = "3_month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Treasury Yield.

    Parameters
    ----------
    maturity: str
        Maturity to plot, options: ['5_year', '10_year', '30_year']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = yfinance_model.get_series(
        TY_TO_ID[maturity], start_date=start_date, end_date=end_date
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(f"{maturity.replace('-', ' ')} Treasury Yield [Percent]")
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        maturity,
        pd.DataFrame(df, columns=[maturity]) / 100,
    )
