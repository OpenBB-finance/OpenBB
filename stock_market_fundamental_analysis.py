import FundamentalAnalysis as fa
from alpha_vantage.fundamentaldata import FundamentalData
import config_bot as cfg
import argparse
from stock_market_helper_funcs import *
import pandas as pd

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


# ---------------------------------------------------- INCOME_STATEMENT ----------------------------------------------------
def income_statement(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='income', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of latest info')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
    parser.add_argument('--fmp', action="store_true", default=False, dest="b_fmp", help='Use Financial Modeling Prep instead of Alpha Vantage')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        if ns_parser.n_num == 1:
            pd.set_option('display.max_colwidth', -1)
        else:
            pd.options.display.max_colwidth = 40

        # Use Financial Modeling Prep API
        if ns_parser.b_fmp:
            if ns_parser.b_quarter:
                df_fd = fa.income_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
            else:
                df_fd = fa.income_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

            df_fd = df_fd.iloc[:, 0:ns_parser.n_num]
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fd = df_fd.applymap(lambda x: long_number_format(x))
            df_fd.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fd.index.tolist()]
            df_fd.index = [s_val.capitalize() for s_val in df_fd.index]
            df_fd.columns.name = "Fiscal Date Ending"
        # Use Alpha Vantage API
        else:
            fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
            if ns_parser.b_quarter:
                df_fd, d_fd_metadata = fd.get_income_statement_quarterly(symbol=s_ticker)
            else:
                df_fd, d_fd_metadata = fd.get_income_statement_annual(symbol=s_ticker)

            df_fd = df_fd.set_index('fiscalDateEnding')
            df_fd = df_fd.head(n=ns_parser.n_num).T
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fd = df_fd.applymap(lambda x: long_number_format(x))
            df_fd.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fd.index.tolist()]
            df_fd.index = [s_val.capitalize() for s_val in df_fd.index]
            df_fd.columns.name = "Fiscal Date Ending"
        
        print(df_fd)
        print("")
    except:
        print("")
        return

# ---------------------------------------------------- BALANCE_SHEET ----------------------------------------------------
def balance_sheet(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='balance', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
    parser.add_argument('--fmp', action="store_true", default=False, dest="b_fmp", help='Use Financial Modeling Prep instead of Alpha Vantage')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        # Use Financial Modeling Prep API
        if ns_parser.b_fmp:
            if ns_parser.b_quarter:
                df_fd = fa.balance_sheet_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
            else:
                df_fd = fa.balance_sheet_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
            
            df_fd = df_fd.iloc[:, 0:ns_parser.n_num]
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fd = df_fd.applymap(lambda x: long_number_format(x))
            df_fd.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fd.index.tolist()]
            df_fd.index = [s_val.capitalize() for s_val in df_fd.index]
            df_fd.columns.name = "Fiscal Date Ending"

        # Use Alpha Vantage API
        else:
            fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
            if ns_parser.b_quarter:
                df_fd, d_fd_metadata = fd.get_balance_sheet_quarterly(symbol=s_ticker)
            else:
                df_fd, d_fd_metadata = fd.get_balance_sheet_annual(symbol=s_ticker)

            df_fd = df_fd.set_index('fiscalDateEnding')
            df_fd = df_fd.head(n=ns_parser.n_num).T
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fd = df_fd.applymap(lambda x: long_number_format(x))
            df_fd.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fd.index.tolist()]
            df_fd.index = [s_val.capitalize() for s_val in df_fd.index]
            df_fd.columns.name = "Fiscal Date Ending"

        print(df_fd)
        print("")
    except:
        print("")
        return
    

# ---------------------------------------------------- CASH_FLOW ----------------------------------------------------
def cash_flow(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='cash', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
    parser.add_argument('--fmp', action="store_true", default=False, dest="b_fmp", help='Use Financial Modeling Prep instead of Alpha Vantage')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        if ns_parser.n_num == 1:
            pd.set_option('display.max_colwidth', -1)
        else:
            pd.options.display.max_colwidth = 40

        # Use Financial Modeling Prep API
        if ns_parser.b_fmp:
            if ns_parser.b_quarter:
                df_fd = fa.cash_flow_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
            else:
                df_fd = fa.cash_flow_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

            df_fd = df_fd.iloc[:, 0:ns_parser.n_num]
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fd = df_fd.applymap(lambda x: long_number_format(x))
            df_fd.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fd.index.tolist()]
            df_fd.index = [s_val.capitalize() for s_val in df_fd.index]
            df_fd.columns.name = "Fiscal Date Ending"
        # Use Alpha Vantage API
        else:
            fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
            if ns_parser.b_quarter:
                df_fd, d_fd_metadata = fd.get_cash_flow_quarterly(symbol=s_ticker)
            else:
                df_fd, d_fd_metadata = fd.get_cash_flow_annual(symbol=s_ticker)

            df_fd = df_fd.set_index('fiscalDateEnding')
            df_fd = df_fd.head(n=ns_parser.n_num).T
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fd = df_fd.mask(df_fd.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fd = df_fd.applymap(lambda x: long_number_format(x))
            df_fd.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fd.index.tolist()]
            df_fd.index = [s_val.capitalize() for s_val in df_fd.index]
            df_fd.columns.name = "Fiscal Date Ending"

        print(df_fd)
        print("")
    except:
        print("")
        return