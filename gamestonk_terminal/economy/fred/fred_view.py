""" Fred View """
__docformat__ = "numpy"

import logging
import os
import textwrap
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy.fred import fred_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def format_units(num: int) -> str:
    """Helper to format number into string with K,M,B,T.  Number will be in form of 10^n"""
    number_zeros = int(np.log10(num))
    if number_zeros < 3:
        return str(num)
    if number_zeros < 6:
        return f"{int(num/1000)}K"
    if number_zeros < 9:
        return f"{int(num/1_000_000)}M"
    if number_zeros < 12:
        return f"{int(num/1_000_000_000)}B"
    if number_zeros < 15:
        return f"{int(num/1_000_000_000_000)}T"
    return f"10^{number_zeros}"


@log_start_end(log=logger)
def notes(series_term: str, num: int):
    """Print Series notes. [Source: FRED]
    Parameters
    ----------
    series_term : str
        Search for these series_term
    num : int
        Maximum number of series notes to display
    """
    df_search = fred_model.get_series_notes(series_term)
    if df_search.empty:
        console.print("No matches found. \n")
        return
    df_search["notes"] = df_search["notes"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=100)) if isinstance(x, str) else x
    )
    df_search["title"] = df_search["title"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=50)) if isinstance(x, str) else x
    )
    print_rich_table(
        df_search[["id", "title", "notes"]].head(num),
        title=f"[bold]Search results for {series_term}[/bold]",
        show_index=False,
        headers=["Series ID", "Title", "Description"],
    )
    console.print("")


@log_start_end(log=logger)
def display_fred_series(
    d_series: Dict[str, Dict[str, str]],
    start_date: str,
    raw: bool = False,
    export: str = "",
    limit: int = 10,
):
    """Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]

    Parameters
    ----------
    series : str
        FRED Series ID from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3
    start_date : str
        Starting date (YYYY-MM-DD) of data
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    limit: int
        Number of raw data rows to show
    """
    series_ids = list(d_series.keys())
    data = pd.DataFrame()

    for s_id in series_ids:
        data = pd.concat(
            [
                data,
                pd.DataFrame(
                    fred_model.get_series_data(s_id, start_date), columns=[s_id]
                ),
            ],
            axis=1,
        )
    data = data.dropna()
    # Try to get everything onto the same 0-10 scale.
    # To do so, think in scientific notation.  Divide the data by whatever the E would be
    if not data.empty:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if len(series_ids) == 1:
            s_id = series_ids[0]
            sub_dict: Dict = d_series[s_id]
            title = f"{sub_dict['title']} ({sub_dict['units']})"
            ax.plot(data.index, data, label="\n".join(textwrap.wrap(title, 80)))
        else:
            for s_id, sub_dict in d_series.items():
                data_to_plot = data[s_id].dropna()
                exponent = int(np.log10(data_to_plot.max()))
                data_to_plot /= 10**exponent
                multiplier = f"x {format_units(10**exponent)}" if exponent > 0 else ""
                title = f"{sub_dict['title']} ({sub_dict['units']}) {'['+multiplier+']' if multiplier else ''}"
                ax.plot(
                    data_to_plot.index,
                    data_to_plot,
                    label="\n".join(textwrap.wrap(title, 80))
                    if len(series_ids) < 5
                    else title,
                )

        ax.legend(prop={"size": 10}, bbox_to_anchor=(0, 1), loc="lower left")
        ax.grid()
        ax.set_xlim(data.index[0], data.index[-1])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.gcf().autofmt_xdate()
        fig.tight_layout()
        if gtff.USE_ION:
            plt.ion()

        plt.show()
        data.index = [x.strftime("%Y-%m-%d") for x in data.index]
        if raw:
            print_rich_table(
                data.tail(limit),
                headers=list(data.columns),
                show_index=True,
                index_name="Date",
            )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "plot",
            data,
        )
        console.print("")
    else:
        console.print("[red]Unable to get data for the fred series [/red]\n")
