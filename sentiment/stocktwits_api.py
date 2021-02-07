import argparse
import requests
import pandas as pd
from stock_market_helper_funcs import *

# -------------------------------------------------------------------------------------------------------------------
def sentiment(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='sentiment', 
                                     description="""Gather a stock sentiment based on last 30 messages on the board.
                                     Also prints the watchlist_count [stocktwits] """)

    parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", type=str, default=s_ticker, help='Ticker to gather sentiment')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        result = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{ns_parser.s_ticker}.json")
        if result.status_code == 200:
            print(f"Watchlist count: {result.json()['symbol']['watchlist_count']}")
            n_cases = 0
            n_bull = 0
            n_bear = 0
            for message in result.json()['messages']:
                if (message['entities']['sentiment']):
                    n_cases += 1
                    n_bull += (message['entities']['sentiment']['basic'] == 'Bullish')
                    n_bear += (message['entities']['sentiment']['basic'] == 'Bearish')
            if n_cases > 0:
                print(f"\nOver {n_cases} sentiment messages:")
                print(f"Bullish {round(100*n_bull/n_cases, 2)}%")
                print(f"Bearish {round(100*n_bear/n_cases, 2)}%")
        else:
            print("Invalid symbol")
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def messages(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='messages', 
                                     description="""Gather last 30 messages on the board [stocktwits] """)

    parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", type=str, default=s_ticker, help='Ticker to get board messages')
    parser.add_argument('-l', "--limit", action="store", dest="n_lim", type=check_positive, default=30, help='Limit messages shown')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        result = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{ns_parser.s_ticker}.json")
        if result.status_code == 200:
            for idx, message in enumerate(result.json()['messages']):
                print("------------------------------------------------------------------------------------------")
                print(message['body'])
                if idx > ns_parser.n_lim-1:
                    break
        else:
            print("Invalid symbol")
    
        print("")

    except:
        print("")


# -------------------------------------------------------------------------------------------------------------------
def trending(l_args):
    parser = argparse.ArgumentParser(prog='trending', 
                                     description="""Stocks trending [stocktwits] """)

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        result = requests.get(f"https://api.stocktwits.com/api/2/trending/symbols.json")
        if result.status_code == 200:
            l_symbols = list()
            for symbol in result.json()['symbols']:
                l_symbols.append([symbol['symbol'], symbol['watchlist_count'], symbol['title']])

            pd.set_option('display.max_colwidth', -1)
            df_trending = pd.DataFrame(l_symbols, columns=['Ticker', 'Watchlist Count', 'Name'])
            print(df_trending.to_string(index=False))
        else:
            print("Error!") 
        print("")

    except:
        print("")


