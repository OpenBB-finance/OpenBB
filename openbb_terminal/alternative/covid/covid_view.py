"""Covid View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.alternative.covid import covid_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_covid_ov(
    country: str,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots historical cases and deaths by country.

    Parameters
    ----------
    country: str
        Country to plot
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot
    """
    cases = covid_model.get_global_cases(country) / 1_000
    deaths = covid_model.get_global_deaths(country)
    if cases.empty or deaths.empty:
        return
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


def plot_covid_stat(
    country: str,
    stat: str = "cases",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots historical stat by country.

    Parameters
    ----------
    country: str
        Country to plot
    external_axis: Optional[List[plt.Axes]]
        List of external axes to include in plot
    """
    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    if stat == "cases":
        data = covid_model.get_global_cases(country) / 1_000
        ax.set_ylabel(stat.title() + " [1k]")
        color = theme.up_color
    elif stat == "deaths":
        data = covid_model.get_global_deaths(country)
        ax.set_ylabel(stat.title())
        color = theme.down_color
    elif stat == "rates":
        cases = covid_model.get_global_cases(country)
        deaths = covid_model.get_global_deaths(country)
        data = (deaths / cases).fillna(0) * 100
        ax.set_ylabel(stat.title() + " (Deaths/Cases)")
        color = theme.get_colors(reverse=True)[0]
    else:
        console.print("Invalid stat selected.\n")
        return

    ax.plot(data.index, data, color=color, alpha=0.2)
    ax.plot(data.index, data.rolling(7).mean(), color=color)
    ax.set_title(f"{country} COVID {stat}")
    ax.set_xlim(data.index[0], data.index[-1])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_covid_ov(
    country: str,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    plot: bool = True,
) -> None:
    """Prints table showing historical cases and deaths by country.

    Parameters
    ----------
    country: str
        Country to get data for
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    plot: bool
        Flag to display historical plot
    """
    if country.lower() == "us":
        country = "US"
    if plot:
        plot_covid_ov(country)
    if raw:
        data = covid_model.get_covid_ov(country, limit)
        print_rich_table(
            data,
            headers=[x.title() for x in data.columns],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID Numbers[/bold]",
        )

    if export:
        data = covid_model.get_covid_ov(country, limit)
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "ov",
            data,
            sheet_name,
        )


@log_start_end(log=logger)
def display_covid_stat(
    country: str,
    stat: str = "cases",
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    plot: bool = True,
) -> None:
    """Prints table showing historical cases and deaths by country.

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
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    plot : bool
        Flag to plot data
    """
    data = covid_model.get_covid_stat(country, stat, limit)
    if plot:
        plot_covid_stat(country, stat)

    if raw:
        print_rich_table(
            data,
            headers=[stat.title()],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID {stat}[/bold]",
        )
    if export:
        data["date"] = data.index
        data = data.reset_index(drop=True)
        # make sure date is first column in export
        cols = data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        data = data[cols]
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            stat,
            data,
            sheet_name,
        )


@log_start_end(log=logger)
def display_case_slopes(
    days_back: int = 30,
    limit: int = 10,
    threshold: int = 10000,
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing countries with the highest case slopes.

    Parameters
    ----------
    days_back: int
        Number of historical days to get slope for
    limit: int
        Number to show in table
    ascend: bool
        Flag to sort in ascending order
    threshold: int
        Threshold for total cases over period
    export : str
        Format to export data
    """
    data = covid_model.get_case_slopes(days_back, limit, threshold, ascend)

    print_rich_table(
        data,
        show_index=True,
        index_name="Country",
        title=f"[bold]{('Highest','Lowest')[ascend]} Sloping Cases[/bold] (Cases/Day)",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"slopes_{days_back}day",
        data,
        sheet_name,
    )
