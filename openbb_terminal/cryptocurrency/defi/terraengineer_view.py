"""Terra Engineer View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.defi import terraengineer_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_terra_asset_history(
    asset: str = "",
    address: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots the 30-day history of specified asset in terra address
    [Source: https://terra.engineer/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = terraengineer_model.get_history_asset_from_terra_address(
        address=address, asset=asset
    )
    if df.empty:
        console.print("[red]No data in the provided dataframe[/red]\n")

    fig = OpenBBFigure(yaxis_title=f"{asset.upper()} Amount")
    fig.set_title(f"{asset.upper()} Amount in {address}")
    fig.add_scatter(x=df["x"], y=df["y"], name=f"{asset.upper()} Amount")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "aterra",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_anchor_yield_reserve(
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file, by default False
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = terraengineer_model.get_anchor_yield_reserve()
    if df.empty:
        return console.print("[red]No data was found[/red]\n")

    fig = OpenBBFigure(yaxis_title="UST Amount")
    fig.set_title("Anchor UST Yield Reserve")

    fig.add_scatter(x=df["x"], y=df["y"], name="UST Amount")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ayr",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
