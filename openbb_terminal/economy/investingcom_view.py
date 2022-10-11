""" Investing.com View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List, Union

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import seaborn as sns

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import investingcom_model
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_matrix(
    countries: Union[str, List[str]] = "G7",
    maturity: str = "10Y",
    change: bool = False,
    raw: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
    export: str = "",
):

    df = investingcom_model.get_matrix(countries, maturity, change)

    if not df.empty:

        if raw:
            pretty_df = df.copy()

            # Convert to string
            pretty_df[list(pretty_df.columns)[1:]] = pretty_df[
                list(pretty_df.columns)[1:]
            ].applymap(lambda x: f"{x:.1f}" if x != 0 else "")

            # Convert to string
            pretty_df[list(pretty_df.columns)[0]] = pd.DataFrame(
                df[list(pretty_df.columns)[0]]
            ).applymap(lambda x: f"{x/100:.3f}" if not change else f"{x:.1f}")

            # Add colors
            pretty_df = pretty_df.applymap(
                lambda x: f"[{theme.down_color}]{x}[/{theme.down_color}]"
                if "-" in x
                else f"[{theme.up_color}]{x}[/{theme.up_color}]"
            )

            if isinstance(countries, str):
                title = f"{countries} - Yield Curve Matrix - {maturity}"
            else:
                title = f"Yield Curve Matrix - {maturity}"

            print_rich_table(
                pretty_df,
                headers=list(pretty_df.columns),
                show_index=True,
                title=title,
            )

        else:
            # This plot has 1 axis
            if not external_axes:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            elif is_valid_axes_count(external_axes, 1):
                (ax,) = external_axes
            else:
                return

            mask = np.zeros((df.shape[0], df.shape[1]), dtype=bool)
            mask[np.tril_indices(len(mask))] = True
            mask[:, 0] = False
            for i in range(df.shape[0]):
                mask[i][i + 1] = True

            labels = list(df.columns)
            labels[1] = ""

            heatmap = sns.heatmap(
                df,
                cmap=ListedColormap([theme.up_color, theme.down_color]),
                cbar=False,
                annot=True,
                annot_kws={
                    "fontsize": 12,
                },
                center=0,
                fmt=".1f",
                linewidths=0.5,
                linecolor="black",
                xticklabels=labels,
                mask=mask,
                ax=ax,
            )

            ax.yaxis.tick_left()
            plt.yticks(rotation=0)
            ax.xaxis.tick_top()
            plt.xticks(rotation=45, ha="center")
            plt.tick_params(labelright=True)

            # Set 3 decimal places for yield and 1 spread
            if not change:
                spacing = df.shape[1] - 1
                k = 0
                for index, t in enumerate(heatmap.texts):
                    current_text = t.get_text()

                    if index == k:
                        k += spacing
                        spacing -= 1

                        text_transform = lambda x: f"{round(float(x)/100, 3)}"
                        t.set_text(text_transform(current_text))
                    else:
                        t.set_text(current_text)

            if isinstance(countries, str):
                ax.set_title(
                    f"{countries} - Interest rates matrix - {maturity}", loc="center"
                )
            else:
                ax.set_title(f"Interest rates matrix - {maturity}", loc="center")

            if not external_axes:
                theme.visualize_output()

        export_data(export, os.path.dirname(os.path.abspath(__file__)), "matrix", df)
        console.print("")


@log_start_end(log=logger)
def display_yieldcurve(
    country: str,
    external_axes: Optional[List[plt.Axes]] = None,
    raw: bool = False,
    export: str = "",
):
    """Display yield curve for specified country. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = investingcom_model.get_yieldcurve(country)

    if not df.empty:
        if external_axes is None:
            _, (ax1, ax2) = plt.subplots(
                nrows=2,
                ncols=1,
                figsize=plot_autoscale(),
                dpi=PLOT_DPI,
                gridspec_kw={"height_ratios": [2, 1]},
            )

        else:
            if len(external_axes) != 2:
                logger.error("Expected list of 3 axis items")
                console.print("[red]Expected list of 3 axis items.\n[/red]")
                return
            (ax1, ax2) = external_axes

        ax1.plot(
            df["Tenor"],
            df["Previous"],
            linestyle="--",
            marker="o",
            label="Previous",
        )
        ax1.plot(df["Tenor"], df["Current"], "-o", label="Current")
        ax1.set_ylabel("Yield (%)")
        theme.style_primary_axis(ax1)
        ax1.yaxis.set_label_position("left")
        ax1.yaxis.set_ticks_position("left")
        ax1.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax1.legend(
            loc="lower right",
            prop={"size": 9},
            ncol=3,
        )

        colors = [
            theme.up_color if x > 0 else theme.down_color for x in df["Change"].values
        ]
        ax2.bar(df["Tenor"], df["Change"], width=1, color=colors)
        ax2.set_ylabel("Change (bps)")
        ax2.set_xlabel("Maturity (years)")
        theme.style_primary_axis(ax2)
        ax2.yaxis.set_label_position("left")
        ax2.yaxis.set_ticks_position("left")

        if external_axes is None:
            ax1.set_title(f"Yield Curve - {country.title()} ")
            theme.visualize_output()

        if raw:
            print_rich_table(
                df,
                headers=list(df.columns),
                show_index=False,
                title=f"{country.title()} Yield Curve",
                floatfmt=".3f",
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "ycrv",
            df,
        )


@log_start_end(log=logger)
def display_economic_calendar(
    country: str = "all",
    importance: str = "",
    category: str = "",
    start_date: str = "",
    end_date: str = "",
    limit=100,
    export: str = "",
):
    """Display economic calendar. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country selected. List of available countries is accessible through get_events_countries().
    importances: str
        Importance selected from high, medium, low or all.
    categories: str
        Event category. List of available categories is accessible through get_events_categories().
    start_date: datetime.date
        First date to get events.
    end_date: datetime.date
        Last date to get events.
    limit: int
        The maximum number of events to show, default is 100.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df, detail = investingcom_model.get_economic_calendar(
        country, importance, category, start_date, end_date, limit
    )

    if not df.empty:

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=detail,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "events",
            df,
        )
