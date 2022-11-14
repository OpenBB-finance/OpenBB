# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class CryptoRoot(Category):
    """OpenBB SDK Cryptocurrency Module

    Attributes:
        `candles`: Plot candle chart from dataframe. [Source: Binance]\n
        `chart`: Load data for Technical Analysis\n
        `find`: Find similar coin by coin name,symbol or id.\n
        `load`: Load crypto currency to get data for\n
    """

    def __init__(self):
        super().__init__()
        self.candles = lib.crypto_helpers.plot_candles
        self.chart = lib.crypto_helpers.plot_chart
        self.find = lib.crypto_helpers.find
        self.load = lib.crypto_helpers.load


class CryptoDueDiligence(Category):
    """OpenBB SDK Due Diligence Module.

    Attributes:
        `active`: Returns active addresses of a certain symbol\n
        `active_view`: Display active addresses of a certain symbol over time\n
        `balance`: Get account holdings for asset. [Source: Binance]\n
        `balance_view`: Get account holdings for asset. [Source: Binance]\n
        `basic_info`: Basic coin information [Source: CoinPaprika]\n
        `binance_available_quotes_for_each_coin`: Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]\n
        `book`: Get order book for currency. [Source: Binance]\n
        `book_view`: Get order book for currency. [Source: Binance]\n
        `candles`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
        `candles_view`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
        `cbbook`: Get orders book for chosen trading pair. [Source: Coinbase]\n
        `cbbook_view`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
        `change`: Returns 30d change of the supply held in exchange wallets of a certain symbol.\n
        `change_view`: Display 30d change of the supply held in exchange wallets.\n
        `check_valid_binance_string`: Check if symbol is in defined binance. [Source: Binance]\n
        `close`: Returns the price of a cryptocurrency\n
        `coin`: Get coin by id [Source: CoinPaprika]\n
        `coin_market_chart`: Get prices for given coin. [Source: CoinGecko]\n
        `eb`: Returns the total amount of coins held on exchange addresses in units and percentage.\n
        `eb_view`: Display total amount of coins held on exchange addresses in units and percentage.\n
        `events`: Get all events related to given coin like conferences, start date of futures trading etc.\n
        `events_view`: Get all events for given coin id. [Source: CoinPaprika]\n
        `ex`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
        `ex_view`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
        `exchanges`: Helper method to get all the exchanges supported by ccxt\n
        `fr`: Returns coin fundraising\n
        `fr_view`: Display coin fundraising\n
        `get_binance_trading_pairs`: Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset\n
        `get_mt`: Returns available messari timeseries\n
        `get_mt_view`: Display messari timeseries list\n
        `gh`: Returns  a list of developer activity for a given coin and time interval.\n
        `gh_view`: Returns a list of github activity for a given coin and time interval.\n
        `gov`: Returns coin governance\n
        `gov_view`: Display coin governance\n
        `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]\n
        `headlines_view`: Sentiment analysis from FinBrain for Cryptocurrencies\n
        `inv`: Returns coin investors\n
        `inv_view`: Display coin investors\n
        `links`: Returns asset's links\n
        `links_view`: Display coin links\n
        `mcapdom`: Returns market dominance of a coin over time\n
        `mcapdom_view`: Display market dominance of a coin over time\n
        `mkt`: All markets for given coin and currency [Source: CoinPaprika]\n
        `mkt_view`: Get all markets for given coin id. [Source: CoinPaprika]\n
        `mt`: Returns messari timeseries\n
        `mt_view`: Display messari timeseries\n
        `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
        `news_view`: Display recent posts from CryptoPanic news aggregator platform.\n
        `nonzero`: Returns addresses with non-zero balance of a certain symbol\n
        `nonzero_view`: Display addresses with non-zero balance of a certain symbol\n
        `ohlc_historical`: Open/High/Low/Close values with volume and market_cap. [Source: CoinPaprika]\n
        `oi`: Returns open interest by exchange for a certain symbol\n
        `oi_view`: Displays open interest by exchange for a certain cryptocurrency\n
        `pi`: Returns coin product info\n
        `pi_view`: Display project info\n
        `pr`: Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]\n
        `pr_view`: Displays potential returns of a certain coin. [Source: CoinGecko]\n
        `ps`: Get all most important ticker related information for given coin id [Source: CoinPaprika]\n
        `ps_view`: Get ticker information for single coin [Source: CoinPaprika]\n
        `rm`: Returns coin roadmap\n
        `rm_view`: Display coin roadmap\n
        `show_available_pairs_for_given_symbol`: Return all available quoted assets for given symbol. [Source: Binance]\n
        `stats`: Get 24 hr stats for the product. Volume is in base currency units.\n
        `stats_view`: Get 24 hr stats for the product. Volume is in base currency units.\n
        `team`: Returns coin team\n
        `team_view`: Display coin team\n
        `tk`: Returns coin tokenomics\n
        `tk_view`: Display coin tokenomics\n
        `tokenomics`: Get tokenomics for given coin. [Source: CoinGecko]\n
        `trades`: Get last N trades for chosen trading pair. [Source: Coinbase]\n
        `trades_view`: Display last N trades for chosen trading pair. [Source: Coinbase]\n
        `trading_pair_info`: Get information about chosen trading pair. [Source: Coinbase]\n
        `trading_pairs`: Helper method that return all trading pairs on binance. Methods ause this data for input for e.g\n
        `twitter`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
        `twitter_view`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
    """

    def __init__(self):
        super().__init__()
        self.active = lib.crypto_dd_glassnode_model.get_active_addresses
        self.active_view = lib.crypto_dd_glassnode_view.display_active_addresses
        self.balance = lib.crypto_dd_binance_model.get_balance
        self.balance_view = lib.crypto_dd_binance_view.display_balance
        self.basic_info = lib.crypto_dd_coinpaprika_model.basic_coin_info
        self.binance_available_quotes_for_each_coin = (
            lib.crypto_dd_binance_model.get_binance_available_quotes_for_each_coin
        )
        self.book = lib.crypto_dd_binance_model.get_order_book
        self.book_view = lib.crypto_dd_binance_view.display_order_book
        self.candles = lib.crypto_dd_coinbase_model.get_candles
        self.candles_view = lib.crypto_dd_coinbase_view.display_candles
        self.cbbook = lib.crypto_dd_coinbase_model.get_order_book
        self.cbbook_view = lib.crypto_dd_coinbase_view.display_order_book
        self.change = lib.crypto_dd_glassnode_model.get_exchange_net_position_change
        self.change_view = (
            lib.crypto_dd_glassnode_view.display_exchange_net_position_change
        )
        self.check_valid_binance_string = (
            lib.crypto_dd_binance_model.check_valid_binance_str
        )
        self.close = lib.crypto_dd_glassnode_model.get_close_price
        self.coin = lib.crypto_dd_coinpaprika_model.get_coin
        self.coin_market_chart = lib.crypto_dd_pycoingecko_model.get_coin_market_chart
        self.eb = lib.crypto_dd_glassnode_model.get_exchange_balances
        self.eb_view = lib.crypto_dd_glassnode_view.display_exchange_balances
        self.events = lib.crypto_dd_coinpaprika_model.get_coin_events_by_id
        self.events_view = lib.crypto_dd_coinpaprika_view.display_events
        self.ex = lib.crypto_dd_coinpaprika_model.get_coin_exchanges_by_id
        self.ex_view = lib.crypto_dd_coinpaprika_view.display_exchanges
        self.exchanges = lib.crypto_dd_ccxt_model.get_exchanges
        self.fr = lib.crypto_dd_messari_model.get_fundraising
        self.fr_view = lib.crypto_dd_messari_view.display_fundraising
        self.get_binance_trading_pairs = (
            lib.crypto_dd_binance_model.get_all_binance_trading_pairs
        )
        self.get_mt = lib.crypto_dd_messari_model.get_available_timeseries
        self.get_mt_view = lib.crypto_dd_messari_view.display_messari_timeseries_list
        self.gh = lib.crypto_dd_santiment_model.get_github_activity
        self.gh_view = lib.crypto_dd_santiment_view.display_github_activity
        self.gov = lib.crypto_dd_messari_model.get_governance
        self.gov_view = lib.crypto_dd_messari_view.display_governance
        self.headlines = lib.stocks_ba_finbrain_model.get_sentiment
        self.headlines_view = (
            lib.crypto_dd_crypto_finbrain_view.display_crypto_sentiment_analysis
        )
        self.inv = lib.crypto_dd_messari_model.get_investors
        self.inv_view = lib.crypto_dd_messari_view.display_investors
        self.links = lib.crypto_dd_messari_model.get_links
        self.links_view = lib.crypto_dd_messari_view.display_links
        self.mcapdom = lib.crypto_dd_messari_model.get_marketcap_dominance
        self.mcapdom_view = lib.crypto_dd_messari_view.display_marketcap_dominance
        self.mkt = lib.crypto_dd_coinpaprika_model.get_coin_markets_by_id
        self.mkt_view = lib.crypto_dd_coinpaprika_view.display_markets
        self.mt = lib.crypto_dd_messari_model.get_messari_timeseries
        self.mt_view = lib.crypto_dd_messari_view.display_messari_timeseries
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_view = lib.crypto_dd_cryptopanic_view.display_news
        self.nonzero = lib.crypto_dd_glassnode_model.get_non_zero_addresses
        self.nonzero_view = lib.crypto_dd_glassnode_view.display_non_zero_addresses
        self.ohlc_historical = lib.crypto_dd_coinpaprika_model.get_ohlc_historical
        self.oi = lib.crypto_dd_coinglass_model.get_open_interest_per_exchange
        self.oi_view = lib.crypto_dd_coinglass_view.display_open_interest
        self.pi = lib.crypto_dd_messari_model.get_project_product_info
        self.pi_view = lib.crypto_dd_messari_view.display_project_info
        self.pr = lib.crypto_dd_pycoingecko_model.get_coin_potential_returns
        self.pr_view = lib.crypto_dd_pycoingecko_view.display_coin_potential_returns
        self.ps = lib.crypto_dd_coinpaprika_model.get_tickers_info_for_coin
        self.ps_view = lib.crypto_dd_coinpaprika_view.display_price_supply
        self.rm = lib.crypto_dd_messari_model.get_roadmap
        self.rm_view = lib.crypto_dd_messari_view.display_roadmap
        self.show_available_pairs_for_given_symbol = (
            lib.crypto_dd_binance_model.show_available_pairs_for_given_symbol
        )
        self.stats = lib.crypto_dd_coinbase_model.get_product_stats
        self.stats_view = lib.crypto_dd_coinbase_view.display_stats
        self.team = lib.crypto_dd_messari_model.get_team
        self.team_view = lib.crypto_dd_messari_view.display_team
        self.tk = lib.crypto_dd_messari_model.get_tokenomics
        self.tk_view = lib.crypto_dd_messari_view.display_tokenomics
        self.tokenomics = lib.crypto_dd_pycoingecko_model.get_coin_tokenomics
        self.trades = lib.crypto_dd_coinbase_model.get_trades
        self.trades_view = lib.crypto_dd_coinbase_view.display_trades
        self.trading_pair_info = lib.crypto_dd_coinbase_model.get_trading_pair_info
        self.trading_pairs = lib.crypto_dd_binance_model._get_trading_pairs
        self.twitter = lib.crypto_dd_coinpaprika_model.get_coin_twitter_timeline
        self.twitter_view = lib.crypto_dd_coinpaprika_view.display_twitter


class CryptoDeFi(Category):
    """OpenBB SDK DeFi Module.

    Attributes:
        `aterra`: Returns historical data of an asset in a certain terra address\n
        `aterra_view`: Displays the 30-day history of specified asset in terra address\n
        `ayr`: Displays the 30-day history of the Anchor Yield Reserve.\n
        `ayr_view`: Displays the 30-day history of the Anchor Yield Reserve.\n
        `dtvl`: Returns information about historical tvl of a defi protocol.\n
        `dtvl_view`: Displays historical TVL of different dApps\n
        `gacc`: Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
        `gacc_view`: Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
        `gdapps`: Display top dApps (in terms of TVL) grouped by chain.\n
        `gdapps_view`: Display top dApps (in terms of TVL) grouped by chain.\n
        `gov_proposals`: Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
        `gov_proposals_view`: Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
        `ldapps`: Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.\n
        `ldapps_view`: Display information about listed DeFi protocols, their current TVL and changes to it in\n
        `luna_supply`: Get supply history of the Terra ecosystem\n
        `luna_supply_view`: Display Luna circulating supply stats\n
        `newsletters`: Scrape all substack newsletters from url list.\n
        `newsletters_view`: Display DeFi related substack newsletters.\n
        `pairs`: Get lastly added trade-able pairs on Uniswap with parameters like:\n
        `pairs_view`: Displays Lastly added pairs on Uniswap DEX.\n
        `pools`: Get uniswap pools by volume. [Source: https://thegraph.com/en/]\n
        `pools_view`: Displays uniswap pools by volume.\n
        `sinfo`: Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]\n
        `sinfo_view`: Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]\n
        `sratio`: Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]\n
        `sratio_view`: Display terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]\n
        `sreturn`: Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]\n
        `sreturn_view`: Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]\n
        `stats`: Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
        `stats_view`: Displays base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
        `stvl`: Returns historical values of the total sum of TVLs from all listed protocols.\n
        `stvl_view`: Displays historical values of the total sum of TVLs from all listed protocols.\n
        `swaps`: Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]\n
        `swaps_view`: Displays last swaps done on Uniswap\n
        `tokens`: Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]\n
        `tokens_view`: Displays tokens trade-able on Uniswap DEX.\n
        `validators`: Get information about terra validators [Source: https://fcd.terra.dev/swagger]\n
        `validators_view`: Display information about terra validators [Source: https://fcd.terra.dev/swagger]\n
    """

    def __init__(self):
        super().__init__()
        self.aterra = (
            lib.crypto_defi_terraengineer_model.get_history_asset_from_terra_address
        )
        self.aterra_view = (
            lib.crypto_defi_terraengineer_view.display_terra_asset_history
        )
        self.ayr = lib.crypto_defi_terraengineer_model.get_anchor_yield_reserve
        self.ayr_view = lib.crypto_defi_terraengineer_view.display_anchor_yield_reserve
        self.dtvl = lib.crypto_defi_llama_model.get_defi_protocol
        self.dtvl_view = lib.crypto_defi_llama_view.display_historical_tvl
        self.gacc = lib.crypto_defi_terramoney_fcd_model.get_account_growth
        self.gacc_view = lib.crypto_defi_terramoney_fcd_view.display_account_growth
        self.gdapps = lib.crypto_defi_llama_model.get_grouped_defi_protocols
        self.gdapps_view = lib.crypto_defi_llama_view.display_grouped_defi_protocols
        self.gov_proposals = lib.crypto_defi_terramoney_fcd_model.get_proposals
        self.gov_proposals_view = (
            lib.crypto_defi_terramoney_fcd_view.display_gov_proposals
        )
        self.ldapps = lib.crypto_defi_llama_model.get_defi_protocols
        self.ldapps_view = lib.crypto_defi_llama_view.display_defi_protocols
        self.luna_supply = lib.crypto_defi_smartstake_model.get_luna_supply_stats
        self.luna_supply_view = (
            lib.crypto_defi_smartstake_view.display_luna_circ_supply_change
        )
        self.newsletters = lib.crypto_defi_substack_model.get_newsletters
        self.newsletters_view = lib.crypto_defi_substack_view.display_newsletters
        self.pairs = lib.crypto_defi_graph_model.get_uniswap_pool_recently_added
        self.pairs_view = lib.crypto_defi_graph_view.display_recently_added
        self.pools = lib.crypto_defi_graph_model.get_uni_pools_by_volume
        self.pools_view = lib.crypto_defi_graph_view.display_uni_pools
        self.sinfo = lib.crypto_defi_terramoney_fcd_model.get_staking_account_info
        self.sinfo_view = (
            lib.crypto_defi_terramoney_fcd_view.display_account_staking_info
        )
        self.sratio = lib.crypto_defi_terramoney_fcd_model.get_staking_ratio_history
        self.sratio_view = (
            lib.crypto_defi_terramoney_fcd_view.display_staking_ratio_history
        )
        self.sreturn = lib.crypto_defi_terramoney_fcd_model.get_staking_returns_history
        self.sreturn_view = (
            lib.crypto_defi_terramoney_fcd_view.display_staking_returns_history
        )
        self.stats = lib.crypto_defi_graph_model.get_uniswap_stats
        self.stats_view = lib.crypto_defi_graph_view.display_uni_stats
        self.stvl = lib.crypto_defi_llama_model.get_defi_tvl
        self.stvl_view = lib.crypto_defi_llama_view.display_defi_tvl
        self.swaps = lib.crypto_defi_graph_model.get_last_uni_swaps
        self.swaps_view = lib.crypto_defi_graph_view.display_last_uni_swaps
        self.tokens = lib.crypto_defi_graph_model.get_uni_tokens
        self.tokens_view = lib.crypto_defi_graph_view.display_uni_tokens
        self.validators = lib.crypto_defi_terramoney_fcd_model.get_validators
        self.validators_view = lib.crypto_defi_terramoney_fcd_view.display_validators


class CryptoDiscovery(Category):
    """OpenBB SDK Discovery Module.

    Attributes:
        `cmctop`: Shows top n coins. [Source: CoinMarketCap]\n
        `cmctop_view`: Shows top n coins. [Source: CoinMarketCap]\n
        `coin_list`: Get list of coins available on CoinGecko [Source: CoinGecko]\n
        `coins`: Get N coins from CoinGecko [Source: CoinGecko]\n
        `coins_view`: Display top coins [Source: CoinGecko]\n
        `coins_for_given_exchange`: Helper method to get all coins available on binance exchange [Source: CoinGecko]\n
        `cpsearch`: Search CoinPaprika. [Source: CoinPaprika]\n
        `cpsearch_view`: Search over CoinPaprika. [Source: CoinPaprika]\n
        `gainers`: Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
        `gainers_view`: Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
        `gainers_or_losers`: Returns data about top gainers - coins which gain the most in given period and\n
        `losers`: Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]\n
        `losers_view`: Shows Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]\n
        `top_dapps`: Get top decentralized applications by daily volume and users [Source: https://dappradar.com/]\n
        `top_dapps_view`: Displays top decentralized exchanges [Source: https://dappradar.com/]\n
        `top_dexes`: Get top dexes by daily volume and users [Source: https://dappradar.com/]\n
        `top_dexes_view`: Displays top decentralized exchanges [Source: https://dappradar.com/]\n
        `top_games`: Get top blockchain games by daily volume and users [Source: https://dappradar.com/]\n
        `top_games_view`: Displays top blockchain games [Source: https://dappradar.com/]\n
        `top_nfts`: Get top nft collections [Source: https://dappradar.com/]\n
        `top_nfts_view`: Displays top nft collections [Source: https://dappradar.com/]\n
        `trending`: Returns trending coins [Source: CoinGecko]\n
        `trending_view`: Display trending coins [Source: CoinGecko]\n
    """

    def __init__(self):
        super().__init__()
        self.categories_keys = lib.crypto_disc_pycoingecko_model.get_categories_keys
        self.cmctop = lib.crypto_disc_coinmarketcap_model.get_cmc_top_n
        self.cmctop_view = lib.crypto_disc_coinmarketcap_view.display_cmc_top_coins
        self.coin_list = lib.crypto_disc_pycoingecko_model.get_coin_list
        self.coins = lib.crypto_disc_pycoingecko_model.get_coins
        self.coins_view = lib.crypto_disc_pycoingecko_view.display_coins
        self.coins_for_given_exchange = (
            lib.crypto_disc_pycoingecko_model.get_coins_for_given_exchange
        )
        self.cpsearch = lib.crypto_disc_coinpaprika_model.get_search_results
        self.cpsearch_view = lib.crypto_disc_coinpaprika_view.display_search_results
        self.gainers = lib.crypto_disc_pycoingecko_model.get_gainers
        self.gainers_view = lib.crypto_disc_pycoingecko_view.display_gainers
        self.gainers_or_losers = lib.crypto_disc_pycoingecko_model.get_gainers_or_losers
        self.losers = lib.crypto_disc_pycoingecko_model.get_losers
        self.losers_view = lib.crypto_disc_pycoingecko_view.display_losers
        self.top_dapps = lib.crypto_disc_dappradar_model.get_top_dapps
        self.top_dapps_view = lib.crypto_disc_dappradar_view.display_top_dapps
        self.top_dexes = lib.crypto_disc_dappradar_model.get_top_dexes
        self.top_dexes_view = lib.crypto_disc_dappradar_view.display_top_dexes
        self.top_games = lib.crypto_disc_dappradar_model.get_top_games
        self.top_games_view = lib.crypto_disc_dappradar_view.display_top_games
        self.top_nfts = lib.crypto_disc_dappradar_model.get_top_nfts
        self.top_nfts_view = lib.crypto_disc_dappradar_view.display_top_nfts
        self.trending = lib.crypto_disc_pycoingecko_model.get_trending_coins
        self.trending_view = lib.crypto_disc_pycoingecko_view.display_trending


class CryptoNFT(Category):
    """OpenBB SDK NFT Module.

    Attributes:
        `collections`: Get nft collections [Source: https://nftpricefloor.com/]\n
        `collections_view`: Display NFT collections. [Source: https://nftpricefloor.com/]\n
        `fp`: Get nft collections [Source: https://nftpricefloor.com/]\n
        `fp_view`: Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]\n
        `stats`: Get stats of a nft collection [Source: opensea.io]\n
        `stats_view`: Display collection stats. [Source: opensea.io]\n
    """

    def __init__(self):
        super().__init__()
        self.collections = lib.crypto_nft_pricefloor_model.get_collections
        self.collections_view = lib.crypto_nft_pricefloor_view.display_collections
        self.fp = lib.crypto_nft_pricefloor_model.get_floor_price
        self.fp_view = lib.crypto_nft_pricefloor_view.display_floor_price
        self.stats = lib.crypto_nft_opensea_model.get_collection_stats
        self.stats_view = lib.crypto_nft_opensea_view.display_collection_stats


class CryptoOnChain(Category):
    """OpenBB SDK OnChain Module.

    Attributes:
        `baas`: Get an average bid and ask prices, average spread for given crypto pair for chosen time period.\n
        `baas_view`: Display an average bid and ask prices, average spread for given crypto pair for chosen\n
        `balance`: Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which\n
        `balance_view`: Display info about tokens for given ethereum blockchain balance e.g. ETH balance,\n
        `btc_supply`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
        `btc_supply_view`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
        `btc_transac`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
        `btc_transac_view`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
        `dex_trades_monthly`: Get list of trades on Decentralized Exchanges monthly aggregated.\n
        `dvcp`: Get daily volume for given pair [Source: https://graphql.bitquery.io/]\n
        `dvcp_view`: Display daily volume for given pair\n
        `erc20_tokens`: Helper method that loads ~1500 most traded erc20 token.\n
        `gwei`: Returns the most recent Ethereum gas fees in gwei\n
        `gwei_view`: Current gwei fees\n
        `hist`: Get information about balance historical transactions. [Source: Ethplorer]\n
        `hist_view`: Display information about balance historical transactions. [Source: Ethplorer]\n
        `holders`: Get info about top token holders. [Source: Ethplorer]\n
        `holders_view`: Display info about top ERC20 token holders. [Source: Ethplorer]\n
        `hr`: Returns dataframe with mean hashrate of btc or eth blockchain and symbol price\n
        `hr_view`: Display dataframe with mean hashrate of btc or eth blockchain and symbol price.\n
        `info`: Get info about ERC20 token. [Source: Ethplorer]\n
        `info_view`: Display info about ERC20 token. [Source: Ethplorer]\n
        `lt`: Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]\n
        `lt_view`: Trades on Decentralized Exchanges aggregated by DEX or Month\n
        `prices`: Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]\n
        `prices_view`: Display token historical prices with volume and market cap, and average price.\n
        `query_graph`: Helper methods for querying graphql api. [Source: https://bitquery.io/]\n
        `th`: Get info about token historical transactions. [Source: Ethplorer]\n
        `th_view`: Display info about token history. [Source: Ethplorer]\n
        `token_decimals`: Helper methods that gets token decimals number. [Source: Ethplorer]\n
        `top`: Get top 50 tokens. [Source: Ethplorer]\n
        `top_view`: Display top ERC20 tokens [Source: Ethplorer]\n
        `ttcp`: Get most traded crypto pairs on given decentralized exchange in chosen time period.\n
        `ttcp_view`: Display most traded crypto pairs on given decentralized exchange in chosen time period.\n
        `tv`: Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]\n
        `tv_view`: Display token volume on different Decentralized Exchanges.\n
        `tx`: Get info about transaction. [Source: Ethplorer]\n
        `tx_view`: Display info about transaction. [Source: Ethplorer]\n
        `ueat`: Get number of unique ethereum addresses which made a transaction in given time interval.\n
        `ueat_view`: Display number of unique ethereum addresses which made a transaction in given time interval\n
        `whales`: Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.\n
        `whales_view`: Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]\n
    """

    def __init__(self):
        super().__init__()
        self.baas = lib.crypto_onchain_bitquery_model.get_spread_for_crypto_pair
        self.baas_view = lib.crypto_onchain_bitquery_view.display_spread_for_crypto_pair
        self.balance = lib.crypto_onchain_ethplorer_model.get_address_info
        self.balance_view = lib.crypto_onchain_ethplorer_view.display_address_info
        self.btc_supply = lib.crypto_onchain_blockchain_model.get_btc_circulating_supply
        self.btc_supply_view = (
            lib.crypto_onchain_blockchain_view.display_btc_circulating_supply
        )
        self.btc_transac = (
            lib.crypto_onchain_blockchain_model.get_btc_confirmed_transactions
        )
        self.btc_transac_view = (
            lib.crypto_onchain_blockchain_view.display_btc_confirmed_transactions
        )
        self.dex_trades_monthly = (
            lib.crypto_onchain_bitquery_model.get_dex_trades_monthly
        )
        self.dvcp = (
            lib.crypto_onchain_bitquery_model.get_daily_dex_volume_for_given_pair
        )
        self.dvcp_view = (
            lib.crypto_onchain_bitquery_view.display_daily_volume_for_given_pair
        )
        self.erc20_tokens = lib.crypto_onchain_bitquery_model.get_erc20_tokens
        self.gwei = lib.crypto_onchain_ethgasstation_model.get_gwei_fees
        self.gwei_view = lib.crypto_onchain_ethgasstation_view.display_gwei_fees
        self.hist = lib.crypto_onchain_ethplorer_model.get_address_history
        self.hist_view = lib.crypto_onchain_ethplorer_view.display_address_history
        self.holders = lib.crypto_onchain_ethplorer_model.get_top_token_holders
        self.holders_view = lib.crypto_onchain_ethplorer_view.display_top_token_holders
        self.hr = lib.crypto_dd_glassnode_model.get_hashrate
        self.hr_view = lib.crypto_dd_glassnode_view.display_hashrate
        self.info = lib.crypto_onchain_ethplorer_model.get_token_info
        self.info_view = lib.crypto_onchain_ethplorer_view.display_token_info
        self.lt = lib.crypto_onchain_bitquery_model.get_dex_trades_by_exchange
        self.lt_view = lib.crypto_onchain_bitquery_view.display_dex_trades
        self.prices = lib.crypto_onchain_ethplorer_model.get_token_historical_price
        self.prices_view = (
            lib.crypto_onchain_ethplorer_view.display_token_historical_prices
        )
        self.query_graph = lib.crypto_onchain_bitquery_model.query_graph
        self.th = lib.crypto_onchain_ethplorer_model.get_token_history
        self.th_view = lib.crypto_onchain_ethplorer_view.display_token_history
        self.token_decimals = lib.crypto_onchain_ethplorer_model.get_token_decimals
        self.top = lib.crypto_onchain_ethplorer_model.get_top_tokens
        self.top_view = lib.crypto_onchain_ethplorer_view.display_top_tokens
        self.ttcp = lib.crypto_onchain_bitquery_model.get_most_traded_pairs
        self.ttcp_view = lib.crypto_onchain_bitquery_view.display_most_traded_pairs
        self.tv = lib.crypto_onchain_bitquery_model.get_token_volume_on_dexes
        self.tv_view = lib.crypto_onchain_bitquery_view.display_dex_volume_for_token
        self.tx = lib.crypto_onchain_ethplorer_model.get_tx_info
        self.tx_view = lib.crypto_onchain_ethplorer_view.display_tx_info
        self.ueat = lib.crypto_onchain_bitquery_model.get_ethereum_unique_senders
        self.ueat_view = (
            lib.crypto_onchain_bitquery_view.display_ethereum_unique_senders
        )
        self.whales = lib.crypto_onchain_whale_alert_model.get_whales_transactions
        self.whales_view = (
            lib.crypto_onchain_whale_alert_view.display_whales_transactions
        )


class CryptoOverview(Category):
    """OpenBB SDK Overview Module.

    Attributes:
        `altindex`: Get altcoin index overtime\n
        `altindex_view`: Displays altcoin index overtime\n
        `btcrb`: Get bitcoin price data\n
        `btcrb_view`: Displays bitcoin rainbow chart\n
        `cbpairs`: Get a list of available currency pairs for trading. [Source: Coinbase]\n
        `cbpairs_view`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
        `cgcategories`: Returns top crypto categories [Source: CoinGecko]\n
        `cgcategories_view`: Shows top cryptocurrency categories by market capitalization\n
        `cgdefi`: Get global statistics about Decentralized Finances [Source: CoinGecko]\n
        `cgdefi_view`: Shows global statistics about Decentralized Finances. [Source: CoinGecko]\n
        `cgderivatives`: Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]\n
        `cgderivatives_view`: Shows  list of crypto derivatives. [Source: CoinGecko]\n
        `cgexrates`: Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]\n
        `cgexrates_view`: Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]\n
        `cgglobal`: Get global statistics about crypto markets from CoinGecko API like:\n
        `cgglobal_view`: Shows global statistics about crypto. [Source: CoinGecko]\n
        `cgh`: Get N coins from CoinGecko [Source: CoinGecko]\n
        `cgh_view`: Shows cryptocurrencies heatmap [Source: CoinGecko]\n
        `cghold`: Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]\n
        `cghold_view`: Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]\n
        `cgindexes`: Get list of crypto indexes from CoinGecko API [Source: CoinGecko]\n
        `cgindexes_view`: Shows list of crypto indexes. [Source: CoinGecko]\n
        `cgproducts`: Get list of financial products from CoinGecko API\n
        `cgproducts_view`: Shows list of financial products. [Source: CoinGecko]\n
        `cgstables`: Returns top stable coins [Source: CoinGecko]\n
        `cgstables_view`: Shows stablecoins data [Source: CoinGecko]\n
        `cpcontracts`: Gets all contract addresses for given platform [Source: CoinPaprika]\n
        `cpcontracts_view`: Gets all contract addresses for given platform. [Source: CoinPaprika]\n
        `cpexchanges`: List exchanges from CoinPaprika API [Source: CoinPaprika]\n
        `cpexchanges_view`: List exchanges from CoinPaprika API. [Source: CoinPaprika]\n
        `cpexmarkets`: List markets by exchange ID [Source: CoinPaprika]\n
        `cpexmarkets_view`: Get all markets for given exchange [Source: CoinPaprika]\n
        `cpglobal`: Return data frame with most important global crypto statistics like:\n
        `cpglobal_view`: Return data frame with most important global crypto statistics like:\n
        `cpinfo`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
        `cpinfo_view`: Displays basic coin information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
        `cpmarkets`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
        `cpmarkets_view`: Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
        `cpplatforms`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]\n
        `cpplatforms_view`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama.\n
        `cr`: Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
        `cr_view`: Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
        `crypto_hack`: Get crypto hack\n
        `crypto_hack_slugs`: Get all crypto hack slugs\n
        `crypto_hacks`: Get major crypto-related hacks\n
        `crypto_hacks_view`: Display list of major crypto-related hacks. If slug is passed\n
        `ewf`: Scrapes exchange withdrawal fees\n
        `ewf_view`: Exchange withdrawal fees\n
        `exchanges`: Get list of top exchanges from CoinGecko API [Source: CoinGecko]\n
        `exchanges_view`: Shows list of top exchanges from CoinGecko. [Source: CoinGecko]\n
        `global_info`: Get global statistics about crypto from CoinGecko API like:\n
        `list_of_coins`: Get list of all available coins on CoinPaprika  [Source: CoinPaprika]\n
        `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
        `news_view`: Display recent posts from CryptoPanic news aggregator platform.\n
        `platforms`: Get list of financial platforms from CoinGecko API [Source: CoinGecko]\n
        `platforms_view`: Shows list of financial platforms. [Source: CoinGecko]\n
        `wf`: Scrapes top coins withdrawal fees\n
        `wf_view`: Top coins withdrawal fees\n
        `wfpe`: Scrapes coin withdrawal fees per exchange\n
        `wfpe_view`: Coin withdrawal fees per exchange\n
    """

    def __init__(self):
        super().__init__()
        self.altindex = lib.crypto_ov_blockchaincenter_model.get_altcoin_index
        self.altindex_view = lib.crypto_ov_blockchaincenter_view.display_altcoin_index
        self.btcrb = lib.crypto_ov_glassnode_model.get_btc_rainbow
        self.btcrb_view = lib.crypto_ov_glassnode_view.display_btc_rainbow
        self.cbpairs = lib.crypto_ov_coinbase_model.get_trading_pairs
        self.cbpairs_view = lib.crypto_ov_coinbase_view.display_trading_pairs
        self.cgcategories = lib.crypto_ov_pycoingecko_model.get_top_crypto_categories
        self.cgcategories_view = lib.crypto_ov_pycoingecko_view.display_categories
        self.cgdefi = lib.crypto_ov_pycoingecko_model.get_global_defi_info
        self.cgdefi_view = lib.crypto_ov_pycoingecko_view.display_global_defi_info
        self.cgderivatives = lib.crypto_ov_pycoingecko_model.get_derivatives
        self.cgderivatives_view = lib.crypto_ov_pycoingecko_view.display_derivatives
        self.cgexrates = lib.crypto_ov_pycoingecko_model.get_exchange_rates
        self.cgexrates_view = lib.crypto_ov_pycoingecko_view.display_exchange_rates
        self.cgglobal = lib.crypto_ov_pycoingecko_model.get_global_markets_info
        self.cgglobal_view = lib.crypto_ov_pycoingecko_view.display_global_market_info
        self.cgh = lib.crypto_ov_pycoingecko_model.get_coins
        self.cgh_view = lib.crypto_ov_pycoingecko_view.display_crypto_heatmap
        self.cghold = lib.crypto_ov_pycoingecko_model.get_holdings_overview
        self.cghold_view = lib.crypto_ov_pycoingecko_view.display_holdings_overview
        self.cgindexes = lib.crypto_ov_pycoingecko_model.get_indexes
        self.cgindexes_view = lib.crypto_ov_pycoingecko_view.display_indexes
        self.cgproducts = lib.crypto_ov_pycoingecko_model.get_finance_products
        self.cgproducts_view = lib.crypto_ov_pycoingecko_view.display_products
        self.cgstables = lib.crypto_ov_pycoingecko_model.get_stable_coins
        self.cgstables_view = lib.crypto_ov_pycoingecko_view.display_stablecoins
        self.cpcontracts = lib.crypto_ov_coinpaprika_model.get_contract_platform
        self.cpcontracts_view = lib.crypto_ov_coinpaprika_view.display_contracts
        self.cpexchanges = lib.crypto_ov_coinpaprika_model.get_list_of_exchanges
        self.cpexchanges_view = lib.crypto_ov_coinpaprika_view.display_all_exchanges
        self.cpexmarkets = lib.crypto_ov_coinpaprika_model.get_exchanges_market
        self.cpexmarkets_view = lib.crypto_ov_coinpaprika_view.display_exchange_markets
        self.cpglobal = lib.crypto_ov_coinpaprika_model.get_global_market
        self.cpglobal_view = lib.crypto_ov_coinpaprika_view.display_global_market
        self.cpinfo = lib.crypto_ov_coinpaprika_model.get_coins_info
        self.cpinfo_view = lib.crypto_ov_coinpaprika_view.display_all_coins_info
        self.cpmarkets = lib.crypto_ov_coinpaprika_model.get_coins_market_info
        self.cpmarkets_view = (
            lib.crypto_ov_coinpaprika_view.display_all_coins_market_info
        )
        self.cpplatforms = lib.crypto_ov_coinpaprika_model.get_all_contract_platforms
        self.cpplatforms_view = lib.crypto_ov_coinpaprika_view.display_all_platforms
        self.cr = lib.crypto_ov_loanscan_model.get_rates
        self.cr_view = lib.crypto_ov_loanscan_view.display_crypto_rates
        self.crypto_hack = lib.crypto_ov_rekt_model.get_crypto_hack
        self.crypto_hack_slugs = lib.crypto_ov_rekt_model.get_crypto_hack_slugs
        self.crypto_hacks = lib.crypto_ov_rekt_model.get_crypto_hacks
        self.crypto_hacks_view = lib.crypto_ov_rekt_view.display_crypto_hacks
        self.ewf = (
            lib.crypto_ov_withdrawalfees_model.get_overall_exchange_withdrawal_fees
        )
        self.ewf_view = (
            lib.crypto_ov_withdrawalfees_view.display_overall_exchange_withdrawal_fees
        )
        self.exchanges = lib.crypto_ov_pycoingecko_model.get_exchanges
        self.exchanges_view = lib.crypto_ov_pycoingecko_view.display_exchanges
        self.global_info = lib.crypto_ov_pycoingecko_model.get_global_info
        self.list_of_coins = lib.crypto_ov_coinpaprika_model.get_list_of_coins
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_view = lib.crypto_ov_cryptopanic_view.display_news
        self.platforms = lib.crypto_ov_pycoingecko_model.get_financial_platforms
        self.platforms_view = lib.crypto_ov_pycoingecko_view.display_platforms
        self.wf = lib.crypto_ov_withdrawalfees_model.get_overall_withdrawal_fees
        self.wf_view = lib.crypto_ov_withdrawalfees_view.display_overall_withdrawal_fees
        self.wfpe = lib.crypto_ov_withdrawalfees_model.get_crypto_withdrawal_fees
        self.wfpe_view = (
            lib.crypto_ov_withdrawalfees_view.display_crypto_withdrawal_fees
        )


class CryptoTools(Category):
    """OpenBB SDK Tools Module.

    Attributes:
        `apy`: Converts apr into apy\n
        `apy_view`: Displays APY value converted from APR\n
        `il`: Calculates Impermanent Loss in a custom liquidity pool\n
        `il_view`: Displays Impermanent Loss in a custom liquidity pool\n
    """

    def __init__(self):
        super().__init__()
        self.apy = lib.crypto_tools_model.calculate_apy
        self.apy_view = lib.crypto_tools_view.display_apy
        self.il = lib.crypto_tools_model.calculate_il
        self.il_view = lib.crypto_tools_view.display_il
