import FundamentalAnalysis as fa
import config_bot as cfg
import argparse
from stock_market_helper_funcs import *

# ---------------------------------------------------- RATINGS ----------------------------------------------------
def ratings(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='ratings', 
                                     description=""" Gives information about the rating of a company which includes 
                                                 i.a. the company rating and recommendation as well as ratings based 
                                                 on a variety of ratios.""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_ratings = fa.rating(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        print(df_ratings)
        print("")
    except:
        print("")
