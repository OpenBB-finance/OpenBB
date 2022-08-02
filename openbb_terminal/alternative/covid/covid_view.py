"""Covid View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.alternative.covid import covid_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_covid_ov(
    country,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Show historical cases and deaths by country

    Parameters
    ----------
    country: str
        Country to get data for
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    cases = covid_model.get_global_cases(country) / 1_000
    deaths = covid_model.get_global_deaths(country)
    ov = pd.concat([cases, deaths], axis=1)
    ov.columns = ["Cases", "Deaths"]

    # This plot has 2 axes
    if external_axes is None:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax2 = ax1.twinx()
    elif is_valid_axes_count(external_axes, 2):
        ax1, ax2 = external_axes
    else:
        return

    ax1.plot(cases.index, cases, color=theme.up_color, alpha=0.2)
    ax1.plot(cases.index, cases.rolling(7).mean(), color=theme.up_color)
    ax1.set_ylabel("Cases [1k]")
    theme.style_primary_axis(ax1)
    ax1.yaxis.set_label_position("left")

    ax2.plot(deaths.index, deaths, color=theme.down_color, alpha=0.2)
    ax2.plot(deaths.index, deaths.rolling(7).mean(), color=theme.down_color)
    ax2.set_title(f"Overview for {country.upper()}")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Deaths")
    theme.style_twin_axis(ax2)
    ax2.yaxis.set_label_position("right")

    ax1.set_xlim(ov.index[0], ov.index[-1])
    legend = ax2.legend(ov.columns)
    legend.legendHandles[1].set_color(theme.down_color)
    legend.legendHandles[0].set_color(theme.up_color)

    if external_axes is None:
        theme.visualize_output()

    if raw:
        ov.index = [x.strftime("%Y-%m-%d") for x in ov.index]
        print_rich_table(
            ov.tail(limit),
            headers=[x.title() for x in ov.columns],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID Numbers[/bold]",
        )

    if export:
        export_data(export, os.path.dirname(os.path.abspath(__file__)), "ov", ov)


@log_start_end(log=logger)
def display_covid_stat(
    country,
    stat: str = "cases",
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Show historical cases and deaths by country

    Parameters
    ----------
    country: str
        Country to get data for
    stat: str
        Statistic to get.  Either "cases", "deaths" or "rates"
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    console.print("")
    if stat == "cases":
        data = covid_model.get_global_cases(country) / 1_000
    elif stat == "deaths":
        data = covid_model.get_global_deaths(country)
    elif stat == "rates":
        cases = covid_model.get_global_cases(country)
        deaths = covid_model.get_global_deaths(country)
        data = (deaths / cases).fillna(0) * 100
    else:
        console.print("Invalid stat selected.\n")
        return

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    if stat == "cases":
        ax.set_ylabel(stat.title() + " [1k]")
        color = theme.up_color
    elif stat == "deaths":
        ax.set_ylabel(stat.title())
        color = theme.down_color
    else:
        ax.set_ylabel(stat.title() + " (Deaths/Cases)")
        color = theme.get_colors(reverse=True)[0]

    ax.plot(data.index, data, color=color, alpha=0.2)
    ax.plot(data.index, data.rolling(7).mean(), color=color)
    ax.set_title(f"{country} COVID {stat}")
    ax.set_xlim(data.index[0], data.index[-1])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    if raw:
        data.index = [x.strftime("%Y-%m-%d") for x in data.index]
        print_rich_table(
            data.tail(limit),
            headers=[stat.title()],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID {stat}[/bold]",
        )

    export_data(export, os.path.dirname(os.path.abspath(__file__)), stat, data)


@log_start_end(log=logger)
def display_country_slopes(
    days_back: int = 30,
    limit: int = 10,
    ascend: bool = False,
    threshold: int = 10000,
    export: str = "",
) -> None:
    """

    Parameters
    ----------
    days_back: int
        Number of historical days to get slope for
    limit: int
        Number to show in table
    ascend: bool
        Boolean to sort in ascending order
    threshold: int
        Threshold for total cases over period
    export : str
        Format to export data
    """
    hist_slope = covid_model.get_case_slopes(days_back, threshold).sort_values(
        by="Slope", ascending=ascend
    )
    print_rich_table(
        hist_slope.head(limit),
        show_index=True,
        index_name="Country",
        title=f"[bold]{('Highest','Lowest')[ascend]} Sloping Cases[/bold] (Cases/Day)",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"slopes_{days_back}day",
        hist_slope,
    )
