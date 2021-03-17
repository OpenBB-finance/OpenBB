from fredapi import Fred
import argparse
import matplotlib.pyplot as plt
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    valid_date,
    str_to_bool,
)
from gamestonk_terminal.config_terminal import API_FRED_KEY


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
        "-p",
        dest="plot",
        type=str_to_bool,
        default=True,
        required=False,
        help="Plot GDP",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if not ns_parser:
            return

        gdp = fred.get_series("GDP", ns_parser.start_date)

        if int(ns_parser.n_to_get) > 0:
            lastn = gdp.tail(int(ns_parser.n_to_get))

        else:
            lastn = gdp

        for date, val in lastn.iteritems():
            print(f'Date: {date.strftime("%m-%d-%Y")}, GDP: {val} ')

        if ns_parser.plot:
            plt.figure()
            lastn.plot(style="-ok")
            plt.xlabel("Time")
            plt.ylabel("GDP")
            plt.show()

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
        "-id", dest="series_id", required=True, type=str, help="FRED Series ID"
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
        "-p",
        dest="plot",
        type=str_to_bool,
        default=True,
        required=False,
        help="Plot data",
    )
    parser.add_argument(
        "-disp",
        dest="disp",
        type=str_to_bool,
        default=False,
        required=False,
        help="Print data",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if not ns_parser:
            return

        data = fred.get_series(ns_parser.series_id, ns_parser.start_date)
        if ns_parser.disp:
            for date, val in data.iteritems():
                print(f'Date: {date.strftime("%m-%d-%Y")}, DATA: {val} ')
        try:
            if ns_parser.plot:
                plt.figure()
                data.plot(style="-ok")
                plt.xlabel("Time")
                plt.ylabel("DATA")
                plt.show()
        except Exception as e:
            print(e)
            print("")
            return
    except SystemExit:
        print("")
    except Exception as e:
        print(e)
        print("")
        return
