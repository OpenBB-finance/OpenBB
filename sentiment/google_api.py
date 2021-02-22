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

    try:
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

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def regions(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='regions',
                                     description="""Plot bars of regions based on stock's interest. [Source: Google]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10,
                        help='number of regions to plot that show highest interest.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[s_ticker])
        df_interest_region = pytrend.interest_by_region()
        df_interest_region = df_interest_region.sort_values([s_ticker], ascending=False).head(ns_parser.n_num)

        plt.figure(figsize=(25,5))
        plt.title(f"Top's regions interest on {s_ticker}")
        plt.bar(df_interest_region.index, df_interest_region[s_ticker], width=0.8)
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.ylabel('Interest [%]')
        plt.xlabel("Time")
        plt.show()
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def queries(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='queries',
                                     description="""Print top related queries with this stock's query. [Source: Google]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10,
                        help='number of top related queries to print.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[s_ticker])
        df_related_queries = pytrend.related_queries()
        df_related_queries = df_related_queries[s_ticker]['top'].head(ns_parser.n_num)
        df_related_queries['value'] = df_related_queries['value'].apply(lambda x: str(x)+'%')
        print(f"Top {s_ticker}'s related queries")
        print(df_related_queries.to_string(index=False))
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def rise(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='rise',
                                     description="""Print top rising related queries with this stock's query.
                                    [Source: Google]""")
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10,
                        help='number of top rising related queries to print.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[s_ticker])
        df_related_queries = pytrend.related_queries()
        df_related_queries = df_related_queries[s_ticker]['rising'].head(ns_parser.n_num)
        print(f"Top rising {s_ticker}'s related queries")
        print(df_related_queries.to_string(index=False))
        print("")

    except:
        print("")

