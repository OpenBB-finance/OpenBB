import yfinance as yf
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import argparse
import datetime
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn, valid_date



def volume_graph(l_args, s_ticker):
    """ Show traded options volume. [Source: Yahoo Finance] """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="volume",
        description="""Display volume graph for a date. [Source: Yahoo Finance].""",
    )
    parser.add_argument(
        "-e",
        "--expiry",
        type=valid_date,
        dest="s_expiry_date",
        help="The expiry date (format YYYY-MM-DD) for the option chain",
        required=True
    )
    l_similar = []
    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        opt = yf.Ticker(s_ticker).option_chain(ns_parser.s_expiry_date.strftime("%Y-%m-%d"))
        # data available via: opt.calls, opt.puts

        volume_data = pd.concat(
            [
                __volume_data(opt.calls, 'calls'),
                __volume_data(opt.puts, 'puts')
            ],
            axis=0
        )
        fig = px.line(
            volume_data,
            x="strike",
            y="volume",
            title=f'{s_ticker} Volume for {ns_parser.s_expiry_date.strftime("%Y-%m-%d")}',
            color='type'
        )
        fig.show()

    except SystemExit:
         print("")
    except Exception as e:
        print(e)

def __volume_data(opt_data, flag):
    # get option chain for specific expiration
    df = opt_data.pivot_table(
        index='strike',
        values=['volume', 'openInterest'],
        aggfunc='sum')
    df.reindex()
    df['strike'] = df.index
    df['type'] = flag
    return df
