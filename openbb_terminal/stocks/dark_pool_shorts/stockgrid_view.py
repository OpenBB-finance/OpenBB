""" Stockgrid View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.qt_app.config.openbb_styles import PLT_COLORWAY, PLT_FONT
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import stockgrid_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def dark_pool_short_positions(
    limit: int = 10, sortby: str = "dpp_dollar", ascend: bool = False, export: str = ""
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
        df.iloc[:limit],
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
    )

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dppos", df)


@log_start_end(log=logger)
def short_interest_days_to_cover(
    limit: int = 10, sortby: str = "float", export: str = ""
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
        df.iloc[:limit],
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
    )

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "shortdtc", df)


@log_start_end(log=logger)
def short_interest_volume(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None

    """
    del external_axes

    df, prices = stockgrid_model.get_short_interest_volume(symbol)
    if df.empty:
        console.print("[red]No data available[/red]\n")
        return

    if raw:
        df.date = df.date.dt.date

        print_rich_table(
            df.iloc[:limit],
            headers=list(df.columns),
            show_index=False,
            title="Price vs Short Volume",
        )
    else:
        # Output data
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            horizontal_spacing=0,
            row_width=[0.3, 0.6],
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
        )
        # pycodestyle: disable=E501,E203
        fig.add_trace(
            go.Scatter(
                name=symbol,
                x=df["date"].values,
                y=prices[len(prices) - len(df) :],  # pycodestyle: disable=E501,E203
                line=dict(color="#fdc708", width=2),
                opacity=1,
                showlegend=False,
            ),
            row=1,
            col=1,
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                x=df["date"], y=df["Total Vol. [1M]"], name="Total Volume", yaxis="y2"
            ),
            row=1,
            col=1,
            secondary_y=True,
        )
        fig.add_trace(
            go.Bar(
                x=df["date"], y=df["Short Vol. [1M]"], name="Short Volume", yaxis="y2"
            ),
            row=1,
            col=1,
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                name="Short Vol. %",
                x=df["date"].values,
                y=df["Short Vol. %"],
                line=dict(width=2),
                opacity=1,
                showlegend=False,
            ),
            row=2,
            col=1,
            secondary_y=False,
        )

        fig.update_traces(hovertemplate="%{y:.2f}")
        fig.update_layout(
            margin=dict(l=10, r=0, t=60, b=50),
            template="plotly_dark",
            colorway=PLT_COLORWAY,
            title=f"<b>Price vs Short Volume Interest for {symbol}</b>",
            title_x=0.025,
            title_font_size=14,
            yaxis_title="Stock Price ($)",
            yaxis2_title="FINRA Volume [M]",
            yaxis3_title="Short Vol. %",
            font=PLT_FONT,
            yaxis=dict(
                side="right",
                fixedrange=False,
                showgrid=False,
                titlefont=dict(color="#fdc708"),
                tickfont=dict(color="#fdc708"),
                nticks=20,
            ),
            yaxis2=dict(
                side="left",
                fixedrange=False,
                anchor="x",
                overlaying="y",
                titlefont=dict(color="#d81aea"),
                tickfont=dict(color="#d81aea"),
                nticks=20,
            ),
            yaxis3=dict(
                fixedrange=False,
                titlefont=dict(color="#9467bd"),
                tickfont=dict(color="#9467bd"),
                nticks=20,
            ),
            xaxis=dict(rangeslider=dict(visible=False), type="date"),
            dragmode="pan",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=14, family="Fire Code"),
                bgcolor="rgba(0, 0, 0, 0)",
            ),
            hovermode="x unified",
            spikedistance=1,
            hoverdistance=1,
        )
        dt_unique_days = pd.bdate_range(
            start=df["date"].iloc[-1], end=df["date"].iloc[0]
        )
        dt_unique = [d.strftime("%Y-%m-%d") for d in df["date"].tolist()]
        mkt_holidays = [
            d
            for d in dt_unique_days.strftime("%Y-%m-%d").tolist()
            if d not in dt_unique
        ]
        fig.update_xaxes(
            rangebreaks=[dict(bounds=["sat", "mon"]), dict(values=mkt_holidays)]
        )
        fig.show()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "shortint(stockgrid)", df
    )


@log_start_end(log=logger)
def net_short_position(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None

    """

    df = stockgrid_model.get_net_short_position(symbol)
    if df.empty:
        console.print("[red]No data available[/red]\n")
        return

    if raw:

        df["dates"] = df["dates"].dt.date

        print_rich_table(
            df.iloc[:limit],
            headers=list(df.columns),
            show_index=False,
            title="Net Short Positions",
        )

    else:

        # This plot has 2 axes
        if not external_axes:
            _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax2 = ax1.twinx()
        elif is_valid_axes_count(external_axes, 2):
            (ax1, ax2) = external_axes
        else:
            return

        df = df.sort_values(by=["dates"])
        ax1.bar(
            df["dates"],
            df["Net Short Vol. (1k $)"],
            color=theme.down_color,
            label="Net Short Vol. (1k $)",
        )
        ax1.set_ylabel("Net Short Vol. (1k $)")

        ax2.plot(
            df["dates"].values,
            df["Position (1M $)"],
            c=theme.up_color,
            label="Position (1M $)",
        )
        ax2.set_ylabel("Position (1M $)")

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax1.set_xlim(
            df["dates"].values[max(0, len(df) - limit)], df["dates"].values[len(df) - 1]
        )

        ax1.set_title(f"Net Short Vol. vs Position for {symbol}")

        theme.style_twin_axes(ax1, ax2)

        if not external_axes:
            theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "shortpos", df)
