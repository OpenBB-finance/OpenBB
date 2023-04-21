"""NASDAQ Data Link View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.economy import nasdaq_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_economic_calendar(
    countries: List[str],
    start_date: str,
    end_date: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display economic calendar for specified country between start and end dates

    Parameters
    ----------
    countries : List[str]
        List of countries to include in calendar.  Empty returns all
    start_date : str
        Start date for calendar
    end_date : str
        End date for calendar
    limit : int
        Limit number of rows to display
    export : str
        Export data to csv or excel file
    """
    df = nasdaq_model.get_economic_calendar(countries, start_date, end_date)
    if df.empty:
        return
    print_rich_table(
        df,
        title="Economic Calendar",
        show_index=False,
        headers=df.columns,
        export=bool(export),
        limit=limit,
    )
    console.print()
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "events",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def display_big_mac_index(
    country_codes: Optional[List[str]] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display Big Mac Index for given countries

    Parameters
    ----------
    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format data, by default ""
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    big_mac = nasdaq_model.get_big_mac_indices(country_codes)

    if not big_mac.empty:
        fig = OpenBBFigure(title="Big Mac Index", yaxis_title="Price of Big Mac in USD")
        for country in big_mac.columns:
            fig.add_scatter(
                x=big_mac.index,
                y=big_mac[country],
                mode="lines+markers",
                name=country,
            )

        if raw:
            print_rich_table(
                big_mac,
                headers=list(big_mac.columns),
                title="Big Mac Index",
                show_index=True,
                export=bool(export),
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "bigmac",
            big_mac,
            sheet_name,
            fig,
        )

        return fig.show(external=raw or external_axes)

    logger.error("Unable to get big mac data")
    return console.print("[red]Unable to get big mac data[/red]\n")
