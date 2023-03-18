""" NFT Price Floor View """
__docformat__ = "numpy"

# flake8: noqa

import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt

from openbb_terminal import config_terminal as cfg
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.nft import nftpricefloor_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_collections(
    show_fp: bool = False,
    show_sales: bool = False,
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display NFT collections. [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    show_fp : bool
        Show NFT Price Floor for top collections
    limit: int
        Number of NFT collections to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = nftpricefloor_model.get_collections()

    if df.empty:
        console.print("No data found.", "\n")
    else:
        df = df[
            [
                "slug",
                "floorInfo.currentFloorEth",
                "totalSupply",
                "listedCount",
                "blockchain",
            ]
        ]
        if show_fp or show_sales:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            for collection in df["slug"].head(limit).values:
                df_collection = nftpricefloor_model.get_floor_price(collection)
                if not df_collection.empty:
                    values = (
                        df_collection["floorEth"]
                        if show_fp
                        else df_collection["salesCount"]
                    )
                    ax.plot(df_collection.index, values, label=collection)
            ax.set_ylabel("Floor Price [ETH]" if show_fp else "Sales")
            cfg.theme.style_primary_axis(ax)
            ax.legend()
            ax.set_title("Collections Floor Price" if show_fp else "Collections Sales")
            cfg.theme.visualize_output()

        print_rich_table(
            df.head(limit),
            headers=list(df.columns),
            show_index=False,
            title="NFT Collections",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "collections",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_floor_price(
    slug: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
):
    """Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    slug: str
        NFT collection slug
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df = nftpricefloor_model.get_floor_price(slug)
    if df.empty:
        console.print("No data found.", "\n")
    elif not df.empty:
        if raw:
            print_rich_table(
                df.head(limit),
                index_name="date",
                headers=list(df.columns),
                show_index=True,
                title=f"{slug} Floor Price",
            )
        # This plot has 1 axis
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        ax.bar(df.index, df["salesCount"], color=theme.down_color, label="Sales")
        ax.set_xlim(
            df.index[0],
            df.index[-1],
        )

        ax2 = ax.twinx()
        ax2.plot(df["floorEth"], color=theme.up_color, label="Floor Price")
        ax2.set_ylabel("Sales", labelpad=20)
        ax2.set_zorder(ax2.get_zorder() + 1)
        ax.patch.set_visible(False)
        ax2.yaxis.set_label_position("left")
        ax.set_ylabel("Floor Price [ETH]", labelpad=30)
        ax.set_title(f"{slug} Floor Price")
        ax.legend(loc="upper left")
        ax2.legend(loc="upper right")
        cfg.theme.style_primary_axis(ax)

        if external_axes is None:
            cfg.theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "fp",
            df,
            sheet_name,
        )
