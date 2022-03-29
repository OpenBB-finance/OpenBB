"""Cryptosaurio View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional
import matplotlib.pyplot as plt
from openbb_terminal import config_terminal as cfg
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.defi import (
    cryptosaurio_model,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_anchor_data(
    address: str = "",
    export: str = "",
    show_transactions: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Displays anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    show_transactions : bool
        Flag to show history of transactions in Anchor protocol for address specified. Default False
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df, df_deposits, stats_str = cryptosaurio_model.get_anchor_data(address=address)

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes
    print("")
    print(stats_str)
    print("")

    if show_transactions:
        print_rich_table(
            df_deposits,
            headers=list(df_deposits.columns),
            show_index=False,
            title="Transactions history in Anchor Earn",
        )

    ax.plot(df["time"], df["yield"])
    ax.set_ylabel("Earnings Value [UST]")
    ax.set_title("Earnings in Anchor Earn")

    cfg.theme.style_primary_axis(ax)

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "anchor",
        df,
    )
