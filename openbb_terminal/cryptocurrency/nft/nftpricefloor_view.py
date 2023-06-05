""" NFT Price Floor View """
__docformat__ = "numpy"

# flake8: noqa

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.nft import nftpricefloor_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
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
    fig = OpenBBFigure()
    df = nftpricefloor_model.get_collections()

    if df.empty:
        return console.print("No data found.", "\n")

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
        fig = OpenBBFigure(yaxis_title="Floor Price [ETH]" if show_fp else "Sales")
        fig.set_title("Collections Floor Price" if show_fp else "Collections Sales")
        for collection in df["slug"].head(limit).values:
            df_collection = nftpricefloor_model.get_floor_price(collection)
            if not df_collection.empty:
                values = (
                    df_collection["floorEth"].values
                    if show_fp
                    else df_collection["salesCount"].values
                )
                fig.add_scatter(
                    x=df_collection.index, y=values, mode="lines", name=collection
                )

        if not fig.is_image_export(export):
            fig.show()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="NFT Collections",
        export=bool(export),
        limit=limit,
    )

    return export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "collections",
        df,
        sheet_name,
        fig,
    )


@log_start_end(log=logger)
def display_floor_price(
    slug: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
    raw: bool = False,
) -> Union[None, OpenBBFigure]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = nftpricefloor_model.get_floor_price(slug)
    if df.empty:
        return console.print("No data found.", "\n")

    if raw:
        print_rich_table(
            df,
            index_name="date",
            headers=list(df.columns),
            show_index=True,
            title=f"{slug} Floor Price",
            export=bool(export),
            limit=limit,
        )

    fig = OpenBBFigure.create_subplots(
        1, 1, shared_yaxes=False, specs=[[{"secondary_y": True}]]
    )
    fig.set_title(f"{slug} Floor Price")
    fig.set_yaxis_title("Floor Price [ETH]", secondary_y=False)
    fig.set_yaxis_title("Sales", side="left", secondary_y=True)
    fig.set_xaxis_title("Date")

    fig.add_bar(
        x=df.index,
        y=df["salesCount"],
        name="Sales",
        marker_color=theme.down_color,
        secondary_y=True,
    )
    fig.add_scatter(
        x=df.index,
        y=df["floorEth"],
        name="Floor Price",
        mode="lines",
        line_color=theme.up_color,
        secondary_y=False,
    )
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fp",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
