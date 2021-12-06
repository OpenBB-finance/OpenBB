"""Withdrawal Fees model"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import math

from gamestonk_terminal.helper_funcs import get_user_agent

def get_overall_withdrawal_fees(top: int = 100) -> pd.DataFrame:
    """Scrapes top coins withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    top: int
        Number of coins to search, by default n=100, one page has 100 coins, so 1 page is scraped.
    Returns
    -------
    pandas.DataFrame:
        Coin, Lowest, Average, Median, Highest, Exchanges Compared 
    """

    COINS_PER_PAGE = 100
    withdrawal_fees_homepage = BeautifulSoup(
        requests.get(
            "https://withdrawalfees.com/",
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    table = withdrawal_fees_homepage.find_all('table')
    df = pd.read_html(str(table))[0]
    df["Highest"] = df["Highest"].apply(lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})' if '.' in x and isinstance(x, str) else x)
    num_pages = int(math.ceil(top / COINS_PER_PAGE))
    if(num_pages > 1):
        for idx in range(2, num_pages + 1):
            withdrawal_fees_homepage = BeautifulSoup(
                requests.get(
                    f'https://withdrawalfees.com/coins/page/{idx}',
                    headers={"User-Agent": get_user_agent()},
                ).text,
                "lxml",
            )
            table = withdrawal_fees_homepage.find_all('table')
            new_df = pd.read_html(str(table))[0]
            new_df["Highest"] = new_df["Highest"].apply(lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})' if '.' in x else x)
            df = df.append(new_df)
    return df

def get_overall_exchange_withdrawal_fees() -> pd.DataFrame:
    """Scrapes exchange withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    
    Returns
    -------
    pandas.DataFrame:
        Exchange, Coins, Lowest, Average, Median, Highest
    """
    exchange_withdrawal_fees = BeautifulSoup(
        requests.get(
            "https://withdrawalfees.com/exchanges",
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    table = exchange_withdrawal_fees.find_all('table')
    df = pd.read_html(str(table))[0]
    return df


def get_crypto_withdrawal_fees(symbol: str) -> pd.DataFrame:
    """Scrapes coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    symbol: str
        Coin to check withdrawal fees. By default bitcoin
    Returns
    -------
    pandas.DataFrame:
        Exchange, Withdrawal Fee, Minimum Withdrawal Amount
    """
    crypto_withdrawal_fees = BeautifulSoup(
        requests.get(
            f'https://withdrawalfees.com/coins/{symbol}',
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    table = crypto_withdrawal_fees.find_all('table')
    df = pd.read_html(str(table))[0]
    df["Withdrawal Fee"] = df["Withdrawal Fee"].apply(lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})' if '.' in x and isinstance(x, str) else x)
    df["Minimum Withdrawal Amount"] = df["Minimum Withdrawal Amount"].apply(lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})' if isinstance(x, str) and '.' in x else x)
    return df
    
    
def get_crypto_withdrawal_fees_stats(symbol: str) -> pd.DataFrame:
    """Scrapes coin withdrawal fees statistics
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    symbol: str
        Coin to check withdrawal fees. By default bitcoin
    Returns
    -------
    pandas.DataFrame:
        Exchanges, Lowest, Average, Median
    """    
    crypto_withdrawal_fees = BeautifulSoup(
        requests.get(
            f'https://withdrawalfees.com/coins/{symbol}',
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    html_stats = crypto_withdrawal_fees.find("div", { "class" : "details" }).find_all("div", recursive=False)
    stats = [[]]
    for stat in html_stats:
        stats[0].append(stat.find("div", {"class": "value"}).text)
        
    df = pd.DataFrame(stats, columns = ['Exchanges', 'Lowest', 'Average', 'Median'])
    return df