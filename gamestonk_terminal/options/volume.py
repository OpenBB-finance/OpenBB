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

        __get_volume_graph(s_ticker, ns_parser.s_expiry_date.strftime("%Y-%m-%d"))

    except SystemExit:
         print("")
    except Exception as e:
        print(e)



def __get_volume_graph(ticker_name, exp_date):
    df = __get_volume_data(ticker_name, exp_date)
    __generate_graph_sns(df, ticker_name, exp_date)
    #__generate_graph_plotly(df, ticker_name, exp_date)

def __pull_call_put_data(call_put, flag):
    df = call_put.pivot_table(
        index='strike',
        values = ['volume','openInterest'],
        aggfunc='sum')

    df.reindex()

    df['strike'] = df.index
    df['type'] = flag

    return df

def __get_volume_data(ticker_name, exp_date):

    option_chain = yf.Ticker(ticker_name).option_chain(exp_date)

    calls = __pull_call_put_data(
        option_chain.calls,
        'calls'
        )

    puts = __pull_call_put_data(
        option_chain.puts,
        'puts'
        )

    volume_data = pd.concat(
        [
            calls,
            puts
        ],
            axis = 0
            )
    #dataframe
    return volume_data

def __generate_graph_plotly(df, ticker_name, exp_date):
    #version with plotly express
    fig = px.line(
        df,
        x="strike",
        y="volume",
        title=f'{ticker_name} options volume for {exp_date}',
        color= 'type'
        )
    fig.show()

    return

def __generate_graph_sns(df, ticker_name, exp_date):
    #version with seaborn express
    plt.figure(figsize=(12,6))
    fig = sns.lineplot(
        data = df,
        x = 'strike',
        y = 'volume',
        hue = 'type',
        palette=  ['limegreen', 'tomato'])

    plt.title(f'{ticker_name} options volume for {exp_date}')

    plt.show()
    return
