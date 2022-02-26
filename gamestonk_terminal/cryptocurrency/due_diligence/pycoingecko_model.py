"""CoinGecko model"""
__docformat__ = "numpy"

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import regex as re
from pycoingecko import CoinGeckoAPI

from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    lambda_replace_underscores_in_column_names,
)
from gamestonk_terminal.cryptocurrency.discovery.pycoingecko_model import read_file_data
from gamestonk_terminal.cryptocurrency.pycoingecko_helpers import (
    DENOMINATION,
    calc_change,
    create_dictionary_with_prefixes,
    filter_list,
    find_discord,
    remove_keys,
    rename_columns_in_dct,
)
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

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


@log_start_end(log=logger)
def get_coin_potential_returns(
    main_coin: str,
    vs: Union[str, None] = None,
    top: Union[int, None] = None,
    price: Union[int, None] = None,
) -> pd.DataFrame:
    """Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]

    Parameters
    ----------
    main_coin   : str
        Coin loaded to check potential returns for (e.g., algorand)
    vs          : str | None
        Coin to compare main_coin with (e.g., bitcoin)
    top         : int | None
        Number of coins with highest market cap to compare main_coin with (e.g., 5)
    price
        Target price of main_coin to check potential returns (e.g., 5)

    Returns
    -------
    pd.DataFrame
            Potential returns data
            Columns: Coin, Current Price, Target Coin, Potential Price, Potential Market Cap ($), Change (%)
    """
    client = CoinGeckoAPI()
    COLUMNS = [
        "Coin",
        "Current Price ($)",
        "Current Market Cap ($)",
        "Target Coin",
        "Potential Price ($)",
        "Potential Market Cap ($)",
        "Change (%)",
    ]
    if top and top > 0:  # user wants to compare with top coins
        data = client.get_price(
            ids=f"{main_coin}",
            vs_currencies="usd",
            include_market_cap=True,
            include_24hr_vol=False,
            include_24hr_change=False,
            include_last_updated_at=False,
        )
        top_coins_data = client.get_coins_markets(
            vs_currency="usd", per_page=top, order="market_cap_desc"
        )
        main_coin_data = data[main_coin]
        diff_arr = []
        for coin in top_coins_data:
            market_cap_difference_percentage = calc_change(
                coin["market_cap"], main_coin_data["usd_market_cap"]
            )
            future_price = main_coin_data["usd"] * (
                1 + market_cap_difference_percentage / 100
            )
            diff_arr.append(
                [
                    main_coin,
                    main_coin_data["usd"],
                    main_coin_data["usd_market_cap"],
                    coin["id"],
                    future_price,
                    coin["market_cap"],
                    market_cap_difference_percentage,
                ]
            )
        return pd.DataFrame(
            data=diff_arr,
            columns=COLUMNS,
        )

    if vs:  # user passed a coin
        data = client.get_price(
            ids=f"{main_coin},{vs}",
            vs_currencies="usd",
            include_market_cap=True,
            include_24hr_vol=False,
            include_24hr_change=False,
            include_last_updated_at=False,
        )
        main_coin_data = data[main_coin]
        vs_coin_data = data[vs]

        if main_coin_data and vs_coin_data:
            market_cap_difference_percentage = calc_change(
                vs_coin_data["usd_market_cap"], main_coin_data["usd_market_cap"]
            )
            future_price = main_coin_data["usd"] * (
                1 + market_cap_difference_percentage / 100
            )
            return pd.DataFrame(
                data=[
                    [
                        main_coin,
                        main_coin_data["usd"],
                        main_coin_data["usd_market_cap"],
                        vs,
                        future_price,
                        vs_coin_data["usd_market_cap"],
                        market_cap_difference_percentage,
                    ]
                ],
                columns=COLUMNS,
            )

    if price and price > 0:  # user passed a price
        data = client.get_price(
            ids=main_coin,
            vs_currencies="usd",
            include_market_cap=True,
            include_24hr_vol=False,
            include_24hr_change=False,
            include_last_updated_at=False,
        )
        main_coin_data = data[main_coin]
        if main_coin_data:
            final_market_cap = (
                main_coin_data["usd_market_cap"] * price / main_coin_data["usd"]
            )
            market_cap_difference_percentage = calc_change(
                final_market_cap, main_coin_data["usd_market_cap"]
            )
            future_price = main_coin_data["usd"] * (
                1 + market_cap_difference_percentage / 100
            )
            return pd.DataFrame(
                data=[
                    [
                        main_coin,
                        main_coin_data["usd"],
                        main_coin_data["usd_market_cap"],
                        "",
                        future_price,
                        final_market_cap,
                        market_cap_difference_percentage,
                    ]
                ],
                columns=COLUMNS,
            )

    return pd.DataFrame()


@log_start_end(log=logger)
def check_coin(coin_id: str):
    coins = read_file_data("coingecko_coins.json")
    for coin in coins:
        if coin["id"] == coin_id:
            return coin["id"]
        if coin["symbol"] == coin_id:
            return coin["id"]
    return None


@log_start_end(log=logger)
def get_coin_market_chart(
    coin_id: str = "", vs_currency: str = "usd", days: int = 30, **kwargs: Any
) -> pd.DataFrame:
    """Get prices for given coin. [Source: CoinGecko]

    Parameters
    ----------
    vs_currency: str
        currency vs which display data
    days: int
        number of days to display the data
    kwargs

    Returns
    -------
    pandas.DataFrame
        Prices for given coin
        Columns: time, price, currency
    """
    client = CoinGeckoAPI()
    prices = client.get_coin_market_chart_by_id(coin_id, vs_currency, days, **kwargs)
    prices = prices["prices"]
    df = pd.DataFrame(data=prices, columns=["time", "price"])
    df["time"] = pd.to_datetime(df.time, unit="ms")
    df = df.set_index("time")
    df["currency"] = vs_currency
    return df


class Coin:
    """Coin class, it holds loaded coin"""

    @log_start_end(log=logger)
    def __init__(self, symbol: str, load_from_api: bool = False):
        self.client = CoinGeckoAPI()
        if load_from_api:
            self._coin_list = self.client.get_coins_list()
        else:
            self._coin_list = read_file_data("coingecko_coins.json")
        self.coin_symbol, self.symbol = self._validate_coin(symbol)

        if self.coin_symbol:
            self.coin: Dict[Any, Any] = self._get_coin_info()

    @log_start_end(log=logger)
    def __str__(self):
        return f"{self.coin_symbol}"

    @log_start_end(log=logger)
    def _validate_coin(self, search_coin: str) -> Tuple[Optional[Any], Optional[Any]]:
        """Validate if given coin symbol or id exists in list of available coins on CoinGecko.
        If yes it returns coin id. [Source: CoinGecko]

        Parameters
        ----------
        symbol: str
            Either coin symbol or coin id

        Returns
        -------
        Tuple[str, str]
            - str with coin
            - str with symbol
        """

        coin = None
        symbol = None
        for dct in self._coin_list:
            if search_coin.lower() in [
                dct["id"],
                dct["symbol"],
            ]:
                coin = dct.get("id")
                symbol = dct.get("symbol")
                return coin, symbol
        raise ValueError(f"Could not find coin with the given id: {search_coin}\n")

    @log_start_end(log=logger)
    def coin_list(self) -> list:
        """List all available coins [Source: CoinGecko]

        Returns
        -------
        list
            list of all available coin ids
        """

        return [token.get("id") for token in self._coin_list]

    @log_start_end(log=logger)
    def _get_coin_info(self) -> dict:
        """Helper method which fetch the coin information by id from CoinGecko API like:
         (name, price, market, ... including exchange tickers) [Source: CoinGecko]

        Returns
        -------
        dict
            Coin information
        """

        params = dict(localization="false", tickers="false", sparkline=True)
        return self.client.get_coin_by_id(self.coin_symbol, **params)

    @log_start_end(log=logger)
    def _get_links(self) -> Dict:
        """Helper method that extracts links from coin [Source: CoinGecko]

        Returns
        -------
        dict
            Links related to coin
        """

        return self.coin.get("links", {})

    @log_start_end(log=logger)
    def get_repositories(self) -> Optional[Any]:
        """Get list of all repositories for given coin [Source: CoinGecko]

        Returns
        -------
        list
            Repositories related to coin
        """

        return self._get_links().get("repos_url")

    @log_start_end(log=logger)
    def get_developers_data(self) -> pd.DataFrame:
        """Get coin development data from GitHub or BitBucket like:
            number of pull requests, contributor etc [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            Developers Data
            Columns: Metric, Value
        """

        dev = self.coin.get("developer_data", {})
        useless_keys = (
            "code_additions_deletions_4_weeks",
            "last_4_weeks_commit_activity_series",
        )
        remove_keys(useless_keys, dev)
        df = pd.Series(dev).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )

        return df[df["Value"].notna()]

    @log_start_end(log=logger)
    def get_blockchain_explorers(self) -> Union[pd.DataFrame, Any]:
        """Get list of URLs to blockchain explorers for given coin. [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            Blockchain Explorers
            Columns: Metric, Value
        """

        blockchain = self._get_links().get("blockchain_site")
        if blockchain:
            dct = filter_list(blockchain)
            df = pd.Series(dct).to_frame().reset_index()
            df.columns = ["Metric", "Value"]
            df["Metric"] = df["Metric"].apply(
                lambda x: lambda_replace_underscores_in_column_names(x)
                if isinstance(x, str)
                else x
            )
            return df[df["Value"].notna()]
        return None

    @log_start_end(log=logger)
    def get_social_media(self) -> pd.DataFrame:
        """Get list of URLs to social media like twitter, facebook, reddit... [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            Urls to social media
            Columns: Metric, Value
        """

        social_dct = {}
        links = self._get_links()
        for (
            channel
        ) in CHANNELS.keys():  # pylint: disable=consider-iterating-dictionary)
            if channel in links:
                value = links.get(channel, "")
                if channel == "twitter_screen_name":
                    value = "https://twitter.com/" + value
                elif channel == "bitcointalk_thread_identifier" and value is not None:
                    value = f"https://bitcointalk.org/index.php?topic={value}"
                social_dct[channel] = value
        social_dct["discord"] = find_discord(links.get("chat_url"))
        dct = rename_columns_in_dct(social_dct, CHANNELS)
        df = pd.Series(dct).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )
        return df[df["Value"].notna()]

    @log_start_end(log=logger)
    def get_websites(self) -> pd.DataFrame:
        """Get list of URLs to websites like homepage of coin, forum. [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            Urls to website, homepage, forum
            Columns: Metric, Value
        """

        websites_dct = {}
        links = self._get_links()
        sites = ["homepage", "official_forum_url", "announcement_url"]
        for site in sites:
            websites_dct[site] = filter_list(links.get(site))
        df = pd.Series(websites_dct).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Value"] = df["Value"].apply(lambda x: ",".join(x))
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )
        return df[df["Value"].notna()]

    @log_start_end(log=logging)
    def get_categories(self) -> Union[Dict[Any, Any], List[Any]]:
        """Coins categories. [Source: CoinGecko]

        Returns
        -------
        list/dict
            Coin categories
        """

        return self.coin.get("categories", {})

    @log_start_end(log=logger)
    def _get_base_market_data_info(self) -> dict:
        """Helper method that fetches all the base market/price information about given coin. [Source: CoinGecko]

        Returns
        -------
        dict
            All market related information for given coin
        """
        market_dct = {}
        market_data = self.coin.get("market_data", {})
        for stat in [
            "total_supply",
            "max_supply",
            "circulating_supply",
            "price_change_percentage_24h",
            "price_change_percentage_7d",
            "price_change_percentage_30d",
        ]:
            market_dct[stat] = market_data.get(stat)
        prices = create_dictionary_with_prefixes(
            ["current_price"], market_data, DENOMINATION
        )
        market_dct.update(prices)
        return market_dct

    @log_start_end(log=logger)
    def get_base_info(self) -> pd.DataFrame:
        """Get all the base information about given coin. [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            Base information about coin
        """

        regx = r'<a href="(.+?)">|</a>'

        results = {}
        for attr in BASE_INFO:
            info_obj = self.coin.get(attr, {})
            if attr == "description":
                info_obj = info_obj.get("en")
                info_obj = re.sub(regx, "", info_obj)
                info_obj = re.sub(r"\r\n\r\n", " ", info_obj)
            results[attr] = info_obj
        results.update(self._get_base_market_data_info())
        df = pd.Series(results).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )

        return df[df["Value"].notna()]

    @log_start_end(log=logger)
    def get_market_data(self) -> pd.DataFrame:
        """Get all the base market information about given coin. [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            Base market information about coin
            Metric,Value
        """

        market_data = self.coin.get("market_data", {})
        market_columns_denominated = [
            "market_cap",
            "fully_diluted_valuation",
            "total_volume",
            "high_24h",
            "low_24h",
        ]
        denominated_data = create_dictionary_with_prefixes(
            market_columns_denominated, market_data, DENOMINATION
        )

        market_single_columns = [
            "market_cap_rank",
            "total_supply",
            "max_supply",
            "circulating_supply",
            "price_change_percentage_24h",
            "price_change_percentage_7d",
            "price_change_percentage_30d",
            "price_change_percentage_60d",
            "price_change_percentage_1y",
            "market_cap_change_24h",
        ]
        single_stats = {}
        for col in market_single_columns:
            single_stats[col] = market_data.get(col)
        single_stats.update(denominated_data)

        try:
            single_stats["circulating_supply_to_total_supply_ratio"] = (
                single_stats["circulating_supply"] / single_stats["total_supply"]
            )
        except (ZeroDivisionError, TypeError) as e:
            logger.exception(str(e))
            console.print(e)
        df = pd.Series(single_stats).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )
        return df[df["Value"].notna()]

    @log_start_end(log=logger)
    def get_all_time_high(self, currency: str = "usd") -> pd.DataFrame:
        """Get all time high data for given coin. [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            All time high price data
            Metric,Value
        """

        market_data = self.coin.get("market_data", {})
        if market_data == {}:
            return pd.DataFrame()
        ath_columns = [
            "current_price",
            "ath",
            "ath_date",
            "ath_change_percentage",
        ]

        results = {}
        for column in ath_columns:
            results[column] = market_data[column].get(currency)

        df = pd.Series(results).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )
        df["Metric"] = df["Metric"].apply(lambda x: x.replace("Ath", "All Time High"))
        df["Metric"] = df["Metric"] + f" {currency.upper()}"
        return df[df["Value"].notna()]

    @log_start_end(log=logger)
    def get_all_time_low(self, currency: str = "usd") -> pd.DataFrame:
        """Get all time low data for given coin. [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            All time low price data
            Metric,Value
        """

        market_data = self.coin.get("market_data", {})
        if market_data == {}:
            return pd.DataFrame()

        ath_columns = [
            "current_price",
            "atl",
            "atl_date",
            "atl_change_percentage",
        ]
        results = {}
        for column in ath_columns:
            results[column] = market_data[column].get(currency)

        df = pd.Series(results).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )
        df["Metric"] = df["Metric"].apply(lambda x: x.replace("Atl", "All Time Low"))
        df["Metric"] = df["Metric"] + f" {currency.upper()}"
        return df[df["Value"].notna()]

    @log_start_end(log=logger)
    def get_scores(self) -> pd.DataFrame:
        """Get different kind of scores for given coin. [Source: CoinGecko]

        Returns
        -------
        pandas.DataFrame
            Social, community, sentiment scores for coin
            Metric,Value
        """

        score_columns = [
            "coingecko_rank",
            "coingecko_score",
            "developer_score",
            "community_score",
            "liquidity_score",
            "sentiment_votes_up_percentage",
            "sentiment_votes_down_percentage",
            "public_interest_score",
            "community_data",
            "public_interest_stats",
        ]

        single_stats = {col: self.coin.get(col) for col in score_columns[:-2]}
        nested_stats = {}
        for col in score_columns[-2:]:
            _dct = self.coin.get(col, {})
            for k, _ in _dct.items():
                nested_stats[k] = _dct.get(k, {})

        single_stats.update(nested_stats)
        df = pd.Series(single_stats).reset_index()
        df.replace({0: ""}, inplace=True)
        df = df.fillna("")
        df.columns = ["Metric", "Value"]

        # pylint: disable=unsupported-assignment-operation
        df["Metric"] = df["Metric"].apply(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x
        )
        return df[df["Value"].notna()]

    @log_start_end(log=logger)
    def get_coin_market_chart(
        self, vs_currency: str = "usd", days: int = 30, **kwargs: Any
    ) -> pd.DataFrame:
        """Get prices for given coin. [Source: CoinGecko]

        Parameters
        ----------
        vs_currency: str
            currency vs which display data
        days: int
            number of days to display the data
        kwargs

        Returns
        -------
        pandas.DataFrame
            Prices for given coin
            Columns: time, price, currency
        """

        prices = self.client.get_coin_market_chart_by_id(
            self.coin_symbol, vs_currency, days, **kwargs
        )
        prices = prices["prices"]
        df = pd.DataFrame(data=prices, columns=["time", "price"])
        df["time"] = pd.to_datetime(df.time, unit="ms")
        df = df.set_index("time")
        df["currency"] = vs_currency
        return df

    @log_start_end(log=logger)
    def get_ohlc(self, vs_currency: str = "usd", days: int = 90) -> pd.DataFrame:
        """Get Open, High, Low, Close prices for given coin. [Source: CoinGecko]

        Parameters
        ----------
        vs_currency: str
            currency vs which display data
        days: int
            number of days to display the data
            on from (1/7/14/30/90/180/365, max)

        Returns
        -------
        pandas.DataFrame
            OHLC data for coin
            Columns: time, price, currency
        """

        prices = self.client.get_coin_ohlc_by_id(self.coin_symbol, vs_currency, days)
        df = pd.DataFrame(data=prices, columns=["time", "open", "high", "low", "close"])
        df["time"] = pd.to_datetime(df.time, unit="ms")
        df = df.set_index("time")
        df["currency"] = vs_currency
        return df
