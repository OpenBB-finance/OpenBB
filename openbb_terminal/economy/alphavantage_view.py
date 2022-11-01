""" Alpha Vantage View """
__docformat__ = "numpy"

from typing import List, Optional
import logging
import os

import matplotlib
import matplotlib.pyplot as plt
from openbb_terminal.decorators import check_api_key
from openbb_terminal.config_terminal import theme
from openbb_terminal import config_plot as cfp
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import alphavantage_model
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def realtime_performance_sector(
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display Real-Time Performance sector. [Source: AlphaVantage]

    Parameters
    ----------
    raw : bool
        Output only raw data
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_rtp = alphavantage_model.get_sector_data()

    # pylint: disable=E1101
    if df_rtp.empty:
        return

    if raw:
        print_rich_table(
            df_rtp,
            show_index=False,
            headers=df_rtp.columns,
            title="Real-Time Performance",
        )

    else:

        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        df_rtp.set_index("Sector", inplace=True)
        df_rtp = df_rtp.squeeze(axis=1)
        colors = [theme.up_color if x > 0 else theme.down_color for x in df_rtp.values]
        df_rtp.plot(kind="barh", color=colors, ax=ax)
        theme.style_primary_axis(ax)
        ax.set_title("Real Time Performance (%) per Sector")
        ax.tick_params(axis="x", labelrotation=90)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.2f"))

        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rtps",
        df_rtp,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_real_gdp(
    interval: str = "q",
    start_year: int = 2010,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display US GDP from AlphaVantage

    Parameters
    ----------
    interval : str
        Interval for GDP.  Either "a" or "q", by default "q"
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    gdp = alphavantage_model.get_real_gdp(interval, start_year)

    if gdp.empty:
        return

    int_string = "Annual" if interval == "a" else "Quarterly"
    year_str = str(start_year) if interval == "a" else str(list(gdp["date"])[-1].year)

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(gdp["date"], gdp["GDP"], marker="o")
    ax.set_title(f"{int_string} US GDP ($B) from {year_str}")
    ax.set_ylabel("US GDP ($B) ")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdp",
        gdp,
    )
    if raw:
        print_rich_table(
            gdp.head(20), headers=["Date", "GDP"], show_index=False, title="US GDP"
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
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
    gdp = alphavantage_model.get_gdp_capita(start_year)
    if gdp.empty:
        console.print("Error getting data.  Check API Key")
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(gdp["date"], gdp["GDP"], marker="o")
    ax.set_title(f"US GDP per Capita (Chained 2012 USD) from {start_year}")
    ax.set_ylabel("US GDP (Chained 2012 USD) ")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdpc",
        gdp,
    )
    if raw:
        print_rich_table(
            gdp.head(20),
            headers=["Date", "GDP"],
            show_index=False,
            title="US GDP Per Capita",
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_inflation(
    start_year: int = 2010,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display US Inflation from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    inf = alphavantage_model.get_inflation(start_year)
    if inf.empty:
        console.print("Error getting data.  Check API Key")
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(inf["date"], inf["Inflation"], marker="o")
    ax.set_title(f"US Inflation from {list(inf['date'])[-1].year}")
    ax.set_ylabel("Inflation (%)")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "inf",
        inf,
    )
    if raw:
        print_rich_table(
            inf.head(20),
            headers=["Date", "Inflation"],
            show_index=False,
            title="US Inflation",
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_cpi(
    interval: str = "m",
    start_year: int = 2010,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    cpi = alphavantage_model.get_cpi(interval, start_year)
    if cpi.empty:
        console.print("Error getting data.  Check API Key")
        return

    int_string = "Semi-Annual" if interval == "s" else "Monthly"
    year_str = str(list(cpi["date"])[-1].year)

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(cpi["date"], cpi["CPI"], marker="o")
    ax.set_title(f"{int_string} Consumer Price Index from {year_str}")
    ax.set_ylabel("CPI")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpi",
        cpi,
    )
    if raw:
        print_rich_table(
            cpi.head(20), headers=["Date", "CPI"], show_index=False, title="US CPI"
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_treasury_yield(
    interval: str = "m",
    maturity: str = "10y",
    start_date: str = "2010-01-01",
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical treasury yield for given maturity

    Parameters
    ----------
    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"
    start_date: str
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    d_maturity = {"3m": "3month", "5y": "5year", "10y": "10year", "30y": "30year"}
    yld = alphavantage_model.get_treasury_yield(interval, maturity, start_date)
    if yld.empty:
        console.print("Error getting data.  Check API Key")
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(yld["date"], yld["Yield"], marker="o")
    ax.set_title(f"{d_maturity[maturity]} Treasury Yield")
    ax.set_ylabel("Yield (%)")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "tyld",
        yld,
    )
    if raw:
        print_rich_table(
            yld.head(20),
            headers=["Date", "Yield"],
            title="Historical Treasury Yield",
            show_index=False,
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_unemployment(
    start_year: int = 2010,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display US unemployment AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    un = alphavantage_model.get_unemployment(start_year)

    if un.empty:
        console.print("Error getting data. Check API Key")
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(un["date"], un["unemp"], marker="o")
    ax.set_title(f"US Unemployment from {start_year}")
    ax.set_ylabel("US Unemployment (%)")
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "unemp",
        un,
    )

    if raw:
        print_rich_table(
            un.head(20),
            headers=["Date", "GDP"],
            title="US Unemployment",
            show_index=False,
        )
