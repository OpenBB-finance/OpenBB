""" Example or something

    Is this not informative enough?

    Finviz for data

"""
from alpha_vantage.timeseries import TimeSeries
import argparse
import config_bot as cfg
import pandas as pd
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# -----------------------------------------------------------------------------------------------------------------------
def print_help():
    """ Print help
    """
    print("What do you want to do?")
    print("gainers     show latest top gainers")
    print("view        view a specific stock tick")
    print("help        help to see this menu again")
    print("quit        to abandon the program")


# -----------------------------------------------------------------------------------------------------------------------
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


# -----------------------------------------------------------------------------------------------------------------------
def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date: {s}")


# -----------------------------------------------------------------------------------------------------------------------
def plot_dataframe(df, symbol):
    pfig, axVolume = plt.subplots()
    plt.bar(df.index, df['5. volume'].values, color='k')
    plt.ylabel('Volume')
    axPrice = axVolume.twinx()
    plt.plot(df.index, df.iloc[:, :-1])
    plt.title(symbol + ' (Time Series)')
    plt.xlim(df.index[0], df.index[-1])
    plt.xlabel('Time')
    plt.ylabel('Share Price ($)')
    plt.legend(df.columns)
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()


# -----------------------------------------------------------------------------------------------------------------------
def main():
    """ Main function of the program
    """ 

    # temporary
    #parser.add_argument('-a', action="store_true", default=False, help='example of flag')
    #parser.add_argument('-b', action="store", dest="b", help='example of string')
    #parser.add_argument('-c', action="store", dest="c", type=int, help='example of int')

    main_parser = argparse.ArgumentParser(prog='stock_market_bot', # program name
                                          # disable default help flag so that help can be an option
                                          add_help=False)

    # Add list of arguments that the main parser accepts
    main_parser.add_argument('cmd', choices=['quit', 'help', 'gainers' ,'view'])

    # Print first welcome message and help
    print("\nWelcome to Didier's Stock Market Bot\n")
    print_help()
    print("\n")

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse main command of the list of possible commands
        try:
            (ns_known_args, l_args) = main_parser.parse_known_args(as_input.split())
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        # ---------------------------------------------------- GAINERS ----------------------------------------------------
        if ns_known_args.cmd == 'gainers':
            parser = argparse.ArgumentParser(prog='gainers', 
                                             description='Show top ticker gainers from Yahoo Finance')
            parser.add_argument('-n', action="store", dest="n_gainers", type=int, default=5, choices=range(1, 25),
                                help='Number of the top gainers stocks to retrieve (default 5)')

            try:
                (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
            except SystemExit:
                print("")
                continue
            
            if l_unknown_args:
                print(f"The following args couldn't be interpreted: {l_unknown_args}")

            df_gainers = pd.read_html('https://finance.yahoo.com/screener/predefined/day_gainers')[0]
            print(df_gainers.head(ns_parser.n_gainers).to_string(index=False))

        # ---------------------------------------------------- VIEW ----------------------------------------------------
        elif ns_known_args.cmd == 'view':
            parser = argparse.ArgumentParser(prog='view', 
                                             description='Given a stock market ticker, allows to see historical data of \
                                                the corresponding stock. Note that the alpha_vantage key is necessary \
                                                for this to work!')
            parser.add_argument('-t', action="store", dest="s_ticker", required=True, help='Stock ticker')
            parser.add_argument('--type', action="store", dest="n_type", type=check_positive, default=4,
                                help='1234 corresponds to types: 1. open; 2. high; 3.low; 4. close \
                                    while 14 corresponds to types: 1.open; 4. close')
            parser.add_argument("-s", "--start", type=s_start_date, dest="start_date",
                                help="The starting date (format YYYY-MM-DD) of the stock")

            try:
                (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
            except SystemExit:
                print("")
                continue
            
            if l_unknown_args:
                print(f"The following args couldn't be interpreted: {l_unknown_args}")

            # Currently only supports daily stocks
            # TODO: Intra-daily perhaps
            ts = TimeSeries(key=cfg.API_KEY,
                            output_format='pandas')
            try:
                df, meta_data = ts.get_daily(symbol=ns_parser.s_ticker,
                                             outputsize='full')     
            except:
                print("Either the ticker or the API_KEY are invalids. Try again!")
                continue   

            # Add function to plot data
            ln_col_idx = [int(x)-1 for x in list(str(ns_parser.n_type))]
            # Check that the types given are not bigger than 3, as there are only 4 types (0-3)
            if len([i for i in ln_col_idx if i > 3]) > 0:
                print("An index bigger than 3 was given, which is wrong. Try again")
                continue

            # Slice dataframe from the starting date YYYY-MM-DD selected
            if ns_parser.s_start_date:
                df = df[ns_parser.s_start_date:]

            ln_col_idx.append(4) # Append last column of df to be filtered which corresponds to: 5. Volume

            plot_dataframe(df.iloc[:, ln_col_idx], ns_parser.s_ticker)
        
            
        # ---------------------------------------------------- HELP ----------------------------------------------------
        elif ns_known_args.cmd == 'help':
            print_help()

        # ---------------------------------------------------- QUIT ----------------------------------------------------
        elif ns_known_args.cmd == 'quit':
            print("Hope you made money today. Good bye my lover, good bye my friend.\n")
            break
            
        else:
            print('Shouldnt see this command!')

        print("\n")

if __name__ == "__main__":
    main()
    