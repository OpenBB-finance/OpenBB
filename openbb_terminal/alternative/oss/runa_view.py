"""Rekt view"""
import logging
import os
from typing import Optional, List

from matplotlib import pyplot as plt
from matplotlib import ticker
from openbb_terminal.alternative.oss import runa_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    lambda_long_number_format,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_rossindex(
    top: int,
    sortby: str,
    descend: bool,
    show_chart: bool = False,
    show_growth: bool = True,
    chart_type: str = "stars",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display list of startups from ross index [Source: https://runacap.com/]

    Parameters
    ----------
    top: int
        Number of startups to search
    sortby: str
        Key by which to sort data. Default: Stars AGR [%]
    descend: bool
        Flag to sort data descending
    show_chart: bool
        Flag to show chart with startups
    show_growth: bool
        Flag to show growth line chart
    chart_type: str
        Chart type {stars,forks}
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df = runa_model.get_startups()

    if df.empty:
        console.print("\nError in runa request\n")
    else:
        if sortby in runa_model.SORT_COLUMNS:
            df = df.sort_values(by=sortby, ascending=descend)
        df = df.head(top)
        if show_chart:
            if external_axes is None:
                _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            elif is_valid_axes_count(external_axes, 2):
                (ax1, _) = external_axes
            else:
                return
            for _, row in df[::-1].iterrows():
                ax1.barh(
                    y=row["GitHub"],
                    width=row["Forks" if chart_type == "forks" else "Stars"],
                )
            ax1.set_xlabel("Forks" if chart_type == "forks" else "Stars")
            ax1.get_xaxis().set_major_formatter(
                ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
            )
            ax1.grid(axis="y")
            ax1.yaxis.set_label_position("left")
            ax1.yaxis.set_ticks_position("left")
            ax1.set_ylabel("Company")
            ax1.yaxis.set_tick_params(labelsize=8)
            title = "Total Forks" if chart_type == "forks" else "Total Stars"
            ax1.set_title(f"ROSS Index - {title}")
            if external_axes is None:
                theme.visualize_output()
        if show_growth:
            if external_axes is None:
                fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            elif is_valid_axes_count(external_axes, 2):
                (ax, _) = external_axes
            else:
                return
            for _, row in df[::-1].iterrows():
                ax.barh(
                    y=row["GitHub"],
                    width=row["FG" if chart_type == "forks" else "SG"],
                )
            ax.yaxis.set_label_position("left")
            ax.yaxis.set_ticks_position("left")
            ax.set_ylabel("Company")
            ax.set_xlabel("Annual Growth [times]")
            ax.yaxis.set_tick_params(labelsize=8)
            title = (
                "Forks Annual Growth"
                if chart_type == "forks"
                else "Stars Annual Growth"
            )
            ax.set_title(f"ROSS Index - {title}")
            fig.tight_layout()
            if external_axes is None:
                theme.visualize_output()
        show_df = df.drop(["SG", "FG"], axis=1)
        show_df = show_df.fillna("")
        show_df["GitHub"] = show_df["GitHub"].str.wrap(10)
        print_rich_table(
            show_df.head(top),
            headers=list(show_df.columns),
            floatfmt=".1f",
            show_index=False,
            title="ROSS Index - the fastest-growing open-source startups",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "runaidx",
            df,
        )
