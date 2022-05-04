"""LoanScan view"""
import logging
import os
from typing import List, Optional
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from openbb_terminal.cryptocurrency.overview import loanscan_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal import config_terminal as cfg
from openbb_terminal.config_plot import PLOT_DPI

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_crypto_rates(
    cryptos: str,
    platforms: str,
    rate_type: str,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]

    Parameters
    ----------
    rate_type: str
        Interest rate type: {borrow, supply}. Default: supply
    cryptos: str
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
        console.print("\nError in loanscan request\n")
    else:
        df = df[cryptos.upper().split(",")].loc[platforms.lower().split(",")]
        df = df.sort_values(df.columns[0], ascending=False, na_position="last")

        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                logger.error("Expected list of one axis item.")
                console.print("[red]Expected list of one axis item.\n[/red]")
                return
            (ax,) = external_axes

        df_non_null = pd.melt(df.reset_index(), id_vars=["index"]).dropna()

        assets = df_non_null.variable.unique().tolist()
        colors = iter(cfg.theme.get_colors(reverse=True))

        for asset in assets:

            width = df_non_null.loc[(df_non_null.variable == asset)]
            # silence Setcopywarnings
            pd.options.mode.chained_assignment = None
            width["id"] = width["index"] + width["variable"]

            ax.barh(
                y=width["id"],
                width=width.value * 100,
                label=asset,
                height=0.5,
                color=next(colors),
            )

        ylabels = df_non_null["index"].values.tolist()
        ax.set_yticks(np.arange(len(ylabels)))
        ax.set_yticklabels(ylabels)

        ax.set_xlabel("Rate (%)")
        ax.set_ylabel("Platform")
        ax.set_title(f"Cryptos {rate_type} interest rate")
        cfg.theme.style_primary_axis(ax)
        ax.tick_params(axis="y", labelsize=8)

        ax.yaxis.set_label_position("left")
        ax.yaxis.set_ticks_position("left")

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc="best")

        if not external_axes:
            cfg.theme.visualize_output()

        df = df.fillna("N/A")
        df = df.applymap(lambda x: str(round(100 * x, 2)) + "%" if x != "N/A" else x)

        print_rich_table(
            df.head(limit),
            headers=list(df.columns),
            index_name="Platform",
            show_index=True,
            title=f"Crypto {rate_type.capitalize()} Interest Rates",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cr",
            df,
        )
