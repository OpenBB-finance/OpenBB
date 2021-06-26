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
    """Coin class, it holds loaded coin in"""

    def __init__(self, symbol):
        self.client = CoinGeckoAPI()
        self._coin_list = self.client.get_coins_list()
        self.coin_symbol = self._validate_coin(symbol)

        if self.coin_symbol:
            self.coin = self._get_coin_info()

    def __str__(self):
        return f"{self.coin_symbol}"

    def _validate_coin(self, symbol):
        coin = None
        for dct in self._coin_list:
            if symbol.lower() in list(dct.values()):
                coin = dct.get("id")
        if not coin:
            raise ValueError(f"Could not find coin with the given id: {symbol}\n")
        return coin

    def coin_list(self):
        return [token.get("id") for token in self._coin_list]

    def _get_coin_info(self):
        params = dict(localization="false", tickers="false", sparkline=True)
        return self.client.get_coin_by_id(self.coin_symbol, **params)

    def _get_links(self):
        return self.coin.get("links")

    @property
    def repositories(self):
        return self._get_links().get("repos_url")

    @property
    def developers_data(self):
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
        blockchain = self._get_links().get("blockchain_site")
        if blockchain:
            dct = filter_list(blockchain)
            df = pd.Series(dct).to_frame().reset_index()
            df.columns = ["Metric", "Value"]
            return df
        return None

    @property
    def social_media(self):
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
        return self.coin.get("categories")

    def _get_base_market_data_info(self):
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
        prices = self.client.get_coin_market_chart_by_id(
            self.coin_symbol, vs_currency, days, **kwargs
        )
        prices = prices["prices"]
        df = pd.DataFrame(data=prices, columns=["time", "price"])
        df["time"] = pd.to_datetime(df.time, unit="ms")
        df = df.set_index("time")
        df["currency"] = vs_currency
        return df
