""" Fred View """
__docformat__ = "numpy"

import logging
import os
import textwrap
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.economy import fred_model
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

# pylint: disable=too-many-arguments


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
def notes(search_query: str, limit: int = 10):
    """Display series notes. [Source: FRED]

    Parameters
    ----------
    search_query : str
        Text query to search on fred series notes database
    limit : int
        Maximum number of series notes to display
    """
    df_search = fred_model.get_series_notes(search_query, limit)

    if df_search.empty:
        return

    print_rich_table(
        df_search[["id", "title", "notes"]],
        title=f"[bold]Search results for {search_query}[/bold]",
        show_index=False,
        headers=["Series ID", "Title", "Description"],
    )


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def display_fred_series(
    series_ids: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10,
    get_data: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]

    Parameters
    ----------
    series_ids : List[str]
        FRED Series ID from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3
    start_date : Optional[str]
        Starting date (YYYY-MM-DD) of data
    end_date : Optional[str]
        Ending date (YYYY-MM-DD) of data
    limit : int
        Number of data points to display.
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    data, detail = fred_model.get_aggregated_series_data(
        series_ids, start_date, end_date
    )

    if data.empty:
        logger.error("No data")
        console.print("[red]No data available.[/red]\n")
    else:
        # Try to get everything onto the same 0-10 scale.
        # To do so, think in scientific notation.  Divide the data by whatever the E would be
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return None

        for s_id, sub_dict in detail.items():
            data_to_plot, title = format_data_to_plot(data[s_id], sub_dict)

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

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "fred",
            data,
            sheet_name,
        )

    if get_data:
        return data, detail

    return None


def format_data_to_plot(data: pd.DataFrame, detail: dict) -> Tuple[pd.DataFrame, str]:
    """Helper to format data to plot"""

    data_to_plot = data.dropna()
    exponent = int(np.log10(data_to_plot.max()))
    data_to_plot /= 10**exponent
    multiplier = f"x {format_units(10**exponent)}" if exponent > 0 else ""
    title = f"{detail['title']} ({detail['units']}) {'['+multiplier+']' if multiplier else ''}"

    data_to_plot.index = pd.to_datetime(data_to_plot.index)

    return data_to_plot, title


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def display_yield_curve(
    date: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display yield curve based on US Treasury rates for a specified date.

    Parameters
    ----------
    date: str
        Date to get curve for. If None, gets most recent date (format yyyy-mm-dd)
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    rates, date_of_yield = fred_model.get_yield_curve(date, True)
    if rates.empty:
        console.print(f"[red]Yield data not found for {date_of_yield}.[/red]\n")
        return
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(rates["Maturity"], rates["Rate"], "-o")
    ax.set_xlabel("Maturity")
    ax.set_ylabel("Rate (%)")
    theme.style_primary_axis(ax)
    if external_axes is None:
        ax.set_title(f"US Yield Curve for {date_of_yield} ")
        theme.visualize_output()

    if raw:
        print_rich_table(
            rates,
            headers=list(rates.columns),
            show_index=False,
            title=f"United States Yield Curve for {date_of_yield}",
            floatfmt=".3f",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ycrv",
        rates,
        sheet_name,
    )
