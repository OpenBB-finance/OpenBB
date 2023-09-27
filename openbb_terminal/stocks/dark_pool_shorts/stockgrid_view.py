""" Stockgrid View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import stockgrid_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def dark_pool_short_positions(
    limit: int = 10,
    sortby: str = "dpp_dollar",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Get dark pool short positions. [Source: Stockgrid]

    Parameters
    ----------
    limit : int
        Number of top tickers to show
    sortby : str
        Field for which to sort by, where 'sv': Short Vol. [1M],
        'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],
        'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],
        'dpp_dollar': DP Position ($1B)
    ascend : bool
        Data in ascending order
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = stockgrid_model.get_dark_pool_short_positions(sortby, ascend)

    dp_date = df["Date"].values[0]
    df = df.drop(columns=["Date"])

    df["Net Short Volume $"] = df["Net Short Volume $"] / 100_000_000
    df["Short Volume"] = df["Short Volume"] / 1_000_000
    df["Net Short Volume"] = df["Net Short Volume"] / 1_000_000
    df["Short Volume %"] = df["Short Volume %"] * 100
    df["Dark Pools Position $"] = df["Dark Pools Position $"] / (1_000_000_000)
    df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000
    df.columns = [
        "Ticker",
        "Short Vol. [1M]",
        "Short Vol. %",
        "Net Short Vol. [1M]",
        "Net Short Vol. ($100M)",
        "DP Position [1M]",
        "DP Position ($1B)",
    ]

    # Assuming that the datetime is the same, which from my experiments seems to be the case
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dppos",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def short_interest_days_to_cover(
    limit: int = 10,
    sortby: str = "float",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Print short interest and days to cover. [Source: Stockgrid]

    Parameters
    ----------
    limit : int
        Number of top tickers to show
    sortby : str
        Field for which to sort by, where 'float': Float Short %%,
        'dtc': Days to Cover, 'si': Short Interest
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = stockgrid_model.get_short_interest_days_to_cover(sortby)

    dp_date = df["Date"].values[0]
    df = df.drop(columns=["Date"])

    # Assuming that the datetime is the same, which from my experiments seems to be the case
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortdtc",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def short_interest_volume(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plot price vs short interest volume. [Source: Stockgrid]

    Parameters
    ----------
    symbol : str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    """

    df, prices = stockgrid_model.get_short_interest_volume(symbol)
    if df.empty:
        return console.print("[red]No data available[/red]\n")

    if raw:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "shortint(stockgrid)",
            df,
            sheet_name,
        )

        df.date = df.date.dt.date
        return print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Price vs Short Volume",
            export=bool(export),
            limit=limit,
        )

    fig = OpenBBFigure.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        horizontal_spacing=0,
        row_width=[0.3, 0.6],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    )
    fig.set_title(f"Price vs Short Volume Interest for {symbol}")

    # pycodestyle: disable=E501,E203
    fig.add_scatter(
        name=symbol,
        x=df["date"],
        y=prices[len(prices) - len(df) :],  # pycodestyle: disable=E501,E203
        line=dict(color="#fdc708", width=2),
        connectgaps=True,
        yaxis="y2",
        opacity=1,
        showlegend=False,
        row=1,
        col=1,
        secondary_y=True,
    )
    fig.add_bar(
        x=df["date"],
        y=df["Total Vol. [1M]"],
        name="Total Volume",
        marker_color=theme.up_color,
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_bar(
        x=df["date"],
        y=df["Short Vol. [1M]"],
        name="Short Volume",
        marker_color=theme.down_color,
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_scatter(
        name="Short Vol. %",
        x=df["date"],
        y=df["Short Vol. %"],
        line=dict(width=2),
        connectgaps=True,
        opacity=1,
        showlegend=False,
        row=2,
        col=1,
        secondary_y=False,
    )

    fig.update_traces(hovertemplate="%{y:.2f}")
    fig.update_layout(
        margin=dict(t=30),
        yaxis2_title="Stock Price ($)",
        yaxis_title="FINRA Volume [M]",
        yaxis3_title="Short Vol. %",
        yaxis=dict(
            side="left",
            fixedrange=False,
            showgrid=False,
            nticks=15,
            layer="above traces",
        ),
        yaxis2=dict(
            side="right",
            fixedrange=False,
            anchor="x",
            overlaying="y",
            nticks=10,
            layer="below traces",
            title_standoff=10,
        ),
        yaxis3=dict(
            fixedrange=False,
            nticks=10,
        ),
        hovermode="x unified",
        spikedistance=1,
        hoverdistance=1,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortint(stockgrid)",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def net_short_position(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plot net short position. [Source: Stockgrid]

    Parameters
    ----------
    symbol: str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    """

    df = stockgrid_model.get_net_short_position(symbol)
    if df.empty:
        return console.print("[red]No data available[/red]\n")

    if raw:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "shortpos",
            df,
            sheet_name,
        )

        df["dates"] = df["dates"].dt.date

        return print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Net Short Positions",
            export=bool(export),
            limit=limit,
        )

    df = df.sort_values(by=["dates"])

    fig = OpenBBFigure.create_subplots(
        rows=1,
        cols=1,
        shared_xaxes=True,
        specs=[[{"secondary_y": True}]],
    )
    fig.set_title(f"Net Short Vol. vs Position for {symbol}")

    fig.add_bar(
        x=df["dates"],
        y=df["Net Short Vol. (1k $)"],
        name="Net Short Vol. (1k $)",
        marker_color=theme.down_color,
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_scatter(
        name="Position (1M $)",
        x=df["dates"],
        y=df["Position (1M $)"],
        connectgaps=True,
        marker_color=theme.up_color,
        row=1,
        col=1,
        secondary_y=True,
        yaxis="y2",
    )
    fig.update_traces(hovertemplate="%{y:.2f}")
    fig.update_layout(
        margin=dict(l=40),
        yaxis2_title="Net Short Vol. (1k $)",
        yaxis_title="Position (1M $)",
        yaxis=dict(
            side="left",
            fixedrange=False,
            showgrid=False,
            nticks=15,
            layer="above traces",
        ),
        yaxis2=dict(
            side="right",
            fixedrange=False,
            anchor="x",
            overlaying="y",
            nticks=10,
            layer="below traces",
            title_standoff=10,
        ),
        hovermode="x unified",
        spikedistance=1,
        hoverdistance=1,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortpos",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
