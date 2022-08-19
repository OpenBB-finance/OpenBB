""" NFT Price Floor View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional
from matplotlib import pyplot as plt
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
def display_collections(num: int = 5, export: str = ""):
    """Display NFT collections. [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    num: int
        Number of NFT drops to display
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
                "name",
                "floorPriceETH",
                "totalSupply",
                "countOnSale",
                "blockchain",
            ]
        ]
        print_rich_table(
            df.head(num),
            headers=list(df.columns),
            show_index=False,
            title="NFT Collections",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "collections",
        df,
    )


@log_start_end(log=logger)
def display_floor_price(
    slug: str,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
):
    """Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    num: int
        Number of NFT drops to display
    export : str
        Export dataframe data to csv,json,xlsx file
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
        else:
            # This plot has 1 axis
            if external_axes is None:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            elif is_valid_axes_count(external_axes, 1):
                (ax,) = external_axes
            ax.bar(df.index, df["sales"], color=theme.get_colors()[1])
            ax.set_xlim(
                df.index[0],
                df.index[-1],
            )

            ax2 = ax.twinx()
            ax2.plot(df["dataPriceFloorETH"])
            ax2.set_ylabel("Sales", labelpad=20)
            ax2.set_zorder(ax2.get_zorder() + 1)
            ax.patch.set_visible(False)
            ax2.yaxis.set_label_position("left")
            ax.set_ylabel("Floor Price [ETH]", labelpad=30)
            ax.set_title(f"{slug} Floor Price")
            theme.style_primary_axis(ax)

            if external_axes is None:
                theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "fp",
            df,
        )
