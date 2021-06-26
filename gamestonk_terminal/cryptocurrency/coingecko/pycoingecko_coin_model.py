import pandas as pd
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_helpers import (
    remove_keys,
    filter_list,
    find_discord,
    rename_columns_in_dct,
    create_dictionary_with_prefixes,
)

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


class Coin:
    """Coin class, it holds loaded coin"""

    def __init__(self, symbol):
        self.client = CoinGeckoAPI()
        self._coin_list = self.client.get_coins_list()
        self.coin_symbol = self._validate_coin(symbol)

        if self.coin_symbol:
            self.coin = self._get_coin_info()

    def __str__(self):
        return f"{self.coin_symbol}"

    def _validate_coin(self, symbol):
        """Validate if given coin symbol or id exists in list of available coins on CoinGecko.
        If yes it returns coin id.

        Parameters
        ----------
        symbol: str
            Either coin symbol or coin id

        Returns
        -------
        id of the coin on CoinGecko service.

        """
        coin = None
        for dct in self._coin_list:
            if symbol.lower() in list(dct.values()):
                coin = dct.get("id")
        if not coin:
            raise ValueError(f"Could not find coin with the given id: {symbol}\n")
        return coin

    def coin_list(self):
        """
        Returns
        -------
        list of all available coin ids
        """
        return [token.get("id") for token in self._coin_list]

    def _get_coin_info(self):
        """Helper method which fetch the coin information by id from CoinGecko API like:
         (name, price, market, ... including exchange tickers)

        Returns
        -------
        dict
        """
        params = dict(localization="false", tickers="false", sparkline=True)
        return self.client.get_coin_by_id(self.coin_symbol, **params)

    def _get_links(self):
        """Helper method that extracts links from coin

        Returns
        -------
        dict
        """
        return self.coin.get("links")

    @property
    def repositories(self):
        """Get list of all repositories for given coin

        Returns
        -------
        list with repositories
        """
        return self._get_links().get("repos_url")

    @property
    def developers_data(self):
        """Get coin development data from GitHub or BitBucket like:
            number of pull requests, contributor etc

        Returns
        -------
        pandas.DataFrame
            Metric, Value
        """
        dev = self.coin.get("developer_data")
        useless_keys = (
            "code_additions_deletions_4_weeks",
            "last_4_weeks_commit_activity_series",
        )
        remove_keys(useless_keys, dev)
        df = pd.Series(dev).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def blockchain_explorers(self):
        """Get list of URLs to blockchain explorers for given coin:

        Returns
        -------
        pandas.DataFrame
            Metric, Value
        """
        blockchain = self._get_links().get("blockchain_site")
        if blockchain:
            dct = filter_list(blockchain)
            df = pd.Series(dct).to_frame().reset_index()
            df.columns = ["Metric", "Value"]
            return df
        return None

    @property
    def social_media(self):
        """Get list of URLs to social media like twitter, facebook, reddit...

        Returns
        -------
        pandas.DataFrame
            Metric, Value
        """
        social_dct = {}
        links = self._get_links()
        for (
            channel
        ) in CHANNELS.keys():  # pylint: disable=consider-iterating-dictionary)
            if channel in links:
                value = links.get(channel)
                if channel == "twitter_screen_name":
                    value = "https://twitter.com/" + value
                elif channel == "bitcointalk_thread_identifier" and value is not None:
                    value = f"https://bitcointalk.org/index.php?topic={value}"
                social_dct[channel] = value
        social_dct["discord"] = find_discord(links.get("chat_url"))
        dct = rename_columns_in_dct(social_dct, CHANNELS)
        df = pd.Series(dct).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def websites(self):
        """Get list of URLs to websites like homepage of coin, forum,

        Returns
        -------
        pandas.DataFrame
            Metric, Value
        """
        websites_dct = {}
        links = self._get_links()
        sites = ["homepage", "official_forum_url", "announcement_url"]
        for site in sites:
            websites_dct[site] = filter_list(links.get(site))
        df = pd.Series(websites_dct).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Value"] = df["Value"].apply(lambda x: ",".join(x))
        return df

    @property
    def categories(self):
        """Coins categories
        Returns
        -------
        list/dict
        """
        return self.coin.get("categories")

    def _get_base_market_data_info(self):
        """Helper method that fetches all the base market/price information about given coin

        Returns
        -------
        dict
        """
        market_dct = {}
        market_data = self.coin.get("market_data")
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

    @property
    def base_info(self):
        """Get all the base information about given coin

        Returns
        -------
        pandas.DataFrame
        """
        results = {}
        for attr in BASE_INFO:
            info_obj = self.coin.get(attr)
            if attr == "description":
                info_obj = info_obj.get("en")
            results[attr] = info_obj
        results.update(self._get_base_market_data_info())
        return pd.Series(results).to_frame().reset_index()

    @property
    def market_data(self):
        """Get all the base market information about given coin

        Returns
        -------
        pandas.DataFrame
            Metric,Value
        """
        market_data = self.coin.get("market_data")
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
            print(e)
        df = pd.Series(single_stats).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def all_time_high(self):
        """Get all time high data for given coin

        Returns
        -------
        pandas.DataFrame
            Metric,Value
        """
        market_data = self.coin.get("market_data")
        ath_columns = [
            "current_price",
            "ath",
            "ath_date",
            "ath_change_percentage",
        ]
        results = create_dictionary_with_prefixes(
            ath_columns, market_data, DENOMINATION
        )
        df = pd.Series(results).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def all_time_low(self):
        """Get all time low data for given coin

        Returns
        -------
        pandas.DataFrame
            Metric,Value
        """
        market_data = self.coin.get("market_data")
        ath_columns = [
            "current_price",
            "atl",
            "atl_date",
            "atl_change_percentage",
        ]
        results = create_dictionary_with_prefixes(
            ath_columns, market_data, DENOMINATION
        )
        df = pd.Series(results).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def scores(self):
        """Get different kind of scores for given coin

        Returns
        -------
        pandas.DataFrame
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
            _dct = self.coin.get(col)
            for k, _ in _dct.items():
                nested_stats[k] = _dct.get(k)

        single_stats.update(nested_stats)
        df = pd.Series(single_stats).reset_index()
        df.replace({0: ""}, inplace=True)
        df = df.fillna("")
        df.columns = ["Metric", "Value"]
        return df

    def get_coin_market_chart(self, vs_currency="usd", days=30, **kwargs):
        """Get prices for given coin

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
            time, price, currency
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

    def get_ohlc(self, vs_currency="usd", days=90):
        """Get Open, High, Low, Close prices for given coin

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
            time, price, currency
        """

        prices = self.client.get_coin_ohlc_by_id(self.coin_symbol, vs_currency, days)
        df = pd.DataFrame(data=prices, columns=["time", "open", "high", "low", "close"])
        df["time"] = pd.to_datetime(df.time, unit="ms")
        df = df.set_index("time")
        df["currency"] = vs_currency
        return df
