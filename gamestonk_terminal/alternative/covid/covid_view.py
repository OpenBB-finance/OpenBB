import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from rich.console import Console

import gamestonk_terminal.feature_flags as gtff
from gamestonk_terminal.alternative.covid import covid_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale

t_console = Console()


def display_covid_ov(country, raw: bool = False, export: str = ""):
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
    t_console.print("")
    if raw and export:
        t_console.print("In porgress")
    cases = covid_model.get_global_cases(country)
    deaths = covid_model.get_global_deaths(country)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    ax.plot(cases.index, cases, alpha=0.2, c="b")
    ax.plot(cases.index, cases.rolling(7).mean(), lw=4, c="b")
    ax.set_ylabel("Cases", color="blue")
    ax.tick_params(axis="y", labelcolor="blue")
    ax2 = ax.twinx()
    ax2.plot(deaths.index, deaths, "r", alpha=0.2)
    ax2.plot(deaths.index, deaths.rolling(7).mean(), "r", lw=4)

    ax2.grid()
    ax2.set_title(f"Cases for {country.upper()}")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Deaths", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    dateFmt = mdates.DateFormatter("%m/%d/%Y")
    ax.xaxis.set_major_formatter(dateFmt)
    ax.tick_params(axis="x", labelrotation=45)
    fig.tight_layout(pad=2)
    if gtff.USE_ION:
        plt.ion()

    plt.show()
