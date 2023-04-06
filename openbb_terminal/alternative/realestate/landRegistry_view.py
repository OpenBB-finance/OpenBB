""" UK Land Registry View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.alternative.realestate import landRegistry_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_estate_sales(postcode: str, limit: int, export: str = "") -> None:
    """Display real estate sales.

    Parameters
    ----------
    postcode : str
        Postcode

    limit : int
        number of rows to return

    """
    sales = landRegistry_model.get_estate_sales(postcode, limit)

    if sales.empty or len(sales) == 0:
        console.print(
            "[red]"
            + "No data loaded.\n"
            + "Make sure you picked a valid postcode."
            + "[/red]\n"
        )
        return

    print_rich_table(
        sales,
        show_index=False,
        title=f"[bold]{postcode}[/bold]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sales",
        sales,
    )


@log_start_end(log=logger)
def display_towns_sold_prices(
    town: str, start_date: str, end_date: str, limit: int, export: str = ""
):
    """Get towns sold house price data.

    Parameters
    ----------
    town : str
        town

    start_date : str
        startDate

    end_date : str
        endDate

    limit : int
        number of rows to return


    Returns
    -------
    pd.DataFrame
        All sales for that town within the date range specified
    """

    sales = landRegistry_model.get_towns_sold_prices(town, start_date, end_date, limit)

    if sales.empty or len(sales) == 0:
        console.print(
            "[red]"
            + "No data loaded.\n"
            + "Make sure you picked a valid town and date range."
            + "[/red]\n"
        )
        return

    print_rich_table(
        sales,
        show_index=False,
        title=f"[bold]{town} : {start_date} - {end_date}[/bold]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "towns_sold_prices",
        sales,
    )


@log_start_end(log=logger)
def display_region_stats(region: str, start_date: str, end_date: str, export: str = ""):
    """Get towns sold house price data.

    Parameters
    ----------
    region : str
        region

    start_date : str
        startDate

    end_date : str
        endDate


    Returns
    -------
    pd.DataFrame
        All stats for that region within the date range specified
    """

    stats = landRegistry_model.get_region_stats(region, start_date, end_date)

    if stats.empty or len(stats) == 0:
        console.print(
            "[red]"
            + "No data loaded.\n"
            + "Make sure you picked a valid region and date range."
            + "[/red]\n"
        )
        return

    print_rich_table(
        stats,
        show_index=False,
        title=f"[bold]{region} : {start_date} - {end_date}[/bold]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "region_stats",
        stats,
    )
