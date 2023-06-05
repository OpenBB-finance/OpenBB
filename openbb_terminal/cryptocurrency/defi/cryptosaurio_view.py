"""Cryptosaurio View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.defi import cryptosaurio_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_anchor_data(
    address: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    show_transactions: bool = False,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    show_transactions : bool
        Flag to show history of transactions in Anchor protocol for address. Default False
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df, df_deposits, stats_str = cryptosaurio_model.get_anchor_data(address=address)

    if stats_str:
        console.print(f"\n{stats_str}\n")

    if not df_deposits.empty and show_transactions:
        print_rich_table(
            df_deposits,
            headers=list(df_deposits.columns),
            show_index=False,
            title="Transactions history in Anchor Earn",
            export=bool(export),
        )

    if not df.empty:
        fig = OpenBBFigure(yaxis_title="Earnings Value [UST]")
        fig.set_title("Earnings in Anchor Earn")

        fig.add_scatter(x=df["time"], y=df["yield"], name="Earnings")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "anchor",
            df,
            sheet_name,
            fig,
        )

        return fig.show(external=external_axes)
    return None
