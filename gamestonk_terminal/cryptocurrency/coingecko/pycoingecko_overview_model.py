import math
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import (
    wrap_text_in_df,
    percent_to_float,
    create_df_index,
)
from gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_helpers import (
    changes_parser,
    replace_qm,
    clean_row,
    collateral_auditors_parse,
    swap_columns,
)

PERIODS = {
    "1h": "?time=h1",
    "24h": "?time=h24",
    "7d": "?time=d7",
    "14d": "?time=d14",
    "30d": "?time=d30",
    "60d": "?time=d60",
    "1y": "?time=y1",
}

CATEGORIES = {
    "trending": 0,
    "most_voted": 1,
    "positive_sentiment": 2,
    "recently_added": 3,
    "most_visited": 4,
}

COLUMNS = {
    "id": "id",
    "rank": "rank",
    "name": "name",
    "symbol": "symbol",
    "price": "price",
    "change_1h": "change_1h",
    "change_24h": "change_24h",
    "change_7d": "change_7d",
    "volume_24h": "volume_24h",
    "market_cap": "market_cap",
    "country": "country",
    "total_market_cap": "total_market_cap",
    "total_volume": "total_volume",
    "market_cap_percentage": "market_cap_percentage",
    "company": "company",
    "ticker": "ticker",
    "last_added": "added",
    "title": "title",
    "author": "author",
    "posted": "posted",
    "article": "article",
    "url": "url",
    "price_btc": "price_btc",
    "price_usd": "price_usd",
    "n_of_coins": "n_of_coins",
    "exchanges": "exchanges",
    "change_30d": "change_30d",
}

CHANNELS = {
    "telegram_channel_identifier": "telegram",
    "twitter_screen_name": "twitter",
    "subreddit_url": "subreddit",
    "bitcointalk_thread_identifier": "bitcointalk",
    "facebook_username": "facebook",
    "discord": "discord",
}

BASE_INFO = [
    "id",
    "name",
    "symbol",
    "asset_platform_id",
    "description",
    "contract_address",
    "market_cap_rank",
    "public_interest_score",
]

DENOMINATION = ("usd", "btc", "eth")

client = CoinGeckoAPI()

GECKO_BASE_URL = "https://www.coingecko.com"


def scrape_gecko_data(url: str) -> BeautifulSoup:
    """Helper method that scrape Coin Gecko site.

    Parameters
    ----------
    url : str
        coin gecko url to scrape e.g: "https://www.coingecko.com/en/discover"

    Returns
    -------
        BeautifulSoup object
    """

    req = requests.get(url)
    return BeautifulSoup(req.text, features="lxml")


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
        rank, company, ticker, country, total_btc, entry_value, today_value, pct_of_supply, url
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
            COLUMNS["rank"],
            COLUMNS["company"],
            COLUMNS["ticker"],
            COLUMNS["country"],
            "total_btc",
            "entry_value",
            "today_value",
            "pct_of_supply",
            COLUMNS["url"],
        ],
    )
    return df


def get_gainers_or_losers(period="1h", typ="gainers"):
    """Scrape data about top gainers - coins which gain the most in given period and
    top losers - coins that lost the most in given period of time.

    Parameters
    ----------
    period: str
        One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    typ: str
        Either "gainers" or "losers"
    Returns
    -------
    pandas.DataFrame
        symbol, name, volume, price, change_{period}, url
    """
    category = {
        "gainers": 0,
        "losers": 1,
    }

    if period not in PERIODS:
        raise ValueError(
            f"Wrong time period\nPlease chose one from list: {PERIODS.keys()}"
        )

    url = f"https://www.coingecko.com/en/coins/trending{PERIODS.get(period)}"
    rows = scrape_gecko_data(url).find_all("tbody")[category.get(typ)].find_all("tr")
    results = []
    for row in rows:
        url = GECKO_BASE_URL + row.find("a")["href"]
        symbol, name, *_, volume, price, change = clean_row(row)
        try:
            change = percent_to_float(change)
        except (ValueError, TypeError):
            ...
        results.append([symbol, name, volume, price, change, url])
    df = pd.DataFrame(
        results,
        columns=[
            COLUMNS["symbol"],
            COLUMNS["name"],
            "volume",
            COLUMNS["price"],
            f"%change_{period}",
            COLUMNS["url"],
        ],
    )
    df.index = df.index + 1
    df.reset_index(inplace=True)
    df = df.rename(columns={"index": "rank"})
    return df


def get_btc_price():
    """Get BTC/USD price from CoinGecko API

    Returns
    -------
    str
        latest bitcoin price in usd.
    """
    req = requests.get(
        "https://api.coingecko.com/api/v3/simple/"
        "price?ids=bitcoin&vs_currencies=usd&include_market_cap"
        "=false&include_24hr_vol"
        "=false&include_24hr_change=false&include_last_updated_at=false"
    )
    return req.json()["bitcoin"]["usd"]


def discover_coins(category: str = "trending") -> pd.DataFrame:
    """Scrapes data from "https://www.coingecko.com/en/discover"
        - Most voted coins
        - Most popular coins
        - Recently added coins
        - Most positive sentiment coins
    Parameters
    ----------
    category: str
        - one from list: [trending, most_voted, positive_sentiment,recently_added, most_visited]
    Returns
    -------
    pandas.DataFrame:
        name, price_btc, price_usd, url
    """
    if category not in CATEGORIES:
        raise ValueError(
            f"Wrong category name\nPlease chose one from list: {CATEGORIES.keys()}"
        )
    url = "https://www.coingecko.com/en/discover"
    popular = scrape_gecko_data(url).find_all(
        "div", class_="col-12 col-sm-6 col-md-6 col-lg-4"
    )[CATEGORIES[category]]
    rows = popular.find_all("a")
    results = []
    btc_price = get_btc_price()

    for row in rows:
        name, *_, price = clean_row(row)
        url = GECKO_BASE_URL + row["href"]
        if price.startswith("BTC"):
            price = price.replace("BTC", "").replace(",", ".")

        price_usd = (int(btc_price) * float(price)) if btc_price else None
        results.append([name, price, price_usd, url])
    return pd.DataFrame(
        results,
        columns=[
            COLUMNS["name"],
            COLUMNS["price_btc"],
            COLUMNS["price_usd"],
            COLUMNS["url"],
        ],
    )


def get_news(n: int = 100) -> pd.DataFrame:
    """Scrapes news from "https://www.coingecko.com/en/news?page={}"

    Parameters
    ----------
    n: int
        Number of news, by default n=100, one page has 25 news, so 4 pages are scraped.
    Returns
    -------
    pandas.DataFrame:
        title, author, posted, article
    """

    n_of_pages = (math.ceil(n / 25) + 1) if n else 2
    dfs = []
    for page in range(1, n_of_pages):
        url = f"https://www.coingecko.com/en/news?page={page}"
        rows = scrape_gecko_data(url).find_all(COLUMNS["article"])
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
                    COLUMNS["title"],
                    COLUMNS["author"],
                    COLUMNS["posted"],
                    COLUMNS["article"],
                    COLUMNS["url"],
                ],
            )
        )
    df = pd.concat(dfs, ignore_index=True).head(n)
    df.drop("article", axis=1, inplace=True)
    df.index = df.index + 1
    df.reset_index(inplace=True)
    return df


def get_top_crypto_categories():
    """Scrapes top crypto categories from "https://www.coingecko.com/en/categories"

    Returns
    -------
    pandas.DataFrame
       rank, name, change_1h, change_7d, market_cap, volume_24h, n_of_coins, url
    """
    columns = [
        COLUMNS["rank"],
        COLUMNS["name"],
        COLUMNS["change_1h"],
        COLUMNS["change_24h"],
        COLUMNS["change_7d"],
        COLUMNS["market_cap"],
        COLUMNS["volume_24h"],
        COLUMNS["n_of_coins"],
        COLUMNS["url"],
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
    df["rank"] = df["rank"].astype(int)
    return df


def get_recently_added_coins():
    """Scrape recently added coins on CoinGecko from "https://www.coingecko.com/en/coins/recently_added"

    Returns
    -------
    pandas.DataFrame
        name, symbol, price, change_1h, change_24h, last_added
    """
    columns = [
        COLUMNS["name"],
        COLUMNS["symbol"],
        COLUMNS["price"],
        COLUMNS["change_1h"],
        COLUMNS["change_24h"],
        COLUMNS["last_added"],
        COLUMNS["url"],
    ]

    url = "https://www.coingecko.com/en/coins/recently_added"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []

    for row in rows:
        url = GECKO_BASE_URL + row.find("a")["href"]
        row_cleaned = clean_row(row)
        (
            name,
            symbol,
            _,
            price,
            *changes,
            _,
            _volume,
            last_added,
        ) = row_cleaned
        change_1h, change_24h, _ = changes_parser(changes)
        results.append([name, symbol, price, change_1h, change_24h, last_added, url])
    df = replace_qm(pd.DataFrame(results, columns=columns))
    df.index = df.index + 1
    df.reset_index(inplace=True)
    df.rename(columns={"index": "rank"}, inplace=True)
    return df


def get_stable_coins():
    """Scrapes stable coins data from "https://www.coingecko.com/en/stablecoins"

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, change_24h, exchanges, market_cap, change_30, url
    """
    columns = [
        COLUMNS["rank"],
        COLUMNS["name"],
        COLUMNS["symbol"],
        COLUMNS["price"],
        COLUMNS["change_24h"],
        COLUMNS["exchanges"],
        COLUMNS["market_cap"],
        COLUMNS["change_30d"],
        COLUMNS["url"],
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
    df.drop("rank", axis=1, inplace=True)
    create_df_index(df, "rank")
    return df


def get_yield_farms():
    """Scrapes yield farms data from "https://www.coingecko.com/en/yield-farming"

    Returns
    -------
    pandas.DataFrame
        rank, name, pool, audits, collateral,value_locked, returns_year, returns_hour
    """
    columns = [
        COLUMNS["rank"],
        COLUMNS["name"],
        "pool",
        "audits",
        "collateral",
        "value_locked",
        "return_year",
    ]
    url = "https://www.coingecko.com/en/yield-farming"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:
        row_cleaned = clean_row(row)[:-2]
        if " New" in row_cleaned:  # find better way to fix it in future
            row_cleaned.remove(" New")

        if len(row_cleaned) == 7:
            row_cleaned.insert(2, None)
        (
            rank,
            name,
            pool,
            *others,
            _,
            value_locked,
            apy1,
            _,  # hourly removed for most cases it's 0.00 so it doesn't bring any value for user
        ) = row_cleaned
        auditors, collateral = collateral_auditors_parse(others)
        auditors = ", ".join(aud.strip() for aud in auditors)
        collateral = ", ".join(coll.strip() for coll in collateral)
        results.append(
            [
                rank,
                name,
                pool,
                auditors,
                collateral,
                value_locked,
                apy1,
            ]
        )
    df = pd.DataFrame(results, columns=columns).replace({"": None})
    for col in ["return_year"]:
        df[col] = df[col].apply(
            lambda x: x.replace(" Yearly", "") if isinstance(x, str) else x
        )
    df["rank"] = df["rank"].astype(int)
    df = wrap_text_in_df(df, w=30)
    return df


def get_top_volume_coins():
    """Scrapes top coins by trading volume "https://www.coingecko.com/en/coins/high_volume"

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, change_1h, change_24h, change_7d, volume_24h, market_cap
    """
    columns = [
        COLUMNS["rank"],
        COLUMNS["name"],
        COLUMNS["symbol"],
        COLUMNS["price"],
        COLUMNS["change_1h"],
        COLUMNS["change_24h"],
        COLUMNS["change_7d"],
        COLUMNS["volume_24h"],
        COLUMNS["market_cap"],
    ]
    url = "https://www.coingecko.com/en/coins/high_volume"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:
        row_cleaned = clean_row(row)
        if len(row_cleaned) == 9:
            row_cleaned.insert(0, "?")
        row_cleaned.pop(3)
        results.append(row_cleaned)
    df = replace_qm(pd.DataFrame(results, columns=columns))
    df.drop("rank", axis=1, inplace=True)
    create_df_index(df, "rank")
    return df


def get_top_defi_coins():
    """Scrapes top decentralized finance coins "https://www.coingecko.com/en/defi"

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, change_1h, change_24h, change_7d, volume_24h, market_cap, url
    """
    url = "https://www.coingecko.com/en/defi"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:

        row_cleaned = clean_row(row)
        row_cleaned.pop(2)
        url = GECKO_BASE_URL + row.find("a")["href"]
        row_cleaned.append(url)
        if len(row_cleaned) == 11:
            row_cleaned.insert(4, "?")
        results.append(row_cleaned)

    df = pd.DataFrame(
        results,
        columns=[
            COLUMNS["rank"],
            COLUMNS["name"],
            COLUMNS["symbol"],
            COLUMNS["price"],
            COLUMNS["change_1h"],
            COLUMNS["change_24h"],
            COLUMNS["change_7d"],
            COLUMNS["volume_24h"],
            COLUMNS["market_cap"],
            "fully_diluted_market_cap",
            "market_cap_to_tvl_ratio",
            COLUMNS["url"],
        ],
    )
    df.drop(
        ["fully_diluted_market_cap", "market_cap_to_tvl_ratio"],
        axis=1,
        inplace=True,
    )
    df["rank"] = df["rank"].astype(int)
    return df


def get_top_dexes():
    """Scrapes top decentralized exchanges from "https://www.coingecko.com/en/dex"

    Returns
    -------
    pandas.DataFrame
        name, rank, volume_24h, n_coins, n_pairs, visits, most_traded, market_share_by_vol
    """
    columns = [
        COLUMNS["name"],
        COLUMNS["rank"],
        COLUMNS["volume_24h"],
        "n_coins",
        "n_pairs",
        "visits",
        "most_traded",
        "market_share_by_vol",
    ]
    url = "https://www.coingecko.com/en/dex"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:
        row_cleaned = clean_row(row)
        if " Trading Incentives" in row_cleaned:
            row_cleaned.remove(" Trading Incentives")
        if len(row_cleaned) == 8:
            row_cleaned.insert(-3, "N/A")
        results.append(row_cleaned)
    df = pd.DataFrame(results)
    df[COLUMNS["name"]] = df.iloc[:, 1] + " " + df.iloc[:, 2].replace("N/A", "")
    df.drop(df.columns[1:3], axis=1, inplace=True)
    df = swap_columns(df)
    df.columns = columns
    df["most_traded"] = (
        df["most_traded"]
        .apply(lambda x: x.split("$")[0])
        .str.replace(",", "", regex=True)
        .str.replace(".", "", regex=True)
    )
    df["most_traded"] = df["most_traded"].apply(lambda x: None if x.isdigit() else x)
    df["rank"] = df["rank"].astype(int)
    df.set_index("rank", inplace=True)
    return df.reset_index()


def get_top_nfts():
    """Scrapes top nfts from "https://www.coingecko.com/en/nft"

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, change_1d, change_24h, change_7d, market_cap, url
    """
    url = "https://www.coingecko.com/en/nft"
    rows = scrape_gecko_data(url).find("tbody").find_all("tr")
    results = []
    for row in rows:
        link = GECKO_BASE_URL + row.find("a")["href"]
        row_cleaned = clean_row(row)
        if len(row_cleaned) == 9:
            row_cleaned.insert(5, "N/A")
        row_cleaned.append(link)
        row_cleaned.pop(3)
        results.append(row_cleaned)
    df = pd.DataFrame(
        results,
        columns=[
            COLUMNS["rank"],
            COLUMNS["name"],
            COLUMNS["symbol"],
            COLUMNS["price"],
            COLUMNS["change_1h"],
            COLUMNS["change_24h"],
            COLUMNS["change_7d"],
            COLUMNS["volume_24h"],
            COLUMNS["market_cap"],
            COLUMNS["url"],
        ],
    )
    df["rank"] = df["rank"].astype(int)
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
                COLUMNS["author"]: " ".join(author),
                "desc": description,
                COLUMNS["url"]: GECKO_BASE_URL + row.find("a")["href"],
                "img": row.find("img")["src"],
            }
        )
        .to_frame()
        .reset_index()
    )
    df.columns = ["Metric", "Value"]
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
        trust_score, id, name, country, year_established, trade_volume_24h_btc, url
    """
    df = pd.DataFrame(client.get_exchanges_list(per_page=250))
    df.replace({float(np.NaN): None}, inplace=True)
    df = df[
        [
            "trust_score",
            COLUMNS["id"],
            COLUMNS["name"],
            COLUMNS["country"],
            "year_established",
            "trade_volume_24h_btc",
            COLUMNS["url"],
        ]
    ]
    create_df_index(df, "rank")
    return df


def get_financial_platforms():
    """Get list of financial platforms from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        rank, name, category, centralized, website_url
    """
    df = pd.DataFrame(client.get_finance_platforms())
    df.drop("facts", axis=1, inplace=True)
    create_df_index(df, "rank")
    return df


def get_finance_products():
    """Get list of financial products from CoinGecko API

    Returns
    -------
    pandas.DataFrame
       rank,  platform, identifier, supply_rate_percentage, borrow_rate_percentage
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
    create_df_index(df, "rank")
    return df


def get_indexes():
    """Get list of crypto indexes from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        name, id, market, last, is_multi_asset_composite
    """
    df = pd.DataFrame(client.get_indexes(per_page=250))
    create_df_index(df, "rank")
    return df


def get_derivatives():
    """Get list of crypto derivatives from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        market, symbol, price, pct_change_24h, contract_type, basis, spread, funding_rate, volume_24h
    """
    df = pd.DataFrame(client.get_derivatives(include_tickers="unexpired"))
    df.drop(
        ["index", "last_traded_at", "expired_at", "index_id", "open_interest"],
        axis=1,
        inplace=True,
    )

    df.rename(columns={"price_percentage_change_24h": "pct_change_24h"}, inplace=True)
    create_df_index(df, "rank")
    return df


def get_exchange_rates():
    """Get list of crypto, fiats, commodity exchange rates from CoinGecko API

    Returns
    -------
    pandas.DataFrame
        index, name, unit, value, type
    """
    df = pd.DataFrame(client.get_exchange_rates()["rates"]).T.reset_index()
    df.drop("index", axis=1, inplace=True)
    create_df_index(df, "index")
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
    for key in [COLUMNS["total_market_cap"], COLUMNS["total_volume"], "updated_at"]:
        del results[key]
    results["eth_market_cap_in_pct"] = eth
    results["btc_market_cap_in_pct"] = btc
    results["altcoin_market_cap_in_pct"] = 100 - (float(eth) + float(btc))
    df = pd.Series(results).reset_index()
    df.columns = ["Metric", "Value"]
    return df


def get_global_markets_info():
    """Get global statistics about crypto markets from CoinGecko API like:
        - total_market_cap
        - total_volume
        - market_cap_percentage

    Returns
    -------
    pandas.DataFrame
        total_market_cap, total_volume, market_cap_percentage
    """
    columns = [
        COLUMNS["total_market_cap"],
        COLUMNS["total_volume"],
        COLUMNS["market_cap_percentage"],
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
    return df


def get_coin_list():
    """Get list of coins available on CoinGecko

    Returns
    -------
    pandas.DataFrame
        id, symbol, name
    """

    return pd.DataFrame(
        client.get_coins_list(),
        columns=[COLUMNS["id"], COLUMNS["symbol"], COLUMNS["name"]],
    ).reset_index()
