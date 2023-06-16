""" Finviz View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import finviz_model
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_performance_map(period: str = "1d", map_filter: str = "sp500"):
    """Opens Finviz map website in a browser. [Source: Finviz]

    Parameters
    ----------
    period : str
        Performance period. Available periods are 1d, 1w, 1m, 3m, 6m, 1y.
    map_filter : str
        Map filter. Available map filters are sp500, world, full, etf.
    """
    finviz_model.get_performance_map(period, map_filter)


@log_start_end(log=logger)
def display_valuation(
    group: str = "sector",
    sortby: str = "Name",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display group (sectors, industry or country) valuation data. [Source: Finviz]

    Parameters
    ----------
    group : str
        Group by category. Available groups can be accessed through get_groups().
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    df_group = finviz_model.get_valuation_data(group, sortby, ascend)

    if df_group.empty:
        return
    df_group = df_group.rename(columns={"Name": ""})
    print_rich_table(
        df_group,
        show_index=False,
        headers=list(df_group.columns),
        title=f"{group.replace('_',' ').title()} Valuation Data",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "valuation",
        df_group,
        sheet_name,
    )


@log_start_end(log=logger)
def display_performance(
    group: str = "sector",
    sortby: str = "Name",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """View group (sectors, industry or country) performance data. [Source: Finviz]

    Parameters
    ----------
    group : str
        Group by category. Available groups can be accessed through get_groups().
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    df_group = finviz_model.get_performance_data(group, sortby, ascend)
    df_group = df_group.rename(columns={"Name": ""})
    if df_group.empty:
        return
    print_rich_table(
        df_group,
        show_index=False,
        headers=df_group.columns,
        title=f"{group.replace('_',' ').title()} Performance Data",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "performance",
        df_group,
        sheet_name,
    )


@log_start_end(log=logger)
def display_future(
    future_type: str = "Indices",
    sortby: str = "ticker",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display table of a particular future type. [Source: Finviz]

    Parameters
    ----------
    future_type : str
        From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    df = finviz_model.get_futures(future_type, sortby, ascend)

    print_rich_table(
        df,
        show_index=True,
        headers=["prevClose", "last", "change (%)"],
        title="Future Table [Source: FinViz]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        future_type.lower(),
        df,
        sheet_name,
    )
