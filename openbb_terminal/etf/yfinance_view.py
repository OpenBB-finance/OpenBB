"""Yahoo Finance view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import yfinance_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_etf_weightings(
    name: str,
    raw: bool = False,
    min_pct_to_display: float = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
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
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    sectors = yfinance_model.get_etf_sector_weightings(name)

    if not sectors:
        return console.print("No data was found for that ETF\n")

    holdings = pd.DataFrame(sectors, index=[0]).T

    title = f"Sector holdings of {name}"

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "weights",
        holdings,
        sheet_name,
    )

    if raw:
        console.print(f"\n{title}")
        holdings.columns = ["% of holdings in the sector"]
        return print_rich_table(
            holdings,
            headers=list(holdings.columns),
            show_index=True,
            title="Sector Weightings Allocation",
        )

    main_holdings = holdings[holdings.values > min_pct_to_display].to_dict()[
        holdings.columns[0]
    ]
    if len(main_holdings) < len(holdings):
        main_holdings["Others"] = 100 - sum(main_holdings.values())

    legend, values = zip(*main_holdings.items())
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

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_etf_description(name: str):
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
