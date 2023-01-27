""" FINRA View """
__docformat__ = "numpy"

import logging
import os
from typing import List

import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import finra_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def darkpool_ats_otc(
    symbol: str,
    export: str = "",
    sheet_name: str = None,
    external_axes: bool = False,
):
    """Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]

    Parameters
    ----------
    symbol : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    del external_axes
    ats, otc = finra_model.getTickerFINRAdata(symbol)
    if ats.empty:
        console.print("[red]Could not get data[/red]\n")
        return

    if ats.empty and otc.empty:
        console.print("No ticker data found!")

    fig = OpenBBFigure.create_subplots(
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
        margin=dict(l=40),
        title=f"<b>Dark Pools (ATS) vs OTC (Non-ATS) Data for {symbol}</b>",
        title_x=0.025,
        title_font_size=14,
        yaxis3_title="Shares per Trade",
        yaxis_title="Total Weekly Shares",
        xaxis2_title="Weeks",
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
        barmode="group",
        bargap=0.5,
        bargroupgap=0,
        hovermode="x unified",
        spikedistance=1,
        hoverdistance=1,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dpotc_ats",
        ats,
        sheet_name,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dpotc_otc",
        otc,
        sheet_name,
    )

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dpotc_ats", ats)
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dpotc_otc", otc)

    return fig.show()


@log_start_end(log=logger)
def plot_dark_pools_ats(data: pd.DataFrame, symbols: List, external_axes: bool = False):
    """Plots promising tickers based on growing ATS data

    Parameters
    ----------
    data: pd.DataFrame
        Dark Pools (ATS) Data
    symbols: List
        List of tickers from most promising with better linear regression slope
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    """

    # This plot has 1 axis
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

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
    sheet_name: str = None,
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
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

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "prom",
            df_ats,
            sheet_name,
        )
    else:
        console.print("[red]Could not get data[/red]\n")
        return
