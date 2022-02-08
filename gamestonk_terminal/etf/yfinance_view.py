"""Yahoo Finance view"""
__docformat__ = "numpy"

from typing import Optional, List
import logging
import os

import pandas as pd
from matplotlib import pyplot as plt
import mplfinance as mpf

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
from gamestonk_terminal.stocks import stocks_helper

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


@log_start_end(log=logger)
def display_candle(
    etf_name: str,
    etf_data: pd.DataFrame,
    export: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display ETF candle. [Source: Yahoo Finance]

    Parameters
    ----------
    etf_name: str
        ETF name
    etf_data: pd.DataFrame
        The ETF's dataframe
    export: str
        Where to export to
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis are expected in the list), by default None
    """
    if etf_name:
        data = stocks_helper.process_candle(etf_data)
        df_etf = stocks_helper.find_trendline(data, "OC_High", "high")
        df_etf = stocks_helper.find_trendline(data, "OC_Low", "low")

        ap0 = []

        if "OC_High_trend" in df_etf.columns:
            ap0.append(
                mpf.make_addplot(df_etf["OC_High_trend"], color="g"),
            )

        if "OC_Low_trend" in df_etf.columns:
            ap0.append(
                mpf.make_addplot(df_etf["OC_Low_trend"], color="b"),
            )

        candle_chart_kwargs = {
            "type": "candle",
            "style": theme.mpf_style,  # mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=True)
            "mav": (20, 50),
            "volume": True,
            "xrotation": theme.xticks_rotation,
            "update_width_config": {
                "candle_linewidth": 1.0,
                "candle_width": 0.8,
                "volume_linewidth": 1.0,
                "volume_width": 0.8,
            },
            "title": f"\nETF: {etf_name}",
            "addplot": ap0,
        }

        # This plot has 2 axes
        if not external_axes:
            candle_chart_kwargs["returnfig"] = True
            candle_chart_kwargs["figratio"] = (10, 7)
            candle_chart_kwargs["figscale"] = 1.10
            candle_chart_kwargs["figsize"] = plot_autoscale()
            _, _ = mpf.plot(data, **candle_chart_kwargs)
            theme.visualize_output(force_tight_layout=False)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of 1 axis items./n[/red]")
                return
            (ax1,) = external_axes
            candle_chart_kwargs["ax"] = ax1
            mpf.plot(data, **candle_chart_kwargs)

        export_data(
            export,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "candle"),
            f"{etf_name}",
            etf_data,
        )

    else:
        console.print("No ticker loaded. First use `load {ticker}`\n")
