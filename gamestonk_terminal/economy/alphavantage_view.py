""" Alpha Vantage View """
__docformat__ = "numpy"

from typing import List, Optional
import logging
import os

import matplotlib.pyplot as plt

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import alphavantage_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def realtime_performance_sector(raw: bool, export: str):
    """Display Real-Time Performance sector. [Source: AlphaVantage]

    Parameters
    ----------
    raw : bool
        Output only raw data
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_sectors = alphavantage_model.get_sector_data()

    # pylint: disable=invalid-sequence-index
    df_rtp = df_sectors["Rank A: Real-Time Performance"]

    if raw:
        print_rich_table(
            df_rtp.to_frame(),
            show_index=True,
            headers=["Sector", "Real-Time Performance"],
            title="Real-Time Performance",
        )

    else:
        # TODO: convert to mpl
        df_rtp.plot(kind="bar")
        plt.title("Real Time Performance (%) per Sector")
        plt.tight_layout()
        plt.grid()

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rtps",
        df_sectors,
    )

    if not raw:
        if gtff.USE_ION:
            plt.ion()
        plt.show()


@log_start_end(log=logger)
def display_real_gdp(
    interval: str, start_year: int = 2010, raw: bool = False, export: str = ""
):
    """Display US GDP from AlphaVantage

    Parameters
    ----------
    interval : str
        Interval for GDP.  Either "a" or "q"
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    """
    gdp_full = alphavantage_model.get_real_gdp(interval)
    if gdp_full.empty:
        console.print("Error getting data.  Check API Key")
        return
    gdp = gdp_full[gdp_full.date >= f"{start_year}-01-01"]
    int_string = "Annual" if interval == "a" else "Quarterly"
    year_str = str(start_year) if interval == "a" else str(list(gdp.date)[-1].year)
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    ax.plot(gdp.date, gdp.GDP, marker="o", c="dodgerblue")
    ax.set_xlabel("Date")
    ax.set_title(f"{int_string} US GDP ($B) from {year_str}")
    ax.set_ylabel("US GDP ($B) ")
    ax.grid("on")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdp",
        gdp_full,
    )
    if raw:
        print_rich_table(
            gdp.head(20), headers=["Date", "GDP"], show_index=False, title="US GDP"
        )
    console.print("")


@log_start_end(log=logger)
def display_gdp_capita(
    start_year: int = 2010,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display US GDP per Capita from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    gdp_capita = alphavantage_model.get_gdp_capita()
    if gdp_capita.empty:
        console.print("Error getting data.  Check API Key")
        return
    gdp = gdp_capita[gdp_capita.date >= f"{start_year}-01-01"]

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(gdp.date, gdp.GDP, marker="o")
    ax.set_title(f"US GDP per Capita (Chained 2012 USD) from {start_year}")
    ax.set_ylabel("US GDP (Chained 2012 USD)  ")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdpc",
        gdp_capita,
    )
    if raw:
        print_rich_table(
            gdp.head(20),
            headers=["Date", "GDP"],
            show_index=False,
            title="US GDP Per Capita",
        )
        console.print("")


@log_start_end(log=logger)
def display_inflation(start_year: int = 2010, raw: bool = False, export: str = ""):
    """Display US Inflation from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    """
    inflation = alphavantage_model.get_inflation()
    if inflation.empty:
        console.print("Error getting data.  Check API Key")
        return
    inf = inflation[inflation.date >= f"{start_year}-01-01"]
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    ax.plot(inf.date, inf.Inflation, marker="o", c="dodgerblue")
    ax.set_xlabel("Date")
    ax.set_title(f"US Inflation from {list(inf.date)[-1].year}")
    ax.set_ylabel("Inflation (%)")
    ax.grid("on")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "inf",
        inflation,
    )
    if raw:
        print_rich_table(
            inf.head(20),
            headers=["Date", "Inflation"],
            show_index=False,
            title="US Inflation",
        )
    console.print("")


@log_start_end(log=logger)
def display_cpi(
    interval: str, start_year: int = 2010, raw: bool = False, export: str = ""
):
    """Display US consumer price index (CPI) from AlphaVantage

    Parameters
    ----------
    interval : str
        Interval for GDP.  Either "m" or "s"
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    """
    cpi_full = alphavantage_model.get_cpi(interval)
    if cpi_full.empty:
        console.print("Error getting data.  Check API Key")
        return
    cpi = cpi_full[cpi_full.date >= f"{start_year}-01-01"]
    int_string = "Semi-Annual" if interval == "s" else "Monthly"
    year_str = str(list(cpi.date)[-1].year)
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    ax.plot(cpi.date, cpi.CPI, marker="o", c="dodgerblue")
    ax.set_xlabel("Date")
    ax.set_title(f"{int_string} Consumer Price Index from {year_str}")
    ax.set_ylabel("CPI ")
    ax.grid("on")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpi",
        cpi_full,
    )
    if raw:
        print_rich_table(
            cpi.head(20), headers=["Date", "CPI"], show_index=False, title="US CPI"
        )
    console.print("")


@log_start_end(log=logger)
def display_treasury_yield(
    interval: str, maturity: str, start_date: str, raw: bool = False, export: str = ""
):
    """Display historical treasury yield for given maturity

    Parameters
    ----------
    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y"
    start_date: str
        Start date for data.  Should be in YYYY-MM-DD format
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format to export data, by default ""
    """
    d_maturity = {"3m": "3month", "5y": "5year", "10y": "10year", "30y": "30year"}
    yields = alphavantage_model.get_treasury_yield(interval, maturity)
    if yields.empty:
        console.print("Error getting data.  Check API Key")
        return
    yld = yields[yields.date >= start_date]
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    ax.plot(yld.date, yld.Yield, marker="o", c="dodgerblue")
    ax.set_xlabel("Date")
    ax.set_title(f"{d_maturity[maturity]} Treasury Yield")
    ax.set_ylabel("Yield")
    ax.grid("on")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tyld",
        yields,
    )
    if raw:
        print_rich_table(
            yld.head(20),
            headers=["Date", "Yield"],
            title="Historical Treasurey Yield",
            show_index=False,
        )
    console.print("")


@log_start_end(log=logger)
def display_unemployment(start_year: int = 2015, raw: bool = False, export: str = ""):
    """Display US unemployment AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    """

    unemp = alphavantage_model.get_unemployment()

    if unemp.empty:
        console.print("Error getting data.  Check API Key")
        return

    un = unemp[unemp.date >= f"{start_year}-01-01"]

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    ax.plot(un.date, un.unemp, marker="o", c="dodgerblue")
    ax.set_xlabel("Date")
    ax.set_title(f"US Unemployment from {start_year}")
    ax.set_ylabel("US Unemployment  ")
    ax.grid("on")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "unemp",
        unemp,
    )

    if raw:
        print_rich_table(
            un.head(20),
            headers=["Date", "GDP"],
            title="US Unemployment",
            show_index=False,
        )

    console.print("")
