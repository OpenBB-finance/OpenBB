"""OpenBB Terminal SDK Crypto Controller."""
import logging

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.categories import crypto_sdk_model as model

logger = logging.getLogger(__name__)


class Crypto:
    """OpenBB SDK Crypto Module.

    Submodules:
        `defi`: DeFi Module
        `disc`: Discovery Module
        `dd`: Due Diligence Module
        `onchain`: On-Chain Module
        `ov`: Overview Module
        `tools`: Tools Module

    Attributes:
        `load`: Load Crypto Data
        `find`: Find similar coin by coin name, symbol or id
        `chart`: Display Chart
        `candle`: Display Candlestick Chart
    """

    def __init__(self):
        self.disc = model.CryptoDiscovery()
        self.onchain = model.CryptoOnChain()
        self.ov = model.CryptoOverview()
        self.tools = model.CryptoTools()
        self.load = lib.crypto_helpers.load
        self.find = lib.crypto_helpers.find
        self.chart = lib.crypto_helpers.plot_chart
        self.candles = lib.crypto_helpers.plot_candles

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"    defi={self.defi!r},\n"
            f"    disc={self.disc!r},\n"
            f"    dd={self.dd!r},\n"
            f"    onchain={self.onchain!r},\n"
            f"    ov={self.ov!r},\n"
            f"    tools={self.tools!r},\n)"
        )

    @property
    def dd(self):
        """Crypto Due Diligence Module

        Attributes:
            `active`: Returns active addresses of a certain symbol\n
            `active_view`: Display active addresses of a certain symbol over time\n
            `basic_info`: Basic coin information [Source: CoinPaprika]\n
            `balance_view`: Get account holdings for asset. [Source: Binance]\n
            `balance`: Get account holdings for asset. [Source: Binance]\n
            `binance_available_quotes_for_each_coin`: Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]\n
            `book`: Get order book for currency. [Source: Binance]\n
            `book_view`: Get order book for currency. [Source: Binance]\n
            `btcrb`: Get bitcoin price data\n
            `btcrb_view`: Displays bitcoin rainbow chart\n
            `candles`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
            `candles_view`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
            `cbbook`: Get orders book for chosen trading pair. [Source: Coinbase]\n
            `cbbook_view`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
            `change`: Returns 30d change of the supply held in exchange wallets of a certain symbol.\n
            `change_view`: Display 30d change of the supply held in exchange wallets.\n
            `check_valid_binance_string`: Check if symbol is in defined binance. [Source: Binance]\n
            `close`: Returns the price of a cryptocurrency\n
            `coin`: Get coin by id [Source: CoinPaprika]\n
            `events`: Get all events related to given coin like conferences, start date of futures trading etc.\n
            `events_view`: Get all events for given coin id. [Source: CoinPaprika]\n
            `ex`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
            `ex_view`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
            `exchanges`: Helper method to get all the exchanges supported by ccxt\n
            `trading_pairs`: Helper method that return all trading pairs on binance. Methods ause this data for input for e.g\n  # noqa: E501
            `get_binance_trading_pairs`: Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset\n  # noqa: E501
            `show_available_pairs_for_given_symbol`: Return all available quoted assets for given symbol. [Source: Binance]\n  # noqa: E501
            `stats`: Get 24 hr stats for the product. Volume is in base currency units.\n
            `stats_view`: Get 24 hr stats for the product. Volume is in base currency units.\n
            `trades`: Get last N trades for chosen trading pair. [Source: Coinbase]\n
            `trades_view`: Display last N trades for chosen trading pair. [Source: Coinbase]\n
            `trading_pair_info`: Get information about chosen trading pair. [Source: Coinbase]\n
            `oi`: Returns open interest by exchange for a certain symbol\n
            `oi_view`: Displays open interest by exchange for a certain cryptocurrency\n
            `mkt`: All markets for given coin and currency [Source: CoinPaprika]\n
            `mkt_view`: Get all markets for given coin id. [Source: CoinPaprika]\n
            `twitter`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
            `twitter_view`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
            `ohlc_historical`:\n
            `ps`: Get all most important ticker related information for given coin id [Source: CoinPaprika]\n
            `ps_view`: Get ticker information for single coin [Source: CoinPaprika]\n
            `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
            `news_view`: Display recent posts from CryptoPanic news aggregator platform.\n
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]\n
            `headlines_view`: Sentiment analysis from FinBrain for Cryptocurrencies\n
            `eb`: Returns the total amount of coins held on exchange addresses in units and percentage.\n
            `eb_view`: Display total amount of coins held on exchange addresses in units and percentage.\n
            `nonzero`: Returns addresses with non-zero balance of a certain symbol\n
            `nonzero_view`: Display addresses with non-zero balance of a certain symbol\n
            `get_mt`: Returns available messari timeseries\n
            `get_mt_view`: Display messari timeseries list\n
            `fr`: Returns coin fundraising\n
            `fr_view`: Display coin fundraising\n
            `gov`: Returns coin governance\n
            `gov_view`: Display coin governance\n
            `inv`: Returns coin investors\n
            `inv_view`: Display coin investors\n
            `links`: Returns asset's links\n
            `links_view`: Display coin links\n
            `mcapdom`: Returns market dominance of a coin over time\n
            `mcapdom_view`: Display market dominance of a coin over time\n
            `mt`: Returns messari timeseries\n
            `mt_view`: Display messari timeseries\n
            `pi`: Returns coin product info\n
            `pi_view`: Display project info\n
            `rm`: Returns coin roadmap\n
            `rm_view`: Display coin roadmap\n
            `team`: Returns coin team\n
            `team_view`: Display coin team\n
            `tk`: Returns coin tokenomics\n
            `tk_view`: Display coin tokenomics\n
            `coin_market_chart`: Get prices for given coin. [Source: CoinGecko]\n
            `pr`: Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]\n
            `pr_view`: Displays potential returns of a certain coin. [Source: CoinGecko]\n
            `tokenomics`: Get tokenomics for given coin. [Source: CoinGecko]\n
            `gh`: Returns  a list of developer activity for a given coin and time interval.\n
            `gh_view`: Returns a list of github activity for a given coin and time interval.\n
        """
        return model.CryptoDueDiligence()

    @property
    def defi(self):
        """Crypto Defi related methods

        Attributes:
            `dpi`: Scrapes data from DeFi Pulse with all DeFi Pulse crypto protocols.\n
            `dpi_view`: Displays all DeFi Pulse crypto protocols.\n
            `swaps`: Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]\n
            `swaps_view`: Displays last swaps done on Uniswap\n
            `pools`: Get uniswap pools by volume. [Source: https://thegraph.com/en/]\n
            `pools_view`: Displays uniswap pools by volume.\n
            `tokens`: Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `tokens_view`: Displays tokens trade-able on Uniswap DEX.\n
            `pairs`: Get lastly added trade-able pairs on Uniswap with parameters like:\n
            `pairs_view`: Displays Lastly added pairs on Uniswap DEX.\n
            `stats`: Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `stats_view`: Displays base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `dtvl`: Returns information about historical tvl of a defi protocol.\n
            `dtvl_view`: Displays historical TVL of different dApps\n
            `ldapps`: Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.\n  # noqa: E501
            `ldapps_view`: Display information about listed DeFi protocols, their current TVL and changes to it in\n
            `stvl`: Returns historical values of the total sum of TVLs from all listed protocols.\n
            `stvl_view`: Displays historical values of the total sum of TVLs from all listed protocols.\n
            `gdapps`: Display top dApps (in terms of TVL) grouped by chain.\n
            `gdapps_view`: Display top dApps (in terms of TVL) grouped by chain.\n
            `luna_supply`: Get supply history of the Terra ecosystem\n
            `luna_supply_view`: Display Luna circulating supply stats\n
            `newsletters`: Scrape all substack newsletters from url list.\n
            `newsletters_view`: Display DeFi related substack newsletters.\n
            `aterra`: Returns historical data of an asset in a certain terra address\n
            `aterra_view`: Displays the 30-day history of specified asset in terra address\n
            `ayr`: Displays the 30-day history of the Anchor Yield Reserve.\n
            `ayr_view`: Displays the 30-day history of the Anchor Yield Reserve.\n
            `gacc`: Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gacc_view`: Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gov_proposals`: Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
            `gov_proposals_view`: Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n  # noqa: E501
            `sinfo`: Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]\n
            `sinfo_view`: Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]\n  # noqa: E501
            `sratio`: Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]\n
            `sratio_view`: Display terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]\n
            `sreturn`: Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]\n
            `sreturn_view`: Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]\n
            `validators`: Get information about terra validators [Source: https://fcd.terra.dev/swagger]\n
            `validators_view`: Display information about terra validators [Source: https://fcd.terra.dev/swagger]\n
        """
        return model.CryptoDefi()
