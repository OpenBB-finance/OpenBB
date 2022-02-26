"""Yahoo Finance view"""
__docformat__ = "numpy"

from typing import Optional, List
import logging
import os

import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.etf import yfinance_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_etf_weightings(
    name: str,
    raw: bool = False,
    min_pct_to_display: float = 5,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display sector weightings allocation of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name
    raw: bool
        Display sector weighting allocation
    min_pct_to_display: float
        Minimum percentage to display sector
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    sectors = yfinance_model.get_etf_sector_weightings(name)
    if not sectors:
        console.print("No data was found for that ETF\n")
        return

    holdings = pd.DataFrame(sectors, index=[0]).T

    title = f"Sector holdings of {name}"

    if raw:
        console.print(f"\n{title}")
        holdings.columns = ["% of holdings in the sector"]
        print_rich_table(
            holdings,
            headers=list(holdings.columns),
            show_index=True,
            title="Sector Weightings Allocation",
        )
        console.print("")

    else:
        main_holdings = holdings[holdings.values > min_pct_to_display].to_dict()[
            holdings.columns[0]
        ]
        if len(main_holdings) < len(holdings):
            main_holdings["Others"] = 100 - sum(main_holdings.values())

        legend, values = zip(*main_holdings.items())
        leg = [f"{le}\n{round(v,2)}%" for le, v in zip(legend, values)]

        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        else:
            if len(external_axes) != 1:
                logger.error("Expected list of 1 axis items.")
                console.print("[red]Expected list of 1 axis items./n[/red]")
                return
            (ax,) = external_axes

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

        console.print("")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "weights", holdings)


@log_start_end(log=logger)
def display_etf_description(
    name: str,
):
    """Display ETF description summary. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name
    """
    description = yfinance_model.get_etf_summary_description(name)
    if not description:
        console.print("No data was found for that ETF\n")
        return

    console.print(description, "\n")
