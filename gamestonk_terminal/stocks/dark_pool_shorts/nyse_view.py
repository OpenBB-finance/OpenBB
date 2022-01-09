"""NYSE Short Data View"""
__docformat__ = "numpy"


import os
import matplotlib.pyplot as plt
import seaborn as sns
from plotly import express as px
from tabulate import tabulate
from gamestonk_terminal.stocks.dark_pool_shorts import nyse_model
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
from gamestonk_terminal.feature_flags import USE_ION, USE_TABULATE_DF
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.rich_config import console


def display_short_by_exchange(
    ticker: str,
    raw: bool = False,
    sort: str = "",
    asc: bool = False,
    mpl: bool = False,
    export: str = "",
):
    """Display short data by exchange

    Parameters
    ----------
    ticker : str
        Stock ticker
    raw : bool
        Flag to display raw data
    sort: str
        Column to sort by
    asc: bool
        Flag to sort in ascending order
    mpl: bool
        Flag to display using matplotlib
    export : str, optional
        Format  of export data
    """
    volume_by_exchange = nyse_model.get_short_data_by_exchange(ticker).sort_values(
        by="Date"
    )
    if volume_by_exchange.empty:
        console.print(
            "No short data found.  Ping @terp340 on discord if you believe this is an error."
        )

    if sort:
        if sort in volume_by_exchange.columns:
            volume_by_exchange = volume_by_exchange.sort_values(by=sort, ascending=asc)
        else:
            console.print(
                f"{sort} not a valid option.  Selectone of {list(volume_by_exchange.columns)}.  Not sorting."
            )

    if mpl:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        sns.lineplot(
            data=volume_by_exchange, x="Date", y="NetShort", hue="Exchange", ax=ax
        )
        ax.set_title(f"Net Short Volume for {ticker}")
        if USE_ION:
            plt.ion()

        fig.tight_layout()
        plt.show()
    else:
        fig = px.line(
            volume_by_exchange,
            x="Date",
            y="NetShort",
            color="Exchange",
            title=f"Net Short Volume for {ticker}",
        )
        fig.show()

    if raw:
        if not USE_TABULATE_DF:
            console.print(volume_by_exchange.head(20).to_string())
        else:
            print(
                tabulate(
                    volume_by_exchange.head(20),
                    showindex=False,
                    tablefmt="fancy_grid",
                    headers=volume_by_exchange.columns,
                )
            )
    console.print("")
    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "volexch",
            volume_by_exchange,
        )
