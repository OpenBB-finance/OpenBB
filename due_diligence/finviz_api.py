import argparse

import finviz
import pandas as pd
from helper_funcs import check_positive

# ---------------------------------------------------- INSIDER ----------------------------------------------------
def insider(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='insider',
                                     description="""Prints information about inside traders. The following fields are expected:
                                     Date, Relationship, Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading,
                                     SEC Form 4. [Source: Finviz]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10,
                        help='number of latest inside traders.')

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


# ---------------------------------------------------- NEWS ----------------------------------------------------
def news(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='news',
                                     description="""Prints latest news about company, including title and web link.
                                     [Source: Finviz]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=5,
                        help='Number of latest news being printed.')

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



# ---------------------------------------------------- ANALYST ----------------------------------------------------
def analyst(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='analyst',
                                     description="""Print analyst prices and ratings of the company. The following fields
                                     are expected: date, analyst, category, price from, price to, and rating.
                                     [Source: Finviz]""")

    (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
        return

    d_finviz_analyst_price = finviz.get_analyst_price_targets(s_ticker)
    df_fa = pd.DataFrame.from_dict(d_finviz_analyst_price)
    df_fa.set_index("date", inplace=True)
    print(df_fa)
    print("")
