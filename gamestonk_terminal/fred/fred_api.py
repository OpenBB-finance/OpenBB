import argparse
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from fredapi import Fred
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    valid_date,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.config_terminal import API_FRED_KEY
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def get_GDP(l_args):
    fred = Fred(api_key=API_FRED_KEY)
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="GDP",
        description="""
                GDP
            """,
    )
    parser.add_argument(
        "-n",
        dest="n_to_get",
        type=int,
        default=-1,
        required=False,
        help="Number of GDP Values to Grab",
    )

    parser.add_argument(
        "-s",
        dest="start_date",
        type=valid_date,
        default="2015-01-01",
        required=False,
        help="Date to Start",
    )

    parser.add_argument(
        "--noplot",
        action="store_false",
        default=True,
        dest="noplot",
        help="Suppress output plot",
    )

    parser.add_argument(
        "--hidedata",
        action="store_false",
        default=True,
        dest="hidedata",
        help="Suppress data display plot",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if not ns_parser:
            return

        gdp = fred.get_series("GDP", ns_parser.start_date)
        gdp = pd.DataFrame(gdp, columns=["GDP"])
        gdp.index.name = "Date"
        if int(ns_parser.n_to_get) > 0:
            lastn = gdp.tail(int(ns_parser.n_to_get))

        else:
            lastn = gdp

        if ns_parser.hidedata:
            print(lastn)
            print("")

        if ns_parser.noplot:
            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
            plt.plot(lastn.index, lastn.GDP, "-ok")
            plt.xlabel("Time")
            plt.xlim(lastn.index[0], lastn.index[-1])
            plt.ylabel("GDP (bn $)")
            plt.title("FRED GDP Data (in Billions of USD)")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.minorticks_on()
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            plt.show()
            print("")

    except Exception as e:
        print(e)
        print("")
        return


def custom_data(l_args):
    fred = Fred(api_key=API_FRED_KEY)

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="Custom",
        description="""
                    Custom Data
                """,
    )
    parser.add_argument(
        "-i", "--id", dest="series_id", required=True, type=str, help="FRED Series ID"
    )

    parser.add_argument(
        "-s",
        dest="start_date",
        type=valid_date,
        default="2015-01-01",
        required=False,
        help="Starting date (YYYY-MM-DD) of data",
    )

    parser.add_argument(
        "--noplot",
        action="store_false",
        default=True,
        dest="noplot",
        help="Suppress output plot",
    )

    parser.add_argument(
        "--hidedata",
        action="store_false",
        default=True,
        dest="hidedata",
        help="Suppress data display plot",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if not ns_parser:
            return

        data = fred.get_series(ns_parser.series_id, ns_parser.start_date)

        data = pd.DataFrame(data, columns=[f"{ns_parser.series_id}"])
        data.index.name = "Date"
        if ns_parser.hidedata:
            print(data)
            print("")
        if ns_parser.noplot:
            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
            plt.plot(data.index, data.iloc[:, 0], "-ok")
            plt.xlabel("Time")
            plt.xlim(data.index[0], data.index[-1])
            plt.ylabel(f"{ns_parser.series_id}")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.minorticks_on()
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            plt.title(f"FRED {ns_parser.series_id} Series")
            plt.show()
            print("")

            if gtff.USE_ION:
                plt.ion()

    except SystemExit:
        print("")
    except Exception as e:
        print(e)
        print("")
        return
