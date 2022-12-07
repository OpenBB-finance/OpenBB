""" FINRA View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots

from openbb_terminal.base_helpers import PLT_FONT, PLT_TA_COLORWAY, go
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import finra_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def darkpool_ats_otc(
    symbol: str, export: str = "", external_axes: Optional[List[plt.Axes]] = None
):
    """Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]

    Parameters
    ----------
    symbol : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    del external_axes
    ats, otc = finra_model.getTickerFINRAdata(symbol)
    if ats.empty:
        console.print("[red]Could not get data[/red]\n")
        return

    if ats.empty and otc.empty:
        console.print("No ticker data found!")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_width=[0.4, 0.6],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    )

    if not ats.empty and not otc.empty:
        fig.add_trace(
            go.Bar(
                x=ats.index,
                y=(ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"]),
                name="ATS",
                opacity=0.8,
            ),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                x=otc.index,
                y=otc["totalWeeklyShareQuantity"],
                name="OTC",
                opacity=0.8,
                yaxis="y2",
                offset=0.0001,
            ),
            row=1,
            col=1,
        )

    elif not ats.empty:
        fig.add_trace(
            go.Bar(
                x=ats.index,
                y=(ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"]),
                name="ATS",
                opacity=0.8,
            ),
            row=1,
            col=1,
            secondary_y=False,
        )

    elif not otc.empty:
        fig.add_trace(
            go.Bar(
                x=otc.index,
                y=otc["totalWeeklyShareQuantity"],
                name="OTC",
                opacity=0.8,
                yaxis="y2",
                secondary_y=False,
            ),
            row=1,
            col=1,
        )

    if not ats.empty:
        fig.add_trace(
            go.Scatter(
                name="ATS",
                x=ats.index,
                y=ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
                line=dict(color="#fdc708", width=2),
                opacity=1,
                showlegend=False,
                yaxis="y2",
            ),
            row=2,
            col=1,
        )

        if not otc.empty:
            fig.add_trace(
                go.Scatter(
                    name="OTC",
                    x=otc.index,
                    y=otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                    line=dict(color="#d81aea", width=2),
                    opacity=1,
                    showlegend=False,
                ),
                row=2,
                col=1,
            )
    else:
        fig.add_trace(
            go.Scatter(
                name="OTC",
                x=otc.index,
                y=otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                line=dict(color="#d81aea", width=2),
                opacity=1,
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=50),
        colorway=PLT_TA_COLORWAY,
        title=f"<b>Dark Pools (ATS) vs OTC (Non-ATS) Data for {symbol}</b>",
        title_x=0.025,
        title_font_size=14,
        yaxis3_title="Shares per Trade",
        yaxis_title="Total Weekly Shares",
        xaxis2_title="Weeks",
        font=PLT_FONT,
        yaxis=dict(fixedrange=False, side="left", nticks=20),
        yaxis2=dict(
            fixedrange=False,
            showgrid=False,
            overlaying="y",
            anchor="x",
            layer="above traces",
            title_standoff=0,
        ),
        yaxis3=dict(fixedrange=False, nticks=10),
        xaxis=dict(
            rangeslider=dict(visible=False), type="date", showspikes=True, nticks=20
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0, 0, 0, 0)",
        ),
        barmode="group",
        bargap=0.5,
        bargroupgap=0,
        dragmode="pan",
        hovermode="x unified",
        spikedistance=1,
        hoverdistance=1,
    )
    fig.show()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dpotc_ats", ats)
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dpotc_otc", otc)


@log_start_end(log=logger)
def plot_dark_pools_ats(
    data: pd.DataFrame, symbols: List, external_axes: Optional[List[plt.Axes]] = None
):
    """Plots promising tickers based on growing ATS data

    Parameters
    ----------
    data: pd.DataFrame
        Dark Pools (ATS) Data
    symbols: List
        List of tickers from most promising with better linear regression slope
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    for symbol in symbols:
        ax.plot(
            pd.to_datetime(
                data[data["issueSymbolIdentifier"] == symbol]["weekStartDate"]
            ),
            data[data["issueSymbolIdentifier"] == symbol]["totalWeeklyShareQuantity"]
            / 1_000_000,
        )

    ax.legend(symbols)
    ax.set_ylabel("Total Weekly Shares [Million]")
    ax.set_title("Dark Pool (ATS) growing tickers")
    ax.set_xlabel("Weeks")
    data["weekStartDate"] = pd.to_datetime(data["weekStartDate"])
    ax.set_xlim(data["weekStartDate"].iloc[0], data["weekStartDate"].iloc[-1])
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def darkpool_otc(
    input_limit: int = 1000,
    limit: int = 10,
    tier: str = "T1",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]

    Parameters
    ----------
    input_limit : int
        Number of tickers to filter from entire ATS data based on
        the sum of the total weekly shares quantity
    limit : int
        Number of tickers to display from most promising with
        better linear regression slope
    tier : str
        Tier to process data from: T1, T2 or OTCE
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # TODO: Improve command logic to be faster and more useful
    df_ats, d_ats_reg = finra_model.getATSdata(input_limit, tier)

    if not df_ats.empty and d_ats_reg:

        symbols = list(
            dict(
                sorted(d_ats_reg.items(), key=lambda item: item[1], reverse=True)
            ).keys()
        )[:limit]

        plot_dark_pools_ats(df_ats, symbols, external_axes)

        export_data(export, os.path.dirname(os.path.abspath(__file__)), "prom", df_ats)
    else:
        console.print("[red]Could not get data[/red]\n")
        return
