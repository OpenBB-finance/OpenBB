"""Llama View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import read_data_file
from openbb_terminal.cryptocurrency.defi import llama_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_grouped_defi_protocols(
    limit: int = 50,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    num: int
        Number of top dApps to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = llama_model.get_defi_protocols(limit, drop_chain=False)

    df["TVL ($)"] = df["TVL ($)"].apply(lambda x: lambda_long_number_format(x))

    chains = llama_model.get_grouped_defi_protocols(limit)

    fig = OpenBBFigure(
        xaxis_title="Total Value Locked ($)",
        yaxis_title="Decentralized Application Name",
    )
    fig.set_title(f"Top {limit} dApp TVL grouped by chain")

    colors = iter(theme.get_colors(reverse=True))

    for chain in chains:
        chain_filter = df.loc[df.Chain == chain]
        fig.add_bar(
            y=chain_filter.index,
            x=chain_filter["TVL ($)"],
            name=chain,
            orientation="h",
            marker_color=next(colors, "#B6A9CB"),
        )

    fig.update_layout(
        margin=dict(l=150),
        yaxis=dict(side="left", tickfont=dict(size=8)),
        legend=dict(yanchor="bottom", y=0, xanchor="right", x=1),
    )
    fig.update_xaxes(tickvals=list(range(0, 40)), ticktext=list(range(0, 40)))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gdapps",
        chains,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_defi_protocols(
    sortby: str,
    limit: int = 20,
    ascend: bool = False,
    description: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing information about listed DeFi protocols, their current TVL and changes to it in
    the last hour/day/week. [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    limit: int
        Number of records to display
    ascend: bool
        Flag to sort data descending
    description: bool
        Flag to display description of protocol
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = llama_model.get_defi_protocols(limit, sortby, ascend, description)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ldapps",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_historical_tvl(
    dapps: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots historical TVL of different dApps
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    dapps: str
        dApps to search historical TVL. Should be split by , e.g.: anchor,sushiswap,pancakeswap
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    fig = OpenBBFigure(yaxis_title="Total Value Locked ($)")
    fig.set_title("TVL in dApps")

    available_protocols = read_data_file("defillama_dapps.json")

    if isinstance(available_protocols, dict):
        for dapp in dapps.split(","):
            if dapp in available_protocols:
                df = llama_model.get_defi_protocol(dapp)
                if not df.empty:
                    fig.add_scatter(
                        x=df.index,
                        y=df["totalLiquidityUSD"].values,
                        name=available_protocols[dapp],
                    )
            else:
                print(f"{dapp} not found\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "dtvl",
            None,
            sheet_name,
            fig,
        )

        return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
def display_defi_tvl(
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        Number of records to display, by default 5
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    fig = OpenBBFigure(yaxis_title="Total Value Locked ($)")
    fig.set_title("Total Value Locked in DeFi")

    df = llama_model.get_defi_tvl()
    df_data = df.copy()
    df = df.tail(limit)

    fig.add_scatter(x=df["date"], y=df["totalLiquidityUSD"], name="TVL")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stvl",
        df_data,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
