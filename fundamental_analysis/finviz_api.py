import finviz
import argparse
from stock_market_helper_funcs import *
import pandas as pd


# ---------------------------------------------------- SCREENER ----------------------------------------------------
def screener(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='screener', 
                                     description="""Gives several metrics about the company. The following fields are expected: 
                                     Company, Sector, Industry, Country, Index, P/E, EPS (ttm), Insider Own, Shs Outstand, Perf Week, 
                                     Market Cap, Forward P/E, EPS next Y, Insider Trans, Shs Float, Perf Month, Income, EPS next Q, 
                                     Inst Own, Short Float, Perf Quarter, Sales, P/S, EPS this Y, Inst Trans, Short Ratio, Perf Half Y, 
                                     Book/sh, P/B, ROA, Target Price, Perf Year, Cash/sh, P/C, ROE, 52W Range, Perf YTD, P/FCF, 
                                     EPS past 5Y, ROI, 52W High, Beta, Quick Ratio, Sales past 5Y, Gross Margin, 52W Low, ATR, Employees, 
                                     Current Ratio, Sales Q/Q, Oper. Margin, RSI (14), Volatility, Optionable, Debt/Eq, EPS Q/Q, 
                                     Profit Margin, Rel Volume, Prev Close, Shortable, LT Debt/Eq, Earnings, Payout, Avg Volume, 
                                     Price, Recom, SMA20, SMA50, SMA200, Volume, Change. [Source: Finviz API]""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        d_finviz_stock = finviz.get_stock(s_ticker)
        df_fa = pd.DataFrame.from_dict(d_finviz_stock, orient='index', columns=['Values'])
        df_fa = df_fa[df_fa.Values != '-']
        print(df_fa.to_string(header=False))

        print("")
        
    except:
        print("")
        return


# ---------------------------------------------------- INSIDER ----------------------------------------------------
def insider(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='insider', 
                                     description="""Gives information about inside traders. The following fields are expected: 
                                     Date, Relationship, Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading, 
                                     SEC Form 4. [Source: Finviz API]""")
        
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10, help='Number of latest inside traders')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        d_finviz_insider = finviz.get_insider(s_ticker)
        df_fa = pd.DataFrame.from_dict(d_finviz_insider)
        df_fa.set_index("Date", inplace=True) 
        df_fa = df_fa[['Relationship', 'Transaction', '#Shares', 'Cost', 'Value ($)', '#Shares Total', 'Insider Trading', 'SEC Form 4']]
        print(df_fa.head(n=ns_parser.n_num))

        print("")

    except:
        print("")
        return


# ---------------------------------------------------- NEWS ----------------------------------------------------
def news(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='news', 
                                     description="""Gives latest news about company. The following fields are expected: 
                                     Title, and http link. [Source: Finviz API]""")
        
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=5, help='Number of latest inside traders')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        d_finviz_news = finviz.get_news(s_ticker)
        i=0
        for s_news_title, s_news_link in {*d_finviz_news}:
            print(f"-> {s_news_title}")
            print(f"{s_news_link}\n")
            i+=1
            
            if i > (ns_parser.n_num-1):
                break

        print("")

    except:
        print("")
        return


# ---------------------------------------------------- ANALYST ----------------------------------------------------
def analyst(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='analyst', 
                                     description="""Gives analyst prices and ratings of the company. The following fields 
                                     are expected: date, analyst, category, price from, price to, and rating.
                                     [Source: Finviz API]""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        d_finviz_analyst_price = finviz.get_analyst_price_targets(s_ticker)
        df_fa = pd.DataFrame.from_dict(d_finviz_analyst_price)
        df_fa.set_index("date", inplace=True) 
        print(df_fa)

        print("")

    except:
        print("")
        return
