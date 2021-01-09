import argparse
import pandas_ta as ta
from stock_market_helper_funcs import *
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# ----------------------------------------------------- BBANDS -----------------------------------------------------
def bbands(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='bbands', 
                                     description=""" Bollinger Bands consist of three lines. The middle band is a simple 
                                     moving average (generally 20 periods) of the typical price (TP). The upper and lower 
                                     bands are F standard deviations (generally 2) above and below the middle band. 
                                     The bands widen and narrow when the volatility of the price is higher or lower, respectively.
                                     \n \nBollinger Bands do not, in themselves, generate buy or sell signals; they are an 
                                     indicator of overbought or oversold conditions. When the price is near the upper or lower 
                                     band it indicates that a reversal may be imminent. The middle band becomes a support or 
                                     resistance level. The upper and lower bands can also be interpreted as price targets. 
                                     When the price bounces off of the lower band and crosses the middle band, then the 
                                     upper band becomes the price target. """)

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=5, help='length')
    parser.add_argument('-s', "--std", action="store", dest="n_std", type=check_positive, default=2, help='std')
    parser.add_argument('-m', "--mamode", action="store", dest="s_mamode", default="sma", help='mamode')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.bbands(close=df_stock['5. adjusted close'], length=ns_parser.n_length, std=ns_parser.n_std, 
                              mamode=ns_parser.s_mamode, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "BBANDS")
        # Intraday 
        else:
            df_ta = ta.bbands(close=df_stock['4. close'], length=ns_parser.n_length, std=ns_parser.n_std, 
                              mamode=ns_parser.s_mamode, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, "BBANDS")

    except:
        print("")
    