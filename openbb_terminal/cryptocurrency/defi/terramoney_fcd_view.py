"""Terra Money FCD view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
from matplotlib import ticker

from openbb_terminal import config_terminal as cfg
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    prettify_column_names,
    lambda_very_long_number_formatter,
)
from openbb_terminal.cryptocurrency.defi import terramoney_fcd_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_account_staking_info(
    address: str = "", top: int = 10, export: str = ""
) -> None:
    """Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df, report = terramoney_fcd_model.get_staking_account_info(address)
    if not df.empty:
        print_rich_table(
            df.head(top), headers=list(df.columns), show_index=False, title=report
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sinfo",
        df,
    )


@log_start_end(log=logger)
def display_validators(
    top: int = 10, sortby: str = "votingPower", descend: bool = False, export: str = ""
) -> None:
    """Display information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terramoney_fcd_model.get_validators()
    df_data = df.copy()
    df = df.sort_values(by=sortby, ascending=descend)
    df["tokensAmount"] = df["tokensAmount"].apply(
        lambda x: lambda_very_long_number_formatter(x)
    )
    df.columns = [
        x if x not in ["Voting power", "Commission rate", "Uptime"] else f"{x} %"
        for x in prettify_column_names(df.columns)
    ]

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        floatfmt=".2f",
        show_index=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "validators",
        df_data,
    )


@log_start_end(log=logger)
def display_gov_proposals(
    top: int = 10,
    status: str = "all",
    sortby: str = "id",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = terramoney_fcd_model.get_proposals(status)
    df_data = df.copy()
    df = df.sort_values(by=sortby, ascending=descend).head(top)
    df.columns = prettify_column_names(df.columns)

    print_rich_table(
        df,
        headers=list(df.columns),
        floatfmt=".2f",
        show_index=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "govp",
        df_data,
    )


@log_start_end(log=logger)
def display_account_growth(
    kind: str = "total",
    cumulative: bool = False,
    top: int = 90,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    kind: str
        display total account count or active account count. One from list [active, total]
    cumulative: bool
        Flag to show cumulative or discrete values. For active accounts only discrete value are available.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = terramoney_fcd_model.get_account_growth(cumulative)
    if kind not in ["active", "total"]:
        kind = "total"
    options = {"total": "Total accounts", "active": "Active accounts"}

    opt = options[kind]
    label = "Cumulative" if cumulative and opt == "total" else "Daily"

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    df = df.sort_values("date", ascending=False).head(top)
    df = df.set_index("date")

    start, end = df.index[-1], df.index[0]

    if cumulative:
        ax.plot(df[opt], label=df[opt])
    else:
        ax.bar(x=df.index, height=df[opt], label=df[opt])

    ax.set_ylabel(f"{opt}")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )
    ax.set_title(f"{label} number of {opt.lower()} in period from {start} to {end}")
    cfg.theme.style_primary_axis(ax)

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gacc",
        df,
    )


@log_start_end(log=logger)
def display_staking_ratio_history(
    top: int = 90,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """

    df = terramoney_fcd_model.get_staking_ratio_history()
    df = df.sort_values("date", ascending=False).head(top)
    df = df.set_index("date")

    start, end = df.index[-1], df.index[0]

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(df, label=df["stakingRatio"])
    ax.set_ylabel("Staking ratio [%]")
    ax.set_title(f"Staking ratio from {start} to {end}")

    cfg.theme.style_primary_axis(ax)

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sratio",
        df,
    )


@log_start_end(log=logger)
def display_staking_returns_history(
    top: int = 90,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    df = terramoney_fcd_model.get_staking_returns_history()

    df = df.sort_values("date", ascending=False).head(top)
    df = df.set_index("date")

    start, end = df.index[-1], df.index[0]

    ax.plot(df, label=df["annualizedReturn"])
    ax.set_ylabel("Staking returns [%]")
    ax.set_title(f"Staking returns from {start} to {end}")

    cfg.theme.style_primary_axis(ax)

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sreturn",
        df,
    )
