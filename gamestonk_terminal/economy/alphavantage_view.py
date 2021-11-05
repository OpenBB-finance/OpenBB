""" Alpha Vantage View """
__docformat__ = "numpy"

import os

import matplotlib.pyplot as plt
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import alphavantage_model
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal import config_plot as cfp


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
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_rtp.to_frame(),
                    showindex=True,
                    headers=["Sector", "Real-Time Performance"],
                    floatfmt=".5f",
                    tablefmt="fancy_grid",
                )
            )
        else:
            print(df_rtp.to_string())

    else:
        df_rtp.plot(kind="bar")
        plt.title("Real Time Performance (%) per Sector")
        plt.tight_layout()
        plt.grid()

    print("")

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
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    gdp.head(20),
                    headers=["Date", "GDP"],
                    tablefmt="fancy_grid",
                    showindex=False,
                )
            )
        else:
            print(gdp.head(20).to_string())
    print("")


def display_gdp_capita(start_year: int = 2010, raw: bool = False, export: str = ""):
    """Display US GDP per Capita from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    """
    gdp_capita = alphavantage_model.get_gdp_capita()
    gdp = gdp_capita[gdp_capita.date >= f"{start_year}-01-01"]
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    ax.plot(gdp.date, gdp.GDP, marker="o", c="dodgerblue")
    ax.set_xlabel("Date")
    ax.set_title(f"US GDP per Capita (Chained 2012 USD) from {start_year}")
    ax.set_ylabel("US GDP (Chained 2012 USD)  ")
    ax.grid("on")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdpc",
        gdp_capita,
    )
    if raw:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    gdp.head(20),
                    headers=["Date", "GDP"],
                    tablefmt="fancy_grid",
                    showindex=False,
                )
            )
        else:
            print(gdp.head(20).to_string())
    print("")
