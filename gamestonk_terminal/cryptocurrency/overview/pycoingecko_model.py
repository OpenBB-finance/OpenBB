"""CoinGecko model"""
__docformat__ = "numpy"

import math
import pandas as pd
import numpy as np
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    wrap_text_in_df,
    create_df_index,
    replace_underscores_in_column_names,
)
from gamestonk_terminal.cryptocurrency.pycoingecko_helpers import (
    replace_qm,
    clean_row,
    scrape_gecko_data,
    GECKO_BASE_URL,
)


client = CoinGeckoAPI()


def get_holdings_overview(endpoint: str = "bitcoin"):
    """Scrapes overview of public companies that holds ethereum or bitcoin
    from "https://www.coingecko.com/en/public-companies-{bitcoin/ethereum}"

    Parameters
    ----------
    endpoint : str
        "bitcoin" or "ethereum"

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    url = f"https://www.coingecko.com/en/public-companies-{endpoint}"
    rows = scrape_gecko_data(url).find_all(
        "span", class_="overview-box d-inline-block p-3 mr-2"
    )
    kpis = {}
    for row in rows:
        row_cleaned = clean_row(row)
        if row_cleaned:
            value, *kpi = row_cleaned
            name = " ".join(kpi)
            kpis[name] = value

    df = pd.Series(kpis).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    df["Metric"] = df["Metric"].apply(
        lambda x: replace_underscores_in_column_names(x) if isinstance(x, str) else x
    )
    return df


def get_companies_assets(endpoint="bitcoin"):
    """Scrapes list of companies that holds ethereum or bitcoin
    from "https://www.coingecko.com/en/public-companies-{bitcoin/ethereum}"

    Parameters
    ----------
    endpoint : str
        "bitcoin" or "ethereum"

    Returns
    -------
    pandas.DataFrame
        Rank, Company, Ticker, Country, Total_Btc, Entry_Value, Today_Value, Pct_Supply, Url
    """
    url = f"https://www.coingecko.com/en/public-companies-{endpoint}"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:
        link = row.find("a")["href"]
        row_cleaned = clean_row(row)
        row_cleaned.append(link)
        results.append(row_cleaned)
    df = pd.DataFrame(
        results,
        columns=[
            "Rank",
            "Company",
            "Ticker",
            "Country",
            "Total_Btc",
            "Entry_Value",
            "Today_Value",
            "Pct_Supply",
            "Url",
        ],
    )
    return df


def get_news(n: int = 100) -> pd.DataFrame:
    """Scrapes news from "https://www.coingecko.com/en/news?page={}"

    Parameters
    ----------
    n: int
        Number of news, by default n=100, one page has 25 news, so 4 pages are scraped.
    Returns
    -------
    pandas.DataFrame:
        Title, Author, Posted, Article
    """

    n_of_pages = (math.ceil(n / 25) + 1) if n else 2
    dfs = []
    for page in range(1, n_of_pages):
        url = f"https://www.coingecko.com/en/news?page={page}"
        rows = scrape_gecko_data(url).find_all("article")
        results = []
        for row in rows:
            header = row.find("header")
            link = header.find("a")["href"]
            text = [t for t in header.text.strip().split("\n") if t not in ["", " "]]
            article = row.find("div", class_="post-body").text.strip()
            title, *by_who = text
            author, posted = " ".join(by_who).split("(")
            posted = posted.strip().replace(")", "")
            results.append([title, author.strip(), posted, article, link])
        dfs.append(
            pd.DataFrame(
                results,
                columns=[
                    "Title",
                    "Author",
                    "Posted",
                    "Article",
                    "Url",
                ],
            )
        )
    df = pd.concat(dfs, ignore_index=True).head(n)
    df.drop("Article", axis=1, inplace=True)
    df.index = df.index + 1
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Index"}, inplace=True)
    return df


def get_top_crypto_categories():
    """Scrapes top crypto categories from "https://www.coingecko.com/en/categories"

    Returns
    -------
    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url
    """
    columns = [
        "Rank",
        "Name",
        "Change_1h",
        "Change_24h",
        "Change_7d",
        "Market_Cap",
        "Volume_24h",
        "Coins",
        "Url",
    ]
    url = "https://www.coingecko.com/en/categories"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:
        url = GECKO_BASE_URL + row.find("a")["href"]
        (
            rank,
            *names,
            change_1h,
            change_24h,
            change_7d,
            market_cap,
            volume,
            n_of_coins,
        ) = row.text.strip().split()
        results.append(
            [
                rank,
                " ".join(names),
                change_1h,
                change_24h,
                change_7d,
                market_cap,
                volume,
                n_of_coins,
                url,
            ]
        )

    df = pd.DataFrame(results, columns=columns)
    df["Rank"] = df["Rank"].astype(int)
    return df


def get_stable_coins():
    """Scrapes stable coins data from "https://www.coingecko.com/en/stablecoins"

    Returns
    -------
    pandas.DataFrame
        Rank, Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d, Url
    """
    columns = [
        "Rank",
        "Name",
        "Symbol",
        "Price",
        "Change_24h",
        "Exchanges",
        "Market_Cap",
        "Change_30d",
        "Url",
    ]
    url = "https://www.coingecko.com/en/stablecoins"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:
        link = GECKO_BASE_URL + row.find("a")["href"]
        row_cleaned = clean_row(row)
        if len(row_cleaned) == 8:
            row_cleaned.append(None)

        (
            rank,
            name,
            *symbols,
            price,
            volume_24h,
            exchanges,
            market_cap,
            change_30d,
        ) = row_cleaned
        symbol = symbols[0] if symbols else symbols
        results.append(
            [
                rank,
                name,
                symbol,
                price,
                volume_24h,
                exchanges,
                market_cap,
                change_30d,
                link,
            ]
        )
    df = replace_qm(pd.DataFrame(results, columns=columns))
    df.drop("Rank", axis=1, inplace=True)
    create_df_index(df, "Rank")
    df["Price"] = df["Price"].apply(lambda x: float(x.strip("$").replace(",", "")))
    return df


def get_nft_of_the_day():
    """Scrapes data about nft of the day.

    Returns
    -------
        pandas.DataFrame
            metric, value
    """
    url = "https://www.coingecko.com/en/nft"
    soup = scrape_gecko_data(url)
    row = soup.find("div", class_="tw-px-4 tw-py-5 sm:tw-p-6")
    try:
        *author, description, _ = clean_row(row)
        if len(author) > 3:
            author, description = author[:3], author[3]
    except (ValueError, IndexError):
        return {}
    df = (
        pd.Series(
            {
                "author": " ".join(author),
                "desc": description,
                "url": GECKO_BASE_URL + row.find("a")["href"],
                "img": row.find("img")["src"],
            }
        )
        .to_frame()
        .reset_index()
    )
    df.columns = ["Metric", "Value"]
    df["Metric"] = df["Metric"].apply(
        lambda x: replace_underscores_in_column_names(x) if isinstance(x, str) else x
    )
    df = wrap_text_in_df(df, w=100)
    return df


def get_nft_market_status():
    """Scrapes overview data of nft markets from "https://www.coingecko.com/en/nft"

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    url = "https://www.coingecko.com/en/nft"
    rows = scrape_gecko_data(url).find_all(
        "span", class_="overview-box d-inline-block p-3 mr-2"
    )
    kpis = {}
    for row in rows:
        value, *kpi = clean_row(row)
        name = " ".join(kpi)
        kpis[name] = value
    df = pd.Series(kpis).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    return df


def get_exchanges():
    """Get list of top exchanges from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC, Url
    """
    df = pd.DataFrame(client.get_exchanges_list(per_page=250))
    df.replace({float(np.NaN): None}, inplace=True)
    df = df[
        [
            "trust_score",
            "id",
            "name",
            "country",
            "year_established",
            "trade_volume_24h_btc",
            "url",
        ]
    ]
    df.columns = [
        "Trust_Score",
        "Id",
        "Name",
        "Country",
        "Year_Established",
        "Trade_Volume_24h_BTC",
        "Url",
    ]
    create_df_index(df, "Rank")
    return df


def get_financial_platforms():
    """Get list of financial platforms from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        Rank, Name, Category, Centralized, Url
    """
    df = pd.DataFrame(client.get_finance_platforms())
    df.drop("facts", axis=1, inplace=True)
    create_df_index(df, "rank")
    df.columns = ["Rank", "Name", "Category", "Centralized", "Url"]
    return df


def get_finance_products():
    """Get list of financial products from CoinGecko API

    Returns
    -------
    pandas.DataFrame
       Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate
    """
    df = pd.DataFrame(
        client.get_finance_products(per_page=250),
        columns=[
            "platform",
            "identifier",
            "supply_rate_percentage",
            "borrow_rate_percentage",
        ],
    )
    df.columns = ["Platform", "Identifier", "Supply_Rate", "Borrow_Rate"]
    create_df_index(df, "Rank")
    return df


def get_indexes():
    """Get list of crypto indexes from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        Name, Id, Market, Last, MultiAsset
    """
    df = pd.DataFrame(client.get_indexes(per_page=250))
    df.columns = ["Name", "Id", "Market", "Last", "MultiAsset"]
    create_df_index(df, "Rank")
    return df


def get_derivatives():
    """Get list of crypto derivatives from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h,

    """
    df = pd.DataFrame(client.get_derivatives(include_tickers="unexpired"))
    df.drop(
        ["index", "last_traded_at", "expired_at", "index_id", "open_interest"],
        axis=1,
        inplace=True,
    )

    df.rename(columns={"price_percentage_change_24h": "pct_change_24h"}, inplace=True)
    create_df_index(df, "rank")
    df["price"] = df["price"].apply(lambda x: float(x.strip("$").replace(",", "")))

    df.columns = [
        "Rank",
        "Market",
        "Symbol",
        "Price",
        "Pct_Change_24h",
        "Contract_Type",
        "Basis",
        "Spread",
        "Funding_Rate",
        "Volume_24h",
    ]
    return df


def get_exchange_rates():
    """Get list of crypto, fiats, commodity exchange rates from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        Index, Name, Unit, Value, Type
    """
    df = pd.DataFrame(client.get_exchange_rates()["rates"]).T.reset_index()
    df.drop("index", axis=1, inplace=True)
    create_df_index(df, "index")
    df.columns = ["Index", "Name", "Unit", "Value", "Type"]
    return df


def get_global_info():
    """Get global statistics about crypto from CoinGecko API like:
        - market cap change
        - number of markets
        - icos
        - number of active crypto

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    results = client.get_global()

    total_mcap = results.pop("market_cap_percentage")
    eth, btc = total_mcap.get("btc"), total_mcap.get("eth")
    for key in ["total_market_cap", "total_volume", "updated_at"]:
        del results[key]
    results["eth_market_cap_in_pct"] = eth
    results["btc_market_cap_in_pct"] = btc
    results["altcoin_market_cap_in_pct"] = 100 - (float(eth) + float(btc))
    df = pd.Series(results).reset_index()
    df.columns = ["Metric", "Value"]
    df["Metric"] = df["Metric"].apply(
        lambda x: replace_underscores_in_column_names(x) if isinstance(x, str) else x
    )
    return df


def get_global_markets_info():
    """Get global statistics about crypto markets from CoinGecko API like:
        Market_Cap, Volume, Market_Cap_Percentage

    Returns
    -------
    pandas.DataFrame
        Market_Cap, Volume, Market_Cap_Percentage
    """
    columns = [
        "Market_Cap",
        "Volume",
        "Market_Cap_Percentage",
    ]
    data = []
    results = client.get_global()
    for key in columns:
        data.append(results.get(key))
    df = pd.DataFrame(data).T
    df.columns = columns
    df.replace({float("nan"): None}, inplace=True)
    return df.reset_index()


def get_global_defi_info():
    """Get global statistics about Decentralized Finances from CoinGecko API like:

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    results = client.get_global_decentralized_finance_defi()
    for key, value in results.items():
        try:
            results[key] = round(float(value), 4)
        except (ValueError, TypeError):
            pass

    df = pd.Series(results).reset_index()
    df.columns = ["Metric", "Value"]
    df["Metric"] = df["Metric"].apply(
        lambda x: replace_underscores_in_column_names(x) if isinstance(x, str) else x
    )
    return df
