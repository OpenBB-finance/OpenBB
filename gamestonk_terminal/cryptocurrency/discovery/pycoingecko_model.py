"""CoinGecko model"""
__docformat__ = "numpy"

import pandas as pd
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    percent_to_float,
    create_df_index,
    wrap_text_in_df,
)
from gamestonk_terminal.cryptocurrency.pycoingecko_helpers import (
    changes_parser,
    replace_qm,
    clean_row,
    collateral_auditors_parse,
    swap_columns,
    scrape_gecko_data,
    get_btc_price,
    GECKO_BASE_URL,
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


def get_gainers_or_losers(period: str = "1h", typ: str = "gainers") -> pd.DataFrame:
    """Scrape data about top gainers - coins which gain the most in given period and
    top losers - coins that lost the most in given period of time. [Source: CoinGecko]

    Parameters
    ----------
    period: str
        One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    typ: str
        Either "gainers" or "losers"
    Returns
    -------
    pandas.DataFrame
        Top Gainers / Top Losers - coins which gain/lost most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{period}, Url
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
        except (ValueError, TypeError) as e:
            print(e)
        results.append([symbol, name, volume, price, change, url])
    df = pd.DataFrame(
        results,
        columns=[
            "Symbol",
            "Name",
            "Volume",
            "Price",
            f"%Change_{period}",
            "Url",
        ],
    )
    df.index = df.index + 1
    df.reset_index(inplace=True)
    df = df.rename(columns={"index": "Rank"})
    df["Price"] = df["Price"].apply(lambda x: float(x.strip("$").replace(",", "")))
    return df


def get_discovered_coins(category: str = "trending") -> pd.DataFrame:
    """Scrapes data from "https://www.coingecko.com/en/discover" [Source: CoinGecko]
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
        Most voted, most trending, recently added, most positive sentiment coins.
        Columns: Name, Price_BTC, Price_USD, Url
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
            "Name",
            "Price_BTC",
            "Price_USD",
            "Url",
        ],
    )


def get_recently_added_coins() -> pd.DataFrame:
    """Scrape recently added coins on CoinGecko from "https://www.coingecko.com/en/coins/recently_added"
    [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Recently Added Coins on CoinGecko
        Columns: Name, Symbol, Price, Change_1h, Change_24h, Added
    """

    columns = [
        "Name",
        "Symbol",
        "Price",
        "Change_1h",
        "Change_24h",
        "Added",
        "Url",
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
    df.rename(columns={"index": "Rank"}, inplace=True)
    df["Price"] = df["Price"].apply(lambda x: float(x.strip("$").replace(",", "")))
    return df


def get_yield_farms() -> pd.DataFrame:
    """Scrapes yield farms data from "https://www.coingecko.com/en/yield-farming" [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Top Yield Farms
        Columns: Rank, Name, Pool, Audits, Collateral, Value Locked, Return Year, Return Hour
    """

    columns = [
        "Rank",
        "Name",
        "Pool",
        "Audits",
        "Collateral",
        "Value_Locked",
        "Return_Year",
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
    for col in ["Return_Year"]:
        df[col] = df[col].apply(
            lambda x: x.replace(" Yearly", "") if isinstance(x, str) else x
        )
    df["Rank"] = df["Rank"].astype(int)
    df = wrap_text_in_df(df, w=30)
    return df


def get_top_volume_coins() -> pd.DataFrame:
    """Scrapes top coins by trading volume "https://www.coingecko.com/en/coins/high_volume" [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Top Coins by Trading Volume
        Columns: Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap
    """

    columns = [
        "Rank",
        "Name",
        "Symbol",
        "Price",
        "Change_1h",
        "Change_24h",
        "Change_7d",
        "Volume_24h",
        "Market_Cap",
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
    df.drop("Rank", axis=1, inplace=True)
    create_df_index(df, "Rank")
    df["Price"] = df["Price"].apply(lambda x: float(x.strip("$").replace(",", "")))
    return df


def get_top_defi_coins() -> pd.DataFrame:
    """Scrapes top decentralized finance coins "https://www.coingecko.com/en/defi" [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Top Decentralized Finance Coins
        Columns: Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap, Url
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
            "Rank",
            "Name",
            "Symbol",
            "Price",
            "Change_1h",
            "Change_24h",
            "Change_7d",
            "Volume_24h",
            "Market_Cap",
            "Fully Diluted Market Cap",
            "Market Cap to TVL Ratio",
            "Url",
        ],
    )
    df.drop(
        ["Fully Diluted Market Cap", "Market Cap to TVL Ratio"],
        axis=1,
        inplace=True,
    )
    df["Rank"] = df["Rank"].astype(int)
    df["Price"] = df["Price"].apply(lambda x: float(x.strip("$").replace(",", "")))
    return df


def get_top_dexes() -> pd.DataFrame:
    """Scrapes top decentralized exchanges from "https://www.coingecko.com/en/dex" [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Top Decentralized Crypto Exchanges
        Columns: Name, Rank, Volume_24h, Coins, Pairs, Visits, Most_Traded, Market_Share
    """

    columns = [
        "Name",
        "Rank",
        "Volume_24h",
        "Coins",
        "Pairs",
        "Visits",
        "Most_Traded",
        "Market_Share",
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
    df["Name"] = df.iloc[:, 1] + " " + df.iloc[:, 2].replace("N/A", "")
    df.drop(df.columns[1:3], axis=1, inplace=True)
    df = swap_columns(df)
    df.columns = columns
    df["Most_Traded"] = (
        df["Most_Traded"]
        .apply(lambda x: x.split("$")[0])
        .str.replace(",", "", regex=True)
        .str.replace(".", "", regex=True)
    )
    df["Most_Traded"] = df["Most_Traded"].apply(lambda x: None if x.isdigit() else x)
    df["Rank"] = df["Rank"].astype(int)
    df.set_index("Rank", inplace=True)
    return df.reset_index()


def get_top_nfts() -> pd.DataFrame:
    """Scrapes top nfts from "https://www.coingecko.com/en/nft" [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Top NFTs (Non-Fungible Tokens)
        Columns: Rank, Name, Symbol, Price, Change_1d, Change_24h, Change_7d, Market_Cap, Url
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
            "Rank",
            "Name",
            "Symbol",
            "Price",
            "Change_1h",
            "Change_24h",
            "Change_7d",
            "Volume_24h",
            "Market_Cap",
            "Url",
        ],
    )
    df["Rank"] = df["Rank"].astype(int)
    df["Price"] = df["Price"].apply(lambda x: x.strip("$").replace(",", ""))
    return df


def get_coin_list() -> pd.DataFrame:
    """Get list of coins available on CoinGecko [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Coins available on CoinGecko
        Columns: id, symbol, name
    """

    client = CoinGeckoAPI()
    return pd.DataFrame(
        client.get_coins_list(),
        columns=["id", "symbol", "name"],
    ).reset_index()


def get_coins_for_given_exchange(exchange_id: str = "binance", page: int = 1) -> dict:
    """Helper method to get all coins available on binance exchange [Source: CoinGecko]

    Parameters
    ----------
    exchange_id: str
        id of exchange
    page: int
        number of page. One page contains 100 records

    Returns
    -------
    dict
        dictionary with all trading pairs on binance
    """

    client = CoinGeckoAPI()
    binance_coins = client.get_exchanges_tickers_by_id(id=exchange_id, page=page)
    return binance_coins["tickers"]


def get_mapping_matrix_for_exchange(exchange_id: str, pages: int = 12) -> dict:
    """Creates a matrix with all coins available on Binance with corresponding coingecko coin_id. [Source: CoinGecko]

    Parameters
    ----------
    exchange_id: str
        id of exchange: binance
    pages: int
        number of pages. One page contains 100 records

    Returns
    -------
    dict
        dictionary with all coins: {"ETH" : "ethereum"}
    """

    coins_dct = {}
    for i in range(pages):
        coins = get_coins_for_given_exchange(exchange_id=exchange_id, page=i)
        for coin in coins:
            bin_symbol, gecko_id = coin["base"], coin["coin_id"]
            if bin_symbol not in coins_dct:
                coins_dct[bin_symbol] = gecko_id
    return coins_dct
