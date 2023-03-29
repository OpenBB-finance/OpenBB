""" FINRA View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import finra_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def darkpool_ats_otc(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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

    ats, otc = finra_model.getTickerFINRAdata(symbol)
    if ats.empty:
        return console.print("[red]Could not get data[/red]\n")

    if ats.empty and otc.empty:
        return console.print("No ticker data found!")

    fig = OpenBBFigure.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_width=[0.4, 0.6],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    )

    if not ats.empty and not otc.empty:
        fig.add_bar(
            x=ats.index,
            y=(ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"]),
            name="ATS",
            opacity=0.8,
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_bar(
            x=otc.index,
            y=otc["totalWeeklyShareQuantity"],
            name="OTC",
            opacity=0.8,
            yaxis="y2",
            offset=0.0001,
            row=1,
            col=1,
        )

    elif not ats.empty:
        fig.add_bar(
            x=ats.index,
            y=(ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"]),
            name="ATS",
            opacity=0.8,
            row=1,
            col=1,
            secondary_y=False,
        )

    elif not otc.empty:
        fig.add_bar(
            x=otc.index,
            y=otc["totalWeeklyShareQuantity"],
            name="OTC",
            opacity=0.8,
            yaxis="y2",
            secondary_y=False,
            row=1,
            col=1,
        )

    if not ats.empty:
        fig.add_scatter(
            name="ATS",
            x=ats.index,
            y=ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
            line=dict(color="#fdc708", width=2),
            opacity=1,
            yaxis="y2",
            row=2,
            col=1,
        )

        if not otc.empty:
            fig.add_scatter(
                name="OTC",
                x=otc.index,
                y=otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                line=dict(color="#d81aea", width=2),
                opacity=1,
                row=2,
                col=1,
            )
    else:
        fig.add_scatter(
            name="OTC",
            x=otc.index,
            y=otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
            line=dict(color="#d81aea", width=2),
            opacity=1,
            row=2,
            col=1,
        )

    fig.update_layout(
        margin=dict(t=30),
        title=f"<b>Dark Pools (ATS) vs OTC (Non-ATS) Data for {symbol}</b>",
        title_font_size=14,
        yaxis3_title="Shares per Trade",
        yaxis_title="Total Weekly Shares",
        xaxis2_title="Weeks",
        yaxis=dict(fixedrange=False, nticks=20),
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
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def plot_dark_pools_ats(
    data: pd.DataFrame, symbols: List, external_axes: bool = False
) -> Union[OpenBBFigure, None]:
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

    fig = OpenBBFigure(xaxis_title="Weeks", yaxis_title="Total Weekly Shares")
    fig.set_title("Dark Pool (ATS) growing tickers")

    for symbol in symbols:
        fig.add_scatter(
            x=pd.to_datetime(
                data[data["issueSymbolIdentifier"] == symbol]["weekStartDate"]
            ),
            y=data[data["issueSymbolIdentifier"] == symbol]["totalWeeklyShareQuantity"],
            name=symbol,
            mode="lines",
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def darkpool_otc(
    input_limit: int = 1000,
    limit: int = 10,
    tier: str = "T1",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
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

        fig = plot_dark_pools_ats(df_ats, symbols, True)

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "prom",
            df_ats,
            sheet_name,
            fig,
        )
        return fig.show(external=external_axes)

    return console.print("[red]Could not get data[/red]\n")
