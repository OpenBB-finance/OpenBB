from fredapi import Fred
import argparse
import matplotlib.pyplot as plt
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)
from gamestonk_terminal.config_terminal import FRED_API_KEY

def get_GDP(l_args):
    fred = Fred(api_key=FRED_API_KEY)
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="GDP",
        description="""
                GDP
            """,
    )
    parser.add_argument(
        "-n",
        dest='n_to_get',
        type=int,
        default=-1,
        required=False,
        help="Number of GDP Values to Grab",
    )

    parser.add_argument("-s",
                        dest = "start_date",
                        type = str,
                        default='1/1/2020',
                        required=False,
                        help='Date to Start')

    parser.add_argument("-p",
                        dest = "plot_",
                        type = bool,
                        default = False,
                        required=False,
                        help = 'Plot GDP')

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)

        if not ns_parser:
            return

        #gdp = fred.get_series_latest_release('GDP')
        gdp = fred.get_series('GDP',ns_parser.start_date)
        if int(ns_parser.n_to_get) > 0:
            lastn = gdp.tail(int(ns_parser.n_to_get))
        else:
            lastn = gdp
        for date, val in lastn.iteritems():
            print(f'Date: {date.strftime("%m-%d-%Y")}, GDP: {val} ')
        if ns_parser.plot_:
            plt.figure()
            lastn.plot(style = 'ok')
            plt.xlabel('Time')
            plt.ylabel('GDP')
            plt.show()
    except Exception as e:
        print(e)
        print("")
        return


