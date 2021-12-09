""" Fred View """
__docformat__ = "numpy"

import os
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.economy import fred_model
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale

register_matplotlib_converters()


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
        print("No matches found. \n")
        return
    df_search["notes"] = df_search["notes"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=100)) if isinstance(x, str) else x
    )
    df_search["title"] = df_search["title"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=50)) if isinstance(x, str) else x
    )
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_search[["id", "title", "notes"]].head(num),
                tablefmt="fancy_grid",
                headers=["Series ID", "Title", "Description"],
                showindex=False,
            )
        )
    else:
        print(df_search[["id", "title", "notes"]].head(num).to_string(index=False))
    print("")


def display_series(series: str, start_date: str, raw: bool, export: str):
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
    """
    if export:
        l_series_fred = []

    if not raw:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.axes.get_yaxis().set_visible(False)
        plt.subplots_adjust(right=0.9 - series.count(",") * 0.1)
        l_colors = [
            "tab:blue",
            "tab:orange",
            "tab:green",
            "tab:red",
            "tab:purple",
            "tab:brown",
            "tab:pink",
            "tab:gray",
            "tab:olive",
            "tab:cyan",
        ]

        l_ts_start = []
        l_ts_end = []
        p = {}
        success = -1
        success_series = []
        success_titles = []

    for series_term in series.split(","):
        if series_term:
            l_series, l_title = fred_model.get_series_ids(series_term, 5)

            if len(l_series) == 0:
                print(f"No series found for term '{series_term}'\n")
                continue

            print(f"For '{series_term}', series IDs found: {', '.join(l_series)}.\n")

            ser = l_series[0]
            ser_title = l_title[0]
            df_fred = fred_model.get_series_data(ser, start_date)

            if export:
                l_series_fred.append(df_fred)

            df_fred.index.name = "Date"

            if raw:
                df_fred.index = df_fred.index.strftime("%d/%m/%Y")
                if gtff.USE_TABULATE_DF:
                    print(
                        tabulate(
                            df_fred.dropna().to_frame(),
                            showindex=True,
                            headers=[f"{ser}: {ser_title}"],
                            tablefmt="fancy_grid",
                            floatfmt=".2f",
                        ),
                        "\n",
                    )
                else:
                    print(df_fred.dropna().to_frame().to_string(), "\n")

            else:
                success += 1
                success_series.append(ser.upper())
                success_titles.append(ser_title)

                axes = ax.twinx()
                axes.spines["right"].set_position(("axes", 1 + success * 0.15))
                axes.spines["right"].set_color(l_colors[success])
                (p[success],) = axes.plot(
                    df_fred.index,
                    df_fred.values,
                    c=l_colors[success],
                    label=ser.upper(),
                )

                axes.yaxis.label.set_color(l_colors[success])

                l_ts_start.append(df_fred.index[0])
                l_ts_end.append(df_fred.index[-1])

    if not raw and success > -1:
        plt.title("FRED: " + ", ".join(success_series))
        plt.xlim(min(l_ts_start), max(l_ts_end))
        plt.gcf().autofmt_xdate()
        plt.xlabel("Time")
        plt.legend(
            [val for _, val in p.items()], success_titles, loc="best", prop={"size": 6}
        )
        plt.gca().spines["left"].set_visible(False)
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "series",
        )
        if gtff.USE_ION:
            plt.ion()
        plt.show()

    if export and raw:
        df_data = pd.concat(l_series_fred, axis=1)
        df_data.columns = success_series

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "series",
            df_data,
        )
