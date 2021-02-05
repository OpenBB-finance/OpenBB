import argparse
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from stock_market_helper_funcs import *

# ---------------------------------------------------- ORDERS ----------------------------------------------------
def orders(l_args):
    parser = argparse.ArgumentParser(prog='orders', description='''Orders by Fidelity customers''')

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10, help='Top orders')
    
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        url_orders = f"https://eresearch.fidelity.com/eresearch/gotoBL/fidelityTopOrders.jhtml"
        text_soup_url_orders = BeautifulSoup(requests.get(url_orders).text, "lxml")
        
        l_orders = list()
        l_orders_vals = list()
        idx = 0
        for orders in text_soup_url_orders.findAll('td', {'class' : ['second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eight']}):
            
            if ((idx+1)%3 == 0) or ((idx+1)%4 == 0) or ((idx+1)%6 == 0):
                l_orders_vals.append(orders.contents[1])
            elif ((idx+1)%5 == 0):
                s_orders = str(orders)
                l_orders_vals.append(s_orders[s_orders.find('title="') + len('title="'): s_orders.find('"/>')])
            else:
                l_orders_vals.append(orders.text.strip())
            
            idx += 1
            
            # Add value to dictionary
            if (idx+1)%8 == 0:
                l_orders.append(l_orders_vals)
                l_orders_vals = list()
                idx = 0

        df_orders = pd.DataFrame(l_orders, columns = ['Symbol', 'Company', 'Price Change', '# Buy Orders', 
                                                'Buy / Sell Ratio', '# Sell Orders', 'Latest News'])

        df_orders = df_orders[['Symbol', 'Buy / Sell Ratio', 'Price Change', 'Company', '# Buy Orders', '# Sell Orders', 'Latest News']]

        print(text_soup_url_orders.findAll('span', {'class' : 'source'})[0].text.capitalize() + ':')

        pd.set_option('display.max_colwidth', -1)
        print(df_orders.head(n=ns_parser.n_num).iloc[:,:-1].to_string(index=False))
        print("")

    except SystemExit:
        print("")
        return
