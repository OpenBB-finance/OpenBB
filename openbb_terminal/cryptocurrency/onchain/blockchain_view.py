"""Blockchain View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import List, Optional

import matplotlib.pyplot as plt
from matplotlib import ticker

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.onchain import blockchain_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    plot_autoscale,
    is_valid_axes_count,
    str_date_to_timestamp,
    print_rich_table,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_btc_circulating_supply(
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Returns BTC circulating supply [Source: https://api.blockchain.info/]

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
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

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(df["x"], df["y"])
    ax.set_ylabel("BTC")
    ax.set_title("BTC Circulating Supply")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btccp",
        df,
    )


@log_start_end(log=logger)
def display_btc_confirmed_transactions(
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Returns BTC confirmed transactions [Source: https://api.blockchain.info/]

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
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

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(df["x"], df["y"], lw=0.8)
    ax.set_ylabel("Transactions")
    ax.set_title("BTC Confirmed Transactions")
    ax.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "btcct",
        df,
    )


@log_start_end(log=logger)
def display_btc_single_block(
    blockhash: str,
    export: str = "",
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
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "btcblockdata",
            df_data,
        )
