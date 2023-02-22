"""Blockchain View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.onchain import blockchain_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
    str_date_to_timestamp,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_btc_circulating_supply(
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Returns BTC circulating supply [Source: https://api.blockchain.info/]

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df = blockchain_model.get_btc_circulating_supply()

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    df = df[
        (df["x"] > datetime.fromtimestamp(ts_start_date))
        & (df["x"] < datetime.fromtimestamp(ts_end_date))
    ]

    fig = OpenBBFigure(yaxis_title="BTC")
    fig.set_title("BTC Circulating Supply")

    fig.add_scatter(x=df["x"], y=df["y"], mode="lines", showlegend=False)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btccp",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_btc_confirmed_transactions(
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Returns BTC confirmed transactions [Source: https://api.blockchain.info/]

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    df = blockchain_model.get_btc_confirmed_transactions()

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    df = df[
        (df["x"] > datetime.fromtimestamp(ts_start_date))
        & (df["x"] < datetime.fromtimestamp(ts_end_date))
    ]

    fig = OpenBBFigure(yaxis_title="Transactions")
    fig.set_title("BTC Confirmed Transactions")

    fig.add_scatter(x=df["x"], y=df["y"], mode="lines", showlegend=False)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btcct",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_btc_single_block(
    blockhash: str,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Returns BTC block data. [Source: https://api.blockchain.info/]
    Parameters
    ----------
    blockhash : str
        Hash of the block you are looking for.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = blockchain_model.get_btc_single_block(blockhash)
    if not df.empty:
        df.rename(index={0: "Value"}, inplace=True)
        df_data = df.copy()

        df_essentials = df[
            [
                "hash",
                "ver",
                "prev_block",
                "mrkl_root",
                "bits",
                "next_block",
                "fee",
                "nonce",
                "n_tx",
                "size",
                "block_index",
                "main_chain",
                "height",
                "weight",
            ]
        ]

        df_flipped = df_essentials.transpose()

        print_rich_table(
            df_flipped,
            show_index=True,
            index_name="Metric",
            title=f"Block {int(df['height'])}",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "btcblockdata",
            df_data,
            sheet_name,
        )
