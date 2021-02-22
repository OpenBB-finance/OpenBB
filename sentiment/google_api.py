import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime
import matplotlib.pyplot as plt
from helper_funcs import *
import argparse


# -------------------------------------------------------------------------------------------------------------------
def mentions(l_args, s_ticker, s_start):
    parser = argparse.ArgumentParser(prog='mentions',
                                     description="""Plot weekly bars of stock's interest over time. other users watchlist.
                                     [Source: Google]""")

    parser.add_argument('-s', "--start", type=valid_date, dest="s_start", default=s_start,
                        help="starting date (format YYYY-MM-DD) from when we are interested in stock's mentions.")

    #try:
    if 1:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[s_ticker])
        df_interest = pytrend.interest_over_time()

        plt.title(f"Interest over time on {s_ticker}")
        if ns_parser.s_start:
            df_interest = df_interest[ns_parser.s_start:]
            plt.bar(df_interest.index, df_interest[s_ticker], width=2)
            plt.bar(df_interest.index[-1], df_interest[s_ticker].values[-1], color='tab:orange', width=2)
        else:
            plt.bar(df_interest.index, df_interest[s_ticker], width=1)
            plt.bar(df_interest.index[-1], df_interest[s_ticker].values[-1], color='tab:orange', width=1)

        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.ylabel('Interest [%]')
        plt.xlabel("Time")
        plt.show()
        print("")

    #except:
    #    print("")


# -------------------------------------------------------------------------------------------------------------------
def regions(l_args):
    parser = argparse.ArgumentParser(prog='regions',
                                     description="""Print other users watchlist. [Source: Reddit]""")
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=5,
                        help='limit of posts with watchlists retrieved.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def queries(l_args):
    parser = argparse.ArgumentParser(prog='queries',
                                     description="""Print other users watchlist. [Source: Reddit]""")
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=5,
                        help='limit of posts with watchlists retrieved.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def rise(l_args):
    parser = argparse.ArgumentParser(prog='rise',
                                     description="""Print other users watchlist. [Source: Reddit]""")
    parser.add_argument('-l', "--limit", action="store", dest="n_limit", type=check_positive, default=5,
                        help='limit of posts with watchlists retrieved.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

    except:
        print("")

