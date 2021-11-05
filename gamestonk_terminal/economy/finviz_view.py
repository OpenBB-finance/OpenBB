""" Finviz View """
__docformat__ = "numpy"

import os
import webbrowser
import pandas as pd

from PIL import Image
from tabulate import tabulate
from matplotlib import pyplot as plt

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


def view_group_data(s_group: str, data_type: str, export: str):
    """View group (sectors, industry or country) valuation/performance/spectrum data. [Source: Finviz]

    Parameters
    ----------
    s_group : str
        group between sectors, industry or country
    data_type : str
        select data type to see data between valuation, performance and spectrum
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    if data_type in ("valuation", "performance"):
        df_group = finviz_model.get_valuation_performance_data(s_group, data_type)
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_group.fillna(""),
                    showindex=False,
                    floatfmt=".2f",
                    headers=df_group.columns,
                    tablefmt="fancy_grid",
                )
            )
        else:
            print(df_group.fillna("").to_string(index=False))
        print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            data_type,
            df_group,
        )

    elif data_type == "spectrum":
        finviz_model.get_spectrum_data(s_group)
        print("")

        img = Image.open(s_group + ".jpg")
        plt.imshow(img)

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "spectrum",
        )

        img.show()

    else:
        print(
            "Invalid data type. Choose between valuation, performance and spectrum.\n"
        )


def display_future(future_type: str = "Indices", export: str = ""):
    """Display table of a particular future type. [Source: Finviz]

    Parameters
    ----------
    future_type : str
        From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    d_futures = finviz_model.get_futures()

    df = pd.DataFrame(d_futures[future_type])
    df = df.set_index("label")

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df[["prevClose", "last", "change"]].fillna(""),
                showindex=True,
                floatfmt=".2f",
                headers=df.columns,
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
