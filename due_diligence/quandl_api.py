import argparse

import matplotlib.ticker as ticker
import pandas as pd
import quandl
from matplotlib import pyplot as plt

import config_terminal as cfg
from helper_funcs import check_positive, long_number_format


# -------------------------------------------------------- SHORT_INTEREST --------------------------------------------------------
def short_interest(l_args, s_ticker, s_start):
    parser = argparse.ArgumentParser(prog='short',
                                     description="""Plots the short interest of a stock. This corresponds to the number of shares that
                                     have been sold short but have not yet been covered or closed out. Either NASDAQ or NYSE [Source: Quandl]""")

    parser.add_argument('-n', "--nyse", action="store_true", default=False, dest="b_nyse",
                        help='data from NYSE flag.')
    parser.add_argument('-d', "--days", action="store", dest="n_days", type=check_positive, default=10,
                        help='number of latest days to print data.')

    (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
        return

    quandl.ApiConfig.api_key = cfg.API_KEY_QUANDL

    if ns_parser.b_nyse:
        df_short_interest = quandl.get(f"FINRA/FNYX_{s_ticker}")
    else:
        df_short_interest = quandl.get(f"FINRA/FNSQ_{s_ticker}")

    df_short_interest = df_short_interest[s_start:]
    df_short_interest.columns = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_short_interest.columns.tolist()]
    df_short_interest['% of Volume Shorted'] = round(100*df_short_interest['Short Volume']/df_short_interest['Total Volume'], 2)

    fig, ax = plt.subplots()
    ax.bar(df_short_interest.index, df_short_interest['Short Volume'], 0.3, color='r')
    ax.bar(df_short_interest.index, df_short_interest['Total Volume']-df_short_interest['Short Volume'], 0.3, bottom=df_short_interest['Short Volume'], color='b')
    ax.set_ylabel('Shares')
    ax.set_xlabel('Date')

    if s_start:
        ax.set_title(f"{('NASDAQ', 'NYSE')[ns_parser.b_nyse]} Short Interest on {s_ticker} from {s_start.date()}")
    else:
        ax.set_title(f"{('NASDAQ', 'NYSE')[ns_parser.b_nyse]} Short Interest on {s_ticker}")

    ax.legend(labels=['Short Volume', 'Total Volume'])
    ax.tick_params(axis='both', which='major')
    ax.yaxis.set_major_formatter(ticker.EngFormatter())
    ax_twin = ax.twinx()
    ax_twin.tick_params(axis='y', colors='green')
    ax_twin.set_ylabel('Percentage of Volume Shorted', color='green')
    ax_twin.plot(df_short_interest.index, df_short_interest['% of Volume Shorted'], color='green')
    ax_twin.tick_params(axis='y', which='major', color='green')
    ax_twin.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f%%'))
    plt.xlim([df_short_interest.index[0], df_short_interest.index[-1]])

    df_short_interest['% of Volume Shorted'] = df_short_interest['% of Volume Shorted'].apply(lambda x: f'{x/100:.2%}')
    df_short_interest = df_short_interest.applymap(lambda x: long_number_format(x)).sort_index(ascending=False)

    pd.set_option('display.max_colwidth', 70)
    print(df_short_interest.head(n=ns_parser.n_days).to_string())
    print("")

    plt.show()
