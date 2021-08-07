import pandas as pd
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import (
    wrap_text_in_df,
    percent_to_float,
    create_df_index,
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


client = CoinGeckoAPI()


def get_gainers_or_losers(period="1h", typ="gainers") -> pd.DataFrame:
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


def get_recently_added_coins() -> pd.DataFrame:
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


def get_yield_farms() -> pd.DataFrame:
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


def get_top_volume_coins() -> pd.DataFrame:
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


def get_top_defi_coins() -> pd.DataFrame:
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


def get_top_dexes() -> pd.DataFrame:
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


def get_top_nfts() -> pd.DataFrame:
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


def get_coin_list() -> pd.DataFrame:
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
