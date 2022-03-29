"""Terra Engineer View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional


import matplotlib.pyplot as plt
from matplotlib import ticker

from openbb_terminal import config_terminal as cfg
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.defi import terraengineer_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    plot_autoscale,
)

from openbb_terminal.rich_config import console


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_terra_asset_history(
    asset: str = "",
    address: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Displays the 30-day history of specified asset in terra address
    [Source: https://terra.engineer/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = terraengineer_model.get_history_asset_from_terra_address(
        address=address, asset=asset
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(df["x"], df["y"])
    ax.set_ylabel(f"{asset.upper()} Amount")
    ax.set_title(f"{asset.upper()} Amount in {address}")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    cfg.theme.style_primary_axis(ax)

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "aterra",
        df,
    )


@log_start_end(log=logger)
def display_anchor_yield_reserve(
    export: str = "", external_axes: Optional[List[plt.Axes]] = None
) -> None:
    """Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = terraengineer_model.get_history_asset_from_terra_address(
        address="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(df["x"], df["y"])
    ax.set_ylabel("UST Amount")
    ax.set_title("Anchor UST Yield Reserve")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    cfg.theme.style_primary_axis(ax)

    if not external_axes:
        cfg.theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ayr",
        df,
    )
