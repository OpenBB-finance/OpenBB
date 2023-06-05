"""LoanScan view"""
import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.overview import loanscan_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_crypto_rates(
    symbols: str,
    platforms: str,
    rate_type: str = "borrow",
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]

    Parameters
    ----------
    rate_type: str
        Interest rate type: {borrow, supply}. Default: supply
    symbols: str
        Crypto separated by commas. Default: BTC,ETH,USDT,USDC
    platforms: str
        Platforms separated by commas. Default: BlockFi,Ledn,SwissBorg,Youhodler
    limit: int
        Number of records to show
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = loanscan_model.get_rates(rate_type=rate_type)
    if df.empty:
        return console.print("\nError in loanscan request\n")

    valid_platforms = [
        platform for platform in platforms.lower().split(",") if platform in df.index
    ]
    df = df[symbols.upper().split(",")].loc[valid_platforms]
    df = df.sort_values(df.columns[0], ascending=False, na_position="last")

    fig = OpenBBFigure.create_subplots(
        1,
        3,
        specs=[[{"type": "domain"}, {"type": "bar", "colspan": 2}, None]],
        column_widths=[0.1, 0.8, 0.1],
    )

    df_non_null = pd.melt(df.reset_index(), id_vars=["index"]).dropna()

    assets = df_non_null.variable.unique().tolist()
    colors = iter(theme.get_colors(reverse=True))

    for asset in assets:
        width = df_non_null.loc[(df_non_null.variable == asset)]
        # silence Setcopywarnings
        pd.options.mode.chained_assignment = None
        width["id"] = width["index"] + width["variable"]

        fig.add_bar(
            x=width.value * 100,
            y=width["id"],
            orientation="h",
            name=asset,
            hovertext=width.value * 100,
            hovertemplate="%{hovertext:.2f}%",
            marker_color=next(colors),
            row=1,
            col=2,
        )

    fig.update_layout(
        title=f"Cryptos {rate_type} interest rate",
        xaxis_title="Rate (%)",
        yaxis=dict(side="left", title="Platform"),
        legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=1),
    )

    df = df.fillna("-")
    df = df.applymap(lambda x: str(round(100 * x, 2)) + "%" if x != "-" else x)

    print_rich_table(
        df,
        headers=list(df.columns),
        index_name="Platform",
        show_index=True,
        title=f"Crypto {rate_type.capitalize()} Interest Rates",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "cr", df, sheet_name, fig
    )

    return fig.show(external=external_axes)
