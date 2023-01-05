""" Investing.com View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List, Union
from matplotlib import ticker

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib import colors
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import seaborn as sns

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import investingcom_model
from openbb_terminal.economy.economy_helpers import text_transform
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

COLORS = ["rgb", "binary", "openbb"]

# pylint: disable=unnecessary-lambda-assignment


@log_start_end(log=logger)
def display_spread_matrix(
    countries: Union[str, List[str]] = "G7",
    maturity: str = "10Y",
    change: bool = False,
    color: str = "openbb",
    raw: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
    export: str = "",
):
    """Display spread matrix. [Source: Investing.com]

    Parameters
    ----------
    countries: Union[str, List[str]]
        Countries or group of countries. List of available countries is accessible through get_ycrv_countries().
    maturity: str
        Maturity to get data. By default 10Y.
    change: bool
        Flag to use 1 day change or not. By default False.
    color: str
        Color theme to use on heatmap, from rgb, binary or openbb By default, openbb.
    raw : bool
        Output only raw data.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """

    df = investingcom_model.get_spread_matrix(countries, maturity, change)

    if not df.empty:

        if raw:
            pretty_df = df.copy()

            # Convert to string spreads
            pretty_df[list(pretty_df.columns)[1:]] = pretty_df[
                list(pretty_df.columns)[1:]
            ].applymap(lambda x: f"{x:+.1f}" if x != 0 else "")

            # Convert to string yields
            pretty_df[list(pretty_df.columns)[0]] = pd.DataFrame(
                df[list(pretty_df.columns)[0]]
            ).applymap(lambda x: f"{x/100:.3f}%" if not change else f"{x:+.1f}")

            # Add colors
            pretty_df = pretty_df.applymap(
                lambda x: f"[{theme.down_color}]{x}[/{theme.down_color}]"
                if "-" in x
                else f"[{theme.up_color}]{x}[/{theme.up_color}]"
            )

            if isinstance(countries, str):
                title = f"{countries} - Spread Matrix - {maturity}"
            else:
                title = f"Spread Matrix - {maturity}"

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

            x_labels = list(df.columns)
            x_labels[1] = ""

            # https://stackoverflow.com/questions/53754012/create-a-gradient-colormap-matplotlib
            def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
                new_cmap = colors.LinearSegmentedColormap.from_list(
                    f"trunc({cmap.name},{minval:.2f},{maxval:.2f})",
                    cmap(np.linspace(minval, maxval, n)),
                )
                return new_cmap

            # This is not a bool so that we can add different colors in future
            if color.lower() == "rgb":
                cmap = truncate_colormap(plt.get_cmap("brg"), 1, 0.4)
            elif color.lower() == "openbb":
                cmap = truncate_colormap(plt.get_cmap("magma"), 0.5, 0.1)
            else:  # binary
                cmap = colors.ListedColormap([theme.up_color, theme.down_color])

            heatmap = sns.heatmap(
                df,
                cmap=cmap,
                cbar=False,
                annot=True,
                annot_kws={
                    "fontsize": 12,
                },
                center=0,
                fmt="+.1f",
                linewidths=0.5,
                linecolor="black"
                if any(substring in theme.mpl_style for substring in ["dark", "boring"])
                else "white",
                xticklabels=x_labels,
                mask=mask,
                ax=ax,
            )

            ax.xaxis.tick_top()
            ax.xaxis.set_major_locator(
                ticker.FixedLocator([x + 0.25 for x in ax.get_xticks().tolist()])
            )
            ax.set_xticklabels(x_labels, rotation=45)
            ax.set_yticklabels(list(df.index.values), rotation=0)
            ax.yaxis.set_label_position("left")

            y_labels = list(df.index.values)
            y_labels[-1] = ""
            ax1 = ax.twinx()
            ticks_loc = ax.get_yticks().tolist()
            ax1.yaxis.set_major_locator(ticker.FixedLocator(ticks_loc))
            ax1.set_yticklabels(y_labels, rotation=0)
            ax1.yaxis.set_label_position("right")
            ax1.set_ylim(ax.get_ylim())
            ax1.grid(False)
            ax1.set_frame_on(False)

            # Set 3 decimal places for yield and 1 spread
            if not change:
                spacing = df.shape[1] - 1
                k = 0
                for index, t in enumerate(heatmap.texts):
                    current_text = t.get_text()

                    if index == k:
                        k += spacing
                        spacing -= 1

                        t.set_text(text_transform(current_text))
                    else:
                        t.set_text(current_text)

            if isinstance(countries, str):
                ax.set_title(f"{countries} - Spread matrix - {maturity}", loc="center")
            else:
                ax.set_title(f"Spread matrix - {maturity}", loc="center")

            if not external_axes:
                theme.visualize_output()

        export_data(export, os.path.dirname(os.path.abspath(__file__)), "spread", df)


@log_start_end(log=logger)
def display_yieldcurve(
    country: str = "United States",
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

    country = country.title()
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

        colors_ = [
            theme.up_color if x > 0 else theme.down_color for x in df["Change"].values
        ]
        ax2.bar(df["Tenor"], df["Change"], width=1, color=colors_)
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
