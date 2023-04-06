"""FinancialModelingPrep view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import fmp_model
from openbb_terminal.helper_funcs import (
    export_data,
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
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    sectors = fmp_model.get_etf_sector_weightings(name)
    if not sectors:
        return console.print("No data was found for that ETF\n")

    title = f"Sector holdings of {name}"

    sector_weights_formatted = {}
    for sector_weight in sectors:
        sector_weights_formatted[sector_weight["sector"]] = (
            float(sector_weight["weightPercentage"].strip("%")) / 100
        )
    sector_weights_formatted = dict(sorted(sector_weights_formatted.items()))

    legend, values = zip(*sector_weights_formatted.items())
    colors = theme.get_colors()

    fig = OpenBBFigure.create_subplots(
        1,
        3,
        specs=[[{"type": "domain"}, {"type": "pie", "colspan": 2}, None]],
        row_heights=[1],
        column_widths=[0.1, 0.8, 0.1],
    )

    fig.add_pie(
        labels=legend,
        values=values,
        textinfo="label+percent",
        hoverinfo="label+percent",
        automargin=True,
        rotation=45,
        row=1,
        col=2,
    )
    fig.update_traces(
        textposition="outside",
        textfont_size=15,
        marker=dict(
            colors=colors,
            line=dict(color="#F5EFF3", width=0.8),
        ),
    )

    fig.update_layout(
        margin=dict(t=40, b=20),
        title=dict(
            text=title,
            y=0.98,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        colorway=colors,
        showlegend=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "weights",
        pd.DataFrame([sector_weights_formatted]).T,
        sheet_name,
        fig,
    )

    if raw:
        sectors_df = pd.DataFrame(sectors).sort_values(by="sector")
        return print_rich_table(
            sectors_df,
            headers=["Sector", "Weight"],
            show_index=False,
            title=f"\n{title}",
            export=bool(export),
        )

    return fig.show(external=external_axes)
