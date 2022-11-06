"""OpenBB Terminal SDK Crypto Module."""
import logging

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.sdk_helpers import Category

logger = logging.getLogger(__name__)


class CryptoDueDiligence(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.trading_pairs = lib.crypto_dd_binance_model._get_trading_pairs
        self.check_valid_binance_string = (
            lib.crypto_dd_binance_model.check_valid_binance_str
        )
        self.get_binance_trading_pairs = (
            lib.crypto_dd_binance_model.get_all_binance_trading_pairs
        )
        self.binance_available_quotes_for_each_coin = (
            lib.crypto_dd_binance_model.get_binance_available_quotes_for_each_coin
        )
        self.balance = lib.crypto_dd_binance_model.get_balance
        self.balance_view = lib.crypto_dd_binance_view.display_balance
        self.book = lib.crypto_dd_binance_model.get_order_book
        self.book_view = lib.crypto_dd_binance_view.display_order_book
        self.show_available_pairs_for_given_symbol = (
            lib.crypto_dd_binance_model.show_available_pairs_for_given_symbol
        )
        self.exchanges = lib.crypto_dd_ccxt_model.get_exchanges
        self.candles = lib.crypto_dd_coinbase_model.get_candles
        self.candles_view = lib.crypto_dd_coinbase_view.display_candles
        self.cbbook = lib.crypto_dd_coinbase_model.get_order_book
        self.cbbook_view = lib.crypto_dd_coinbase_view.display_order_book
        self.stats = lib.crypto_dd_coinbase_model.get_product_stats
        self.stats_view = lib.crypto_dd_coinbase_view.display_stats
        self.trades = lib.crypto_dd_coinbase_model.get_trades
        self.trades_view = lib.crypto_dd_coinbase_view.display_trades
        self.trading_pair_info = lib.crypto_dd_coinbase_model.get_trading_pair_info
        self.oi = lib.crypto_dd_coinglass_model.get_open_interest_per_exchange
        self.oi_view = lib.crypto_dd_coinglass_view.display_open_interest
        self.basic_info = lib.crypto_dd_coinpaprika_model.basic_coin_info
        self.coin = lib.crypto_dd_coinpaprika_model.get_coin
        self.events = lib.crypto_dd_coinpaprika_model.get_coin_events_by_id
        self.events_view = lib.crypto_dd_coinpaprika_view.display_events
        self.ex = lib.crypto_dd_coinpaprika_model.get_coin_exchanges_by_id
        self.ex_view = lib.crypto_dd_coinpaprika_view.display_exchanges
        self.mkt = lib.crypto_dd_coinpaprika_model.get_coin_markets_by_id
        self.mkt_view = lib.crypto_dd_coinpaprika_view.display_markets
        self.twitter = lib.crypto_dd_coinpaprika_model.get_coin_twitter_timeline
        self.twitter_view = lib.crypto_dd_coinpaprika_view.display_twitter
        self.ohlc_historical = lib.crypto_dd_coinpaprika_model.get_ohlc_historical
        self.ps = lib.crypto_dd_coinpaprika_model.get_tickers_info_for_coin
        self.ps_view = lib.crypto_dd_coinpaprika_view.display_price_supply
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_view = lib.crypto_dd_cryptopanic_view.display_news
        self.headlines = lib.ba_finbrain_model.get_sentiment
        self.headlines_view = (
            lib.crypto_dd_crypto_finbrain_view.display_crypto_sentiment_analysis
        )
        self.active = lib.crypto_dd_glassnode_model.get_active_addresses
        self.active_view = lib.crypto_dd_glassnode_view.display_active_addresses
        self.close = lib.crypto_dd_glassnode_model.get_close_price
        self.btcrb = lib.crypto_dd_glassnode_model.get_btc_rainbow
        self.btcrb_view = lib.crypto_dd_glassnode_view.display_btc_rainbow
        self.eb = lib.crypto_dd_glassnode_model.get_exchange_balances
        self.eb_view = lib.crypto_dd_glassnode_view.display_exchange_balances
        self.change = lib.crypto_dd_glassnode_model.get_exchange_net_position_change
        self.change_view = (
            lib.crypto_dd_glassnode_view.display_exchange_net_position_change
        )
        self.nonzero = lib.crypto_dd_glassnode_model.get_non_zero_addresses
        self.nonzero_view = lib.crypto_dd_glassnode_view.display_non_zero_addresses
        self.get_mt = lib.crypto_dd_messari_model.get_available_timeseries
        self.get_mt_view = lib.crypto_dd_messari_view.display_messari_timeseries_list
        self.fr = lib.crypto_dd_messari_model.get_fundraising
        self.fr_view = lib.crypto_dd_messari_view.display_fundraising
        self.gov = lib.crypto_dd_messari_model.get_governance
        self.gov_view = lib.crypto_dd_messari_view.display_governance
        self.inv = lib.crypto_dd_messari_model.get_investors
        self.inv_view = lib.crypto_dd_messari_view.display_investors
        self.links = lib.crypto_dd_messari_model.get_links
        self.links_view = lib.crypto_dd_messari_view.display_links
        self.mcapdom = lib.crypto_dd_messari_model.get_marketcap_dominance
        self.mcapdom_view = lib.crypto_dd_messari_view.display_marketcap_dominance
        self.mt = lib.crypto_dd_messari_model.get_messari_timeseries
        self.mt_view = lib.crypto_dd_messari_view.display_messari_timeseries
        self.pi = lib.crypto_dd_messari_model.get_project_product_info
        self.pi_view = lib.crypto_dd_messari_view.display_project_info
        self.rm = lib.crypto_dd_messari_model.get_roadmap
        self.rm_view = lib.crypto_dd_messari_view.display_roadmap
        self.team = lib.crypto_dd_messari_model.get_team
        self.team_view = lib.crypto_dd_messari_view.display_team
        self.tk = lib.crypto_dd_messari_model.get_tokenomics
        self.tk_view = lib.crypto_dd_messari_view.display_tokenomics
        self.coin_market_chart = lib.crypto_dd_pycoingecko_model.get_coin_market_chart
        self.pr = lib.crypto_dd_pycoingecko_model.get_coin_potential_returns
        self.pr_view = lib.crypto_dd_pycoingecko_view.display_coin_potential_returns
        self.tokenomics = lib.crypto_dd_pycoingecko_model.get_coin_tokenomics
        self.gh = lib.crypto_dd_santiment_model.get_github_activity
        self.gh_view = lib.crypto_dd_santiment_view.display_github_activity


class CryptoDefi(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.swaps = lib.crypto_defi_graph_model.get_last_uni_swaps
        self.swaps_view = lib.crypto_defi_graph_view.display_last_uni_swaps
        self.pools = lib.crypto_defi_graph_model.get_uni_pools_by_volume
        self.pools_view = lib.crypto_defi_graph_view.display_uni_pools
        self.tokens = lib.crypto_defi_graph_model.get_uni_tokens
        self.tokens_view = lib.crypto_defi_graph_view.display_uni_tokens
        self.pairs = lib.crypto_defi_graph_model.get_uniswap_pool_recently_added
        self.pairs_view = lib.crypto_defi_graph_view.display_recently_added
        self.stats = lib.crypto_defi_graph_model.get_uniswap_stats
        self.stats_view = lib.crypto_defi_graph_view.display_uni_stats
        self.dtvl = lib.crypto_defi_llama_model.get_defi_protocol
        self.dtvl_view = lib.crypto_defi_llama_view.display_historical_tvl
        self.ldapps = lib.crypto_defi_llama_model.get_defi_protocols
        self.ldapps_view = lib.crypto_defi_llama_view.display_defi_protocols
        self.stvl = lib.crypto_defi_llama_model.get_defi_tvl
        self.stvl_view = lib.crypto_defi_llama_view.display_defi_tvl
        self.gdapps = lib.crypto_defi_llama_model.get_grouped_defi_protocols
        self.gdapps_view = lib.crypto_defi_llama_view.display_grouped_defi_protocols
        self.luna_supply = lib.crypto_defi_smartstake_model.get_luna_supply_stats
        self.luna_supply_view = (
            lib.crypto_defi_smartstake_view.display_luna_circ_supply_change
        )
        self.newsletters = lib.crypto_defi_substack_model.get_newsletters
        self.newsletters_view = lib.crypto_defi_substack_view.display_newsletters
        self.aterra = (
            lib.crypto_defi_terraengineer_model.get_history_asset_from_terra_address
        )
        self.aterra_view = (
            lib.crypto_defi_terraengineer_view.display_terra_asset_history
        )
        self.ayr = lib.crypto_defi_terraengineer_model.get_anchor_yield_reserve
        self.ayr_view = lib.crypto_defi_terraengineer_view.display_anchor_yield_reserve
        self.gacc = lib.crypto_defi_terramoney_fcd_model.get_account_growth
        self.gacc_view = lib.crypto_defi_terramoney_fcd_view.display_account_growth
        self.gov_proposals = lib.crypto_defi_terramoney_fcd_model.get_proposals
        self.gov_proposals_view = (
            lib.crypto_defi_terramoney_fcd_view.display_gov_proposals
        )
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
        self.validators = lib.crypto_defi_terramoney_fcd_model.get_validators
        self.validators_view = lib.crypto_defi_terramoney_fcd_view.display_validators


class CryptoDiscovery(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.cmctop = lib.crypto_disc_coinmarketcap_model.get_cmc_top_n
        self.cmctop_view = lib.crypto_disc_coinmarketcap_view.display_cmc_top_coins
        self.cpsearch = lib.crypto_disc_coinpaprika_model.get_search_results
        self.cpsearch_view = lib.crypto_disc_coinpaprika_view.display_search_results
        self.top_dapps = lib.crypto_disc_dappradar_model.get_top_dapps
        self.top_dapps_view = lib.crypto_disc_dappradar_view.display_top_dapps
        self.top_dexes = lib.crypto_disc_dappradar_model.get_top_dexes
        self.top_dexes_view = lib.crypto_disc_dappradar_view.display_top_dexes
        self.top_games = lib.crypto_disc_dappradar_model.get_top_games
        self.top_games_view = lib.crypto_disc_dappradar_view.display_top_games
        self.top_nfts = lib.crypto_disc_dappradar_model.get_top_nfts
        self.top_nfts_view = lib.crypto_disc_dappradar_view.display_top_nfts
        self.categories_keys = lib.crypto_disc_pycoingecko_model.get_categories_keys
        self.coin_list = lib.crypto_disc_pycoingecko_model.get_coin_list
        self.coins = lib.crypto_disc_pycoingecko_model.get_coins
        self.coins_view = lib.crypto_disc_pycoingecko_view.display_coins
        self.coins_for_given_exchange = (
            lib.crypto_disc_pycoingecko_model.get_coins_for_given_exchange
        )
        self.gainers_or_losers = lib.crypto_disc_pycoingecko_model.get_gainers_or_losers
        self.gainers = lib.crypto_disc_pycoingecko_model.get_gainers
        self.gainers_view = lib.crypto_disc_pycoingecko_view.display_gainers
        self.losers = lib.crypto_disc_pycoingecko_model.get_losers
        self.losers_view = lib.crypto_disc_pycoingecko_view.display_losers
        self.trending = lib.crypto_disc_pycoingecko_model.get_trending_coins
        self.trending_view = lib.crypto_disc_pycoingecko_view.display_trending


class CryptoOnChain(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.hr = lib.crypto_dd_glassnode_model.get_hashrate
        self.hr_view = lib.crypto_dd_glassnode_view.display_hashrate
        self.dvcp = (
            lib.crypto_onchain_bitquery_model.get_daily_dex_volume_for_given_pair
        )
        self.dvcp_view = (
            lib.crypto_onchain_bitquery_view.display_daily_volume_for_given_pair
        )
        self.lt = lib.crypto_onchain_bitquery_model.get_dex_trades_by_exchange
        self.lt_view = lib.crypto_onchain_bitquery_view.display_dex_trades
        self.dex_trades_monthly = (
            lib.crypto_onchain_bitquery_model.get_dex_trades_monthly
        )
        self.erc20_tokens = lib.crypto_onchain_bitquery_model.get_erc20_tokens
        self.ueat = lib.crypto_onchain_bitquery_model.get_ethereum_unique_senders
        self.ueat_view = (
            lib.crypto_onchain_bitquery_view.display_ethereum_unique_senders
        )
        self.ttcp = lib.crypto_onchain_bitquery_model.get_most_traded_pairs
        self.ttcp_view = lib.crypto_onchain_bitquery_view.display_most_traded_pairs
        self.baas = lib.crypto_onchain_bitquery_model.get_spread_for_crypto_pair
        self.baas_view = lib.crypto_onchain_bitquery_view.display_spread_for_crypto_pair
        self.tv = lib.crypto_onchain_bitquery_model.get_token_volume_on_dexes
        self.tv_view = lib.crypto_onchain_bitquery_view.display_dex_volume_for_token
        self.query_graph = lib.crypto_onchain_bitquery_model.query_graph
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
        self.gwei = lib.crypto_onchain_ethgasstation_model.get_gwei_fees
        self.gwei_view = lib.crypto_onchain_ethgasstation_view.display_gwei_fees
        self.hist = lib.crypto_onchain_ethplorer_model.get_address_history
        self.hist_view = lib.crypto_onchain_ethplorer_view.display_address_history
        self.balance = lib.crypto_onchain_ethplorer_model.get_address_info
        self.balance_view = lib.crypto_onchain_ethplorer_view.display_address_info
        self.token_decimals = lib.crypto_onchain_ethplorer_model.get_token_decimals
        self.prices = lib.crypto_onchain_ethplorer_model.get_token_historical_price
        self.prices_view = (
            lib.crypto_onchain_ethplorer_view.display_token_historical_prices
        )
        self.th = lib.crypto_onchain_ethplorer_model.get_token_history
        self.th_view = lib.crypto_onchain_ethplorer_view.display_token_history
        self.info = lib.crypto_onchain_ethplorer_model.get_token_info
        self.info_view = lib.crypto_onchain_ethplorer_view.display_token_info
        self.holders = lib.crypto_onchain_ethplorer_model.get_top_token_holders
        self.holders_view = lib.crypto_onchain_ethplorer_view.display_top_token_holders
        self.top = lib.crypto_onchain_ethplorer_model.get_top_tokens
        self.top_view = lib.crypto_onchain_ethplorer_view.display_top_tokens
        self.tx = lib.crypto_onchain_ethplorer_model.get_tx_info
        self.tx_view = lib.crypto_onchain_ethplorer_view.display_tx_info
        self.whales = lib.crypto_onchain_whale_alert_model.get_whales_transactions
        self.whales_view = (
            lib.crypto_onchain_whale_alert_view.display_whales_transactions
        )


class CryptoOverview(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.altindex = lib.crypto_ov_blockchaincenter_model.get_altcoin_index
        self.altindex_view = lib.crypto_ov_blockchaincenter_view.display_altcoin_index
        self.cbpairs = lib.crypto_ov_coinbase_model.get_trading_pairs
        self.cbpairs_view = lib.crypto_ov_coinbase_view.display_trading_pairs
        self.cpplatforms = lib.crypto_ov_coinpaprika_model.get_all_contract_platforms
        self.cpplatforms_view = lib.crypto_ov_coinpaprika_view.display_all_platforms
        self.cpinfo = lib.crypto_ov_coinpaprika_model.get_coins_info
        self.cpinfo_view = lib.crypto_ov_coinpaprika_view.display_all_coins_info
        self.cpmarkets = lib.crypto_ov_coinpaprika_model.get_coins_market_info
        self.cpmarkets_view = (
            lib.crypto_ov_coinpaprika_view.display_all_coins_market_info
        )
        self.cpcontracts = lib.crypto_ov_coinpaprika_model.get_contract_platform
        self.cpcontracts_view = lib.crypto_ov_coinpaprika_view.display_contracts
        self.cpexmarkets = lib.crypto_ov_coinpaprika_model.get_exchanges_market
        self.cpexmarkets_view = lib.crypto_ov_coinpaprika_view.display_exchange_markets
        self.cpglobal = lib.crypto_ov_coinpaprika_model.get_global_market
        self.cpglobal_view = lib.crypto_ov_coinpaprika_view.display_global_market
        self.list_of_coins = lib.crypto_ov_coinpaprika_model.get_list_of_coins
        self.cpexchanges = lib.crypto_ov_coinpaprika_model.get_list_of_exchanges
        self.cpexchanges_view = lib.crypto_ov_coinpaprika_view.display_all_exchanges
        self.news = lib.crypto_ov_cryptopanic_model.get_news
        self.news_view = lib.crypto_ov_cryptopanic_view.display_news
        self.cr = lib.crypto_ov_loanscan_model.get_rates
        self.cr_view = lib.crypto_ov_loanscan_view.display_crypto_rates
        self.cgderivatives = lib.crypto_ov_pycoingecko_model.get_derivatives
        self.cgderivatives_view = lib.crypto_ov_pycoingecko_view.display_derivatives
        self.cgexrates = lib.crypto_ov_pycoingecko_model.get_exchange_rates
        self.cgexrates_view = lib.crypto_ov_pycoingecko_view.display_exchange_rates
        self.exchanges = lib.crypto_ov_pycoingecko_model.get_exchanges
        self.exchanges_view = lib.crypto_ov_pycoingecko_view.display_exchanges
        self.cgproducts = lib.crypto_ov_pycoingecko_model.get_finance_products
        self.cgproducts_view = lib.crypto_ov_pycoingecko_view.display_products
        self.platforms = lib.crypto_ov_pycoingecko_model.get_financial_platforms
        self.platforms_view = lib.crypto_ov_pycoingecko_view.display_platforms
        self.cgdefi = lib.crypto_ov_pycoingecko_model.get_global_defi_info
        self.cgdefi_view = lib.crypto_ov_pycoingecko_view.display_global_defi_info
        self.global_info = lib.crypto_ov_pycoingecko_model.get_global_info
        self.cgglobal = lib.crypto_ov_pycoingecko_model.get_global_markets_info
        self.cgglobal_view = lib.crypto_ov_pycoingecko_view.display_global_market_info
        self.cghold = lib.crypto_ov_pycoingecko_model.get_holdings_overview
        self.cghold_view = lib.crypto_ov_pycoingecko_view.display_holdings_overview
        self.cgindexes = lib.crypto_ov_pycoingecko_model.get_indexes
        self.cgindexes_view = lib.crypto_ov_pycoingecko_view.display_indexes
        self.cgstables = lib.crypto_ov_pycoingecko_model.get_stable_coins
        self.cgstables_view = lib.crypto_ov_pycoingecko_view.display_stablecoins
        self.cgcategories = lib.crypto_ov_pycoingecko_model.get_top_crypto_categories
        self.cgcategories_view = lib.crypto_ov_pycoingecko_view.display_categories
        self.cgh = lib.crypto_ov_pycoingecko_model.get_coins
        self.cgh_view = lib.crypto_ov_pycoingecko_view.display_crypto_heatmap
        self.crypto_hack = lib.crypto_ov_rekt_model.get_crypto_hack
        self.crypto_hack_slugs = lib.crypto_ov_rekt_model.get_crypto_hack_slugs
        self.crypto_hacks = lib.crypto_ov_rekt_model.get_crypto_hacks
        self.crypto_hacks_view = lib.crypto_ov_rekt_view.display_crypto_hacks
        self.wfpe = lib.crypto_ov_withdrawalfees_model.get_crypto_withdrawal_fees
        self.wfpe_view = (
            lib.crypto_ov_withdrawalfees_view.display_crypto_withdrawal_fees
        )
        self.ewf = (
            lib.crypto_ov_withdrawalfees_model.get_overall_exchange_withdrawal_fees
        )
        self.ewf_view = (
            lib.crypto_ov_withdrawalfees_view.display_overall_exchange_withdrawal_fees
        )
        self.wf = lib.crypto_ov_withdrawalfees_model.get_overall_withdrawal_fees
        self.wf_view = lib.crypto_ov_withdrawalfees_view.display_overall_withdrawal_fees


class CryptoTools(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.apy = lib.crypto_tools_model.calculate_apy
        self.apy_view = lib.crypto_tools_view.display_apy
        self.il = lib.crypto_tools_model.calculate_il
        self.il_view = lib.crypto_tools_view.display_il
