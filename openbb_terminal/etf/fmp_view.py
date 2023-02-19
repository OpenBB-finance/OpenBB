"""FinancialModelingPrep view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import fmp_model
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_etf_weightings(
    name: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display sector weightings allocation of ETF. [Source: FinancialModelingPrep]

    Parameters
    ----------
    name: str
        ETF name
    raw: bool
        Display sector weighting allocation
    min_pct_to_display: float
        Minimum percentage to display sector
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    sectors = fmp_model.get_etf_sector_weightings(name)
    if not sectors:
        console.print("No data was found for that ETF\n")
        return

    title = f"Sector holdings of {name}"

    sector_weights_formatted = {}
    for sector_weight in sectors:
        sector_weights_formatted[sector_weight["sector"]] = (
            float(sector_weight["weightPercentage"].strip("%")) / 100
        )
    sector_weights_formatted = dict(sorted(sector_weights_formatted.items()))

    if raw:
        sectors_df = pd.DataFrame(sectors).sort_values(by="sector")
        print_rich_table(
            sectors_df,
            headers=["Sector", "Weight"],
            show_index=False,
            title=f"\n{title}",
        )

    else:
        legend, values = zip(*sector_weights_formatted.items())
        leg = [f"{le}\n{round(v * 100,2)}%" for le, v in zip(legend, values)]

        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        ax.pie(
            values,
            labels=leg,
            wedgeprops=theme.pie_wedgeprops,
            colors=theme.get_colors(),
            startangle=theme.pie_startangle,
        )
        ax.set_title(title)
        theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "weights",
        pd.DataFrame([sector_weights_formatted]).T,
        sheet_name,
    )
