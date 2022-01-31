"""Covid View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

import gamestonk_terminal.feature_flags as gtff
from gamestonk_terminal.alternative.covid import covid_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_covid_ov(
    country, raw: bool = False, limit: int = 10, export: str = ""
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
    """
    console.print("")
    cases = covid_model.get_global_cases(country) / 1_000
    deaths = covid_model.get_global_deaths(country)
    ov = pd.concat([cases, deaths], axis=1)
    ov.columns = ["Cases", "Deaths"]

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(cases.index, cases, alpha=0.2, c="b")
    ax.plot(cases.index, cases.rolling(7).mean(), lw=4, c="b")
    ax.set_ylabel("Cases (1k)", color="blue")
    ax.tick_params(axis="y", labelcolor="blue")

    ax2 = ax.twinx()
    ax2.plot(deaths.index, deaths, "r", alpha=0.2)
    ax2.plot(deaths.index, deaths.rolling(7).mean(), "r", lw=4)
    ax2.grid()
    ax2.set_title(f"Overview for {country.upper()}")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Deaths", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    dateFmt = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(dateFmt)
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xlim(ov.index[0], ov.index[-1])

    fig.tight_layout(pad=2)
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    if raw:
        ov.index = [x.strftime("%Y-%m-%d") for x in ov.index]
        print_rich_table(
            ov.tail(limit),
            headers=[x.title() for x in ov.columns],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID Numbers[/bold]",
        )

        console.print("")

    if export:
        export_data(export, os.path.dirname(os.path.abspath(__file__)), "ov", ov)


@log_start_end(log=logger)
def display_covid_stat(
    country, stat: str = "cases", raw: bool = False, limit: int = 10, export: str = ""
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

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(data.index, data, alpha=0.2, c="b")
    ax.plot(data.index, data.rolling(7).mean(), lw=4, c="b")
    if stat == "cases":
        ax.set_ylabel(stat.title() + " (1k)", color="blue")
    else:
        ax.set_ylabel(stat.title(), color="blue")
    ax.tick_params(axis="y", labelcolor="blue")
    ax.grid("on")
    dateFmt = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(dateFmt)
    ax.tick_params(axis="x", labelrotation=45)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_title(f"{country} COVID {stat}")
    ax.set_xlim(data.index[0], data.index[-1])
    fig.tight_layout(pad=2)
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    if raw:
        data.index = [x.strftime("%Y-%m-%d") for x in data.index]
        print_rich_table(
            data.tail(limit),
            headers=[stat.title()],
            show_index=True,
            index_name="Date",
            title=f"[bold]{country} COVID {stat}[/bold]",
        )

        console.print("")

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
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"slopes_{days_back}day",
        hist_slope,
    )
