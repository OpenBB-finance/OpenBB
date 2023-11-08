# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class CryptoRoot(Category):
    """Cryptocurrency Module

    Attributes:
        `candle`: Plot candle chart from dataframe. [Source: Binance]\n
        `chart`: Load data for Technical Analysis\n
        `find`: Find similar coin by coin name,symbol or id.\n
        `load`: Load crypto currency to get data for\n
        `price`: Displays live price from pyth live feed [Source: https://pyth.network/]\n
    """

    _location_path = "crypto"

    def __init__(self):
        super().__init__()
        self.candle = lib.crypto_helpers.plot_candles
        self.chart = lib.crypto_helpers.plot_chart
        self.find = lib.crypto_models.find
        self.load = lib.crypto_helpers.load
        self.price = lib.crypto_pyth_view.display_price


class CryptoDueDiligence(Category):
    """Due Diligence Module.

    Attributes:
        `active`: Returns active addresses of a certain symbol\n
        `active_chart`: Plots active addresses of a certain symbol over time\n
        `all_binance_trading_pairs`: Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset\n
        `ath`: Get all time high for a coin in a given currency\n
        `atl`: Get all time low for a coin in a given currency\n
        `balance`: Get account holdings for asset. [Source: Binance]\n
        `balance_chart`: Prints table showing account holdings for asset. [Source: Binance]\n
        `basic`: Basic coin information [Source: CoinPaprika]\n
        `basic_chart`: Prints table showing basic information for coin. Like:\n
        `binance_available_quotes_for_each_coin`: Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]\n
        `candle`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
        `change`: Returns 30d change of the supply held in exchange wallets of a certain symbol.\n
        `change_chart`: Plots 30d change of the supply held in exchange wallets.\n
        `check_valid_binance_str`: Check if symbol is in defined binance. [Source: Binance]\n
        `close`: Returns the price of a cryptocurrency\n
        `coin`: Get coin by id [Source: CoinPaprika]\n
        `coin_market_chart`: Get prices for given coin. [Source: CoinGecko]\n
        `dev`: Get developer stats for a coin\n
        `eb`: Returns the total amount of coins held on exchange addresses in units and percentage.\n
        `eb_chart`: Plots total amount of coins held on exchange addresses in units and percentage.\n
        `events`: Get all events related to given coin like conferences, start date of futures trading etc.\n
        `events_chart`: Prints table showing all events for given coin id. [Source: CoinPaprika]\n
        `ex`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
        `ex_chart`: Prints table showing all exchanges for given coin id. [Source: CoinPaprika]\n
        `exchanges`: Helper method to get all the exchanges supported by ccxt\n
        `fr`: Returns coin fundraising\n
        `fr_chart`: Display coin fundraising\n
        `get_mt`: Returns available messari timeseries\n
        `get_mt_chart`: Prints table showing messari timeseries list\n
        `gh`: Returns  a list of developer activity for a given coin and time interval.\n
        `gh_chart`: Returns a list of github activity for a given coin and time interval.\n
        `gov`: Returns coin governance\n
        `gov_chart`: Prints table showing coin governance\n
        `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain].\n
        `headlines_chart`: Sentiment analysis from FinBrain for Cryptocurrencies\n
        `inv`: Returns coin investors\n
        `inv_chart`: Prints table showing coin investors\n
        `links`: Returns asset's links\n
        `links_chart`: Prints table showing coin links\n
        `mcapdom`: Returns market dominance of a coin over time\n
        `mcapdom_chart`: Plots market dominance of a coin over time\n
        `mkt`: All markets for given coin and currency [Source: CoinPaprika]\n
        `mkt_chart`: Prints table showing all markets for given coin id. [Source: CoinPaprika]\n
        `mt`: Returns messari timeseries\n
        `mt_chart`: Plots messari timeseries\n
        `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
        `news_chart`: Prints table showing recent posts from CryptoPanic news aggregator platform.\n
        `nonzero`: Returns addresses with non-zero balance of a certain symbol\n
        `nonzero_chart`: Plots addresses with non-zero balance of a certain symbol\n
        `ob`: Returns orderbook for a coin in a given exchange\n
        `ob_chart`: Plots order book for a coin in a given exchange\n
        `oi`: Returns open interest by exchange for a certain symbol\n
        `oi_chart`: Plots open interest by exchange for a certain cryptocurrency\n
        `pi`: Returns coin product info\n
        `pi_chart`: Prints table showing project info\n
        `pr`: Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]\n
        `pr_chart`: Prints table showing potential returns of a certain coin. [Source: CoinGecko]\n
        `ps`: Get all most important ticker related information for given coin id [Source: CoinPaprika]\n
        `ps_chart`: Prints table showing ticker information for single coin [Source: CoinPaprika]\n
        `rm`: Returns coin roadmap\n
        `rm_chart`: Plots coin roadmap\n
        `score`: Get scores for a coin from CoinGecko\n
        `show_available_pairs_for_given_symbol`: Return all available quoted assets for given symbol. [Source: Coinbase]\n
        `social`: Get social media stats for a coin\n
        `stats`: Get 24 hr stats for the product. Volume is in base currency units.\n
        `stats_chart`: Prints table showing 24 hr stats for the product. Volume is in base currency units.\n
        `team`: Returns coin team\n
        `team_chart`: Prints table showing coin team\n
        `tk`: Returns coin tokenomics\n
        `tk_chart`: Plots coin tokenomics\n
        `tokenomics`: Get tokenomics for given coin. [Source: CoinGecko]\n
        `trades`: Returns trades for a coin in a given exchange\n
        `trades_chart`: Prints table showing trades for a coin in a given exchange\n
        `trading_pair_info`: Get information about chosen trading pair. [Source: Coinbase]\n
        `trading_pairs`: Helper method that return all trading pairs on binance. Methods ause this data for input for e.g\n
        `twitter`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
        `twitter_chart`: Prints table showing twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
    """

    _location_path = "crypto.dd"

    def __init__(self):
        super().__init__()
        self.active = lib.crypto_dd_glassnode_model.get_active_addresses
        self.active_chart = lib.crypto_dd_glassnode_view.display_active_addresses
        self.all_binance_trading_pairs = (
            lib.crypto_dd_binance_model.get_all_binance_trading_pairs
        )
        self.ath = lib.crypto_dd_sdk_helper.ath
        self.atl = lib.crypto_dd_sdk_helper.atl
        self.balance = lib.crypto_dd_binance_view.get_balance
        self.balance_chart = lib.crypto_dd_binance_view.display_balance
        self.basic = lib.crypto_dd_coinpaprika_model.basic_coin_info
        self.basic_chart = lib.crypto_dd_coinpaprika_view.display_basic
        self.binance_available_quotes_for_each_coin = (
            lib.crypto_dd_binance_model.get_binance_available_quotes_for_each_coin
        )
        self.candle = lib.crypto_dd_coinbase_model.get_candles
        self.change = lib.crypto_dd_glassnode_model.get_exchange_net_position_change
        self.change_chart = (
            lib.crypto_dd_glassnode_view.display_exchange_net_position_change
        )
        self.check_valid_binance_str = (
            lib.crypto_dd_binance_model.check_valid_binance_str
        )
        self.close = lib.crypto_dd_glassnode_model.get_close_price
        self.coin = lib.crypto_dd_coinpaprika_model.get_coin
        self.coin_market_chart = lib.crypto_dd_pycoingecko_model.get_coin_market_chart
        self.dev = lib.crypto_dd_sdk_helper.dev_stats
        self.eb = lib.crypto_dd_glassnode_model.get_exchange_balances
        self.eb_chart = lib.crypto_dd_glassnode_view.display_exchange_balances
        self.events = lib.crypto_dd_coinpaprika_model.get_coin_events_by_id
        self.events_chart = lib.crypto_dd_coinpaprika_view.display_events
        self.ex = lib.crypto_dd_coinpaprika_model.get_coin_exchanges_by_id
        self.ex_chart = lib.crypto_dd_coinpaprika_view.display_exchanges
        self.exchanges = lib.crypto_dd_ccxt_model.get_exchanges
        self.fr = lib.crypto_dd_messari_model.get_fundraising
        self.fr_chart = lib.crypto_dd_messari_view.display_fundraising
        self.get_mt = lib.crypto_dd_messari_model.get_available_timeseries
        self.get_mt_chart = lib.crypto_dd_messari_view.display_messari_timeseries_list
        self.gh = lib.crypto_dd_santiment_model.get_github_activity
        self.gh_chart = lib.crypto_dd_santiment_view.display_github_activity
        self.gov = lib.crypto_dd_messari_model.get_governance
        self.gov_chart = lib.crypto_dd_messari_view.display_governance
        self.headlines = lib.stocks_ba_finbrain_model.get_sentiment
        self.headlines_chart = (
            lib.crypto_dd_finbrain_view.display_crypto_sentiment_analysis
        )
        self.inv = lib.crypto_dd_messari_model.get_investors
        self.inv_chart = lib.crypto_dd_messari_view.display_investors
        self.links = lib.crypto_dd_messari_model.get_links
        self.links_chart = lib.crypto_dd_messari_view.display_links
        self.mcapdom = lib.crypto_dd_messari_model.get_marketcap_dominance
        self.mcapdom_chart = lib.crypto_dd_messari_view.display_marketcap_dominance
        self.mkt = lib.crypto_dd_coinpaprika_model.get_coin_markets_by_id
        self.mkt_chart = lib.crypto_dd_coinpaprika_view.display_markets
        self.mt = lib.crypto_dd_messari_model.get_messari_timeseries
        self.mt_chart = lib.crypto_dd_messari_view.display_messari_timeseries
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_chart = lib.crypto_dd_cryptopanic_view.display_news
        self.nonzero = lib.crypto_dd_glassnode_model.get_non_zero_addresses
        self.nonzero_chart = lib.crypto_dd_glassnode_view.display_non_zero_addresses
        self.ob = lib.crypto_dd_ccxt_model.get_orderbook
        self.ob_chart = lib.crypto_dd_ccxt_view.display_order_book
        self.oi = lib.crypto_dd_coinglass_model.get_open_interest_per_exchange
        self.oi_chart = lib.crypto_dd_coinglass_view.display_open_interest
        self.pi = lib.crypto_dd_messari_model.get_project_product_info
        self.pi_chart = lib.crypto_dd_messari_view.display_project_info
        self.pr = lib.crypto_dd_pycoingecko_model.get_coin_potential_returns
        self.pr_chart = lib.crypto_dd_pycoingecko_view.display_coin_potential_returns
        self.ps = lib.crypto_dd_coinpaprika_model.get_tickers_info_for_coin
        self.ps_chart = lib.crypto_dd_coinpaprika_view.display_price_supply
        self.rm = lib.crypto_dd_messari_model.get_roadmap
        self.rm_chart = lib.crypto_dd_messari_view.display_roadmap
        self.score = lib.crypto_dd_sdk_helper.score
        self.show_available_pairs_for_given_symbol = (
            lib.crypto_dd_coinbase_model.show_available_pairs_for_given_symbol
        )
        self.social = lib.crypto_dd_sdk_helper.social
        self.stats = lib.crypto_dd_coinbase_model.get_product_stats
        self.stats_chart = lib.crypto_dd_coinbase_view.display_stats
        self.team = lib.crypto_dd_messari_model.get_team
        self.team_chart = lib.crypto_dd_messari_view.display_team
        self.tk = lib.crypto_dd_messari_model.get_tokenomics
        self.tk_chart = lib.crypto_dd_messari_view.display_tokenomics
        self.tokenomics = lib.crypto_dd_pycoingecko_model.get_coin_tokenomics
        self.trades = lib.crypto_dd_ccxt_model.get_trades
        self.trades_chart = lib.crypto_dd_ccxt_view.display_trades
        self.trading_pair_info = lib.crypto_dd_coinbase_model.get_trading_pair_info
        self.trading_pairs = lib.crypto_dd_binance_model._get_trading_pairs
        self.twitter = lib.crypto_dd_coinpaprika_model.get_coin_twitter_timeline
        self.twitter_chart = lib.crypto_dd_coinpaprika_view.display_twitter


class CryptoDeFi(Category):
    """DeFi Module.

    Attributes:
        `anchor_data`: Returns anchor protocol earnings data of a certain terra address\n
        `anchor_data_chart`: Plots anchor protocol earnings data of a certain terra address\n
        `aterra`: Returns historical data of an asset in a certain terra address\n
        `aterra_chart`: Plots the 30-day history of specified asset in terra address\n
        `ayr`: Displays the 30-day history of the Anchor Yield Reserve.\n
        `ayr_chart`: Plots the 30-day history of the Anchor Yield Reserve.\n
        `dtvl`: Returns information about historical tvl of a defi protocol.\n
        `dtvl_chart`: Plots historical TVL of different dApps\n
        `gacc`: Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
        `gacc_chart`: Plots terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
        `gdapps`: Display top dApps (in terms of TVL) grouped by chain.\n
        `gdapps_chart`: Plots top dApps (in terms of TVL) grouped by chain.\n
        `gov_proposals`: Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
        `gov_proposals_chart`: Prints table showing terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
        `ldapps`: Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.\n
        `ldapps_chart`: Prints table showing information about listed DeFi protocols, their current TVL and changes to it in\n
        `luna_supply`: Get supply history of the Terra ecosystem\n
        `luna_supply_chart`: Plots and prints table showing Luna circulating supply stats\n
        `newsletters`: Scrape all substack newsletters from url list.\n
        `newsletters_chart`: Prints table showing DeFi related substack newsletters.\n
        `sinfo`: Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]\n
        `sinfo_chart`: Prints table showing staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]\n
        `sratio`: Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]\n
        `sratio_chart`: Plots terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]\n
        `sreturn`: Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]\n
        `sreturn_chart`: Plots terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]\n
        `stvl`: Returns historical values of the total sum of TVLs from all listed protocols.\n
        `stvl_chart`: Plots historical values of the total sum of TVLs from all listed protocols.\n
        `validators`: Get information about terra validators [Source: https://fcd.terra.dev/swagger]\n
        `validators_chart`: Prints table showing information about terra validators [Source: https://fcd.terra.dev/swagger]\n
        `vaults`: Get DeFi Vaults Information. DeFi Vaults are pools of funds with an assigned strategy which main goal is to\n
        `vaults_chart`: Prints table showing Top DeFi Vaults - pools of funds with an assigned strategy which main goal is to\n
    """

    _location_path = "crypto.defi"

    def __init__(self):
        super().__init__()
        self.anchor_data = lib.crypto_defi_cryptosaurio_model.get_anchor_data
        self.anchor_data_chart = lib.crypto_defi_cryptosaurio_view.display_anchor_data
        self.aterra = (
            lib.crypto_defi_terraengineer_model.get_history_asset_from_terra_address
        )
        self.aterra_chart = (
            lib.crypto_defi_terraengineer_view.display_terra_asset_history
        )
        self.ayr = lib.crypto_defi_terraengineer_model.get_anchor_yield_reserve
        self.ayr_chart = lib.crypto_defi_terraengineer_view.display_anchor_yield_reserve
        self.dtvl = lib.crypto_defi_llama_model.get_defi_protocol
        self.dtvl_chart = lib.crypto_defi_llama_view.display_historical_tvl
        self.gacc = lib.crypto_defi_terramoney_fcd_model.get_account_growth
        self.gacc_chart = lib.crypto_defi_terramoney_fcd_view.display_account_growth
        self.gdapps = lib.crypto_defi_llama_model.get_grouped_defi_protocols
        self.gdapps_chart = lib.crypto_defi_llama_view.display_grouped_defi_protocols
        self.gov_proposals = lib.crypto_defi_terramoney_fcd_model.get_proposals
        self.gov_proposals_chart = (
            lib.crypto_defi_terramoney_fcd_view.display_gov_proposals
        )
        self.ldapps = lib.crypto_defi_llama_model.get_defi_protocols
        self.ldapps_chart = lib.crypto_defi_llama_view.display_defi_protocols
        self.luna_supply = lib.crypto_defi_smartstake_model.get_luna_supply_stats
        self.luna_supply_chart = (
            lib.crypto_defi_smartstake_view.display_luna_circ_supply_change
        )
        self.newsletters = lib.crypto_defi_substack_model.get_newsletters
        self.newsletters_chart = lib.crypto_defi_substack_view.display_newsletters
        self.sinfo = lib.crypto_defi_terramoney_fcd_model.get_staking_account_info
        self.sinfo_chart = (
            lib.crypto_defi_terramoney_fcd_view.display_account_staking_info
        )
        self.sratio = lib.crypto_defi_terramoney_fcd_model.get_staking_ratio_history
        self.sratio_chart = (
            lib.crypto_defi_terramoney_fcd_view.display_staking_ratio_history
        )
        self.sreturn = lib.crypto_defi_terramoney_fcd_model.get_staking_returns_history
        self.sreturn_chart = (
            lib.crypto_defi_terramoney_fcd_view.display_staking_returns_history
        )
        self.stvl = lib.crypto_defi_llama_model.get_defi_tvl
        self.stvl_chart = lib.crypto_defi_llama_view.display_defi_tvl
        self.validators = lib.crypto_defi_terramoney_fcd_model.get_validators
        self.validators_chart = lib.crypto_defi_terramoney_fcd_view.display_validators
        self.vaults = lib.crypto_defi_coindix_model.get_defi_vaults
        self.vaults_chart = lib.crypto_defi_coindix_view.display_defi_vaults


class CryptoDiscovery(Category):
    """Discovery Module.

    Attributes:
        `categories_keys`: Get list of categories keys\n
        `coin_list`: Get list of coins available on CoinGecko [Source: CoinGecko]\n
        `coins`: Get N coins from CoinGecko [Source: CoinGecko]\n
        `coins_chart`: Prints table showing top coins [Source: CoinGecko]\n
        `coins_for_given_exchange`: Helper method to get all coins available on binance exchange [Source: CoinGecko]\n
        `cpsearch`: Search CoinPaprika. [Source: CoinPaprika]\n
        `cpsearch_chart`: Prints table showing Search over CoinPaprika. [Source: CoinPaprika]\n
        `dapp_categories`: Get dapp categories [Source: https://dappradar.com/]\n
        `dapp_categories_chart`: Prints table showing dapp categories [Source: https://dappradar.com/]\n
        `dapp_chains`: Get dapp chains [Source: https://dappradar.com/]\n
        `dapp_chains_chart`: Prints table showing dapp chains [Source: https://dappradar.com/]\n
        `dapp_metrics`: Get dapp metrics [Source: https://dappradar.com/]\n
        `dapp_metrics_chart`: Prints table showing dapp metrics [Source: https://dappradar.com/]\n
        `dapps`: Get dapps [Source: https://dappradar.com/]\n
        `dapps_chart`: Prints table showing dapps [Source: https://dappradar.com/]\n
        `defi_chains`: Get defi chains [Source: https://dappradar.com/]\n
        `defi_chains_chart`: Prints table showing defi chains [Source: https://dappradar.com/]\n
        `fees`: Show cryptos with most fees. [Source: CryptoStats]\n
        `fees_chart`: Display crypto with most fees paid [Source: CryptoStats]\n
        `gainers`: Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
        `gainers_chart`: Prints table showing Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
        `losers`: Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]\n
        `losers_chart`: Prints table showing Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]\n
        `nft_mktp`: Get top nft collections [Source: https://dappradar.com/]\n
        `nft_mktp_chart`: Prints table showing nft marketplaces [Source: https://dappradar.com/]\n
        `nft_mktp_chains`: Get nft marketplaces chains [Source: https://dappradar.com/]\n
        `nft_mktp_chains_chart`: Prints table showing nft marketplaces chains [Source: https://dappradar.com/]\n
        `tokens`: Get chains that support tokens [Source: https://dappradar.com/]\n
        `tokens_chart`: Prints table showing chains that support tokens [Source: https://dappradar.com/]\n
        `top_coins`: Get top cryptp coins.\n
        `trending`: Returns trending coins [Source: CoinGecko]\n
        `trending_chart`: Prints table showing trending coins [Source: CoinGecko]\n
    """

    _location_path = "crypto.disc"

    def __init__(self):
        super().__init__()
        self.categories_keys = lib.crypto_disc_pycoingecko_model.get_categories_keys
        self.coin_list = lib.crypto_disc_pycoingecko_model.get_coin_list
        self.coins = lib.crypto_disc_pycoingecko_model.get_coins
        self.coins_chart = lib.crypto_disc_pycoingecko_view.display_coins
        self.coins_for_given_exchange = (
            lib.crypto_disc_pycoingecko_model.get_coins_for_given_exchange
        )
        self.cpsearch = lib.crypto_disc_coinpaprika_model.get_search_results
        self.cpsearch_chart = lib.crypto_disc_coinpaprika_view.display_search_results
        self.dapp_categories = lib.crypto_disc_dappradar_model.get_dapp_categories
        self.dapp_categories_chart = (
            lib.crypto_disc_dappradar_view.display_dapp_categories
        )
        self.dapp_chains = lib.crypto_disc_dappradar_model.get_dapp_chains
        self.dapp_chains_chart = lib.crypto_disc_dappradar_view.display_dapp_chains
        self.dapp_metrics = lib.crypto_disc_dappradar_model.get_dapp_metrics
        self.dapp_metrics_chart = lib.crypto_disc_dappradar_view.display_dapp_metrics
        self.dapps = lib.crypto_disc_dappradar_model.get_dapps
        self.dapps_chart = lib.crypto_disc_dappradar_view.display_dapps
        self.defi_chains = lib.crypto_disc_dappradar_model.get_defi_chains
        self.defi_chains_chart = lib.crypto_disc_dappradar_view.display_defi_chains
        self.fees = lib.crypto_disc_cryptostats_model.get_fees
        self.fees_chart = lib.crypto_disc_cryptostats_view.display_fees
        self.gainers = lib.crypto_disc_pycoingecko_model.get_gainers
        self.gainers_chart = lib.crypto_disc_pycoingecko_view.display_gainers
        self.losers = lib.crypto_disc_pycoingecko_model.get_losers
        self.losers_chart = lib.crypto_disc_pycoingecko_view.display_losers
        self.nft_mktp = lib.crypto_disc_dappradar_model.get_nft_marketplaces
        self.nft_mktp_chart = lib.crypto_disc_dappradar_view.display_nft_marketplaces
        self.nft_mktp_chains = (
            lib.crypto_disc_dappradar_model.get_nft_marketplace_chains
        )
        self.nft_mktp_chains_chart = (
            lib.crypto_disc_dappradar_view.display_nft_marketplace_chains
        )
        self.tokens = lib.crypto_disc_dappradar_model.get_token_chains
        self.tokens_chart = lib.crypto_disc_dappradar_view.display_token_chains
        self.top_coins = lib.crypto_disc_sdk_helpers.top_coins
        self.trending = lib.crypto_disc_pycoingecko_model.get_trending_coins
        self.trending_chart = lib.crypto_disc_pycoingecko_view.display_trending


class CryptoNFT(Category):
    """NFT Module.

    Attributes:
        `collections`: Get nft collections [Source: https://nftpricefloor.com/]\n
        `collections_chart`: Display NFT collections. [Source: https://nftpricefloor.com/]\n
        `fp`: Get nft collections [Source: https://nftpricefloor.com/]\n
        `fp_chart`: Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]\n
        `stats`: Get stats of a nft collection [Source: opensea.io]\n
        `stats_chart`: Prints table showing collection stats. [Source: opensea.io]\n
    """

    _location_path = "crypto.nft"

    def __init__(self):
        super().__init__()
        self.collections = lib.crypto_nft_pricefloor_model.get_collections
        self.collections_chart = lib.crypto_nft_pricefloor_view.display_collections
        self.fp = lib.crypto_nft_pricefloor_model.get_floor_price
        self.fp_chart = lib.crypto_nft_pricefloor_view.display_floor_price
        self.stats = lib.crypto_nft_opensea_model.get_collection_stats
        self.stats_chart = lib.crypto_nft_opensea_view.display_collection_stats


class CryptoOnChain(Category):
    """OnChain Module.

    Attributes:
        `baas`: Get an average bid and ask prices, average spread for given crypto pair for chosen time period.\n
        `baas_chart`: Prints table showing an average bid and ask prices, average spread for given crypto pair for chosen\n
        `balance`: Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which\n
        `balance_chart`: Display info about tokens for given ethereum blockchain balance e.g. ETH balance,\n
        `btc_supply`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
        `btc_supply_chart`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
        `btc_transac`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
        `btc_transac_chart`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
        `btcsingleblock`: Returns BTC block data in json format. [Source: https://blockchain.info/]\n
        `btcsingleblock_chart`: Returns BTC block data. [Source: https://api.blockchain.info/]\n
        `dex_trades_monthly`: Get list of trades on Decentralized Exchanges monthly aggregated.\n
        `dvcp`: Get daily volume for given pair [Source: https://graphql.bitquery.io/]\n
        `dvcp_chart`: Prints table showing daily volume for given pair\n
        `erc20_tokens`: Helper method that loads ~1500 most traded erc20 token.\n
        `gwei`: Returns the most recent Ethereum gas fees in gwei\n
        `gwei_chart`: Current gwei fees\n
        `hist`: Get information about balance historical transactions. [Source: Ethplorer]\n
        `hist_chart`: Display information about balance historical transactions. [Source: Ethplorer]\n
        `holders`: Get info about top token holders. [Source: Ethplorer]\n
        `holders_chart`: Display info about top ERC20 token holders. [Source: Ethplorer]\n
        `hr`: Returns dataframe with mean hashrate of btc or eth blockchain and symbol price\n
        `hr_chart`: Plots dataframe with mean hashrate of btc or eth blockchain and symbol price.\n
        `info`: Get info about ERC20 token. [Source: Ethplorer]\n
        `info_chart`: Display info about ERC20 token. [Source: Ethplorer]\n
        `lt`: Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]\n
        `lt_chart`: Prints table showing Trades on Decentralized Exchanges aggregated by DEX or Month\n
        `prices`: Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]\n
        `prices_chart`: Display token historical prices with volume and market cap, and average price.\n
        `query_graph`: Helper methods for querying graphql api. [Source: https://bitquery.io/]\n
        `th`: Get info about token historical transactions. [Source: Ethplorer]\n
        `th_chart`: Display info about token history. [Source: Ethplorer]\n
        `token_decimals`: Helper methods that gets token decimals number. [Source: Ethplorer]\n
        `top`: Get top 50 tokens. [Source: Ethplorer]\n
        `top_chart`: Display top ERC20 tokens [Source: Ethplorer]\n
        `topledger`: Returns Topledger's Data for the given Organization's Slug[org_slug] based\n
        `topledger_chart`: Display on-chain data from Topledger. [Source: Topledger]\n
        `ttcp`: Get most traded crypto pairs on given decentralized exchange in chosen time period.\n
        `ttcp_chart`: Prints table showing most traded crypto pairs on given decentralized exchange in chosen time period.\n
        `tv`: Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]\n
        `tv_chart`: Prints table showing token volume on different Decentralized Exchanges.\n
        `tx`: Get info about transaction. [Source: Ethplorer]\n
        `tx_chart`: Display info about transaction. [Source: Ethplorer]\n
        `ueat`: Get number of unique ethereum addresses which made a transaction in given time interval.\n
        `ueat_chart`: Prints table showing number of unique ethereum addresses which made a transaction in given time interval\n
        `whales`: Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.\n
        `whales_chart`: Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]\n
    """

    _location_path = "crypto.onchain"

    def __init__(self):
        super().__init__()
        self.baas = lib.crypto_onchain_bitquery_model.get_spread_for_crypto_pair
        self.baas_chart = (
            lib.crypto_onchain_bitquery_view.display_spread_for_crypto_pair
        )
        self.balance = lib.crypto_onchain_ethplorer_model.get_address_info
        self.balance_chart = lib.crypto_onchain_ethplorer_view.display_address_info
        self.btc_supply = lib.crypto_onchain_blockchain_model.get_btc_circulating_supply
        self.btc_supply_chart = (
            lib.crypto_onchain_blockchain_view.display_btc_circulating_supply
        )
        self.btc_transac = (
            lib.crypto_onchain_blockchain_model.get_btc_confirmed_transactions
        )
        self.btc_transac_chart = (
            lib.crypto_onchain_blockchain_view.display_btc_confirmed_transactions
        )
        self.btcsingleblock = lib.crypto_onchain_blockchain_model.get_btc_single_block
        self.btcsingleblock_chart = (
            lib.crypto_onchain_blockchain_view.display_btc_single_block
        )
        self.dex_trades_monthly = (
            lib.crypto_onchain_bitquery_model.get_dex_trades_monthly
        )
        self.dvcp = (
            lib.crypto_onchain_bitquery_model.get_daily_dex_volume_for_given_pair
        )
        self.dvcp_chart = (
            lib.crypto_onchain_bitquery_view.display_daily_volume_for_given_pair
        )
        self.erc20_tokens = lib.crypto_onchain_bitquery_model.get_erc20_tokens
        self.gwei = lib.crypto_onchain_ethgasstation_model.get_gwei_fees
        self.gwei_chart = lib.crypto_onchain_ethgasstation_view.display_gwei_fees
        self.hist = lib.crypto_onchain_ethplorer_model.get_address_history
        self.hist_chart = lib.crypto_onchain_ethplorer_view.display_address_history
        self.holders = lib.crypto_onchain_ethplorer_model.get_top_token_holders
        self.holders_chart = lib.crypto_onchain_ethplorer_view.display_top_token_holders
        self.hr = lib.crypto_dd_glassnode_model.get_hashrate
        self.hr_chart = lib.crypto_dd_glassnode_view.display_hashrate
        self.info = lib.crypto_onchain_ethplorer_model.get_token_info
        self.info_chart = lib.crypto_onchain_ethplorer_view.display_token_info
        self.lt = lib.crypto_onchain_bitquery_model.get_dex_trades_by_exchange
        self.lt_chart = lib.crypto_onchain_bitquery_view.display_dex_trades
        self.prices = lib.crypto_onchain_ethplorer_model.get_token_historical_price
        self.prices_chart = (
            lib.crypto_onchain_ethplorer_view.display_token_historical_prices
        )
        self.query_graph = lib.crypto_onchain_bitquery_model.query_graph
        self.th = lib.crypto_onchain_ethplorer_model.get_token_history
        self.th_chart = lib.crypto_onchain_ethplorer_view.display_token_history
        self.token_decimals = lib.crypto_onchain_ethplorer_model.get_token_decimals
        self.top = lib.crypto_onchain_ethplorer_model.get_top_tokens
        self.top_chart = lib.crypto_onchain_ethplorer_view.display_top_tokens
        self.topledger = lib.crypto_onchain_topledger_model.get_topledger_data
        self.topledger_chart = lib.crypto_onchain_topledger_view.display_topledger_data
        self.ttcp = lib.crypto_onchain_bitquery_model.get_most_traded_pairs
        self.ttcp_chart = lib.crypto_onchain_bitquery_view.display_most_traded_pairs
        self.tv = lib.crypto_onchain_bitquery_model.get_token_volume_on_dexes
        self.tv_chart = lib.crypto_onchain_bitquery_view.display_dex_volume_for_token
        self.tx = lib.crypto_onchain_ethplorer_model.get_tx_info
        self.tx_chart = lib.crypto_onchain_ethplorer_view.display_tx_info
        self.ueat = lib.crypto_onchain_bitquery_model.get_ethereum_unique_senders
        self.ueat_chart = (
            lib.crypto_onchain_bitquery_view.display_ethereum_unique_senders
        )
        self.whales = lib.crypto_onchain_whale_alert_model.get_whales_transactions
        self.whales_chart = (
            lib.crypto_onchain_whale_alert_view.display_whales_transactions
        )


class CryptoOverview(Category):
    """Overview Module.

    Attributes:
        `altindex`: Get altcoin index overtime\n
        `altindex_chart`: Displays altcoin index overtime\n
        `btcrb`: Get bitcoin price data\n
        `btcrb_chart`: Displays bitcoin rainbow chart\n
        `categories`: Returns top crypto categories [Source: CoinGecko]\n
        `categories_chart`: Shows top cryptocurrency categories by market capitalization\n
        `cbpairs`: Get a list of available currency pairs for trading. [Source: Coinbase]\n
        `cbpairs_chart`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
        `coin_list`: Get list of all available coins on CoinPaprika  [Source: CoinPaprika]\n
        `contracts`: Gets all contract addresses for given platform [Source: CoinPaprika]\n
        `contracts_chart`: Gets all contract addresses for given platform. [Source: CoinPaprika]\n
        `cr`: Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
        `cr_chart`: Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
        `crypto_hack`: Get crypto hack\n
        `crypto_hack_slugs`: Get all crypto hack slugs\n
        `crypto_hacks`: Get major crypto-related hacks\n
        `crypto_hacks_chart`: Display list of major crypto-related hacks. If slug is passed\n
        `defi`: Get global statistics about Decentralized Finances [Source: CoinGecko]\n
        `defi_chart`: Shows global statistics about Decentralized Finances. [Source: CoinGecko]\n
        `derivatives`: Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]\n
        `derivatives_chart`: Shows  list of crypto derivatives. [Source: CoinGecko]\n
        `ewf`: Scrapes exchange withdrawal fees\n
        `ewf_chart`: Exchange withdrawal fees\n
        `exchanges`: Show top crypto exchanges.\n
        `exmarkets`: List markets by exchange ID [Source: CoinPaprika]\n
        `exmarkets_chart`: Get all markets for given exchange [Source: CoinPaprika]\n
        `exrates`: Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]\n
        `exrates_chart`: Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]\n
        `globe`: Get global crypto market data.\n
        `hm`: Get N coins from CoinGecko [Source: CoinGecko]\n
        `hm_chart`: Shows cryptocurrencies heatmap [Source: CoinGecko]\n
        `hold`: Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]\n
        `hold_chart`: Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]\n
        `indexes`: Get list of crypto indexes from CoinGecko API [Source: CoinGecko]\n
        `indexes_chart`: Shows list of crypto indexes. [Source: CoinGecko]\n
        `info`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
        `info_chart`: Displays basic coin information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
        `markets`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
        `markets_chart`: Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
        `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
        `news_chart`: Display recent posts from CryptoPanic news aggregator platform.\n
        `platforms`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]\n
        `platforms_chart`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama.\n
        `products`: Get list of financial products from CoinGecko API\n
        `products_chart`: Shows list of financial products. [Source: CoinGecko]\n
        `stables`: Returns top stable coins [Source: CoinGecko]\n
        `stables_chart`: Shows stablecoins data [Source: CoinGecko]\n
        `wf`: Scrapes top coins withdrawal fees\n
        `wf_chart`: Top coins withdrawal fees\n
        `wfpe`: Scrapes coin withdrawal fees per exchange\n
        `wfpe_chart`: Coin withdrawal fees per exchange\n
    """

    _location_path = "crypto.ov"

    def __init__(self):
        super().__init__()
        self.altindex = lib.crypto_ov_blockchaincenter_model.get_altcoin_index
        self.altindex_chart = lib.crypto_ov_blockchaincenter_view.display_altcoin_index
        self.btcrb = lib.crypto_ov_glassnode_model.get_btc_rainbow
        self.btcrb_chart = lib.crypto_ov_glassnode_view.display_btc_rainbow
        self.categories = lib.crypto_ov_pycoingecko_model.get_top_crypto_categories
        self.categories_chart = lib.crypto_ov_pycoingecko_view.display_categories
        self.cbpairs = lib.crypto_ov_coinbase_model.get_trading_pairs
        self.cbpairs_chart = lib.crypto_ov_coinbase_view.display_trading_pairs
        self.coin_list = lib.crypto_dd_coinpaprika_model.get_coin_list
        self.contracts = lib.crypto_ov_coinpaprika_model.get_contract_platform
        self.contracts_chart = lib.crypto_ov_coinpaprika_view.display_contracts
        self.cr = lib.crypto_ov_loanscan_model.get_rates
        self.cr_chart = lib.crypto_ov_loanscan_view.display_crypto_rates
        self.crypto_hack = lib.crypto_ov_rekt_model.get_crypto_hack
        self.crypto_hack_slugs = lib.crypto_ov_rekt_model.get_crypto_hack_slugs
        self.crypto_hacks = lib.crypto_ov_rekt_model.get_crypto_hacks
        self.crypto_hacks_chart = lib.crypto_ov_rekt_view.display_crypto_hacks
        self.defi = lib.crypto_ov_pycoingecko_model.get_global_defi_info
        self.defi_chart = lib.crypto_ov_pycoingecko_view.display_global_defi_info
        self.derivatives = lib.crypto_ov_pycoingecko_model.get_derivatives
        self.derivatives_chart = lib.crypto_ov_pycoingecko_view.display_derivatives
        self.ewf = (
            lib.crypto_ov_withdrawalfees_model.get_overall_exchange_withdrawal_fees
        )
        self.ewf_chart = (
            lib.crypto_ov_withdrawalfees_view.display_overall_exchange_withdrawal_fees
        )
        self.exchanges = lib.crypto_ov_sdk_helpers.exchanges
        self.exmarkets = lib.crypto_ov_coinpaprika_model.get_exchanges_market
        self.exmarkets_chart = lib.crypto_ov_coinpaprika_view.display_exchange_markets
        self.exrates = lib.crypto_ov_pycoingecko_model.get_exchange_rates
        self.exrates_chart = lib.crypto_ov_pycoingecko_view.display_exchange_rates
        self.globe = lib.crypto_ov_sdk_helpers.globe
        self.hm = lib.crypto_disc_pycoingecko_model.get_coins
        self.hm_chart = lib.crypto_ov_pycoingecko_view.display_crypto_heatmap
        self.hold = lib.crypto_ov_pycoingecko_model.get_holdings_overview
        self.hold_chart = lib.crypto_ov_pycoingecko_view.display_holdings_overview
        self.indexes = lib.crypto_ov_pycoingecko_model.get_indexes
        self.indexes_chart = lib.crypto_ov_pycoingecko_view.display_indexes
        self.info = lib.crypto_ov_coinpaprika_model.get_coins_info
        self.info_chart = lib.crypto_ov_coinpaprika_view.display_all_coins_info
        self.markets = lib.crypto_ov_coinpaprika_model.get_coins_market_info
        self.markets_chart = (
            lib.crypto_ov_coinpaprika_view.display_all_coins_market_info
        )
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_chart = lib.crypto_ov_cryptopanic_view.display_news
        self.platforms = lib.crypto_ov_coinpaprika_model.get_all_contract_platforms
        self.platforms_chart = lib.crypto_ov_coinpaprika_view.display_all_platforms
        self.products = lib.crypto_ov_pycoingecko_model.get_finance_products
        self.products_chart = lib.crypto_ov_pycoingecko_view.display_products
        self.stables = lib.crypto_ov_pycoingecko_model.get_stable_coins
        self.stables_chart = lib.crypto_ov_pycoingecko_view.display_stablecoins
        self.wf = lib.crypto_ov_withdrawalfees_model.get_overall_withdrawal_fees
        self.wf_chart = (
            lib.crypto_ov_withdrawalfees_view.display_overall_withdrawal_fees
        )
        self.wfpe = lib.crypto_ov_withdrawalfees_model.get_crypto_withdrawal_fees
        self.wfpe_chart = (
            lib.crypto_ov_withdrawalfees_view.display_crypto_withdrawal_fees
        )


class CryptoTools(Category):
    """Tools Module.

    Attributes:
        `apy`: Converts apr into apy\n
        `apy_chart`: Displays APY value converted from APR\n
        `il`: Calculates Impermanent Loss in a custom liquidity pool\n
        `il_chart`: Displays Impermanent Loss in a custom liquidity pool\n
    """

    _location_path = "crypto.tools"

    def __init__(self):
        super().__init__()
        self.apy = lib.crypto_tools_model.calculate_apy
        self.apy_chart = lib.crypto_tools_view.display_apy
        self.il = lib.crypto_tools_model.calculate_il
        self.il_chart = lib.crypto_tools_view.display_il
