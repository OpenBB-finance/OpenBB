""" Finviz View """
__docformat__ = "numpy"

import os
import webbrowser
import pandas as pd

from PIL import Image
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import finviz_model
from gamestonk_terminal.helper_funcs import export_data


def map_sp500_view(period: str, map_type: str):
    """Opens Finviz map website in a browser. [Source: Finviz]

    Parameters
    ----------
    period : str
        Performance period
    map_type : str
        Map filter type
    """
    # Conversion from period and type, to fit url requirements
    d_period = {"1d": "", "1w": "w1", "1m": "w4", "3m": "w13", "6m": "w26", "1y": "w52"}
    d_type = {"sp500": "sec", "world": "geo", "full": "sec_all", "etf": "etf"}
    # TODO: Try to get this image and output it instead of opening browser
    webbrowser.open(
        f"https://finviz.com/map.ashx?t={d_type[map_type]}&st={d_period[period]}"
    )
    print("")


def display_performance(
    s_group: str,
    sort_col: str = "Name",
    ascending: bool = True,
    export: str = "",
):
    """View group (sectors, industry or country) performance data. [Source: Finviz]

    Parameters
    ----------
    s_group : str
        group between sectors, industry or country
    sort_col : str
        Column to sort by
    ascending : bool
        Flag to sort in ascending order
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    df_group = finviz_model.get_valuation_performance_data(s_group, "performance")
    df_group = df_group.rename(
        columns={
            "Perf Week": "Week",
            "Perf Month": "Month",
            "Perf Quart": "3Month",
            "Perf Half": "6Month",
            "Perf Year": "1Year",
            "Perf YTD": "YTD",
            "Avg Volume": "AvgVolume",
            "Rel Volume": "RelVolume",
        }
    )
    df_group["Week"] = df_group["Week"].apply(lambda x: float(x.strip("%")) / 100)
    df_group = df_group.sort_values(by=sort_col, ascending=ascending)
    df_group["Volume"] = df_group["Volume"] / 1_000_000
    df_group["AvgVolume"] = df_group["AvgVolume"] / 1_000_000
    df_group = df_group.rename(
        columns={"Volume": "Volume (1M)", "AvgVolume": "AvgVolume (1M)"}
    )
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_group.fillna(""),
                showindex=False,
                headers=df_group.columns,
                tablefmt="fancy_grid",
                floatfmt=[
                    "",
                    ".3f",
                    ".3f",
                    ".3f",
                    ".3f",
                    ".3f",
                    ".3f",
                    ".2f",
                    ".0f",
                    ".2f",
                    ".2f",
                    ".0f",
                ],
            )
        )
    else:
        print(df_group.fillna("").to_string(index=False))
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "performance",
        df_group,
    )


def display_valuation(
    s_group: str,
    sort_col: str = "Name",
    ascending: bool = True,
    export: str = "",
):
    """View group (sectors, industry or country) valuation data. [Source: Finviz]

    Parameters
    ----------
    s_group : str
        group between sectors, industry or country
    sort_col : str
        Column to sort by
    ascending : bool
        Flag to sort in ascending order
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    df_group = finviz_model.get_valuation_performance_data(s_group, "valuation")
    df_group["Market Cap"] = df_group["Market Cap"].apply(lambda x: float(x.strip("B")))
    df_group.columns = [col.replace(" ", "") for col in df_group.columns]
    df_group = df_group.sort_values(by=sort_col, ascending=ascending)
    df_group["Volume"] = df_group["Volume"] / 1_000_000
    df_group = df_group.rename(columns={"Volume": "Volume (1M)"})
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df_group.fillna(""),
                showindex=False,
                headers=df_group.columns,
                tablefmt="fancy_grid",
                floatfmt=".2f",
            )
        )
    else:
        print(df_group.fillna("").to_string(index=False))
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "valuation",
        df_group,
    )


def display_spectrum(s_group: str, export: str = ""):
    """Display finviz spectrum in system viewer [Source: Finviz]

    Parameters
    ----------
    s_group: str
        group between sectors, industry or country
    export: str
        Format to export data
    """
    finviz_model.get_spectrum_data(s_group)
    print("")

    img = Image.open(s_group + ".jpg")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "spectrum",
    )

    img.show()


def display_future(
    future_type: str = "Indices",
    sort_col: str = "ticker",
    ascending: bool = False,
    export: str = "",
):
    """Display table of a particular future type. [Source: Finviz]

    Parameters
    ----------
    future_type : str
        From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    sort_col : str
        Column to sort by
    ascending : bool
        Flag to sort in ascending order
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    d_futures = finviz_model.get_futures()

    df = pd.DataFrame(d_futures[future_type])
    df = df.set_index("label")
    df = df.sort_values(by=sort_col, ascending=ascending)
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df[["prevClose", "last", "change"]].fillna(""),
                showindex=True,
                floatfmt=".2f",
                headers=["prevClose", "last", "change (%)"],
                tablefmt="fancy_grid",
            )
        )
    else:
        print(df[["prevClose", "last", "change"]].fillna("").to_string(index=True))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        future_type.lower(),
        df,
    )
    print("")
