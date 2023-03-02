""" Fred View """
__docformat__ = "numpy"

import logging
import os
import textwrap
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.economy import fred_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


# pylint: disable=too-many-arguments,inconsistent-return-statements


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
    external_axes: bool = False,
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    data, detail = fred_model.get_aggregated_series_data(
        series_ids, start_date, end_date
    )

    if data.empty:
        logger.error("No data")
        return console.print("[red]No data available.[/red]\n")

    # Try to get everything onto the same 0-10 scale.
    # To do so, think in scientific notation.  Divide the data by whatever the E would be

    fig = OpenBBFigure()
    for s_id, sub_dict in detail.items():
        data_to_plot, title = format_data_to_plot(data[s_id], sub_dict)

        fig.add_scatter(
            x=data_to_plot.index,
            y=data_to_plot,
            name="\n".join(textwrap.wrap(title, 80)) if len(series_ids) < 5 else title,
        )

    data.index = [x.strftime("%Y-%m-%d") for x in data.index]

    if raw:
        print_rich_table(
            data.tail(limit),
            headers=list(data.columns),
            show_index=True,
            index_name="Date",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fred",
        data,
        sheet_name,
        fig,
    )

    if get_data:
        fig.show(external=external_axes)
        return data, detail

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_cpi(
    countries: list,
    units: str = "growth_same",
    frequency: str = "monthly",
    harmonized: bool = False,
    smart_select: bool = True,
    options: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plot CPI data. [Source: FRED]

    Parameters
    ----------
    countries: list
        List of countries to plot
    units: str
        Units of the data, either "growth_same", "growth_previous", "index_2015"
    frequency: str
        Frequency of the data, either "monthly", "quarterly" or "annual"
    harmonized: bool
        Whether to use harmonized data
    smart_select: bool
        Whether to automatically select the best series
    options: bool
        Whether to show options
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    raw: bool
        Show raw data
    export: str
        Export data to csv or excel file
    sheet_name: str
        Name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series = (
        pd.read_csv(fred_model.harmonized_cpi_path)
        if harmonized
        else pd.read_csv(fred_model.cpi_path)
    )

    df = fred_model.get_cpi(
        countries=countries,
        units=units,
        frequency=frequency,
        harmonized=harmonized,
        smart_select=smart_select,
        options=options,
        start_date=start_date,
        end_date=end_date,
    )

    if options:
        return print_rich_table(series.drop(["series_id"], axis=1))

    ylabel_dict = {
        "growth_same": "Growth Same Period (%)",
        "growth_previous": "Growth Previous Period (%)",
    }

    country = [
        country.replace("_", " ").title()
        for country in countries
        if df.columns.str.contains(country)
    ]

    title = f"{'Harmonized ' if harmonized else ''} Consumer Price"
    title += (
        f" Index for {', '.join(country)}"
        if country
        else " Indices"
        if len(df.columns) > 1
        else ""
    )

    fig = OpenBBFigure(yaxis_title=ylabel_dict.get(units, "Index (2015=100)"))
    fig.set_title(title)

    for column in df.columns:
        country, frequency, units = column.split("-")
        label = f"{str(country).replace('_', ' ').title()} ({frequency}, {units})"

        fig.add_scatter(x=df.index, y=df[column].values, name=label)

    if raw:
        print_rich_table(
            df.iloc[-10:],
            title=title,
            show_index=True,
            floatfmt=".3f",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "CP",
        df / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


def format_data_to_plot(data: pd.DataFrame, detail: dict) -> Tuple[pd.DataFrame, str]:
    """Helper to format data to plot"""

    data_to_plot = data.dropna()
    exponent = int(np.log10(data_to_plot.max()))
    data_to_plot /= 10**exponent
    multiplier = f"x {format_units(10**exponent)}" if exponent > 0 else ""
    title = f"{detail['title']} ({detail['units']}) {'['+multiplier+']' if multiplier else ''}"

    data_to_plot.index = pd.to_datetime(data_to_plot.index)

    return data_to_plot, title
