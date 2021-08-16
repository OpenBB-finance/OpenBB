""" Finviz View """
__docformat__ = "numpy"

import os
import webbrowser

from PIL import Image
from tabulate import tabulate

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
    """View group (sectors, industry or country) valuation/performance/spectrum data

    Parameters
    ----------
    s_group : str
        group between sectors, industry or country
    data_type : str
        select data type to see data between valuation, performance and spectrum
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    if data_type in ("valuation", "performance"):
        df_group = finviz_model.get_valuation_performance_data(s_group, data_type)
        print(
            tabulate(
                df_group.fillna(""),
                showindex=False,
                floatfmt=".2f",
                headers=df_group.columns,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            data_type,
            df_group,
        )

    elif data_type == "spectrum":
        finviz_model.get_spectrum_data(s_group)

        img = Image.open(s_group + ".jpg")
        img.show()

    else:
        print(
            "Invalid data type. Choose between valuation, performance and spectrum.\n"
        )
