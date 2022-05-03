""" Fred View """
__docformat__ = "numpy"

import logging
import os
import textwrap
from typing import Dict, Optional, List
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import fred_model
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def format_units(num: int) -> str:
    """Helper to format number into string with K,M,B,T.  Number will be in form of 10^n"""
    number_zeros = int(np.log10(num))
    if number_zeros < 3:
        return str(num)
    if number_zeros < 6:
        return f"{int(num/1000)}K"
    if number_zeros < 9:
        return f"{int(num/1_000_000)}M"
    if number_zeros < 12:
        return f"{int(num/1_000_000_000)}B"
    if number_zeros < 15:
        return f"{int(num/1_000_000_000_000)}T"
    return f"10^{number_zeros}"


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def notes(series_term: str, num: int) -> pd.DataFrame:
    """Print Series notes. [Source: FRED]

    Parameters
    ----------
    series_term : str
        Search for these series_term
    num : int
        Maximum number of series notes to display
    """
    df_search = fred_model.get_series_notes(series_term)

    if df_search.empty:
        return
    df_search["notes"] = df_search["notes"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=100)) if isinstance(x, str) else x
    )
    df_search["title"] = df_search["title"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=50)) if isinstance(x, str) else x
    )
    print_rich_table(
        df_search[["id", "title", "notes"]].head(num),
        title=f"[bold]Search results for {series_term}[/bold]",
        show_index=False,
        headers=["Series ID", "Title", "Description"],
    )
    console.print("")


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def display_fred_series(
    d_series: Dict[str, Dict[str, str]],
    start_date: str,
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    limit: int = 10,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]

    Parameters
    ----------
    d_series : str
        FRED Series ID from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3
    start_date : str
        Starting date (YYYY-MM-DD) of data
    end_date : str
        Ending date (YYYY-MM-DD) of data
    store : bool
        Whether to prevent plotting the data.
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    limit: int
        Number of raw data rows to show
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    series_ids = list(d_series.keys())
    data = fred_model.get_aggregated_series_data(d_series, start_date, end_date)

    if data.empty:
        logger.error("No data")
        console.print("[red]No data available.[/red]\n")
    else:
        # Try to get everything onto the same 0-10 scale.
        # To do so, think in scientific notation.  Divide the data by whatever the E would be
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        else:
            if len(external_axes) != 3:
                logger.error("Expected list of 3 axis items")
                console.print("[red]Expected list of 3 axis items.\n[/red]")
                return
            (ax,) = external_axes

        if len(series_ids) == 1:
            s_id = series_ids[0]
            sub_dict: Dict = d_series[s_id]
            title = f"{sub_dict['title']} ({sub_dict['units']})"
            ax.plot(data.index, data, label="\n".join(textwrap.wrap(title, 80)))
        else:
            for s_id, sub_dict in d_series.items():
                data_to_plot = data[s_id].dropna()
                exponent = int(np.log10(data_to_plot.max()))
                data_to_plot /= 10**exponent
                multiplier = f"x {format_units(10**exponent)}" if exponent > 0 else ""
                title = f"{sub_dict['title']} ({sub_dict['units']}) {'['+multiplier+']' if multiplier else ''}"
                ax.plot(
                    data_to_plot.index,
                    data_to_plot,
                    label="\n".join(textwrap.wrap(title, 80))
                    if len(series_ids) < 5
                    else title,
                )

        ax.legend(
            bbox_to_anchor=(0, 0.40, 1, -0.52),
            loc="upper right",
            mode="expand",
            borderaxespad=0,
            prop={"size": 9},
        )

        ax.set_xlim(data.index[0], data.index[-1])
        theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

        data.index = [x.strftime("%Y-%m-%d") for x in data.index]

        if raw:
            print_rich_table(
                data.tail(limit),
                headers=list(data.columns),
                show_index=True,
                index_name="Date",
            )
            console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "fred",
            data,
        )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def display_yield_curve(date: datetime, external_axes: Optional[List[plt.Axes]] = None):
    """Display yield curve based on US Treasury rates for a specified date.

    Parameters
    ----------
    date: datetime
        Date to get yield curve for
    external_axes: Optional[List[plt.Axes]]
        External axes to plot data on
    """
    rates, date_of_yield = fred_model.get_yield_curve(date)
    if rates.empty:
        console.print(
            f"[red]Yield data not found for {date.strftime('%Y-%m-%d')}[/red].\n"
        )
        return
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    else:
        if len(external_axes) != 1:
            logger.error("Expected list of 3 axis items")
            console.print("[red]Expected list of 3 axis items.\n[/red]")
            return
        (ax,) = external_axes

    ax.plot(rates.Maturity, rates.Rate, "-o")
    ax.set_xlabel("Maturity")
    ax.set_ylabel("Rate (%)")
    theme.style_primary_axis(ax)
    if external_axes is None:
        ax.set_title(f"US Yield Curve for {date_of_yield.strftime('%Y-%m-%d')} ")
        theme.visualize_output()
