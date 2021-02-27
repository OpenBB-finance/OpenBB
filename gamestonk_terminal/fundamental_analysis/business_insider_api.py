from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import json
import config_terminal as cfg
from datetime import datetime
import argparse
from rapidfuzz import fuzz


# ---------------------------------------------------- MANAGEMENT ----------------------------------------------------
def management(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='mgmt', 
                                     description="""Print management team. Namely: Name, Title, Information from google and 
                                                    (potentially) Insider Activity page. [Source: Business Insider]""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        url_market_business_insider = f"https://markets.businessinsider.com/stocks/{s_ticker.lower()}-stock"
        text_soup_market_business_insider = BeautifulSoup(requests.get(url_market_business_insider).text, "lxml")

        l_titles = list()
        for s_title in text_soup_market_business_insider.findAll('td', {'class': 'table__td text-right'}):
            if any(c.isalpha() for c in s_title.text.strip()) and ('USD' not in s_title.text.strip()):
                l_titles.append(s_title.text.strip())

        l_names = list()
        for s_name in text_soup_market_business_insider.findAll('td', {'class': 'table__td table--allow-wrap'}):
            l_names.append(s_name.text.strip())
            
        df_management = pd.DataFrame({'Name': l_names[-len(l_titles):], 'Title':l_titles}, columns=['Name','Title'])

        df_management['Info'] = '-'
        df_management['Insider Activity'] = '-'
        df_management = df_management.set_index('Name')

        for s_name in df_management.index:
            df_management.loc[s_name]['Info'] = f"http://www.google.com/search?q={s_name} {s_ticker.upper()}".replace(' ', '%20')

        s_url_base = "https://markets.businessinsider.com"
        for insider in text_soup_market_business_insider.findAll('a', {'onclick':"silentTrackPI()"}):
            for s_name in df_management.index:
                if fuzz.token_set_ratio(s_name, insider.text.strip()) > 70:
                    df_management.loc[s_name]['Insider Activity'] = s_url_base + insider.attrs['href']

        for ind in df_management.index:
            s_name = f"{ind}{(max([len(x) for x in df_management.index])-len(ind))*' '}"
            s_title = f"{df_management['Title'][ind]}{(max([len(x) for x in df_management['Title']])-len(df_management['Title'][ind]))*' '}"
            s_management = f"""{s_name} {s_title} {df_management['Info'][ind]}"""
            print(s_management)
            if df_management['Insider Activity'][ind] not in '-':
                print(f"{df_management['Insider Activity'][ind]}")
            print("")
        
    except:
        print("")
        return
